
import os
import toytree
import pandas as pd
from ete3 import Tree

def get_tree_metrics(tree_path):
    """Calculate metrics for a given ETE3 tree."""
    tree = Tree(tree_path)
    num_leaves = len(tree)
    
    balance = 0
    if len(tree) > 2:
        # This is a simplified balance calculation.
        # A more robust method might be needed for complex trees.
        farthest_leaf, farthest_dist = tree.get_farthest_leaf()
        if farthest_dist is not None:
            total_leaves = len(tree.get_leaves())
            if total_leaves > 0:
                balance = farthest_dist / total_leaves

    max_dist = 0
    for leaf in tree:
        dist = tree.get_distance(leaf)
        if dist > max_dist:
            max_dist = dist
            
    return {
        "size": num_leaves,
        "balance": balance,
        "max_distance": max_dist,
    }

def generate_visualization(tree_path, output_dir):
    """
    Generates a rectangular visualization for a single tree.
    """
    tree_name = os.path.basename(tree_path).replace(".newick", "")
    metrics = get_tree_metrics(tree_path)

    # Load tree with toytree
    ttree = toytree.tree(tree_path)

    # Rectangular layout settings for all trees
    kwargs = {
        "tree_style": 'r',  # Always use rectangular layout
        "width": 2000,
        "height": 800 + metrics["size"] * 15,  # Dynamic height based on tree size
        "tip_labels_align": True,
        "tip_labels_style": {
            "font-size": "14px",
        },
        "node_sizes": 5,
        "node_style": {
            "fill": "black", "stroke": "none"
        },
    }

    # Generate drawing
    canvas, axes, mark = ttree.draw(**kwargs)

    # Save SVG visualization
    svg_output_path = os.path.join(output_dir, f"{tree_name}.svg")
    import toyplot.svg
    toyplot.svg.render(canvas, svg_output_path)
    print(f"Generated visualization for {tree_name} at {svg_output_path}")

    # Save PNG visualization with a white background
    png_output_path = os.path.join(output_dir, f"{tree_name}.png")
    import toyplot.png
    canvas.style = {"background-color": "white"}
    toyplot.png.render(canvas, png_output_path)
    print(f"Generated visualization for {tree_name} at {png_output_path}")


def main():
    """
    Main function to generate all publication-quality visualizations.
    """
    tree_dir = "docs/images/trees"
    output_dir = "docs/images/trees/publication_final"
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    tree_files = [f for f in os.listdir(tree_dir) if f.endswith(".newick")]

    for tree_file in tree_files:
        tree_path = os.path.join(tree_dir, tree_file)
        generate_visualization(tree_path, output_dir)

if __name__ == "__main__":
    main()
