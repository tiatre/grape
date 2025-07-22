#!/usr/bin/env python3
"""
Convert lexibank datasets from CSV to TSV format for GRAPE analysis.
This script standardizes the format and selects the most promising language families
for comprehensive phylogenetic demonstrations.
"""

import pandas as pd
import os
from pathlib import Path

def convert_dataset(csv_path, output_path, family_name):
    """Convert a lexibank CSV dataset to GRAPE TSV format."""
    print(f"\n🔄 Converting {family_name}...")
    
    # Read the CSV file
    df = pd.read_csv(csv_path)
    
    # Check required columns
    required_cols = {'Language_Name', 'Parameter_Name', 'Cognacy'}
    if not required_cols.issubset(df.columns):
        print(f"❌ Missing required columns in {csv_path}")
        return False
    
    # Create GRAPE-compatible format
    grape_df = df[['Language_Name', 'Parameter_Name', 'Cognacy']].copy()
    grape_df.columns = ['Language', 'Parameter', 'Cognateset']
    
    # Remove rows with missing cognate sets
    grape_df = grape_df.dropna(subset=['Cognateset'])
    grape_df = grape_df[grape_df['Cognateset'] != '']
    
    # Convert cognate sets to strings (some might be numeric)
    grape_df['Cognateset'] = grape_df['Cognateset'].astype(str)
    
    # Basic stats
    n_languages = grape_df['Language'].nunique()
    n_concepts = grape_df['Parameter'].nunique()
    n_cognates = grape_df['Cognateset'].nunique()
    n_total = len(grape_df)
    
    print(f"  📊 Statistics:")
    print(f"    Languages: {n_languages}")
    print(f"    Concepts: {n_concepts}")
    print(f"    Cognate sets: {n_cognates}")
    print(f"    Total entries: {n_total}")
    
    # Save to TSV
    grape_df.to_csv(output_path, sep='\t', index=False)
    print(f"  ✅ Saved to: {output_path}")
    
    return True

def create_family_info_file(family_name, info, output_dir):
    """Create an information file for each language family."""
    info_path = output_dir / f"{family_name}_info.md"
    
    with open(info_path, 'w') as f:
        f.write(f"# {info['full_name']} Language Family\n\n")
        f.write(f"## Overview\n\n")
        f.write(f"**Family**: {info['full_name']}\n")
        f.write(f"**Geographic distribution**: {info['geography']}\n")
        f.write(f"**Typology**: {info['typology']}\n")
        f.write(f"**Source dataset**: {info['source']}\n\n")
        
        f.write(f"## Linguistic characteristics\n\n")
        f.write(f"{info['description']}\n\n")
        
        f.write(f"## Subgrouping\n\n")
        for subgroup, description in info['subgroups'].items():
            f.write(f"- **{subgroup}**: {description}\n")
        
        f.write(f"\n## Research significance\n\n")
        f.write(f"{info['significance']}\n\n")

def main():
    """Convert selected language families to GRAPE format."""
    
    datasets_dir = Path("data/datasets")
    output_dir = Path("resources/language_families")
    output_dir.mkdir(exist_ok=True)
    
    # Selected language families for demonstration
    families = {
        'romance': {
            'csv_file': 'saenkoromance.csv',
            'full_name': 'Romance',
            'geography': 'Western and Southern Europe, with extensions into the Americas and Africa',
            'typology': 'Fusional, with rich inflectional morphology and complex verbal systems',
            'source': 'Saenko Romance dataset',
            'description': 'The Romance languages descended from Latin show classic patterns of geographic diffusion and dialectal differentiation. This family demonstrates how languages spread through conquest and cultural contact, with clear isoglosses marking major branches.',
            'subgroups': {
                'Italian': 'Standard Italian, regional varieties, and Corsican',
                'Iberian': 'Spanish, Portuguese, Galician, Catalan, and extinct languages',
                'Gallo-Romance': 'French, Occitan, Franco-Provençal dialects',
                'Eastern Romance': 'Romanian, Aromanian, Megleno-Romanian, Istro-Romanian',
                'Rhaeto-Romance': 'Romansh varieties in Switzerland'
            },
            'significance': 'Romance languages provide an ideal test case for historical linguistics due to their well-documented history and clear derivation from Latin. The family shows both geographic and social stratification patterns.'
        },
        
        'austroasiatic': {
            'csv_file': 'peirosaustroasiatic.csv',
            'full_name': 'Austroasiatic',
            'geography': 'Southeast Asia: Vietnam, Cambodia, Myanmar, India, southern China',
            'typology': 'Primarily isolating to mildly agglutinative, with rich phoneme inventories',
            'source': 'Peiros Austroasiatic dataset',
            'description': 'One of the major language families of Southeast Asia, Austroasiatic includes Vietnamese, Khmer, and many smaller languages. The family shows interesting patterns of contact with Sino-Tibetan and Austronesian families.',
            'subgroups': {
                'Mon-Khmer': 'Vietnamese, Khmer, Mon, and related languages',
                'Munda': 'Languages of eastern India',
                'Bahnaric': 'Languages of Vietnam, Laos, and Cambodia',
                'Katuic': 'Languages along the Vietnam-Laos border',
                'Pearic': 'Endangered languages of Cambodia'
            },
            'significance': 'Austroasiatic languages are crucial for understanding Southeast Asian prehistory and the complex linguistic geography of the region. They show both deep genetic relationships and extensive areal features.'
        },
        
        'turkic': {
            'csv_file': 'savelyevturkic.csv',
            'full_name': 'Turkic', 
            'geography': 'Central Asia, Turkey, parts of Eastern Europe and Siberia',
            'typology': 'Agglutinative with extensive vowel harmony and regular morphophonological alternations',
            'source': 'Savelyev Turkic dataset',
            'description': 'The Turkic languages show remarkable geographic spread from Turkey to Siberia, with relatively conservative core vocabulary and systematic sound changes. The family demonstrates nomadic migration patterns and language contact phenomena.',
            'subgroups': {
                'Oghuz': 'Turkish, Azerbaijani, Turkmen, and related varieties',
                'Kipchak': 'Kazakh, Kyrgyz, Tatar, and related languages',
                'Karluk': 'Uzbek, Uyghur, and related varieties',
                'Siberian': 'Yakut (Sakha), Tuvan, and other northern varieties',
                'Oghur': 'Chuvash (highly divergent branch)'
            },
            'significance': 'Turkic languages provide excellent examples of regular sound change, vowel harmony systems, and the effects of geographic dispersal on related languages. The family also shows interesting contact phenomena with Indo-European, Mongolic, and other families.'
        },
        
        'bantu': {
            'csv_file': 'grollemundbantu.csv',
            'full_name': 'Bantu',
            'geography': 'Sub-Saharan Africa from Cameroon to South Africa',
            'typology': 'Agglutinative with complex noun class systems and extensive verbal derivation',
            'source': 'Grollemund Bantu dataset',
            'description': 'The Bantu languages represent one of the most successful language expansions in human history, spreading across most of sub-Saharan Africa. They show systematic sound correspondences and shared innovations in their noun class and verbal systems.',
            'subgroups': {
                'Western Bantu': 'Languages of Cameroon, Equatorial Guinea, and northwestern regions',
                'Eastern Bantu': 'Swahili, Kikuyu, and languages of East Africa',
                'Southern Bantu': 'Zulu, Xhosa, Shona, and related languages',
                'Central Bantu': 'Lingala, Mongo, and languages of the Congo Basin'
            },
            'significance': 'Bantu languages demonstrate massive demographic expansion and provide insights into African prehistory. Their systematic sound correspondences and shared grammatical innovations make them ideal for phylogenetic analysis.'
        }
    }
    
    print("🌍 GRAPE Language Family Dataset Conversion")
    print("=" * 50)
    
    converted_families = []
    
    for family_key, family_info in families.items():
        csv_path = datasets_dir / family_info['csv_file']
        output_path = output_dir / f"{family_key}.tsv"
        
        if csv_path.exists():
            if convert_dataset(csv_path, output_path, family_info['full_name']):
                converted_families.append(family_key)
                create_family_info_file(family_key, family_info, output_dir)
        else:
            print(f"❌ Source file not found: {csv_path}")
    
    # Copy existing datasets that are already in good format
    existing_datasets = {
        'dravidian': 'data/dravlex.tsv',
        'polynesian': 'data/walworthpolynesian.tsv', 
        'tupian': 'data/tuled.tsv'
    }
    
    print(f"\n📋 Copying existing datasets...")
    for family, source_path in existing_datasets.items():
        if os.path.exists(source_path):
            target_path = output_dir / f"{family}.tsv"
            
            # Copy and standardize
            df = pd.read_csv(source_path, sep='\t')
            df.to_csv(target_path, sep='\t', index=False)
            print(f"  ✅ Copied {family}: {source_path} -> {target_path}")
            converted_families.append(family)
    
    # Create master summary
    summary_path = output_dir / "README.md"
    with open(summary_path, 'w') as f:
        f.write("# GRAPE Language Family Resources\n\n")
        f.write("This directory contains curated language family datasets for phylogenetic analysis with GRAPE.\n\n")
        f.write("## Available Language Families\n\n")
        
        for family in sorted(converted_families):
            f.write(f"- **{family.title()}**: `{family}.tsv` - See `{family}_info.md` for details\n")
        
        f.write("\n## Data Format\n\n")
        f.write("All datasets use the standard GRAPE TSV format:\n")
        f.write("- `Language`: Language name/identifier\n")
        f.write("- `Parameter`: Concept/meaning identifier\n") 
        f.write("- `Cognateset`: Cognate set identifier\n\n")
        
        f.write("## Usage\n\n")
        f.write("```bash\n")
        f.write("# Basic analysis\n")
        f.write("python grape.py resources/language_families/romance.tsv --seed 42\n\n")
        f.write("# With specific parameters\n")
        f.write("python grape.py resources/language_families/austroasiatic.tsv \\\n")
        f.write("    --graph adjusted --community louvain --strategy fixed --initial_value 0.5 --seed 42\n")
        f.write("```\n")
    
    print(f"\n🎉 Conversion complete!")
    print(f"  Converted families: {len(converted_families)}")
    print(f"  Output directory: {output_dir}")
    print(f"  Summary: {summary_path}")

if __name__ == "__main__":
    main()