# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GRAPE (Graph Analysis and Phylogenetic Estimation) is a Python library for phylogenetic inference using community detection in graphs. The project focuses on analyzing linguistic cognate data to build phylogenetic trees using graph-based methods.

## Architecture

### Core Components

- **grape.py**: Main module containing community detection methods, parameter search strategies, and tree construction logic
- **common.py**: Shared data structures (HistoryEntry) and utility functions for reading cognate files  
- **distance_tree.py**: Alternative phylogenetic methods using distance matrices (NJ/UPGMA) with BioPython

### Key Classes

- `CommunityMethod` (abstract): Base class for community detection algorithms
  - `GreedyModularity`: Uses NetworkX greedy modularity maximization
  - `LouvainCommunities`: Uses NetworkX Louvain algorithm
- `ParameterSearchStrategy` (abstract): Base class for parameter optimization
  - `FixedParameterStrategy`: Uses fixed resolution value
  - `DynamicParameterStrategy`: Adjusts parameters based on community count
  - `AdaptiveDynamicAdjustmentStrategy`: Adaptive parameter adjustment

### Data Flow

1. Read cognate data from TSV files using `common.read_cognate_file()`
2. Build NetworkX graph with linguistic distance weights
3. Apply community detection at different resolution parameters
4. Convert community structure to phylogenetic tree using ETE3
5. Output final tree in Newick format

## Common Commands

### Running GRAPE Analysis

```bash
# Basic usage with sample data
python grape.py data/iecor_small.tsv

# With specific parameters
python grape.py data/iecor_small.tsv --graph adjusted --community louvain --strategy fixed --initial_value 0.5

# Advanced options
python grape.py data/dataset.tsv --graph adjusted --community greedy --strategy adaptive --proximity_weight 0.8 --sharing_factor 0.3
```

### Command Line Options

- `--graph {adjusted,unadjusted}`: Graph construction method
- `--community {greedy,louvain}`: Community detection algorithm  
- `--strategy {fixed,dynamic,adaptive}`: Parameter search strategy
- `--synonyms {average,min,max}`: Synonym handling for adjusted weights
- `--missing_data {max_dist,zero,ignore}`: Missing data strategy

### Testing with Sample Data

The `data/` directory contains several cognate datasets:
- `iecor_small.tsv`: Small Indo-European dataset (recommended for testing)
- `iecor_full.tsv`: Full Indo-European dataset
- `dravlex.tsv`: Dravidian languages
- `tuled.tsv`: Tupian languages

## Development Notes

### Dependencies

Core dependencies from requirements.txt:
- `ete3`: Tree manipulation and visualization
- `networkx`: Graph algorithms and community detection
- `numpy`: Numerical computations
- `six`: Python 2/3 compatibility (required by ete3)

Additional dependency for distance-based methods:
- `biopython`: Required for distance_tree.py (NJ/UPGMA methods)

### Output Format

GRAPE outputs phylogenetic trees in Newick format to standard output.

### Testing

Run the test suite with:

```bash
# Basic tests
python test_grape.py -v

# Extended tests with different parameter combinations  
python test_grape_extended.py -v
```

Current tests validate:
- **Germanic grouping**: All 7 Germanic languages (Danish, Dutch, Elfdalian, English, Frisian, German, Swedish) form a monophyletic group in `harald_ie.tsv`
- **Spanish positioning**: Spanish is closer to Germanic languages than to Hindi
- **Branch length accuracy**: Swedish-Danish distance < Swedish-English distance
- **Guaranic group**: Mbya, Guarani, and Kaiowa form a monophyletic group in `tuled.tsv`
- **Early branching**: Mawe and Aweti branch early from the rest of the Tupian tree
- **Parameter robustness**: Tests work across different community detection methods and graph types

### Known Issues

- AdaptiveDynamicAdjustmentStrategy has a bug in the `update()` method signature
- BioPython dependency needed for distance_tree.py but not in requirements.txt

### File Format

Input files should be TSV format with columns:
- Language: Language identifier
- Parameter: Concept/meaning identifier  
- Cognateset: Cognate set identifier

Custom column names can be specified via `--language-column`, `--concept-column`, and `--cognateset-column` flags.