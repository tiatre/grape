# Complete Dravidian Language Family Analysis with GRAPE

This document provides a comprehensive, step-by-step walkthrough of analyzing the Dravidian language family using GRAPE. We'll demonstrate the complete process from raw cognate data to phylogenetic tree reconstruction, with detailed explanations of each step.

## Table of Contents

1. [Dataset Overview](#dataset-overview)
2. [Data Structure and Preparation](#data-structure-and-preparation)
3. [Basic Analysis](#basic-analysis)
4. [Advanced Parameter Exploration](#advanced-parameter-exploration)
5. [Results Interpretation](#results-interpretation)
6. [Validation Against Linguistic Knowledge](#validation-against-linguistic-knowledge)
7. [Comparison with Traditional Methods](#comparison-with-traditional-methods)
8. [Conclusion](#conclusion)

## Dataset Overview

### The Dravidian Language Family

The Dravidian language family consists of approximately 80 languages spoken primarily in South India, with some languages in Central India and one (Brahui) in Pakistan. The family is traditionally divided into four main branches:

- **South Dravidian (South I)**: Tamil, Malayalam, Kannada, Tulu, and related languages
- **South-Central Dravidian (South II)**: Telugu and related varieties  
- **Central Dravidian**: Gondi, Kolami, and related languages
- **North Dravidian**: Brahui, Kurukh (Oraon), and Malto

### Our Dataset: `dravlex.tsv`

```bash
# Dataset statistics
wc -l data/dravlex.tsv
# 2115 total rows (including header)

# Number of languages
cut -f1 data/dravlex.tsv | sort -u | grep -v Language | wc -l  
# 19 languages

# Number of concepts (meanings)
cut -f2 data/dravlex.tsv | sort -u | wc -l
# 101 concepts

# Number of cognate sets
cut -f3 data/dravlex.tsv | sort -u | wc -l  
# 779 unique cognate sets
```

**Languages included:**
- **South Dravidian**: Tamil, Malayalam, Kannada, Tulu, Kodava, Badga, Kota, Toda
- **South-Central Dravidian**: Telugu
- **Central Dravidian**: Gondi, Koya, Kuwi, Kolami, Parji, Ollari_Gadba
- **North Dravidian**: Brahui, Kurukh, Malto
- **Additional**: Betta_Kurumba (transitional variety)

## Data Structure and Preparation

### Understanding the Input Format

Let's examine the structure of our cognate data:

```bash
head -10 data/dravlex.tsv
```

```
Language        Parameter       Cognateset
Badga          I               i.001
Betta_Kurumba  I               i.001  
Brahui         I               i.001
Gondi          I               i.001
Kannada        I               i.001
Kodava         I               i.001
Kolami         I               i.001
Kota           I               i.001
Koya           I               i.001
```

**Data Format Explanation:**
- **Language**: The name of the language variety
- **Parameter**: The concept/meaning being compared (e.g., "I" = first person pronoun)
- **Cognateset**: Identifier for cognate relationships (languages sharing the same ID are cognate)

### Data Quality Assessment

```bash
# Check for missing data patterns
grep -c "?" data/dravlex.tsv  # No missing data markers found
grep -c "NULL" data/dravlex.tsv  # No NULL values

# Language coverage per concept
cut -f2 data/dravlex.tsv | sort | uniq -c | sort -nr | head -10
```

The dataset shows good coverage with most concepts represented across all languages.

## Basic Analysis

### Step 1: Default Analysis

Let's start with GRAPE's default parameters:

```bash
python grape.py data/dravlex.tsv > dravidian_default.tree 2> dravidian_default.log
```

**Output analysis:**
```bash
cat dravidian_default.log
```

```
[INFO] Reading cognate file: data/dravlex.tsv
[INFO] Loaded 2114 cognate entries for 19 languages across 100 concepts
[INFO] Building graph with method: adjusted
[INFO] Graph created with 19 nodes and 171 edges
[INFO] Using community detection: LouvainCommunities  
[INFO] Using parameter strategy: DynamicParameterStrategy
[INFO] Initial resolution: 1.0
[INFO] Community detection completed
[INFO] Converting communities to tree structure
[INFO] Final tree constructed with 19 leaves
```

### Step 2: Examining the Default Tree

```bash
cat dravidian_default.tree
```

The output will be a Newick format tree that we can analyze with phylogenetic software or ETE3.

### Step 3: Understanding Graph Construction

GRAPE converts cognate data into a weighted graph. Let's understand this process:

**Graph Construction Process:**
1. **Nodes**: Each language becomes a node
2. **Edges**: Pairs of languages are connected with weights based on cognate sharing
3. **Weight Calculation**: 
   - `w = (shared_cognates / total_concepts) * proximity_factor`
   - Higher weights indicate more similar languages

**With adjusted weights (default):**
- Accounts for synonymy and missing data
- More robust for real linguistic data
- Recommended for most analyses

## Advanced Parameter Exploration

### Experiment 1: Community Detection Algorithms

Let's compare Louvain vs. Greedy Modularity:

```bash
# Louvain algorithm (default)
python grape.py data/dravlex.tsv --community louvain --strategy fixed --initial_value 0.5 \
    > dravidian_louvain.tree 2> dravidian_louvain.log

# Greedy modularity  
python grape.py data/dravlex.tsv --community greedy --strategy fixed --initial_value 0.5 \
    > dravidian_greedy.tree 2> dravidian_greedy.log
```

**Expected differences:**
- **Louvain**: Generally faster, good for large datasets
- **Greedy**: More deterministic, may find different local optima

### Experiment 2: Graph Weight Adjustment

```bash
# Adjusted weights (default - handles synonymy)
python grape.py data/dravlex.tsv --graph adjusted --initial_value 0.5 \
    > dravidian_adjusted.tree

# Unadjusted weights (raw cognate counts)
python grape.py data/dravlex.tsv --graph unadjusted --initial_value 0.5 \
    > dravidian_unadjusted.tree
```

**Key difference:**
- **Adjusted**: Better handles cases where languages have multiple words for the same concept
- **Unadjusted**: Simpler calculation, may be biased by data collection methods

### Experiment 3: Parameter Search Strategies

```bash
# Fixed parameter (manual control)
python grape.py data/dravlex.tsv --strategy fixed --initial_value 0.3

# Dynamic parameter (adjusts based on community count)  
python grape.py data/dravlex.tsv --strategy dynamic --initial_value 0.5

# Adaptive parameter (experimental)
python grape.py data/dravlex.tsv --strategy adaptive --initial_value 0.5
```

### Experiment 4: Resolution Parameter Sweep

Let's systematically explore different resolution values:

```bash
# Low resolution (fewer, larger communities)
for res in 0.1 0.2 0.3; do
    echo "Resolution $res:"
    python grape.py data/dravlex.tsv --strategy fixed --initial_value $res \
        2>&1 | grep -E "(communities|resolution)"
done

# Medium resolution  
for res in 0.4 0.5 0.6; do
    echo "Resolution $res:"
    python grape.py data/dravlex.tsv --strategy fixed --initial_value $res \
        2>&1 | grep -E "(communities|resolution)" 
done

# High resolution (many, smaller communities)
for res in 0.7 0.8 0.9; do
    echo "Resolution $res:"
    python grape.py data/dravlex.tsv --strategy fixed --initial_value $res \
        2>&1 | grep -E "(communities|resolution)"
done
```

**Expected pattern:**
- **Low resolution** (0.1-0.3): Few major groups, may miss fine structure
- **Medium resolution** (0.4-0.6): Balanced grouping, often optimal
- **High resolution** (0.7-0.9): Many small groups, may over-split

## Tree Visualization

The complete phylogenetic tree with linguistic analysis is available here: [**Dravidian Tree Visualization**](../images/trees/dravidian_formatted.txt)

This visualization includes:
- **ASCII tree structure** showing relationships between all 20 Dravidian languages
- **Tree statistics** (height: 4.600, languages: 20)
- **Linguistic groupings** automatically detected and validated
- **Complete language list** with all included varieties

**Key findings from the visualization:**
- South Dravidian languages cluster together as expected
- Central Dravidian languages (Gondi, Kolami, etc.) form distinct groups  
- North Dravidian languages show clear separation from southern varieties
- Tree height indicates moderate linguistic diversity within the family

You can also view:
- [Raw tree file](../images/trees/dravidian.newick) (Newick format)
- [ASCII-only version](../images/trees/dravidian_ascii.txt) (plain text tree)
- [Analysis summary](../images/trees/dravidian_summary.txt) (basic statistics)

## Results Interpretation

### Analyzing Tree Topology

Using Python with ETE3 to analyze our results:

```python
from ete3 import Tree

# Load the tree
tree = Tree("dravidian_adjusted.tree")

# Print basic statistics
print(f"Number of leaves: {len(tree.get_leaves())}")
print(f"Tree height: {tree.get_farthest_leaf()[1]:.3f}")

# Check major groupings
def find_clade(tree, language_list):
    """Find the MRCA of given languages and return all descendants."""
    target_nodes = []
    for leaf in tree.get_leaves():
        if leaf.name in language_list:
            target_nodes.append(leaf)
    
    if len(target_nodes) < 2:
        return set()
    
    mrca = tree.get_common_ancestor(target_nodes)
    return {leaf.name for leaf in mrca.get_leaves()}

# Test South Dravidian grouping
south_dravidian = ['Tamil', 'Malayalam', 'Kannada', 'Tulu']
south_clade = find_clade(tree, south_dravidian)
print(f"South Dravidian clade: {south_clade}")

# Test North Dravidian grouping  
north_dravidian = ['Brahui', 'Kurukh', 'Malto']
north_clade = find_clade(tree, north_dravidian)
print(f"North Dravidian clade: {north_clade}")
```

### Key Metrics to Evaluate

1. **Monophyly Tests**: Do expected groups form single clades?
2. **Branch Lengths**: Do distances reflect linguistic similarity?
3. **Tree Balance**: Is the tree structure reasonable?
4. **Outlier Detection**: Are there unexpected groupings?

## Validation Against Linguistic Knowledge

### Expected Results Based on Comparative Linguistics

**Strong expectations (should always hold):**
1. **North Dravidian monophyly**: Brahui, Kurukh, Malto should group together
2. **South Dravidian core**: Tamil, Malayalam, Kannada should be closely related
3. **Telugu distinctness**: Telugu (South-Central) should be separate from other major groups

**Moderate expectations (usually hold):**
1. **Central Dravidian grouping**: Gondi, Koya, Kuwi should cluster together
2. **Geographic clustering**: Languages from the same region should be similar
3. **Badaga-Kota-Toda relationship**: These Nilgiri languages should be close

### Running Validation Tests

```bash
# Run our validation tests
python -m unittest test_additional_families.TestDravidian -v
```

Expected output:
```
test_central_dravidian_grouping ... ok
test_north_dravidian_grouping ... ok  
test_south_dravidian_grouping ... ok
test_tamil_malayalam_closeness ... ok
```

### Interpreting Deviations from Expected Results

If tests fail, consider:
1. **Parameter adjustment**: Try different resolution values
2. **Data quality**: Check for missing or problematic cognate assignments
3. **Method limitations**: Some relationships may not be captured by community detection
4. **Alternative hypotheses**: Results might reveal new insights about Dravidian relationships

## Comparison with Traditional Methods

### Distance-Based Methods

Let's compare GRAPE results with traditional Neighbor-Joining:

```bash
# If biopython is installed
python distance_tree.py data/dravlex.tsv --method nj > dravidian_nj.tree
python distance_tree.py data/dravlex.tsv --method upgma > dravidian_upgma.tree
```

### Expected Differences

**GRAPE advantages:**
- Captures network-like relationships
- Robust to borrowing and convergence
- Handles missing data well
- Multiple resolution levels

**Traditional method advantages:**
- Well-established statistical framework
- Direct distance interpretation
- Simpler to understand and implement

### Comparative Analysis

```python
# Compare tree topologies
from ete3 import Tree

grape_tree = Tree("dravidian_adjusted.tree")
nj_tree = Tree("dravidian_nj.tree")

# Calculate Robinson-Foulds distance
rf_distance = grape_tree.robinson_foulds(nj_tree)
print(f"Tree similarity (RF distance): {rf_distance[0]}")

# Compare specific groupings
def compare_groupings(tree1, tree2, test_groups):
    """Compare how different methods group languages."""
    for group_name, languages in test_groups.items():
        clade1 = find_clade(tree1, languages)
        clade2 = find_clade(tree2, languages)
        
        print(f"{group_name}:")
        print(f"  GRAPE: {clade1}")
        print(f"  NJ: {clade2}")
        print(f"  Agreement: {clade1 == clade2}")

test_groups = {
    'South Dravidian': ['Tamil', 'Malayalam', 'Kannada'],
    'North Dravidian': ['Brahui', 'Kurukh', 'Malto'],
    'Central Dravidian': ['Gondi', 'Koya', 'Kuwi']
}

compare_groupings(grape_tree, nj_tree, test_groups)
```

## Performance and Scalability

### Timing Analysis

```bash
# Time the analysis
time python grape.py data/dravlex.tsv > /dev/null
```

**Expected performance:**
- **19 languages, 100 concepts**: < 1 second
- **Memory usage**: < 50 MB
- **Scaling**: Linear with number of languages, quadratic with graph density

### Parameter Sensitivity

Test how robust results are to parameter changes:

```bash
# Test multiple parameter values
for res in $(seq 0.3 0.1 0.7); do
    python grape.py data/dravlex.tsv --strategy fixed --initial_value $res \
        > "dravidian_res_${res}.tree"
done

# Compare tree consistency across parameters
# (would need custom script to calculate tree similarities)
```

## Conclusion

### Key Findings

From our Dravidian analysis, GRAPE successfully:

1. **Recovers major groupings**: North, South, and Central Dravidian clades are recovered
2. **Shows appropriate resolution**: Can identify both broad families and fine structure
3. **Handles data quality issues**: Robust to missing data and synonymy
4. **Provides novel insights**: May reveal borrowing patterns not captured by traditional methods

### Best Practices Learned

1. **Parameter selection**: Start with resolution 0.5, adjust based on data size
2. **Method comparison**: Always compare Louvain vs. Greedy modularity
3. **Validation essential**: Use linguistic knowledge to validate computational results
4. **Multiple resolutions**: Explore parameter space systematically

### When to Use GRAPE vs. Traditional Methods

**Use GRAPE when:**
- Data has complex borrowing patterns
- Working with large datasets
- Need to explore multiple grouping hypotheses
- Interested in network-like relationships

**Use traditional methods when:**
- Need established statistical framework
- Working with small, high-quality datasets
- Require direct distance interpretation
- Following standard phylogenetic protocols

### Next Steps

1. **Expand analysis**: Include more Dravidian languages and concepts
2. **Method development**: Explore new community detection algorithms
3. **Integration**: Combine GRAPE with traditional phylogenetic methods
4. **Application**: Apply to other language families and test generalizability

---

*This walkthrough demonstrates GRAPE's capabilities using real linguistic data. The Dravidian family provides an excellent test case due to its well-studied internal relationships and diverse geographic distribution.*