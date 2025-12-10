# LHDiff

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python3 lh-diff/lh-diff.py
```

Output goes to `output/` as XML files.

## File Structure

## Project Structure

```
├── lh-diff/
│   └── lh-diff.py      # LHDiff implementation
├── datasets/
│   └── provided/       # Test datasets + ground truth
│   └── custom/         # add new datasets here...
├── output/             # Generated XML mappings
└── requirements.txt
```

## Tunable Parameters

In `lh-diff.py`:

| Variable | Default | Description |
|----------|---------|-------------|
| `alpha` | 0.6 | Weight: content (higher) vs context (lower) |
| `threshold` | 0.6 | Minimum similarity to match |
| `k` | 15 | SimHash candidates per line |
| `window` | 4 | Context lines for similarity |

## Adding a New Dataset

1. Add files to `datasets/your_dataset/` as `Name_1.java`, `Name_2.java`, etc.

2. In `lh-diff.py`, add your dataset config:
```python
custom_path = "./datasets/your_dataset/"
custom_files = ["Name1", "Name2", ...]
custom_dataset = [
    (i + 1, f, sorted(glob.glob(f"{custom_path}{f}_*")))
    for i, f in enumerate(custom_files)
]
```

3. Set `selected_dataset = custom_dataset`