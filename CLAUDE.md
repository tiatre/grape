# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GRAPE (Graph Analysis and Phylogenetic Estimation) is a Python library for phylogenetic inference using community detection in graphs. The project focuses on analyzing linguistic cognate data to build phylogenetic trees using graph-based methods.

## Documentation Structure

The project includes comprehensive documentation in multiple formats:

### Main Documentation Files
- **README.md**: Main project overview and quick start guide
- **CLAUDE.md**: This file - development guidance and internal documentation
- **docs/**: Comprehensive documentation directory

### Documentation Categories

**For Users** (`docs/user_guide/`):
- Quick start guides and tutorials
- Parameter reference and usage examples
- FAQ and troubleshooting

**For Researchers** (`docs/technical/`):
- Mathematical background and theory
- Implementation details and algorithms
- Performance analysis and benchmarks

**Examples and Walkthroughs** (`docs/examples/`):
- Complete language family analyses
- Interactive Jupyter notebooks
- Advanced usage scenarios

**Academic Documentation** (`docs/academic/`):
- Research paper foundations
- Methodology descriptions
- Comparative studies and validation

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
# Basic tests for original datasets
python test_grape.py -v

# Extended tests with different parameter combinations for original datasets  
python test_grape_extended.py -v

# Tests for additional language families
python test_additional_families.py -v

# Extended tests for additional families with different parameters
python test_additional_families_extended.py -v
```

#### Core Test Coverage

**Original datasets** (test_grape.py, test_grape_extended.py):
- **Germanic grouping**: All 7 Germanic languages (Danish, Dutch, Elfdalian, English, Frisian, German, Swedish) form a monophyletic group in `harald_ie.tsv`
- **Spanish positioning**: Spanish is closer to Germanic languages than to Hindi
- **Branch length accuracy**: Swedish-Danish distance < Swedish-English distance
- **Guaranic group**: Mbya, Guarani, and Kaiowa form a monophyletic group in `tuled.tsv`
- **Early branching**: Mawe and Aweti branch early from the rest of the Tupian tree
- **Parameter robustness**: Tests work across different community detection methods and graph types

**Additional language families** (test_additional_families.py, test_additional_families_extended.py):

*Dravidian languages* (`dravlex.tsv`):
- **South Dravidian grouping**: Tamil, Malayalam, Kannada, Tulu, and related languages form monophyletic group
- **Central Dravidian grouping**: Gondi, Koya, Kuwi, Kolami, Parji, Ollari_Gadba group together
- **North Dravidian grouping**: Brahui, Kurukh, Malto form a monophyletic group
- **Tamil-Malayalam relationship**: Closer to each other than to North Dravidian languages

*Polynesian languages* (`walworthpolynesian.tsv`):
- **Tongic grouping**: Tongan (Lea_Fakatonga) and Niuean (Vagahau_Niue) form a group
- **Eastern Polynesian grouping**: Hawaiian, Tahitian, Maori, Rarotongan, Marquesan, Rapa Nui group together
- **Nuclear Polynesian hypothesis**: Hawaiian closer to Samoan than to Tongan
- **Triangular relationships**: Tahitian closer to Hawaiian than to Tongan

*Arawakan languages* (`chaconarawakan.tsv`):
- **Northern Arawakan grouping**: Baniwa, Tariana, Achagua, Piapoco group together
- **Geographic clustering**: Baniwa and Tariana (both Vaupés region) are closely related
- **Resigaro distinctness**: Maintains reasonable phylogenetic position

*Indo-European full dataset* (`iecor_full.tsv`, 160 languages):
- **Romance grouping**: French, Spanish, Italian, Portuguese, Catalan, Romanian, etc. form monophyletic group
- **Germanic grouping**: English, German, Dutch, Swedish, Danish, Norwegian, Gothic, etc. group together
- **Celtic grouping**: Irish, Welsh, Breton varieties, Scottish Gaelic, Cornish, Manx form a group
- **Slavic grouping**: Russian, Czech, Polish, Bulgarian, Serbian, Ukrainian, etc. form monophyletic group
- **Indo-Iranian grouping**: Sanskrit, Hindi, Persian, Bengali, Kurdish, Pashto, etc. group together

### Known Issues

- AdaptiveDynamicAdjustmentStrategy has a bug in the `update()` method signature
- BioPython dependency needed for distance_tree.py but not in requirements.txt

## Academic Paper Development (Future Work)

### Paper Structure and Content Plan

**Title**: "GRAPE: Graph-Based Community Detection for Phylogenetic Inference in Historical Linguistics"

**Target Venues**:
- Journal of Language Evolution
- Computational Linguistics  
- Digital Scholarship in the Humanities
- PLoS ONE (interdisciplinary approach)

**Abstract Outline**:
- Problem: Traditional phylogenetic methods assume tree-like evolution, but languages exhibit network-like borrowing patterns
- Solution: Graph-based community detection approach using modularity optimization
- Methods: Louvain and Greedy modularity algorithms applied to cognate sharing networks
- Validation: Testing on 7 language families (200+ languages) against established linguistic classifications
- Results: Successfully recovers known language groupings while capturing horizontal relationships
- Impact: Novel computational approach for historical linguistics with broader applicability

**Main Sections**:

1. **Introduction**
   - Historical linguistics and phylogenetic reconstruction challenges
   - Limitations of tree-based models for language evolution
   - Community detection in networks as alternative approach
   - Contribution and significance

2. **Background and Related Work**
   - Traditional phylogenetic methods in linguistics (NJ, ML, Bayesian)
   - Network approaches in historical linguistics
   - Community detection algorithms and applications
   - Graph construction from linguistic data

3. **Methodology**
   - Graph construction from cognate data (adjusted vs. unadjusted methods)
   - Community detection algorithms (Louvain, Greedy Modularity)  
   - Parameter optimization strategies (fixed, dynamic, adaptive)
   - Tree construction from hierarchical community structure
   - Implementation details and computational complexity

4. **Experimental Setup**
   - Dataset description (7 language families, data sources)
   - Validation criteria (linguistic consensus, established classifications)
   - Comparison with traditional methods (NJ, UPGMA)
   - Evaluation metrics (monophyly tests, tree topology comparison)

5. **Results**
   - Detailed results for each language family
   - Comparison with traditional phylogenetic methods
   - Parameter sensitivity analysis
   - Performance evaluation (runtime, scalability)
   - Novel insights and discoveries

6. **Discussion**
   - Methodological advantages and limitations
   - Linguistic implications and interpretations
   - Comparison with existing approaches
   - Future directions and extensions

7. **Conclusion**
   - Summary of contributions
   - Impact on historical linguistics methodology
   - Broader applicability beyond linguistics

**Key Figures and Tables**:
- Figure 1: GRAPE workflow and methodology overview
- Figure 2: Example phylogenetic trees for major language families
- Figure 3: Comparison of GRAPE vs. traditional method results
- Figure 4: Parameter sensitivity and performance analysis
- Table 1: Language families and datasets used
- Table 2: Validation results against linguistic consensus
- Table 3: Performance comparison with existing methods

**Supplementary Materials**:
- Complete dataset descriptions and sources
- Detailed parameter sensitivity analysis
- All phylogenetic trees in machine-readable format
- Source code and reproducibility instructions
- Extended validation results for all language families

### Validation Strategy for Academic Publication

**Quantitative Validation**:
- Monophyly tests for established language groups
- Robinson-Foulds distance comparisons with reference trees
- Bootstrap support analysis (adaptation for community detection)
- Cross-validation across different parameter settings

**Qualitative Validation**:
- Expert linguistic review of controversial groupings
- Comparison with recent phylogenetic studies
- Analysis of novel insights and their plausibility
- Discussion of discrepancies and their potential explanations

**Statistical Analysis**:
- Significance testing for tree topology differences
- Confidence intervals for parameter estimates
- Correlation analysis between different similarity measures
- Power analysis for different dataset sizes

### Technical Requirements for Paper

**Reproducibility Standards**:
- All analyses must use fixed random seeds (--seed 42)
- Complete parameter specifications for all results
- Version-controlled code with DOI assignment
- Docker container for computational environment
- Detailed step-by-step analysis protocols

**Data Availability**:
- All datasets with proper attribution and licensing
- Processed intermediate results (graphs, community structures)
- Complete result files in standard formats
- Metadata describing data sources and preparation

**Code Quality**:
- Comprehensive test suite with >90% coverage
- Documentation following academic software standards
- Performance benchmarking and optimization
- Code review by independent researchers

### Collaboration and Review Process

**Internal Review**:
- Technical validation by independent implementers
- Linguistic validation by domain experts
- Statistical review by quantitative linguists
- Methodological review by network science experts

**External Validation**:
- Replication studies using independent implementations
- Application to additional language families
- Comparison studies by other research groups
- Integration with existing phylogenetic software ecosystems

### Timeline for Paper Development

1. **Phase 1** (Completed): Core methodology and implementation
2. **Phase 2** (Completed): Comprehensive validation and testing  
3. **Phase 3** (Next): Extended analysis and comparison studies
4. **Phase 4**: Manuscript preparation and internal review
5. **Phase 5**: External review and revision cycles
6. **Phase 6**: Journal submission and peer review process

**Estimated Timeline**: 6-12 months from Phase 3 to publication, depending on review cycles and revisions required.

### File Format

Input files should be TSV format with columns:
- Language: Language identifier
- Parameter: Concept/meaning identifier  
- Cognateset: Cognate set identifier

Custom column names can be specified via `--language-column`, `--concept-column`, and `--cognateset-column` flags.