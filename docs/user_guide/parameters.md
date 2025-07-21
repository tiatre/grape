# GRAPE Parameter Guide

This comprehensive guide explains all GRAPE parameters, when to use them, and how they affect your phylogenetic analysis. Understanding these parameters is crucial for getting optimal results from your data.

## Table of Contents

1. [Parameter Overview](#parameter-overview)
2. [Graph Construction Parameters](#graph-construction-parameters)
3. [Community Detection Parameters](#community-detection-parameters)
4. [Parameter Search Strategies](#parameter-search-strategies)
5. [Data Handling Options](#data-handling-options)
6. [Advanced Options](#advanced-options)
7. [Parameter Selection Guide](#parameter-selection-guide)
8. [Troubleshooting with Parameters](#troubleshooting-with-parameters)

## Parameter Overview

GRAPE's flexibility comes from its extensive parameterization. Parameters control:

- **How graphs are built** from linguistic data
- **Which algorithm** finds language communities
- **How parameters** are optimized automatically
- **How data quality issues** are handled

### Command Line Structure

```bash
python grape.py INPUT_FILE [OPTIONS]
```

All parameters have sensible defaults, so you can start with:
```bash
python grape.py data/your_data.tsv
```

## Graph Construction Parameters

### `--graph` (Graph Construction Method)

**Options**: `adjusted` (default), `unadjusted`

Controls how linguistic similarity is calculated from cognate data.

#### `--graph adjusted` (Recommended)
```bash
python grape.py data.tsv --graph adjusted
```

**What it does:**
- Uses sophisticated distance calculations
- Handles synonyms intelligently 
- Accounts for missing data patterns
- Applies proximity and sharing factors

**When to use:**
- **Default choice** for most analyses
- Real linguistic data with quality issues
- Data with synonyms (multiple words per concept)
- When you want robust, publication-quality results

**Example output difference:**
```
Adjusted:   Tamil-Malayalam similarity = 0.73
Unadjusted: Tamil-Malayalam similarity = 0.68
```

#### `--graph unadjusted` (Simple)
```bash
python grape.py data.tsv --graph unadjusted
```

**What it does:**
- Simple shared cognate counting
- Binary similarity calculation
- No synonym handling
- Faster computation

**When to use:**
- High-quality, curated datasets
- Quick exploratory analysis
- Comparison with traditional methods
- When you need maximum speed

### Adjusted Graph Sub-parameters

#### `--synonyms` (Synonym Handling)

**Options**: `average` (default), `min`, `max`

Controls how multiple cognate sets per concept are handled.

```bash
# Conservative: any shared cognate = high similarity
python grape.py data.tsv --synonyms min

# Balanced: average similarity across all cognate pairs
python grape.py data.tsv --synonyms average  

# Strict: only identical cognate sets = high similarity  
python grape.py data.tsv --synonyms max
```

**Detailed Behavior:**

| Strategy  | Lang1: {A,B} vs Lang2: {B,C} | Result | Interpretation |
|-----------|------------------------------|---------|----------------|
| `min`     | min(dist(A,B), dist(A,C), dist(B,B), dist(B,C)) | 0.0 | Any shared cognate = similar |
| `average` | mean(dist(A,B), dist(A,C), dist(B,B), dist(B,C)) | 0.5 | Balanced assessment |
| `max`     | max(dist(A,B), dist(A,C), dist(B,B), dist(B,C)) | 1.0 | Must share all cognates |

#### `--missing_data` (Missing Data Strategy)

**Options**: `max_dist` (default), `zero`, `ignore`

Controls how missing language-concept pairs are handled.

```bash
# Missing data = maximum distance (conservative)
python grape.py data.tsv --missing_data max_dist

# Missing data = zero distance (liberal)
python grape.py data.tsv --missing_data zero

# Ignore missing data entirely
python grape.py data.tsv --missing_data ignore
```

**Impact on Results:**

| Strategy   | Effect | When to Use |
|------------|---------|-------------|
| `max_dist` | Conservative groupings | Sparse data, safety-first approach |
| `zero`     | Liberal groupings | Dense data, when missing = unrelated |
| `ignore`   | Focus on available data | High-quality, complete datasets |

#### `--proximity_weight` and `--sharing_factor`

**Advanced similarity tuning:**

```bash
python grape.py data.tsv --proximity_weight 0.9 --sharing_factor 0.1
```

**Formula:**
```
final_similarity = proximity_weight × base_similarity + sharing_factor × (1 - base_similarity)
```

**Default values**: `proximity_weight=0.8`, `sharing_factor=0.2`

**Effects:**
- Higher `proximity_weight`: Emphasizes close relationships
- Higher `sharing_factor`: Emphasizes distant relationships
- Must sum to 1.0 for meaningful results

## Community Detection Parameters

### `--community` (Algorithm Choice)

**Options**: `louvain` (default), `greedy`

#### `--community louvain` (Recommended)
```bash
python grape.py data.tsv --community louvain
```

**Characteristics:**
- Fast, efficient algorithm
- Good quality results
- Some randomness in results
- Scales well to large datasets

**When to use:**
- **Default choice** for most analyses
- Large datasets (>50 languages)
- When speed is important
- Exploratory analysis

#### `--community greedy`
```bash
python grape.py data.tsv --community greedy
```

**Characteristics:**
- Slower but more deterministic
- Reproducible results
- May find different community structure
- Better for small datasets

**When to use:**
- Need reproducible results
- Small datasets (<30 languages)  
- Comparison studies
- Publication-quality analysis

## Parameter Search Strategies

### `--strategy` (Search Strategy)

**Options**: `dynamic` (default), `fixed`, `adaptive`

Controls how the resolution parameter is optimized.

#### `--strategy dynamic` (Automatic)
```bash
python grape.py data.tsv --strategy dynamic --initial_value 1.0
```

**Behavior:**
- Starts at `initial_value`
- Automatically adjusts resolution
- Stops when reasonable community count reached
- Good for most datasets

**When to use:**
- **Default choice**
- Don't know optimal resolution
- Want automated analysis
- Exploring new datasets

#### `--strategy fixed` (Manual Control)
```bash
python grape.py data.tsv --strategy fixed --initial_value 0.5
```

**Behavior:**
- Uses exactly the specified resolution
- No automatic adjustment
- Deterministic results
- Full user control

**When to use:**
- Know the optimal resolution
- Need reproducible results
- Parameter sensitivity analysis
- Comparing specific resolution values

#### `--strategy adaptive` (Intelligent)
```bash
python grape.py data.tsv --strategy adaptive --initial_value 0.5 --target_communities 10
```

**Behavior:**
- Tries to reach target number of communities
- Adjusts resolution intelligently
- More sophisticated than dynamic
- May converge slowly

**When to use:**
- Know desired number of language groups
- Complex datasets
- When dynamic strategy fails
- Research applications

### Resolution Parameter (`--initial_value`)

**Range**: 0.1 to 2.0 (typical)
**Default**: Varies by strategy

```bash
# Low resolution = fewer, larger communities
python grape.py data.tsv --initial_value 0.2

# Medium resolution = balanced groupings  
python grape.py data.tsv --initial_value 0.5

# High resolution = many, smaller communities
python grape.py data.tsv --initial_value 1.0
```

**Guidelines by Dataset Size:**

| Languages | Recommended Initial Value | Expected Communities |
|-----------|---------------------------|---------------------|
| < 20      | 0.3 - 0.6                | 3 - 6               |
| 20 - 50   | 0.4 - 0.8                | 4 - 10              |
| 50 - 100  | 0.2 - 0.5                | 6 - 15              |
| > 100     | 0.1 - 0.3                | 8 - 20              |

## Data Handling Options

### Column Name Specification

When your data uses non-standard column names:

```bash
python grape.py data.tsv \
    --language-column "Language_Name" \
    --concept-column "Meaning" \
    --cognateset-column "Cognate_Set_ID"
```

**Default names**: `Language`, `Parameter`, `Cognateset`

### File Format Options

```bash
# Specify encoding for non-UTF8 files
python grape.py data.tsv --encoding iso-8859-1

# Specify CSV dialect
python grape.py data.csv --dialect excel
```

## Advanced Options

### Iteration Control

```bash
# Limit maximum iterations for parameter search
python grape.py data.tsv --max_iterations 50
```

**Default**: 100 iterations
**When to adjust**: 
- Increase for complex datasets
- Decrease for quick exploratory analysis

### Logging and Output

```bash
# Quiet mode (minimal output)
python grape.py data.tsv --quiet

# Verbose mode (detailed logging)  
python grape.py data.tsv --verbose
```

## Parameter Selection Guide

### By Dataset Characteristics

#### High-Quality, Curated Data
```bash
python grape.py data.tsv \
    --graph unadjusted \
    --community greedy \
    --strategy fixed \
    --initial_value 0.5
```

#### Real-World, Messy Data
```bash
python grape.py data.tsv \
    --graph adjusted \
    --synonyms average \
    --missing_data max_dist \
    --community louvain \
    --strategy dynamic
```

#### Large Dataset (>100 languages)
```bash  
python grape.py data.tsv \
    --graph adjusted \
    --community louvain \
    --strategy adaptive \
    --initial_value 0.2
```

#### Small Dataset (<20 languages)
```bash
python grape.py data.tsv \
    --graph adjusted \
    --community greedy \
    --strategy fixed \
    --initial_value 0.6
```

### By Research Goals

#### Exploratory Analysis
```bash
python grape.py data.tsv \
    --strategy dynamic \
    --community louvain
```

#### Publication-Quality Results
```bash
python grape.py data.tsv \
    --graph adjusted \
    --synonyms average \
    --missing_data max_dist \
    --community greedy \
    --strategy fixed \
    --initial_value 0.5
```

#### Comparison with Traditional Methods
```bash
python grape.py data.tsv \
    --graph unadjusted \
    --strategy fixed \
    --initial_value 0.5
```

## Troubleshooting with Parameters

### Problem: Too Few Communities (Over-lumping)

**Symptoms**: All languages in 1-2 big groups

**Solutions**:
```bash
# Increase resolution
python grape.py data.tsv --initial_value 0.8

# Try greedy algorithm  
python grape.py data.tsv --community greedy

# Use stricter synonym handling
python grape.py data.tsv --synonyms max
```

### Problem: Too Many Communities (Over-splitting)

**Symptoms**: Each language in its own group

**Solutions**:
```bash
# Decrease resolution
python grape.py data.tsv --initial_value 0.2

# Use liberal synonym handling
python grape.py data.tsv --synonyms min

# Try different missing data strategy
python grape.py data.tsv --missing_data zero
```

### Problem: Unstable Results

**Symptoms**: Different results on repeated runs

**Solutions**:
```bash
# Use deterministic algorithm
python grape.py data.tsv --community greedy

# Use fixed strategy
python grape.py data.tsv --strategy fixed --initial_value 0.5

# Check data quality
```

### Problem: Unexpected Groupings

**Solutions**:
1. **Check data quality**: Verify cognate set assignments
2. **Try different graph method**: `adjusted` vs `unadjusted`
3. **Adjust synonym handling**: Try `min`, `average`, `max`
4. **Parameter sweep**: Test range of resolution values

### Problem: Slow Performance

**Solutions**:
```bash
# Use faster algorithm
python grape.py data.tsv --community louvain

# Limit iterations
python grape.py data.tsv --max_iterations 20

# Use simpler graph construction
python grape.py data.tsv --graph unadjusted
```

## Parameter Interaction Effects

### Critical Interactions

1. **Graph × Synonyms**: 
   - `adjusted` + `average` = balanced results
   - `unadjusted` ignores synonym settings

2. **Community × Strategy**:
   - `greedy` + `fixed` = fully deterministic
   - `louvain` + `dynamic` = good performance/quality balance

3. **Resolution × Dataset Size**:
   - Large datasets need lower resolution values
   - Small datasets need higher resolution values

### Parameter Sensitivity Analysis

To test parameter sensitivity:

```bash
# Test resolution range
for res in 0.1 0.2 0.3 0.4 0.5; do
    echo "Resolution $res:"
    python grape.py data.tsv --strategy fixed --initial_value $res > tree_$res.newick
done

# Compare tree topologies
# (Use external tools like TreeCmp or custom scripts)
```

---

**Summary**: Parameter selection is crucial for GRAPE success. Start with defaults, then adjust based on your data characteristics and research goals. When in doubt, use the exploratory settings first, then refine for final analysis.