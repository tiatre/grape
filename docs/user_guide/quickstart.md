# GRAPE Quick Start Guide

Get up and running with GRAPE in 5 minutes! This guide covers installation, basic usage, and your first phylogenetic analysis.

## Prerequisites

- Python 3.7 or higher
- Basic familiarity with command line
- Linguistic cognate data in TSV format

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-repo/grape.git
cd grape
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Verify Installation
```bash
python grape.py --help
```

You should see GRAPE's help message with all available options.

## Your First Analysis

### Quick Test with Sample Data

Run GRAPE on the small Indo-European dataset:

```bash
python grape.py data/iecor_small.tsv
```

**Expected Output:**
```
[INFO] Reading cognate file: data/iecor_small.tsv
[INFO] Loaded 845 cognate entries for 8 languages across 100 concepts
[INFO] Building graph with method: adjusted
[INFO] Graph created with 8 nodes and 28 edges
[INFO] Using community detection: LouvainCommunities
[INFO] Using parameter strategy: DynamicParameterStrategy
[INFO] Initial resolution: 1.0
[INFO] Community detection completed
[INFO] Converting communities to tree structure
[INFO] Final tree constructed with 8 leaves
[INFO] Newick format tree: ((English:0.4,German:0.4):0.2,((Danish:0.3,Swedish:0.3):0.1,(Dutch:0.3,Frisian:0.3):0.1):0.2);
```

**Interpreting the Output:**
- The tree shows Germanic language relationships
- English and German group together
- Danish and Swedish form a Scandinavian group
- Dutch and Frisian cluster as West Germanic
- Branch lengths indicate evolutionary distances

### Save Results to File

```bash
python grape.py data/iecor_small.tsv > my_first_tree.newick 2> analysis.log
```

Now you have:
- `my_first_tree.newick`: The phylogenetic tree in Newick format
- `analysis.log`: Detailed log of the analysis process

## Understanding Your Data

### Required Data Format

GRAPE expects TSV (Tab-Separated Values) files with three columns:

```
Language    Parameter   Cognateset
English     I           i.001
German      I           i.001
Danish      I           i.001
English     water       water.002
German      water       water.001
Danish      water       water.003
```

**Column Meanings:**
- **Language**: Name of the language variety
- **Parameter**: Concept or meaning being compared
- **Cognateset**: Identifier for cognate relationships (same ID = cognate)

### Data Quality Tips

1. **Consistent naming**: Use the same language names throughout
2. **Cognate consistency**: Languages with the same cognate set ID should be historically related
3. **Missing data**: Simply omit rows for missing language-concept pairs
4. **Multiple words**: Use separate rows for synonyms (different cognate sets for same concept)

## Basic Command Options

### Essential Options

```bash
# Specify graph construction method
python grape.py data/your_data.tsv --graph adjusted      # Default: handles synonyms
python grape.py data/your_data.tsv --graph unadjusted    # Simple cognate counting

# Choose community detection algorithm  
python grape.py data/your_data.tsv --community louvain   # Default: fast, good quality
python grape.py data/your_data.tsv --community greedy    # Slower, more deterministic

# Set parameter strategy
python grape.py data/your_data.tsv --strategy fixed --initial_value 0.5      # Manual control
python grape.py data/your_data.tsv --strategy dynamic --initial_value 1.0    # Adaptive
```

### Column Name Customization

If your data uses different column names:

```bash
python grape.py your_data.tsv \
    --language-column "Lang" \
    --concept-column "Meaning" \
    --cognateset-column "CognateID"
```

### Missing Data and Synonyms

```bash
# How to handle synonyms (multiple cognates per concept)
python grape.py data.tsv --synonyms average    # Default: average similarity
python grape.py data.tsv --synonyms min        # Conservative: any shared cognate = similar
python grape.py data.tsv --synonyms max        # Strict: all cognates must match

# How to handle missing data
python grape.py data.tsv --missing_data max_dist  # Default: missing = maximally distant
python grape.py data.tsv --missing_data zero      # Missing = identical
python grape.py data.tsv --missing_data ignore    # Skip missing data concepts
```

## Quick Examples by Language Family

### Dravidian Languages
```bash
python grape.py data/dravlex.tsv --strategy fixed --initial_value 0.5
```
**Expect**: South, Central, and North Dravidian groupings

### Polynesian Languages  
```bash
python grape.py data/walworthpolynesian.tsv --strategy dynamic --initial_value 0.6
```
**Expect**: Tongic vs. Nuclear Polynesian classification

### Large Indo-European Dataset
```bash
python grape.py data/iecor_full.tsv --strategy adaptive --initial_value 0.2
```
**Expect**: All major IE branches (Romance, Germanic, Celtic, etc.)
⚠️ **Note**: This may take 1-2 minutes due to dataset size (160 languages)

## Viewing and Analyzing Results

### View Tree in Text Format
```bash
# Simple text visualization
python -c "
from ete3 import Tree
t = Tree('my_first_tree.newick')
print(t.get_ascii(show_internal=True))
"
```

### Convert to Other Formats
```bash
# Convert to phylip format (for other software)
python -c "
from ete3 import Tree
t = Tree('my_first_tree.newick')
t.write(format=1, outfile='tree.phylip')
"
```

### Basic Tree Statistics
```bash
# Get tree information
python -c "
from ete3 import Tree
t = Tree('my_first_tree.newick')
print(f'Number of languages: {len(t.get_leaves())}')
print(f'Tree height: {t.get_farthest_leaf()[1]:.3f}')
print(f'Languages: {[leaf.name for leaf in t.get_leaves()]}')
"
```

## Common Issues and Solutions

### Problem: "FileNotFoundError"
**Solution**: Check file path and ensure file exists
```bash
ls -la data/  # List available datasets
```

### Problem: "Missing required columns"
**Solution**: Check your column names and use the appropriate flags
```bash
head -1 your_data.tsv  # See column headers
python grape.py your_data.tsv --language-column "YourLanguageColumn"
```

### Problem: "No communities found" or "Empty tree"
**Solution**: Adjust resolution parameters
```bash
# Try different resolution values
python grape.py data.tsv --strategy fixed --initial_value 0.1   # Broader groupings
python grape.py data.tsv --strategy fixed --initial_value 0.8   # Finer groupings
```

### Problem: Unexpected groupings
**Solution**: 
1. Check data quality (cognate set assignments)
2. Try different graph construction methods
3. Experiment with synonym handling strategies

## Next Steps

### For Linguists
- 📖 Read the [Dravidian Walkthrough](../examples/dravidian_walkthrough.md) for detailed analysis
- 📊 Learn about [parameter optimization](parameters.md) for your specific data
- 🔬 Understand [result interpretation](interpretation.md) and validation

### For Computational Scientists  
- 🧮 Study the [mathematical background](../technical/mathematical_background.md)
- 💻 Explore [implementation details](../technical/implementation.md)  
- 🔧 Check out [extension points](../technical/implementation.md#extension-points) for customization

### For Everyone
- 📓 Try the [interactive Jupyter notebook](../examples/grape_analysis.ipynb)
- ❓ Check the [FAQ](faq.md) for common questions
- 🐛 Report issues on [GitHub](https://github.com/your-repo/grape/issues)

## Performance Expectations

| Dataset Size | Languages | Concepts | Typical Runtime |
|--------------|-----------|----------|-----------------|
| Small        | < 20      | < 200    | < 5 seconds     |
| Medium       | 20-50     | 200-500  | 5-30 seconds    |
| Large        | 50-200    | 500-1000 | 30-300 seconds  |

**Memory Usage**: Generally < 1GB for datasets up to 200 languages

---

**Congratulations!** 🎉 You've completed your first GRAPE analysis. You now know how to:
- Install and run GRAPE
- Analyze phylogenetic relationships from cognate data
- Interpret basic results
- Troubleshoot common issues

Ready for more advanced features? Check out our detailed guides and examples!