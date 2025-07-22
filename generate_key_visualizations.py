#!/usr/bin/env python3
"""
Generate visualizations for key language families (excluding the very large Bantu dataset).
"""

import os
import subprocess
import sys
from ete3 import Tree

# Simplified version focusing on key families
datasets = {
    'Romance': {
        'file': 'resources/language_families/romance.tsv',
        'params': {'strategy': 'fixed', 'initial_value': 0.4}
    },
    'Austroasiatic': {
        'file': 'resources/language_families/austroasiatic.tsv',
        'params': {'strategy': 'fixed', 'initial_value': 0.3}
    },
    'Turkic': {
        'file': 'resources/language_families/turkic.tsv',
        'params': {'strategy': 'fixed', 'initial_value': 0.5}
    }
}

def run_grape_analysis(dataset: str, output_prefix: str, **kwargs):
    """Run GRAPE analysis and return Newick tree string."""
    cmd = ['python', 'grape.py', dataset, '--seed', '42']
    
    for key, value in kwargs.items():
        cmd.extend([f'--{key}', str(value)])
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Save log
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
        
        return None
        
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return None

def generate_formatted_tree(tree: Tree, output_file: str, family_name: str):
    """Generate formatted tree representation."""
    with open(output_file, 'w') as f:
        f.write(f"{family_name} Language Family Phylogenetic Tree\\n")
        f.write("=" * 50 + "\\n\\n")
        
        # Basic tree info
        leaves = tree.get_leaves()
        f.write("TREE STATISTICS:\\n")
        f.write(f"  Languages: {len(leaves)}\\n")
        f.write(f"  Tree height: {tree.get_farthest_leaf()[1]:.3f}\\n\\n")
        
        # ASCII tree
        f.write("TREE STRUCTURE:\\n")
        f.write("-" * 20 + "\\n")
        f.write(tree.get_ascii(show_internal=True))
        f.write("\\n\\n")
        
        f.write("ALL LANGUAGES IN TREE:\\n")
        f.write("-" * 20 + "\\n")
        for lang in sorted([leaf.name for leaf in leaves]):
            f.write(f"  • {lang}\\n")

# Create output directory
os.makedirs('docs/images/trees', exist_ok=True)

print("🌳 Generating Key Language Family Visualizations")
print("=" * 50)

results = {}

for family_name, config in datasets.items():
    print(f"\\n🌳 Processing {family_name}...")
    
    if not os.path.exists(config['file']):
        print(f"   Dataset not found: {config['file']}")
        continue
        
    output_prefix = f"docs/images/trees/{family_name.lower()}"
    
    # Run GRAPE analysis
    newick = run_grape_analysis(config['file'], output_prefix, **config['params'])
    
    if newick:
        try:
            tree = Tree(newick)
            print(f"   ✓ Generated tree with {len(tree.get_leaves())} languages")
            
            # Generate formatted tree
            generate_formatted_tree(tree, f"{output_prefix}_formatted.txt", family_name)
            
            # Generate ASCII tree
            with open(f"{output_prefix}_ascii.txt", 'w') as f:
                f.write(tree.get_ascii(show_internal=True))
            
            results[family_name] = len(tree.get_leaves())
            
        except Exception as e:
            print(f"   Error processing: {e}")
    else:
        print(f"   Failed to generate tree")

print(f"\\n✅ Generated visualizations for {len(results)} families:")
for family, count in results.items():
    print(f"   {family}: {count} languages")