import re
import difflib
import Levenshtein
import numpy as np 
from simhash import Simhash
from lxml import etree as ET
import os
import glob

def normalize_file(path): # remove whitespace and convert to lowercase
    lines = open(path, "r").readlines()
    return [re.sub(r'\s+', ' ', l).strip().lower() for l in lines]
    
def simhash_pairs(candidates, k=15): # k = 15 from project slides
    l_candidates, r_candidates = candidates
    
    res = []
    for li, l_cand in l_candidates:
        l_hash = Simhash(l_cand)

        r_dists = sorted([ # (cand, dist) pairs
            ((ri, r_cand), l_hash.distance(Simhash(r_cand))) for ri, r_cand in r_candidates
        ], key=lambda x: x[1]) # sort ascending, as lower = closer
            
        for r_cand, dist in r_dists[:k]:
            res.append(((li, l_cand), r_cand))
        
    return res
            
def cosine_similarity(context1, context2):
    # get word frequency for each context
    context1_words = " ".join(context1).lower().split()
    context2_words = " ".join(context2).lower().split()

    vocab = set(context1_words + context2_words)
    if len(vocab) == 0: return 1.0 # empty context edgecase

    context_vec_1 = np.array([context1_words.count(w) for w in vocab])
    context_vec_2 = np.array([context2_words.count(w) for w in vocab])
    
    # calculate cosine similarity with frequency vectors
    dot = np.dot(context_vec_1, context_vec_2)
    
    norm_1 = np.linalg.norm(context_vec_1)
    norm_2 = np.linalg.norm(context_vec_2)
    
    if norm_1 == 0 or norm_2 == 0: return 0.0 # edgecase

    return dot / (norm_1 * norm_2)

def write_mappings_to_XML(mappings, test_name, test_num, output='output/'):
    root = ET.Element("TEST")
    root.set("NAME", "TEST " + str(test_num))
    root.set("FILE", test_name)

    for i, mapping in enumerate(mappings):
        version = ET.SubElement(root, "VERSION")
        version.set("NUMBER", str(i + 1))
        version.set("CHECKED", "TRUE")

        for l, rs_ in mapping:
            rs = rs_.copy()
            r = rs.pop()
            location = ET.SubElement(version, "LOCATION")
            location.set("ORIG", str(l))
            location.set("NEW", str(r))

            while len(rs):
                r = rs.pop()
                alt = ET.SubElement(location, "ALT")
                alt.set("NEW", str(r))
    
    tree = ET.ElementTree(root)

    os.makedirs(output, exist_ok=True)
    tree.write(output + test_name + ".xml", pretty_print=True)

if __name__ == "__main__":
    # provided dataset
    prov_path = "./datasets/provided/"
    prov_files = [
        "asdf", "ASTResolving", "ArrayReference", "BaseTypes",
        "BuildPathsPropertyPage", "CPListLabelProvider", 
        "CompilationUnitDocumentProvider", "DeltaProcessor",
        "DialogCustomize", "DirectoryDialog", "DoubleCache",
        "FontData", "GC", "GC2", "JavaCodeScanner",
        "JavaModelManager", "JavaPerspectiveFactory",
        "PluginSearchScope", "RefreshLocal", "ResourceCompareInput",
        "ResourceInfo", "SaveManager", "TabFolder"
    ]

    prov_dataset = [
        (i + 1, f, sorted(glob.glob(f"{prov_path}{f}_*")))
        for i, f in enumerate(prov_files)
    ]

    # TODO : custom dataset

    # select, prepare, normalize dataset
    selected_dataset = prov_dataset
    normalized_dataset = [
        (test_num, name, [normalize_file(f) for f in ds]) for test_num, name, ds in selected_dataset
    ]

    differ = difflib.Differ()
    for test_num, name, ds in normalized_dataset:
        print(f"Processing test {test_num}: {name}")
        pairs = [(i, i+1) for i in range(len(ds) - 1)]
        # TODO : his only checks them all against the first???

        output = [[(i, [i]) for i in range(1, len(ds[0]) + 1)]]
        for i, j in pairs:
            mappings, l_matched, r_matched = {}, set(), set()

            # generate candidates (lines unique to each side)
            candidates, l, r = ([], []), 1, 1
            for d in differ.compare(ds[i], ds[j]):
                if d.startswith('-'):
                    candidates[0].append((l, d[2:]))
                    l += 1
                elif d.startswith('+'):
                    candidates[1].append((r, d[2:]))
                    r += 1
                elif d.startswith(' '):
                    mappings[l] = r
                    l_matched.add(l)
                    r_matched.add(r)

                    l += 1
                    r += 1

            # select top 15 pairs based on simhash
            candidate_pairs = simhash_pairs(candidates)
            
            # for each candidate pair, we calculate the levenstein distance and cosine similarity
            similarities = []
            for l, r in candidate_pairs:
                ls, rs = l[1], r[1]

                # calculate content sim with levenstein distance
                content_sim = Levenshtein.ratio(ls, rs)
                
                li, ri = l[0] - 1, r[0] - 1
                # get context for left and right candidates (for cosine similarity)
                window = 4 # we use 4, per the project slides
                l_context = ds[i][(max(0, li - window)):(min(len(ds[i]), li + window + 1))]
                r_context = ds[j][(max(0, ri - window)):(min(len(ds[j]), ri + window + 1))]

                # calculate context sim with cosine similarity
                context_sim = cosine_similarity(l_context, r_context)

                alpha = 0.6
                combine_sim = alpha * content_sim + (1 - alpha) * context_sim
                similarities.append((li + 1, ri + 1, combine_sim))
            
            similarities = sorted(similarities, key=lambda x: x[2], reverse=True)
            
            # assign mappings greedily based on our scores
            threshold = 0.6
            for l_line, r_line, sim in similarities:
                if sim < threshold: break # sorted, so all further scores are below threshold
                if l_line in l_matched or r_line in r_matched: 
                    continue # already matched

                l_matched.add(l_line)
                r_matched.add(r_line)

                r_lines = [r_line]
                while True:
                    strs_no_change = [ds[j][l] for l in range(r_lines[0] - 1, r_lines[-1])]
                    strs_backward, strs_forward = None, None
                    if r_lines[-1] < len(ds[j]) and r_lines[-1] + 1 not in r_matched:
                        strs_forward = [ds[j][l] for l in range(r_lines[0] - 1, r_lines[-1] + 1)]
                    if r_lines[0] > 1 and r_lines[0] - 1 not in r_matched:
                        strs_backward = [ds[j][l] for l in range(r_lines[0] - 2, r_lines[-1])]

                    # calculate ratios for no move, forward, and backward
                    ratios = [
                        Levenshtein.ratio(ds[i][l_line - 1], " ".join(strs_no_change)),
                        Levenshtein.ratio(ds[i][l_line - 1], " ".join(strs_backward))
                            if strs_backward is not None else 0,
                        Levenshtein.ratio(ds[i][l_line - 1], " ".join(strs_forward))
                            if strs_forward is not None else 0,
                    ]

                    # if adding forwards or backwards improves, do it
                    if max(ratios) == ratios[0]:
                        break
                    elif max(ratios) == ratios[1]:
                        r_lines.insert(0, r_lines[0] - 1)
                        r_matched.add(r_lines[0])
                    elif max(ratios) == ratios[2]:
                        r_lines.append(r_lines[-1] + 1)
                        r_matched.add(r_lines[-1])

                mappings[l_line] = r_lines

            m = []
            for i in range(1, len(ds[i]) + 1):
                r = mappings.get(i, -1)
                if not isinstance(r, list): r = [r]
                m.append((i, r))
            for i in [i for i in range(1, len(ds[j]) + 1) if i not in r_matched]:
                m.append((-1, [i]))

            output.append(sorted(m, key=lambda x: x[0]))
            
        write_mappings_to_XML(output, name, test_num)