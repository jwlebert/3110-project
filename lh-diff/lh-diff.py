import re
import difflib

def normalize_file(path):
    lines = open(path, "r").readlines()
    return [re.sub(r'\s+', ' ', l).strip() for l in lines]
    

if __name__ == "__main__":
    dataset = [
        [
            "../datasets/provided/ArrayReference_1.java", 
            "../datasets/provided/ArrayReference_2.java"
        ]
    ]

    normalized_dataset = [[normalize_file(f) for f in ds] for ds in dataset]
    candidates = []

    differ = difflib.Differ()
    for ds in normalized_dataset:
        pairs = [(i, i+1) for i in range(len(ds) - 1)]
        for i, j in pairs:
            pair = ([], [])
            for d in differ.compare(ds[i], ds[j]):
                if d.startswith('-'):
                    pair[0].append(d[2:])
                elif d.startswith('+'):
                    pair[1].append(d[2:])
            candidates.append(pair)
    
    print(candidates[0][0])
    print(candidates[0][1])
    