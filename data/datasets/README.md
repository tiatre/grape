Instructions
============

Installing the full Lexibank system for installing the data is complex and not necessary for our approach,
introducing a number of dependencies that we would prefer not to deal with. The `extract_lexicore.py`
script in this directory is a pure Python, no dependencies, script for extracting the datasets
from "lexicore" (the set of high quality datasets) into single, denormalized, tabular
files. We only keep the ones with cognate annotation, which should to a large extent match "cogcore".

To reproduce:

1. Install the current version of "lexibank-analysed" (using a virtual environment
is highly recommended):

```bash
git clone https://github.com/lexibank/lexibank-analysed
cd lexibank-analysed
pip install -e .
```

2. Download all the collections:

```bash
cldfbench download lexibank_lexibank_analysed.py
```

3. Run the script to extract them:

```bash
python extract_lexicore.py
```