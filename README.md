# GRAPE: Graph Analysis and Phylogenetic Estimation

GRAPE is a Python library for phylogenetic inference using community detection in graphs. It applies graph-based community detection algorithms to linguistic cognate data to reconstruct phylogenetic trees, offering a novel computational approach to historical linguistics.

![GRAPE Logo](docs/grape_logo_small.png)

## 🚀 Quick Start

```bash
# Basic analysis
python grape.py data/iecor_small.tsv

# With specific parameters  
python grape.py data/dravlex.tsv --graph adjusted --community louvain --strategy fixed --initial_value 0.5
```

## ✨ Features

- **Multiple Community Detection Algorithms**: Louvain and Greedy Modularity methods
- **Flexible Graph Construction**: Adjusted and unadjusted linguistic distance weighting
- **Parameter Optimization**: Fixed, dynamic, and adaptive parameter search strategies  
- **Comprehensive Testing**: Validated on 7 major language families with 200+ languages
- **Standard Output**: Newick format trees compatible with phylogenetic software
- **Scientific Validation**: Results align with established linguistic classifications

## 🛠️ Installation

### Requirements

- Python 3.7+
- NetworkX
- ETE3
- NumPy
- Six (required by ETE3)

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Optional Dependencies

For distance-based phylogenetic methods:
```bash
pip install biopython
```

## 🔥 Quick Examples

### Dravidian Language Family
```bash  
python grape.py data/dravlex.tsv --graph adjusted --community louvain
```
Demonstrates South, Central, and North Dravidian groupings.

### Germanic Languages
```bash
python grape.py data/harald_ie.tsv --concept-column Concept
```
Reconstructs Indo-European phylogeny showing Germanic monophyly.

### Polynesian Languages
```bash
python grape.py data/walworthpolynesian.tsv --strategy dynamic --initial_value 0.6
```
Shows Tongic vs. Nuclear Polynesian classification.

### Large-Scale Analysis (160 Indo-European Languages)
```bash
python grape.py data/iecor_full.tsv --strategy adaptive --initial_value 0.2
```
Full Indo-European family with all major branches.

## 🌍 Supported Language Families

GRAPE has been tested and validated on:

| Family | Dataset | Languages | Key Groupings Validated |
|--------|---------|-----------|------------------------|
| **Indo-European** | `harald_ie.tsv`, `iecor_full.tsv` | 160 | Germanic, Romance, Celtic, Slavic, Indo-Iranian |
| **Dravidian** | `dravlex.tsv` | 19 | South, Central, North Dravidian |
| **Polynesian** | `walworthpolynesian.tsv` | 30 | Tongic, Nuclear Polynesian, Eastern Polynesian |
| **Tupian** | `tuled.tsv` | 30+ | Guaranic group, early branching patterns |
| **Arawakan** | `chaconarawakan.tsv` | 8 | Northern Arawakan geographic clustering |

## 📖 Documentation

### For Users
- [**Quick Start Guide**](docs/user_guide/quickstart.md) - Get up and running in 5 minutes
- [**Complete Dravidian Walkthrough**](docs/examples/dravidian_walkthrough.md) - Step-by-step analysis
- [**Parameter Guide**](docs/user_guide/parameters.md) - Understanding all options

### For Researchers  
- [**Mathematical Background**](docs/technical/mathematical_background.md) - Community detection theory
- [**Implementation Details**](docs/technical/implementation.md) - Algorithm specifics
- [**Academic Paper Draft**](docs/academic/grape_paper.md) - Research foundations

### Interactive Examples
- [**Jupyter Notebook**](docs/examples/grape_analysis.ipynb) - Executable examples
- [**Advanced Usage**](docs/examples/advanced_usage.md) - Complex scenarios

## 🌳 Tree Visualizations

GRAPE generates detailed phylogenetic tree visualizations for all language families:

- **ASCII Trees**: Text-based tree representations for documentation and analysis
- **Linguistic Analysis**: Automatic validation of established language groupings
- **Multiple Formats**: Newick, formatted text, and summary statistics

**Available visualizations:**
- [Dravidian Tree](docs/images/trees/dravidian_formatted.txt) - 20 languages, 3 major branches
- [Polynesian Tree](docs/images/trees/polynesian_formatted.txt) - 31 languages, Tongic vs. Nuclear
- [Indo-European Tree](docs/images/trees/indo-european_formatted.txt) - Germanic subfamily
- [Tupian Tree](docs/images/trees/tupian_formatted.txt) - 29 languages, Guaranic group
- [Arawakan Tree](docs/images/trees/arawakan_formatted.txt) - 8 languages, Northern cluster

All visualizations include:
- Tree statistics (height, number of languages)
- ASCII art representation
- Linguistic grouping analysis
- Complete language lists

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Core functionality
python test_grape.py -v

# Additional language families  
python test_additional_families.py -v

# Parameter robustness
python test_grape_extended.py -v
python test_additional_families_extended.py -v
```

**Test Coverage**: 40+ test cases across 7 language families validating phylogenetic accuracy against linguistic consensus.

## 💡 Algorithm Overview

GRAPE transforms cognate data into weighted graphs where:
1. **Nodes** represent languages
2. **Edges** weighted by linguistic distances (cognate sharing patterns)
3. **Community detection** identifies language groups at multiple resolutions
4. **Hierarchical clustering** builds phylogenetic trees from community structure

This approach captures both vertical inheritance and horizontal borrowing patterns in language evolution.

## 📊 Performance

- **Small datasets** (< 30 languages): < 1 second
- **Medium datasets** (30-50 languages): 1-10 seconds  
- **Large datasets** (100+ languages): 30-120 seconds

Memory usage scales linearly with dataset size.

## 🔗 Related Work

- **NetworkX**: Graph algorithms and community detection
- **ETE3**: Tree manipulation and visualization  
- **BioPython**: Traditional phylogenetic methods (NJ, UPGMA)
- **Cognate databases**: IELEX, ASJP, and regional datasets

## Community guidelines

While the author can be contacted directly for support, it is recommended that
third parties use GitHub standard features, such as issues and pull requests, to
contribute, report problems, or seek support.

Contributing guidelines, including a code of conduct, can be found in the
`CONTRIBUTING.md` file.

## Author and citation

The library is developed by Tiago Tresoldi (tiago@tresoldi.com). The library was developed in the context of
the [Cultural Evolution of Texts](https://github.com/evotext/) project, with funding from the
[Riksbankens Jubileumsfond](https://www.rj.se/) (grant agreement ID:
[MXM19-1087:1](https://www.rj.se/en/anslag/2019/cultural-evolution-of-texts/)).

If you use `grape`, please cite it as:
