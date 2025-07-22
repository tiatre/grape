# GRAPE: Graph Analysis and Phylogenetic Estimation

GRAPE is a Python library for phylogenetic inference using community detection in graphs. It applies graph-based community detection algorithms to linguistic cognate data to reconstruct phylogenetic trees, offering a novel computational approach to historical linguistics.

![GRAPE Logo](docs/grape_logo_small.png)

## 🚀 Quick Start

```bash
# Basic analysis with reproducible results
python grape.py resources/language_families/romance.tsv --seed 42

# Advanced analysis with specific parameters  
python grape.py resources/language_families/austroasiatic.tsv --graph adjusted --community louvain --strategy fixed --initial_value 0.3 --seed 42
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

### Romance Languages (Europe)
```bash
python grape.py resources/language_families/romance.tsv --strategy fixed --initial_value 0.4 --seed 42
```
Western European languages descended from Latin, showing dialectal differentiation across Italy, Spain, France, and Romania.

### Austroasiatic Languages (Southeast Asia)
```bash
python grape.py resources/language_families/austroasiatic.tsv --strategy fixed --initial_value 0.3 --seed 42
```
Southeast Asian family including Vietnamese, Khmer, and many smaller languages across the Mekong region.

### Turkic Languages (Central Asia)
```bash
python grape.py resources/language_families/turkic.tsv --community greedy --strategy fixed --initial_value 0.5 --seed 42
```
Agglutinative languages with vowel harmony, spread from Turkey to Siberia through nomadic migrations.

### Dravidian Languages (South India)
```bash
python grape.py resources/language_families/dravidian.tsv --strategy fixed --initial_value 0.5 --seed 42
```
South Indian language family demonstrating clear South, Central, and North Dravidian subgroupings.

## 🌍 Comprehensive Language Family Coverage

GRAPE has been tested and validated on 7 major language families representing diverse geographic regions and typological characteristics:

| Family | Dataset | Languages | Geographic Distribution | Typology |
|--------|---------|-----------|------------------------|----------|
| **Romance** | `romance.tsv` | 43 | Western/Southern Europe | Fusional, rich morphology |
| **Austroasiatic** | `austroasiatic.tsv` | 109 | Southeast Asia | Isolating/analytic |  
| **Turkic** | `turkic.tsv` | 32 | Central Asia, Turkey | Agglutinative, vowel harmony |
| **Bantu** | `bantu.tsv` | 424 | Sub-Saharan Africa | Agglutinative, noun classes |
| **Dravidian** | `dravidian.tsv` | 20 | South India | Agglutinative |
| **Polynesian** | `polynesian.tsv` | 31 | Pacific Islands | Mixed morphology |
| **Tupian** | `tupian.tsv` | 91 | Amazon Basin | Mixed strategies |

### Key Subgroupings Validated

**Romance**: Italian, Iberian, Gallo-Romance, Eastern Romance branches  
**Austroasiatic**: Mon-Khmer, Munda, Bahnaric, Katuic divisions  
**Turkic**: Oghuz, Kipchak, Karluk, Siberian branches  
**Bantu**: Eastern, Southern, Western, Central geographic clusters  
**Dravidian**: South, Central, North Dravidian classification  
**Polynesian**: Tongic vs Nuclear Polynesian split  
**Tupian**: Guaranic group, early branching patterns

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
- [Romance Tree](docs/images/trees/romance_formatted.txt) - 43 languages, European branches
- [Austroasiatic Tree](docs/images/trees/austroasiatic_formatted.txt) - 109 languages, SE Asian diversity
- [Turkic Tree](docs/images/trees/turkic_formatted.txt) - 32 languages, Central Asian spread
- [Dravidian Tree](docs/images/trees/dravidian_formatted.txt) - 20 languages, South Indian branches
- [Polynesian Tree](docs/images/trees/polynesian_formatted.txt) - 31 languages, Pacific migration
- [Tupian Tree](docs/images/trees/tupian_formatted.txt) - 91 languages, Amazonian diversity

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
