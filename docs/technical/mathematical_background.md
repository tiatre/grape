# Mathematical Background: Graph-Based Phylogenetic Inference

This document provides the mathematical foundation for GRAPE's approach to phylogenetic reconstruction using community detection in graphs. We present the theoretical framework, algorithmic details, and connections to traditional phylogenetic methods.

## Table of Contents

1. [Introduction](#introduction)
2. [Graph Construction from Cognate Data](#graph-construction-from-cognate-data)
3. [Community Detection Theory](#community-detection-theory)
4. [Phylogenetic Tree Construction](#phylogenetic-tree-construction)
5. [Parameter Optimization Strategies](#parameter-optimization-strategies)
6. [Theoretical Properties](#theoretical-properties)
7. [Computational Complexity](#computational-complexity)
8. [Relationship to Traditional Methods](#relationship-to-traditional-methods)

## Introduction

Traditional phylogenetic methods assume tree-like evolutionary relationships and model evolution as a Markov process along branches. However, language evolution often involves:

- **Horizontal transfer** (borrowing between languages)
- **Convergent evolution** (independent development of similar features)
- **Rate variation** across different linguistic features
- **Network-like relationships** that resist simple tree models

GRAPE addresses these challenges by:
1. Converting linguistic data into weighted graphs
2. Using community detection to identify language groups at multiple resolutions
3. Constructing hierarchical phylogenetic trees from community structure

This approach naturally captures both tree-like inheritance and network-like borrowing patterns.

## Graph Construction from Cognate Data

### Input Data Representation

Let **D** be a dataset of cognate assignments where:
- **L** = {l₁, l₂, ..., lₙ} is the set of n languages
- **C** = {c₁, c₂, ..., cₘ} is the set of m concepts (meanings)
- **S** = {s₁, s₂, ..., sₖ} is the set of k cognate sets

For each language lᵢ and concept cⱼ, we have a cognate assignment function:
```
f: L × C → S ∪ {∅}
```
where f(lᵢ, cⱼ) = sₖ means language lᵢ expresses concept cⱼ with a word from cognate set sₖ, and ∅ indicates missing data.

### Basic Distance Calculation

For languages lᵢ and lⱼ, we define several distance measures:

#### Shared Cognate Count
```
shared(lᵢ, lⱼ) = |{c ∈ C : f(lᵢ, c) = f(lⱼ, c) ≠ ∅}|
```

#### Available Concept Count
```
available(lᵢ, lⱼ) = |{c ∈ C : f(lᵢ, c) ≠ ∅ ∧ f(lⱼ, c) ≠ ∅}|
```

#### Basic Similarity
```
sim_basic(lᵢ, lⱼ) = shared(lᵢ, lⱼ) / available(lᵢ, lⱼ)
```

### Adjusted Distance Calculation

The adjusted distance method accounts for synonymy and data quality issues:

#### Concept-wise Similarity
For each concept c, compute the similarity between languages considering all cognate sets they use:

```
sim_c(lᵢ, lⱼ, c) = |Sᵢ,c ∩ Sⱼ,c| / |Sᵢ,c ∪ Sⱼ,c|
```

where Sᵢ,c = {s : f(lᵢ, c) = s} is the set of cognate sets used by language lᵢ for concept c.

#### Weighted Similarity
```
sim_adj(lᵢ, lⱼ) = Σc∈C w(c) · sim_c(lᵢ, lⱼ, c) / Σc∈C w(c)
```

where w(c) is a weight function that can account for:
- **Concept reliability**: More weight to stable concepts
- **Missing data patterns**: Reduced weight for concepts with many gaps
- **Borrowability**: Different weights for core vs. cultural vocabulary

### Graph Construction

Given similarity measures, we construct a weighted graph G = (V, E, W) where:
- **V = L** (languages as vertices)
- **E** contains edges (lᵢ, lⱼ) for all language pairs
- **W(lᵢ, lⱼ)** is the edge weight based on linguistic similarity

#### Weight Transformation
```
W(lᵢ, lⱼ) = α · sim(lᵢ, lⱼ) + β
```

where α and β are scaling parameters that can be adjusted based on:
- **Proximity weight**: How much to emphasize close relationships
- **Sharing factor**: Balance between shared and unshared features

## Community Detection Theory

### Modularity Optimization

Community detection algorithms aim to partition graph vertices into groups that maximize **modularity** Q:

```
Q = (1/2m) Σᵢⱼ [Aᵢⱼ - (kᵢkⱼ/2m)] δ(cᵢ, cⱼ)
```

where:
- **m** = Σᵢⱼ Aᵢⱼ/2 is the total edge weight
- **Aᵢⱼ** is the adjacency matrix (edge weights)
- **kᵢ** = Σⱼ Aᵢⱼ is the degree of vertex i
- **cᵢ** is the community assignment of vertex i
- **δ(cᵢ, cⱼ)** = 1 if cᵢ = cⱼ, 0 otherwise

### Resolution Parameter

To explore different granularities, we use a resolution parameter γ:

```
Q(γ) = (1/2m) Σᵢⱼ [Aᵢⱼ - γ(kᵢkⱼ/2m)] δ(cᵢ, cⱼ)
```

- **γ < 1**: Favors larger communities (broader groupings)
- **γ = 1**: Standard modularity
- **γ > 1**: Favors smaller communities (finer groupings)

### Louvain Algorithm

The Louvain algorithm optimizes modularity through iterative local moves:

1. **Local optimization**: For each vertex, consider moving it to neighboring communities and choose the move that maximally increases modularity
2. **Community aggregation**: Create a new graph where each community becomes a single vertex
3. **Repeat** until no improvement in modularity

**Complexity**: O(m log n) where m is edges and n is vertices.

### Greedy Modularity Algorithm

Alternative approach that builds communities by greedily merging:

1. **Initialize**: Each vertex in its own community
2. **Merge step**: Find the pair of communities whose merger maximally increases modularity
3. **Repeat** until no beneficial mergers remain

**Complexity**: O(m n log n) - slower but more deterministic than Louvain.

## Phylogenetic Tree Construction

### Hierarchical Community Detection

To build trees, we perform community detection at multiple resolution levels:

```
γ_min ≤ γ₁ < γ₂ < ... < γₖ ≤ γ_max
```

This produces a sequence of community partitions:
```
P₁, P₂, ..., Pₖ
```

where Pᵢ is the partition at resolution γᵢ.

### Tree Building Algorithm

1. **Root creation**: Start with all languages in a single community (lowest resolution)
2. **Recursive splitting**: At each internal node:
   - Find the next resolution level where this community splits
   - Create child nodes for each resulting subcommunity
   - Assign branch lengths based on resolution difference
3. **Leaf assignment**: Continue until each leaf represents a single language

### Branch Length Calculation

Branch lengths reflect the "evolutionary distance" between community levels:

```
branch_length(parent → child) = α · (γ_child - γ_parent) + β · structural_distance
```

where:
- **Resolution difference** captures the scale of community structure
- **Structural distance** accounts for graph topology changes

## Parameter Optimization Strategies

### Fixed Parameter Strategy

Uses a single, user-specified resolution value:
```
γ = γ_fixed
```

**Advantages**: Predictable, reproducible, direct control
**Disadvantages**: May miss optimal resolution for data

### Dynamic Parameter Strategy

Adjusts resolution based on community count:

```
γ_new = γ_old · adjust_factor
```

where adjust_factor depends on:
- **Target community count**: Aim for biologically reasonable number of groups
- **Current community count**: Increase/decrease resolution accordingly
- **Convergence criteria**: Stop when community count stabilizes

### Adaptive Dynamic Strategy

More sophisticated adjustment considering:
- **Community quality metrics** (silhouette scores, conductance)
- **Phylogenetic coherence** (tree balance, branch length distribution)
- **Biological constraints** (known relationships, geographic factors)

```
γ_new = optimize(quality_function(γ), constraints)
```

## Theoretical Properties

### Consistency Properties

Under certain conditions, GRAPE exhibits theoretical guarantees:

1. **Identifiability**: Given sufficient data and appropriate parameters, true community structure is recoverable
2. **Consistency**: As data size increases, community detection converges to true structure
3. **Robustness**: Small changes in data produce small changes in community structure

### Assumptions and Limitations

**Key assumptions:**
- **Community structure exists** in the linguistic data
- **Modularity optimization** captures meaningful linguistic relationships
- **Tree representation** is appropriate despite network-like borrowing

**Limitations:**
- **Resolution limit**: Cannot detect communities smaller than (2m/n)^(1/2)
- **Local optima**: Community detection may converge to suboptimal solutions
- **Parameter sensitivity**: Results may vary significantly with parameter choices

## Computational Complexity

### Graph Construction
- **Time**: O(n²m) where n = languages, m = concepts
- **Space**: O(n²) for adjacency matrix storage

### Community Detection
- **Louvain**: O(m log n) per iteration
- **Greedy**: O(mn log n) total
- **Typical iterations**: 5-20 for convergence

### Tree Construction
- **Time**: O(kn) where k = resolution levels
- **Space**: O(n) for tree storage

### Overall Complexity
For typical linguistic datasets (n ≤ 200, m ≤ 500):
- **Total time**: Seconds to minutes
- **Memory usage**: < 1GB
- **Scaling**: Practical for datasets up to ~1000 languages

## Relationship to Traditional Methods

### Distance-Based Methods

Traditional methods like Neighbor-Joining use:
```
d(lᵢ, lⱼ) = -log(sim(lᵢ, lⱼ))
```

GRAPE's similarity measures can be directly compared to these distances.

### Character-Based Methods

Maximum Likelihood and Parsimony methods model character evolution explicitly. GRAPE's cognate sharing patterns provide an aggregate view of character evolution without explicit modeling.

### Network Methods

Recent phylogenetic networks (SplitsTree, NeighborNet) also capture non-tree-like relationships. GRAPE differs by:
- Using community detection rather than split decomposition
- Focusing on hierarchical rather than reticulate structure
- Emphasizing computational efficiency for large datasets

### Advantages and Trade-offs

**GRAPE advantages:**
- Handles borrowing and network effects naturally
- Computationally efficient for large datasets
- Multiple resolution levels provide flexible granularity
- Robust to missing data and synonymy

**Traditional method advantages:**
- Established statistical framework with confidence measures
- Direct evolutionary interpretation of branch lengths
- Well-understood behavior under various evolutionary models
- Standard tools and widespread acceptance

---

*This mathematical foundation provides the theoretical basis for understanding GRAPE's approach to phylogenetic inference. The combination of graph theory, community detection, and phylogenetic reconstruction offers a novel perspective on language evolution that complements traditional methods.*