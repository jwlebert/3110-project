import re
import difflib
import Levenshtein
import numpy as np 
from simhash import Simhash

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

if __name__ == "__main__":
    dataset = [
        # [
        #     "./datasets/provided/asdf_1.java", 
        #     "./datasets/provided/asdf_2.java"
        # ],
        [
            "./datasets/provided/RefreshLocal_1.java",
            "./datasets/provided/RefreshLocal_2.java"
        ],
        # [
        #     "./datasets/provided/DeltaProcessor_1.java",
        #     "./datasets/provided/DeltaProcessor_2.java"    
        # ],
        # [
        #     "./datasets/provided/BaseTypes_1.java", 
        #     "./datasets/provided/BaseTypes_2.java",
        #     "./datasets/provided/BaseTypes_3.java",
        #     "./datasets/provided/BaseTypes_4.java",
        #     "./datasets/provided/BaseTypes_5.java",
        #     "./datasets/provided/BaseTypes_6.java",
        #     "./datasets/provided/BaseTypes_7.java"
        # ],
    ]

    normalized_dataset = [[normalize_file(f) for f in ds] for ds in dataset]

    differ = difflib.Differ()
    for ds in normalized_dataset:
        pairs = [(i, i+1) for i in range(len(ds) - 1)]
        # TODO : his only checks them all against the first???

        for i, j in pairs:
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
                    l += 1
                    r += 1

            # select top 15 pairs based on simhash
            candidate_pairs = simhash_pairs(candidates)
            print([l for l, _ in candidates[0]])
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
            mappings, threshold = [], 0.7
            l_matched, r_matched = set(), set()
            for l_line, r_line, sim in similarities:
                if sim < threshold: break # sorted, so all further scores are below threshold
                if l_line in l_matched or r_line in r_matched: 
                    continue # already matched

                mappings.append((l_line, r_line))
                l_matched.add(l_line)
                r_matched.add(r_line)

            for l_line, r_line, sim in similarities[:20]:  # Top 20
                print(f"{l_line}→{r_line}: {sim:.3f}")

            print(sorted(mappings, key=lambda x: x[0]))