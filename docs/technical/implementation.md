# GRAPE Implementation Details

This document provides a comprehensive guide to GRAPE's implementation, covering the architecture, data structures, algorithms, and code organization. This is essential reading for developers who want to understand, modify, or extend GRAPE.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Core Data Structures](#core-data-structures)
3. [Module Organization](#module-organization)
4. [Algorithm Implementation](#algorithm-implementation)
5. [Graph Construction Details](#graph-construction-details)
6. [Community Detection Implementation](#community-detection-implementation)
7. [Tree Construction Process](#tree-construction-process)
8. [Parameter Strategies](#parameter-strategies)
9. [Error Handling and Logging](#error-handling-and-logging)
10. [Performance Considerations](#performance-considerations)
11. [Extension Points](#extension-points)

## Architecture Overview

GRAPE follows a modular, object-oriented design with clear separation of concerns:

```
Input Data → Graph Construction → Community Detection → Tree Building → Output
     ↓              ↓                    ↓                ↓           ↓
 common.py      grape.py           grape.py        grape.py    Newick Format
```

### Key Design Principles

1. **Modularity**: Each major function is encapsulated in separate classes/modules
2. **Strategy Pattern**: Community detection and parameter search use pluggable strategies  
3. **Type Safety**: Comprehensive type hints throughout the codebase
4. **Configurability**: All major parameters are exposed via command-line interface
5. **Extensibility**: Easy to add new community detection methods and parameter strategies

## Core Data Structures

### HistoryEntry Class

```python
@dataclass
class HistoryEntry:
    parameter: float
    communities: List[FrozenSet[str]]
    
    @cached_property
    def number_of_communities(self) -> int:
        return len(self.communities)
```

**Purpose**: Stores the result of community detection at a specific resolution level.
- `parameter`: The resolution value used for community detection
- `communities`: List of language groups found at this resolution
- `number_of_communities`: Cached property for efficiency

### Cognate Data Representation

```python
Dict[Tuple[str, str], Set[int]]
```

**Structure**: `{(language, concept): {cognate_set_id1, cognate_set_id2, ...}}`
- **Key**: Tuple of (language_name, concept_name)
- **Value**: Set of integer cognate set IDs
- **Handles synonymy**: Multiple cognate sets per language-concept pair
- **Missing data**: Absent keys indicate no data for that language-concept pair

### Graph Representation

GRAPE uses NetworkX Graph objects:
```python
nx.Graph  # Undirected, weighted graph
# Nodes: language names (strings)
# Edges: weighted by linguistic similarity
# Weights: float values between 0 and 1
```

## Module Organization

### `common.py`: Data Handling and Utilities

**Primary Functions:**
- `read_cognate_file()`: CSV parsing with flexible column naming and dialect detection
- `compute_distance_matrix()`: Distance calculation with synonym and missing data handling
- `decompose_sets()`: Hierarchical community decomposition utility

**Key Features:**
- Robust CSV parsing with automatic dialect detection
- Flexible column naming (`--language-column`, `--concept-column`, `--cognateset-column`)
- Multiple strategies for handling synonyms (`average`, `min`, `max`)
- Multiple strategies for missing data (`max_dist`, `zero`, `ignore`)

### `grape.py`: Core Algorithm Implementation  

**Class Hierarchy:**

```python
CommunityMethod (Abstract Base Class)
├── GreedyModularity
└── LouvainCommunities

ParameterSearchStrategy (Abstract Base Class)
├── FixedIncrementStrategy  
├── DynamicAdjustmentStrategy
└── AdaptiveDynamicAdjustmentStrategy
```

**Main Functions:**
- `build_history()`: Orchestrates the entire analysis pipeline
- `build_tree_from_history()`: Converts community history to phylogenetic tree
- `build_graph()`: Factory function for graph construction methods
- `main()`: Command-line interface and argument parsing

## Algorithm Implementation

### 1. Data Loading and Preprocessing

```python
def read_cognate_file(
    input_file: str,
    dialect_name: str = "auto",
    encoding: str = "utf-8",
    lang_col_name: str = "Language", 
    concept_col_name: str = "Parameter",
    cognateset_col_name: str = "Cognateset"
) -> Dict[Tuple[str, str], Set[int]]:
```

**Process:**
1. **Dialect Detection**: Automatically detects CSV format or uses specified dialect
2. **Column Validation**: Ensures required columns are present
3. **Cognate Set Mapping**: Converts string cognate set IDs to integers for efficiency
4. **Data Validation**: Warns about missing values and malformed data
5. **Set Construction**: Groups multiple cognate sets per language-concept pair

### 2. Graph Construction Options

#### Basic Graph Construction

```python
def cognateset_graph(data: Dict[Tuple[str, str], Set[int]]) -> nx.Graph:
```

**Algorithm:**
1. Create nodes for each language
2. For each pair of languages:
   - Count shared cognate sets across all concepts
   - Calculate similarity = shared_concepts / total_available_concepts
   - Add weighted edge with similarity value

#### Adjusted Graph Construction

```python
def adjusted_cognateset_graph(
    data: Dict[Tuple[str, str], Set[int]],
    synonyms: str = "average",
    missing_data: str = "max_dist",
    proximity_weight: float = 0.8,
    sharing_factor: float = 0.2
) -> nx.Graph:
```

**Advanced Features:**
- **Synonym Handling**: Uses Jaccard distance calculations with aggregation strategies
- **Missing Data**: Multiple strategies for handling absent language-concept pairs  
- **Weight Adjustment**: Proximity and sharing factors fine-tune edge weights
- **Robust Calculation**: Handles edge cases and data quality issues

### 3. Community Detection Pipeline

```python
def build_history(
    data: Dict[Tuple[str, str], Set[int]],
    community_method: CommunityMethod,
    strategy_name: ParameterSearchStrategy,
    max_iterations: int = 100
) -> List[HistoryEntry]:
```

**Process:**
1. **Initialize Strategy**: Set starting resolution parameter
2. **Iterative Detection**: 
   - Run community detection at current resolution
   - Evaluate results (number of communities, quality metrics)
   - Update resolution based on strategy
   - Stop when convergence criteria met
3. **History Recording**: Store each resolution level and its communities
4. **Validation**: Ensure sensible community structure

## Graph Construction Details

### Weight Calculation Mathematics

For the adjusted method, edge weights are calculated as:

```python
# For each concept, calculate concept-specific similarity
concept_similarities = []
for concept in concepts:
    cog1 = cognates.get((lang1, concept), set())
    cog2 = cognates.get((lang2, concept), set())
    
    if synonyms == "average":
        # Average Jaccard similarity across all cognate pairs
        sims = [jaccard_sim(c1, c2) for c1 in cog1 for c2 in cog2]
        concept_sim = mean(sims) if sims else (0 if missing_data == "zero" else 1)
    
    concept_similarities.append(concept_sim)

# Overall similarity
overall_sim = mean(concept_similarities)

# Apply proximity and sharing factors
final_weight = proximity_weight * overall_sim + sharing_factor * (1 - overall_sim)
```

### Graph Properties

**Node Properties:**
- **Degree**: Number of languages connected to this language
- **Strength**: Sum of edge weights (total similarity to all other languages)
- **Clustering**: Local clustering coefficient

**Edge Properties:**
- **Weight**: Linguistic similarity measure (0 to 1)
- **Significance**: Statistical significance of the similarity (future feature)

## Community Detection Implementation

### Louvain Algorithm Integration

```python
class LouvainCommunities(CommunityMethod):
    def find_communities(self, resolution: Union[float, int]) -> List[FrozenSet]:
        community_generator = nx.algorithms.community.louvain_communities(
            self.graph, weight=self.weight, resolution=resolution
        )
        return [frozenset(community) for community in community_generator]
```

**NetworkX Integration:**
- Uses NetworkX's optimized Louvain implementation
- Supports resolution parameter for multi-level analysis
- Returns communities as frozensets for immutability

### Greedy Modularity Alternative

```python
class GreedyModularity(CommunityMethod):
    def find_communities(self, resolution: Union[float, int]) -> List[FrozenSet]:
        community_generator = nx.algorithms.community.greedy_modularity_communities(
            self.graph, weight=self.weight, resolution=resolution
        )
        return [frozenset(community) for community in community_generator]
```

**Differences from Louvain:**
- More deterministic (no random initialization)
- Slower but potentially more stable results
- Better for reproducible research

## Tree Construction Process

### Algorithm Overview

```python
def build_tree_from_history(history: List[HistoryEntry]) -> TreeNode:
```

**Process:**
1. **Sort by Resolution**: Order history entries from lowest to highest resolution
2. **Root Creation**: Start with single community containing all languages
3. **Recursive Splitting**: For each resolution level:
   - Find communities that split from previous level
   - Create internal nodes for split points
   - Assign branch lengths based on resolution differences
4. **Leaf Assignment**: Assign individual languages to terminal nodes
5. **Tree Refinement**: Remove single-descendant nodes and optimize topology

### Branch Length Calculation

```python
def calculate_branch_length(parent_resolution: float, child_resolution: float) -> float:
    # Basic branch length proportional to resolution difference
    base_length = child_resolution - parent_resolution
    
    # Apply scaling factors for interpretability
    return max(0.001, base_length * BRANCH_LENGTH_SCALE)
```

### Tree Refinement

```python
def remove_single_descendant_nodes(tree: TreeNode) -> TreeNode:
    """Remove internal nodes with only one child."""
    def prune_node(node: TreeNode):
        if len(node.children) == 1 and not node.is_leaf():
            # Merge single child with parent
            child = node.children[0]
            child.dist += node.dist
            # Replace node with child in parent's children list
```

## Parameter Strategies

### Fixed Strategy
```python
class FixedIncrementStrategy(ParameterSearchStrategy):
    def __init__(self, increment: float = 0.1):
        self.increment = increment
    
    def update(self, current_value: float) -> float:
        return current_value + self.increment
```

**Use Case**: When you know the optimal resolution range and want deterministic results.

### Dynamic Strategy
```python
class DynamicAdjustmentStrategy(ParameterSearchStrategy):
    def update(self, current_value: float) -> float:
        self.value += self.adjust_factor * self.value
        return self.value
```

**Adaptive Logic**: Adjusts step size based on current value - smaller steps at higher resolutions.

### Adaptive Strategy
```python
class AdaptiveDynamicAdjustmentStrategy(ParameterSearchStrategy):
    def update(self, current_value: float, current_communities: int) -> float:
        # Sophisticated logic based on community count trends
        if current_communities < self.target:
            # Increase resolution to get more communities
            self.value += self.adjust_factor
        elif current_communities > self.target:  
            # Decrease resolution to get fewer communities
            self.value -= self.adjust_factor
        
        return max(0.001, self.value)
```

**Intelligence**: Monitors community count and adjusts resolution to reach target number of groups.

## Error Handling and Logging

### Logging Configuration
```python
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
```

**Log Levels:**
- **INFO**: Normal operation progress
- **WARNING**: Data quality issues, fallback behaviors
- **ERROR**: Critical failures that prevent analysis

### Common Error Scenarios

1. **File Format Issues**:
   ```python
   except csv.Error as e:
       raise ValueError(f"CSV processing error in file '{input_file}': {e}") from e
   ```

2. **Missing Columns**:
   ```python
   missing_columns = [col for col in required_columns if col not in reader.fieldnames]
   if missing_columns:
       raise ValueError(f"Missing required columns: {missing_columns}")
   ```

3. **Empty or Invalid Data**:
   ```python
   if not lang or not concept or not cognateset_str:
       logging.warning(f"Skipping row due to missing values: {row_dict}")
   ```

## Performance Considerations

### Memory Optimization

1. **Frozensets**: Immutable sets reduce memory overhead and enable caching
2. **Cached Properties**: Expensive calculations cached on first access
3. **Graph Representation**: NetworkX handles sparse graph storage efficiently

### Time Complexity

1. **Graph Construction**: O(n²m) where n = languages, m = concepts
2. **Community Detection**: O(m log n) for Louvain, O(mn log n) for Greedy  
3. **Tree Building**: O(kn) where k = resolution levels
4. **Overall**: Dominated by graph construction for typical datasets

### Scalability Strategies

```python
# For large datasets, consider:
# 1. Sampling concepts for initial analysis
concepts_sample = random.sample(all_concepts, min(100, len(all_concepts)))

# 2. Progressive resolution search
resolution_range = np.logspace(-2, 0, 20)  # Logarithmic spacing

# 3. Memory-efficient graph construction
# Build graph incrementally rather than storing full adjacency matrix
```

## Extension Points

### Adding New Community Detection Methods

```python
class YourCustomMethod(CommunityMethod):
    def find_communities(self, resolution: Union[float, int]) -> List[FrozenSet]:
        # Implement your algorithm here
        # Must return List[FrozenSet[str]] where each frozenset contains language names
        communities = your_algorithm(self.graph, resolution)
        return [frozenset(community) for community in communities]
```

### Adding New Parameter Strategies

```python
class YourCustomStrategy(ParameterSearchStrategy):
    def initialize(self) -> float:
        return your_initial_value
    
    def update(self, current_value: float) -> float:
        # Your update logic here
        return new_value
    
    def should_stop(self, num_communities: int, target: int) -> bool:
        # Your stopping criteria
        return stopping_condition
```

### Adding New Graph Construction Methods

```python
def your_graph_method(data: Dict[Tuple[str, str], Set[int]], **kwargs) -> nx.Graph:
    """Your custom graph construction method."""
    # Build graph according to your method
    # Must return nx.Graph with language names as nodes and similarity weights as edges
    return graph

# Register in build_graph function:
if method == "your_method":
    return your_graph_method(data, **kwargs)
```

### Configuration and Customization

**Command Line Interface Extension:**
```python
# In main() function, add new arguments:
parser.add_argument("--your-parameter", type=float, default=0.5,
                   help="Your custom parameter description")

# Use in graph construction:
graph = build_graph(args.graph, data, your_parameter=args.your_parameter)
```

## Testing and Validation

### Unit Testing Structure
- **Test Data**: Small, controlled datasets with known relationships
- **Algorithm Testing**: Each community detection method tested separately
- **Integration Testing**: Full pipeline validation
- **Performance Testing**: Timing and memory usage on realistic datasets

### Validation Approaches
1. **Known Relationships**: Test against well-established linguistic groupings
2. **Synthetic Data**: Generate data with known community structure
3. **Parameter Sensitivity**: Ensure robust behavior across parameter ranges
4. **Cross-Validation**: Compare results across different methods and parameters

---

*This implementation guide provides the foundation for understanding, modifying, and extending GRAPE. The modular design makes it straightforward to experiment with new algorithms while maintaining compatibility with the existing framework.*