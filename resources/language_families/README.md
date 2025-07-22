# GRAPE Language Family Resources

This directory contains curated language family datasets for phylogenetic analysis with GRAPE.

## Available Language Families

- **Austroasiatic**: `austroasiatic.tsv` - See `austroasiatic_info.md` for details
- **Bantu**: `bantu.tsv` - See `bantu_info.md` for details
- **Dravidian**: `dravidian.tsv` - See `dravidian_info.md` for details
- **Polynesian**: `polynesian.tsv` - See `polynesian_info.md` for details
- **Romance**: `romance.tsv` - See `romance_info.md` for details
- **Tupian**: `tupian.tsv` - See `tupian_info.md` for details
- **Turkic**: `turkic.tsv` - See `turkic_info.md` for details

## Data Format

All datasets use the standard GRAPE TSV format:
- `Language`: Language name/identifier
- `Parameter`: Concept/meaning identifier
- `Cognateset`: Cognate set identifier

## Usage

```bash
# Basic analysis
python grape.py resources/language_families/romance.tsv --seed 42

# With specific parameters
python grape.py resources/language_families/austroasiatic.tsv \
    --graph adjusted --community louvain --strategy fixed --initial_value 0.5 --seed 42
```
