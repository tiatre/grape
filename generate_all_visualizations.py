#!/usr/bin/env python3
"""
Generate comprehensive tree visualizations for all GRAPE language families.
This script creates visualizations for our expanded set of language families.
"""

import os
import subprocess
import sys
from ete3 import Tree
from typing import Dict, List, Optional

def run_grape_analysis(dataset: str, output_prefix: str, **kwargs) -> Optional[str]:
    """Run GRAPE analysis and return Newick tree string."""
    cmd = ['python', 'grape.py', dataset, '--seed', '42']
    
    # Add custom parameters
    for key, value in kwargs.items():
        cmd.extend([f'--{key}', str(value)])
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Save full log
        with open(f'{output_prefix}_analysis.log', 'w') as f:
            f.write(result.stderr)
        
        # Extract Newick tree
        lines = result.stderr.split('\n')
        for line in lines:
            if '[INFO] Newick format tree:' in line:
                newick = line.split('[INFO] Newick format tree: ', 1)[1].strip()
                
                # Save Newick tree
                with open(f'{output_prefix}.newick', 'w') as f:
                    f.write(newick)
                    
                return newick
        
        print(f"Warning: No Newick tree found in output for {dataset}")
        return None
        
    except subprocess.CalledProcessError as e:
        print(f"Error running GRAPE on {dataset}: {e.stderr}")
        return None

def analyze_tree_structure(tree: Tree, family_name: str) -> Dict:
    """Analyze tree structure and linguistic groupings."""
    analysis = {
        'num_languages': len(tree.get_leaves()),
        'tree_height': tree.get_farthest_leaf()[1],
        'language_list': [leaf.name for leaf in tree.get_leaves()],
        'linguistic_groups': {}
    }
    
    # Define expected linguistic groupings for validation
    groupings = {
        'Romance': {
            'Italian': ['Italian', 'Neapolitan', 'Friulian', 'Ladin', 'Venetian', 'Lombard', 'Piedmontese'],
            'Iberian': ['Spanish', 'Portuguese', 'Galician', 'Catalan', 'Aragonese', 'Mirandese'],
            'Gallo-Romance': ['French', 'Occitan', 'Franco-Provençal', 'Walloon'],
            'Eastern Romance': ['Romanian', 'Aromanian', 'Megleno-Romanian', 'Istro-Romanian'],
            'Rhaeto-Romance': ['Romansh', 'Rumantsch']
        },
        'Austroasiatic': {
            'Mon-Khmer': ['Vietnamese', 'Mon', 'Khmer'],
            'Munda': ['Santali', 'Mundari', 'Ho'],
            'Bahnaric': ['Stieng', 'Chrau', 'Bru'],
            'Katuic': ['Katu', 'Pacoh'],
            'Pearic': ['Pear', 'Chong']
        },
        'Turkic': {
            'Oghuz': ['Turkish', 'Azerbaijani', 'Turkmen', 'Gagauz'],
            'Kipchak': ['Kazakh', 'Kyrgyz', 'Tatar', 'Bashkir'],
            'Karluk': ['Uzbek', 'Uyghur'],
            'Siberian': ['Yakut', 'Tuvan', 'Altai', 'Khakas'],
            'Oghur': ['Chuvash']
        },
        'Bantu': {
            'Eastern Bantu': ['Swahili', 'Kikuyu', 'Kinyarwanda', 'Kirundi'],
            'Southern Bantu': ['Zulu', 'Xhosa', 'Sotho', 'Tswana'],
            'Western Bantu': ['Lingala', 'Kikongo', 'Fang'],
            'Central Bantu': ['Luba', 'Mongo', 'Tetela']
        },
        'Dravidian': {
            'South Dravidian': ['Tamil', 'Malayalam', 'Kannada', 'Tulu', 'Kodava', 'Badga', 'Kota', 'Toda'],
            'Central Dravidian': ['Gondi', 'Koya', 'Kuwi', 'Kolami', 'Parji', 'Ollari_Gadba'],
            'North Dravidian': ['Brahui', 'Kurukh', 'Malto']
        },
        'Polynesian': {
            'Tongic': ['Lea_Fakatonga', 'Vagahau_Niue'],
            'Eastern Polynesian': ['olelo_Hawaii', 'Reo_Tahiti', 'Reo_Maori', 'Rapanui', 'eo_enana'],
            'Nuclear Polynesian': []
        },
        'Tupian': {
            'Guaranic': ['Mbya', 'Guarani', 'Kaiowa'],
            'Early Branching': ['Mawe', 'Aweti']
        }
    }
    
    family_groups = groupings.get(family_name, {})
    
    # Check which languages from each group are present in the tree
    for group_name, expected_langs in family_groups.items():
        present_langs = [lang for lang in expected_langs if lang in analysis['language_list']]
        if present_langs:
            analysis['linguistic_groups'][group_name] = present_langs
    
    return analysis

def generate_ascii_tree(tree: Tree, output_file: str):
    """Generate ASCII representation of the tree."""
    with open(output_file, 'w') as f:
        f.write(tree.get_ascii(show_internal=True))
    print(f"Generated ASCII tree: {output_file}")

def generate_formatted_tree(tree: Tree, output_file: str, family_name: str):
    """Generate formatted tree representation with linguistic annotations."""
    analysis = analyze_tree_structure(tree, family_name)
    
    with open(output_file, 'w') as f:
        f.write(f"{family_name} Language Family Phylogenetic Tree\\n")
        f.write("=" * 50 + "\\n\\n")
        
        # Basic tree info
        f.write("TREE STATISTICS:\\n")
        f.write(f"  Languages: {analysis['num_languages']}\\n")
        f.write(f"  Tree height: {analysis['tree_height']:.3f}\\n\\n")
        
        # ASCII tree
        f.write("TREE STRUCTURE:\\n")
        f.write("-" * 20 + "\\n")
        f.write(tree.get_ascii(show_internal=True))
        f.write("\\n\\n")
        
        # Linguistic groupings
        f.write("LINGUISTIC GROUPINGS FOUND:\\n")
        f.write("-" * 25 + "\\n")
        for group_name, languages in analysis['linguistic_groups'].items():
            f.write(f"{group_name}: {', '.join(languages)}\\n")
        
        if not analysis['linguistic_groups']:
            f.write("No recognized linguistic groupings detected in this tree.\\n")
            
        f.write("\\n")
        f.write("ALL LANGUAGES IN TREE:\\n")
        f.write("-" * 20 + "\\n")
        for lang in sorted(analysis['language_list']):
            f.write(f"  • {lang}\\n")
    
    print(f"Generated formatted tree: {output_file}")

def main():
    """Generate visualizations for all language families."""
    
    # Create output directory
    os.makedirs('docs/images/trees', exist_ok=True)
    
    # Language family datasets with optimized parameters
    datasets = {
        'Romance': {
            'file': 'resources/language_families/romance.tsv',
            'params': {'strategy': 'fixed', 'initial_value': 0.4, 'community': 'louvain'}
        },
        'Austroasiatic': {
            'file': 'resources/language_families/austroasiatic.tsv',
            'params': {'strategy': 'fixed', 'initial_value': 0.3, 'community': 'louvain'}
        },
        'Turkic': {
            'file': 'resources/language_families/turkic.tsv', 
            'params': {'strategy': 'fixed', 'initial_value': 0.5, 'community': 'greedy'}
        },
        'Bantu': {
            'file': 'resources/language_families/bantu.tsv',
            'params': {'strategy': 'fixed', 'initial_value': 0.2, 'community': 'louvain'}  # Lower resolution for large family
        },
        'Dravidian': {
            'file': 'resources/language_families/dravidian.tsv',
            'params': {'strategy': 'fixed', 'initial_value': 0.5, 'community': 'greedy'}
        },
        'Polynesian': {
            'file': 'resources/language_families/polynesian.tsv',
            'params': {'strategy': 'dynamic', 'initial_value': 0.6, 'community': 'louvain'}
        },
        'Tupian': {
            'file': 'resources/language_families/tupian.tsv',
            'params': {'strategy': 'fixed', 'initial_value': 0.5, 'community': 'greedy'}
        }
    }
    
    results = {}
    
    print("=" * 60)
    print("GENERATING COMPREHENSIVE TREE VISUALIZATIONS FOR GRAPE")
    print("=" * 60)
    
    for family_name, config in datasets.items():
        print(f"\\n🌳 Processing {family_name} language family...")
        
        if not os.path.exists(config['file']):
            print(f"   ⚠️  Dataset {config['file']} not found, skipping...")
            continue
            
        output_prefix = f"docs/images/trees/{family_name.lower()}"
        
        # Run GRAPE analysis
        newick = run_grape_analysis(config['file'], output_prefix, **config['params'])
        
        if newick:
            try:
                tree = Tree(newick)
                results[family_name] = {
                    'tree': tree,
                    'newick': newick,
                    'languages': len(tree.get_leaves()),
                    'file': config['file']
                }
                
                print(f"   ✓ Parsed tree with {len(tree.get_leaves())} languages")
                
                # Generate ASCII representation
                generate_ascii_tree(tree, f"{output_prefix}_ascii.txt")
                
                # Generate formatted tree with linguistic analysis
                generate_formatted_tree(tree, f"{output_prefix}_formatted.txt", family_name)
                
                # Generate summary
                with open(f"{output_prefix}_summary.txt", 'w') as f:
                    f.write(f"{family_name} Language Family Tree\\n")
                    f.write("=" * 40 + "\\n\\n")
                    f.write(f"Dataset: {config['file']}\\n")
                    f.write(f"Languages: {len(tree.get_leaves())}\\n")
                    f.write(f"Tree height: {tree.get_farthest_leaf()[1]:.3f}\\n")
                    f.write(f"Parameters: {config['params']}\\n\\n")
                    f.write("Languages in tree:\\n")
                    for leaf in sorted(tree.get_leaves(), key=lambda x: x.name):
                        f.write(f"  - {leaf.name}\\n")
                    f.write(f"\\nNewick format:\\n{newick}\\n")
                
                print(f"   ✓ Generated all visualizations for {family_name}")
                
            except Exception as e:
                print(f"   ❌ Error processing tree for {family_name}: {e}")
        else:
            print(f"   ❌ Failed to generate tree for {family_name}")
    
    # Generate comprehensive summary report
    print(f"\\n📊 Generating comprehensive summary report...")
    
    with open('docs/images/trees/COMPREHENSIVE_SUMMARY.md', 'w') as f:
        f.write("# GRAPE Comprehensive Language Family Visualizations\\n\\n")
        f.write("This directory contains phylogenetic tree visualizations for 7 major language families analyzed by GRAPE.\\n\\n")
        f.write("## Overview\\n\\n")
        f.write("GRAPE has been applied to a diverse set of language families representing different continents, ")
        f.write("typological characteristics, and demographic histories. This comprehensive analysis demonstrates ")
        f.write("the versatility of graph-based phylogenetic methods across various linguistic contexts.\\n\\n")
        
        f.write("## Language Families\\n\\n")
        
        for family_name, data in results.items():
            f.write(f"### {family_name}\\n\\n")
            f.write(f"- **Dataset**: {data['file']}\\n")
            f.write(f"- **Languages**: {data['languages']}\\n") 
            f.write(f"- **Tree height**: {data['tree'].get_farthest_leaf()[1]:.3f}\\n")
            f.write(f"- **Visualization files**:\\n")
            f.write(f"  - ASCII tree: `{family_name.lower()}_ascii.txt`\\n")
            f.write(f"  - Formatted analysis: `{family_name.lower()}_formatted.txt`\\n")
            f.write(f"  - Analysis log: `{family_name.lower()}_analysis.log`\\n")
            f.write(f"  - Newick format: `{family_name.lower()}.newick`\\n")
            f.write(f"  - Summary: `{family_name.lower()}_summary.txt`\\n\\n")
        
        f.write("## Geographic and Typological Diversity\\n\\n")
        f.write("This collection represents:\\n\\n")
        f.write("**Geographic Coverage:**\\n")
        f.write("- **Europe**: Romance languages (Western/Southern Europe)\\n")
        f.write("- **Asia**: Austroasiatic (Southeast Asia), Turkic (Central Asia)\\n")
        f.write("- **Africa**: Bantu languages (Sub-Saharan Africa)\\n") 
        f.write("- **Oceania**: Polynesian languages (Pacific Islands)\\n")
        f.write("- **Americas**: Tupian languages (South America)\\n")
        f.write("- **India**: Dravidian languages (South India)\\n\\n")
        
        f.write("**Typological Diversity:**\\n")
        f.write("- **Fusional**: Romance (complex inflectional morphology)\\n")
        f.write("- **Agglutinative**: Turkic (vowel harmony), Bantu (noun classes), Dravidian\\n")
        f.write("- **Isolating**: Austroasiatic (analytic tendencies)\\n")
        f.write("- **Mixed**: Polynesian, Tupian (various morphological strategies)\\n\\n")
        
        f.write("## Research Applications\\n\\n")
        f.write("These visualizations support research in:\\n")
        f.write("- **Historical linguistics**: Testing phylogenetic hypotheses\\n")
        f.write("- **Comparative method**: Validating traditional subgroupings\\n")
        f.write("- **Language contact**: Understanding areal influences\\n")
        f.write("- **Computational phylogenetics**: Methodological development\\n")
        f.write("- **Linguistic typology**: Cross-family comparative studies\\n\\n")
        
        f.write("## Methodology\\n\\n")
        f.write("All analyses use GRAPE with:\\n")
        f.write("- **Reproducible results**: Fixed random seed (42)\\n")
        f.write("- **Optimized parameters**: Family-specific resolution settings\\n")  
        f.write("- **Standard format**: TSV input with Language/Parameter/Cognateset columns\\n")
        f.write("- **Multiple algorithms**: Louvain and Greedy modularity methods\\n\\n")
        
        f.write("## Citation\\n\\n")
        f.write("When using these visualizations, please cite:\\n")
        f.write("- The original datasets (see individual family info files)\\n")
        f.write("- GRAPE methodology and software\\n")
        f.write("- Specific analysis parameters used for each family\\n")
    
    print(f"\\n🎉 Comprehensive visualization generation complete!")
    print(f"   Generated visualizations for {len(results)} language families")
    print(f"   Files saved to: docs/images/trees/")
    print(f"   Comprehensive summary: docs/images/trees/COMPREHENSIVE_SUMMARY.md")
    
    return results

if __name__ == "__main__":
    results = main()