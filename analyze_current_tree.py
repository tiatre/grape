#!/usr/bin/env python3

from ete3 import Tree
import sys

def analyze_tree_detailed():
    """Analyze the current Indo-European tree structure in detail"""
    try:
        with open('docs/images/trees/indo_european.newick', 'r') as f:
            newick_str = f.read().strip()
        
        print("=== DETAILED TREE ANALYSIS ===")
        print(f"Newick string length: {len(newick_str)}")
        print(f"First 200 chars: {newick_str[:200]}")
        print()
        
        tree = Tree(newick_str)
        
        # Get all leaf names to understand the languages present
        all_leaves = tree.get_leaf_names()
        print(f"Total languages in tree: {len(all_leaves)}")
        
        # Check for Hittite and Tocharian
        hittite_present = 'Hittite' in all_leaves
        tocharian_present = any('Tocharian' in name for name in all_leaves)
        tocharian_langs = [name for name in all_leaves if 'Tocharian' in name]
        
        print(f"Hittite present: {hittite_present}")
        print(f"Tocharian languages present: {tocharian_present}")
        if tocharian_langs:
            print(f"Tocharian languages: {tocharian_langs}")
        print()
        
        # Analyze root structure
        root = tree.get_tree_root()
        root_children = root.children
        
        print(f"Root has {len(root_children)} main branches")
        
        for i, child in enumerate(root_children):
            child_leaves = child.get_leaf_names()
            print(f"Branch {i+1}: {len(child_leaves)} languages")
            
            # Check if this branch contains only Hittite
            if len(child_leaves) == 1 and child_leaves[0] == 'Hittite':
                print(f"  ✓ Branch {i+1} is Hittite alone - GOOD!")
            elif 'Hittite' in child_leaves:
                print(f"  ✗ Branch {i+1} contains Hittite with {len(child_leaves)-1} other languages")
                print(f"  Languages in this branch: {child_leaves[:10]}{'...' if len(child_leaves) > 10 else ''}")
            
            # Check for Tocharian languages
            toch_in_branch = [lang for lang in child_leaves if 'Tocharian' in lang]
            if toch_in_branch:
                print(f"  Tocharian languages in branch {i+1}: {toch_in_branch}")
        
        print("\n=== HIERARCHICAL ANALYSIS ===")
        
        # Find the path to Hittite
        if hittite_present:
            hittite_node = None
            for leaf in tree.get_leaves():
                if leaf.name == 'Hittite':
                    hittite_node = leaf
                    break
            
            if hittite_node:
                # Get path from root to Hittite
                path_to_hittite = []
                current = hittite_node
                while current.up:
                    siblings = current.up.children
                    sibling_leaf_counts = [len(s.get_leaf_names()) for s in siblings]
                    path_to_hittite.append({
                        'level': len(path_to_hittite),
                        'siblings': len(siblings),
                        'sibling_sizes': sibling_leaf_counts
                    })
                    current = current.up
                
                print("Path from root to Hittite:")
                for i, level in enumerate(reversed(path_to_hittite)):
                    print(f"  Level {i}: {level['siblings']} groups with sizes {level['sibling_sizes']}")
        
        # Find Tocharian position
        if tocharian_langs:
            for toch_lang in tocharian_langs:
                toch_node = None
                for leaf in tree.get_leaves():
                    if leaf.name == toch_lang:
                        toch_node = leaf
                        break
                
                if toch_node:
                    # Get the immediate parent group size
                    parent = toch_node.up
                    if parent:
                        siblings = parent.get_leaf_names()
                        print(f"\n{toch_lang} is grouped with {len(siblings)-1} other languages:")
                        print(f"  Group members: {siblings[:5]}{'...' if len(siblings) > 5 else ''}")
        
    except Exception as e:
        print(f"Error analyzing tree: {e}")
        return False
    
    return True

if __name__ == "__main__":
    analyze_tree_detailed()