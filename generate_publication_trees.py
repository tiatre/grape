#!/usr/bin/env python3
"""
Generate publication-quality phylogenetic tree visualizations for GRAPE.
Follows best practices for linguistic phylogenetic tree visualization.
"""

import os
import subprocess
import sys
from pathlib import Path
import colorsys
from ete3 import Tree, TreeStyle, NodeStyle, faces, AttrFace, TextFace
from typing import Dict, List, Optional, Tuple

# Configure matplotlib backend for headless operation
import matplotlib
matplotlib.use('Agg')

def generate_color_palette(n_colors: int) -> List[str]:
    """Generate a visually distinct color palette for language groups."""
    colors = []
    for i in range(n_colors):
        hue = i / n_colors
        saturation = 0.7 + (i % 2) * 0.2  # Vary saturation
        lightness = 0.5 + (i % 3) * 0.15   # Vary lightness
        rgb = colorsys.hls_to_rgb(hue, lightness, saturation)
        hex_color = '#{:02x}{:02x}{:02x}'.format(
            int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)
        )
        colors.append(hex_color)
    return colors

def get_linguistic_groups(family_name: str) -> Dict[str, List[str]]:
    """Define linguistic subgroups for each language family."""
    groupings = {
        'Romance': {
            'Italian': ['Italian', 'Neapolitan', 'Friulian', 'Venetian', 'Lombard', 'Piedmontese', 
                       'Ligurian', 'Corsican', 'Sardinian', 'Sicilian'],
            'Iberian': ['Spanish', 'Portuguese', 'Galician', 'Catalan', 'Aragonese', 'Mirandese',
                       'Leonese', 'Asturian', 'Extremaduran'],
            'Gallo-Romance': ['French', 'Occitan', 'Franco-Provençal', 'Walloon', 'Norman'],
            'Eastern Romance': ['Romanian', 'Aromanian', 'Megleno-Romanian', 'Istro-Romanian'],
            'Rhaeto-Romance': ['Romansh', 'Ladin', 'Friulian']
        },
        'Austroasiatic': {
            'Mon-Khmer': ['Vietnamese', 'Mon', 'Khmer', 'Wa', 'Palaung'],
            'Munda': ['Santali', 'Mundari', 'Ho', 'Korku'],
            'Bahnaric': ['Stieng', 'Chrau', 'Bru', 'Sedang', 'Halang'],
            'Katuic': ['Katu', 'Pacoh', 'Ta-oi', 'So'],
            'Pearic': ['Pear', 'Chong', 'Samre'],
            'Vietic': ['Vietnamese', 'Muong', 'Thavung']
        },
        'Turkic': {
            'Oghuz': ['Turkish', 'Azerbaijani', 'Turkmen', 'Gagauz', 'Qashqai'],
            'Kipchak': ['Kazakh', 'Kyrgyz', 'Tatar', 'Bashkir', 'Nogai', 'Karakalpak'],
            'Karluk': ['Uzbek', 'Uyghur', 'Chagatai'],
            'Siberian': ['Yakut', 'Tuvan', 'Altai', 'Khakas', 'Shor'],
            'Oghur': ['Chuvash']
        },
        'Bantu': {
            'Eastern Bantu': ['Swahili', 'Kikuyu', 'Kinyarwanda', 'Kirundi', 'Luganda'],
            'Southern Bantu': ['Zulu', 'Xhosa', 'Sotho', 'Tswana', 'Ndebele'],
            'Western Bantu': ['Lingala', 'Kikongo', 'Fang', 'Ewondo', 'Beti'],
            'Central Bantu': ['Luba', 'Mongo', 'Tetela', 'Songye']
        },
        'Dravidian': {
            'South Dravidian': ['Tamil', 'Malayalam', 'Kannada', 'Tulu', 'Kodava', 'Badga', 'Kota', 'Toda'],
            'Central Dravidian': ['Gondi', 'Koya', 'Kuwi', 'Kolami', 'Parji', 'Ollari_Gadba', 'Telugu'],
            'North Dravidian': ['Brahui', 'Kurukh', 'Malto']
        },
        'Polynesian': {
            'Tongic': ['Lea_Fakatonga', 'Vagahau_Niue'],
            'Eastern Polynesian': ['olelo_Hawaii', 'Reo_Tahiti', 'Reo_Maori', 'Rapanui', 'eo_enana'],
            'Nuclear Polynesian': ['Gagana_Samoa', 'Leo_Tuvalu', 'Fakauvea']
        },
        'Tupian': {
            'Guaranic': ['Mbya', 'Guarani', 'Kaiowa', 'Chiriguano'],
            'Tupi-Guarani': ['Kamajura', 'Tapirape', 'Kayabi', 'Apiaka'],
            'Early Branching': ['Mawe', 'Aweti', 'Arawete']
        }
    }
    
    return groupings.get(family_name, {})

def style_tree_for_linguistics(tree: Tree, family_name: str) -> TreeStyle:
    """Apply publication-quality styling for linguistic phylogenetic trees."""
    
    # Get linguistic groups and colors
    groups = get_linguistic_groups(family_name)
    colors = generate_color_palette(len(groups))
    group_colors = dict(zip(groups.keys(), colors))
    
    # Create language to group mapping
    lang_to_group = {}
    for group_name, languages in groups.items():
        for lang in languages:
            lang_to_group[lang] = group_name
    
    # Set up tree style
    ts = TreeStyle()
    
    # Overall layout
    ts.mode = "r"  # Rectangular (cladogram) mode
    ts.show_leaf_name = True
    ts.show_branch_length = True
    ts.show_branch_support = False
    ts.scale = None  # Auto-scale
    
    # Branch styling
    ts.branch_vertical_margin = 5  # Space between branches
    ts.min_leaf_separation = 8     # Minimum space between leaf nodes
    
    # Title
    title = TextFace(f"{family_name} Language Family", fsize=16, bold=True)
    title.margin_top = 10
    title.margin_bottom = 15
    ts.title.add_face(title, column=0)
    
    # Legend for language groups if we have them
    if groups:
        legend_text = "Language Groups:"
        legend_face = TextFace(legend_text, fsize=12, bold=True)
        legend_face.margin_top = 20
        ts.legend.add_face(legend_face, column=0)
        
        for group_name, color in group_colors.items():
            if any(lang in [leaf.name for leaf in tree.get_leaves()] for lang in groups[group_name]):
                color_box = faces.RectFace(width=15, height=15, fgcolor=color, bgcolor=color)
                group_face = TextFace(f" {group_name}", fsize=10)
                ts.legend.add_face(color_box, column=0)
                ts.legend.add_face(group_face, column=1)
    
    # Style individual nodes
    for node in tree.traverse():
        # Node styling
        ns = NodeStyle()
        
        if node.is_leaf():
            # Leaf node styling
            ns.size = 6
            ns.shape = "circle"
            
            # Color by linguistic group
            lang_name = node.name
            if lang_name in lang_to_group:
                group = lang_to_group[lang_name]
                ns.fgcolor = group_colors[group]
                ns.bgcolor = group_colors[group]
            else:
                ns.fgcolor = "#666666"
                ns.bgcolor = "#666666"
            
            # Language name styling
            name_face = TextFace(lang_name, fsize=9)
            name_face.margin_left = 5
            node.add_face(name_face, column=0, position="branch-right")
            
        else:
            # Internal node styling
            ns.size = 4
            ns.shape = "circle"
            ns.fgcolor = "#333333"
            ns.bgcolor = "#ffffff"
            
            # Show branch length if available
            if hasattr(node, 'dist') and node.dist > 0:
                length_face = TextFace(f"{node.dist:.3f}", fsize=7, fgcolor="#666666")
                length_face.margin_top = -8
                node.add_face(length_face, column=0, position="branch-top")
        
        node.set_style(ns)
    
    return ts

def run_grape_analysis(dataset: str, output_prefix: str, **kwargs) -> Optional[str]:
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

def generate_publication_tree(tree: Tree, output_path: str, family_name: str, 
                            formats: List[str] = ['png', 'svg']) -> List[str]:
    """Generate publication-quality tree visualization in multiple formats."""
    
    # Apply linguistic styling
    ts = style_tree_for_linguistics(tree, family_name)
    
    generated_files = []
    
    for fmt in formats:
        output_file = f"{output_path}.{fmt}"
        
        try:
            # Set format-specific parameters
            if fmt == 'png':
                tree.render(output_file, tree_style=ts, w=1200, h=800, dpi=300)
            elif fmt == 'svg':
                tree.render(output_file, tree_style=ts, w=1200, h=800, dpi=300)
            elif fmt == 'pdf':
                tree.render(output_file, tree_style=ts, w=1200, h=800, dpi=300)
            
            generated_files.append(output_file)
            print(f"   ✓ Generated {fmt.upper()}: {output_file}")
            
        except Exception as e:
            print(f"   ❌ Error generating {fmt.upper()}: {e}")
    
    return generated_files

def generate_ascii_tree(tree: Tree, output_file: str, family_name: str):
    """Generate ASCII representation (keeping existing functionality)."""
    with open(output_file, 'w') as f:
        f.write(f"{family_name} Language Family Phylogenetic Tree\\n")
        f.write("=" * 50 + "\\n\\n")
        
        # Tree statistics
        leaves = tree.get_leaves()
        f.write("TREE STATISTICS:\\n")
        f.write(f"  Languages: {len(leaves)}\\n")
        f.write(f"  Tree height: {tree.get_farthest_leaf()[1]:.3f}\\n\\n")
        
        # ASCII tree
        f.write("TREE STRUCTURE:\\n")
        f.write("-" * 20 + "\\n")
        f.write(tree.get_ascii(show_internal=True))
        f.write("\\n\\n")
        
        # Language list
        f.write("ALL LANGUAGES IN TREE:\\n")
        f.write("-" * 20 + "\\n")
        for lang in sorted([leaf.name for leaf in leaves]):
            f.write(f"  • {lang}\\n")

def main():
    """Generate publication-quality visualizations for all language families."""
    
    # Create output directories
    os.makedirs('docs/images/trees', exist_ok=True)
    os.makedirs('docs/images/trees/publication', exist_ok=True)
    
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
    
    print("=" * 70)
    print("GENERATING PUBLICATION-QUALITY PHYLOGENETIC TREE VISUALIZATIONS")
    print("=" * 70)
    
    for family_name, config in datasets.items():
        print(f"\\n🌳 Processing {family_name} language family...")
        
        if not os.path.exists(config['file']):
            print(f"   ⚠️  Dataset {config['file']} not found, skipping...")
            continue
            
        # Set up output paths
        base_output = f"docs/images/trees/{family_name.lower()}"
        publication_output = f"docs/images/trees/publication/{family_name.lower()}"
        
        # Run GRAPE analysis (reuse existing Newick if available)
        newick_file = f"{base_output}.newick"
        if os.path.exists(newick_file):
            with open(newick_file, 'r') as f:
                newick = f.read().strip()
            print(f"   ↻ Using existing Newick tree from {newick_file}")
        else:
            newick = run_grape_analysis(config['file'], base_output, **config['params'])
        
        if newick:
            try:
                tree = Tree(newick)
                num_languages = len(tree.get_leaves())
                results[family_name] = {
                    'tree': tree,
                    'languages': num_languages,
                    'file': config['file']
                }
                
                print(f"   ✓ Parsed tree with {num_languages} languages")
                
                # Generate ASCII representation (keeping existing functionality)
                generate_ascii_tree(tree, f"{base_output}_formatted.txt", family_name)
                
                # Generate publication-quality visualizations
                print(f"   🎨 Generating publication-quality visualizations...")
                generated_files = generate_publication_tree(
                    tree, publication_output, family_name, 
                    formats=['png', 'svg']
                )
                
                # Generate summary
                with open(f"{base_output}_publication_summary.txt", 'w') as f:
                    f.write(f"{family_name} Language Family - Publication Visualizations\\n")
                    f.write("=" * 60 + "\\n\\n")
                    f.write(f"Dataset: {config['file']}\\n")
                    f.write(f"Languages: {num_languages}\\n")
                    f.write(f"Tree height: {tree.get_farthest_leaf()[1]:.3f}\\n")
                    f.write(f"Parameters: {config['params']}\\n\\n")
                    
                    f.write("Generated files:\\n")
                    f.write(f"  - ASCII tree: {base_output}_formatted.txt\\n")
                    for generated_file in generated_files:
                        f.write(f"  - Publication image: {generated_file}\\n")
                    
                    f.write(f"\\nNewick format:\\n{newick}\\n")
                
                print(f"   ✅ Generated all visualizations for {family_name}")
                
            except Exception as e:
                print(f"   ❌ Error processing tree for {family_name}: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"   ❌ Failed to generate tree for {family_name}")
    
    # Generate comprehensive summary
    print(f"\\n📊 Generating comprehensive summary...")
    
    with open('docs/images/trees/PUBLICATION_SUMMARY.md', 'w') as f:
        f.write("# GRAPE Publication-Quality Tree Visualizations\\n\\n")
        f.write("This directory contains both ASCII and publication-quality visualizations ")
        f.write("of phylogenetic trees for major language families.\\n\\n")
        
        f.write("## Visualization Types\\n\\n")
        f.write("For each language family, GRAPE provides:\\n\\n")
        f.write("1. **ASCII Trees**: Text-based representations (`*_formatted.txt`)\\n")
        f.write("2. **Publication PNG**: High-resolution raster images (`publication/*.png`)\\n")
        f.write("3. **Publication SVG**: Scalable vector graphics (`publication/*.svg`)\\n")
        f.write("4. **Newick Format**: Standard phylogenetic format (`*.newick`)\\n\\n")
        
        f.write("## Linguistic Best Practices\\n\\n")
        f.write("Publication visualizations follow linguistic phylogenetic standards:\\n\\n")
        f.write("- **Color coding** by established linguistic subgroups\\n")
        f.write("- **Clear typography** with readable language names\\n")
        f.write("- **Branch length display** showing evolutionary distances\\n")
        f.write("- **Comprehensive legends** for language group identification\\n")
        f.write("- **High resolution** (300 DPI) suitable for publication\\n")
        f.write("- **Multiple formats** (PNG, SVG) for different use cases\\n\\n")
        
        f.write("## Language Families\\n\\n")
        
        for family_name, data in results.items():
            f.write(f"### {family_name}\\n\\n")
            f.write(f"- **Languages**: {data['languages']}\\n")
            f.write(f"- **Dataset**: `{data['file']}`\\n")
            f.write(f"- **Tree height**: {data['tree'].get_farthest_leaf()[1]:.3f}\\n")
            f.write(f"- **ASCII tree**: `{family_name.lower()}_formatted.txt`\\n")
            f.write(f"- **Publication PNG**: `publication/{family_name.lower()}.png`\\n")
            f.write(f"- **Publication SVG**: `publication/{family_name.lower()}.svg`\\n")
            f.write(f"- **Newick format**: `{family_name.lower()}.newick`\\n\\n")
        
        f.write("## Usage in Publications\\n\\n")
        f.write("### LaTeX Integration\\n")
        f.write("```latex\\n")
        f.write("\\\\includegraphics[width=0.8\\\\textwidth]{images/trees/publication/romance.png}\\n")
        f.write("\\\\caption{Romance language phylogeny reconstructed using GRAPE}\\n")
        f.write("```\\n\\n")
        
        f.write("### Markdown Integration\\n")
        f.write("```markdown\\n")
        f.write("![Romance Language Tree](publication/romance.png)\\n")
        f.write("```\\n\\n")
        
        f.write("## Technical Specifications\\n\\n")
        f.write("- **Resolution**: 300 DPI for print quality\\n")
        f.write("- **Dimensions**: 1200x800 pixels (PNG)\\n") 
        f.write("- **Format**: PNG (raster), SVG (vector)\\n")
        f.write("- **Color space**: RGB\\n")
        f.write("- **Typography**: Sans-serif, multiple sizes for hierarchy\\n")
        f.write("- **Reproducibility**: All trees generated with `--seed 42`\\n")
    
    print(f"\\n🎉 Publication visualization generation complete!")
    print(f"   Generated visualizations for {len(results)} language families")
    print(f"   ASCII trees: docs/images/trees/*_formatted.txt")
    print(f"   Publication images: docs/images/trees/publication/*.(png,svg)")
    print(f"   Summary: docs/images/trees/PUBLICATION_SUMMARY.md")
    
    return results

if __name__ == "__main__":
    results = main()