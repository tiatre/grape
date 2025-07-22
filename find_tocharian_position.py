#!/usr/bin/env python3

from ete3 import Tree
import sys

def find_tocharian_detailed():
    """Find exactly where Tocharian is positioned in the tree hierarchy"""
    try:
        with open('docs/images/trees/indo_european.newick', 'r') as f:
            newick_str = f.read().strip()
        
        tree = Tree(newick_str)
        
        # Find Tocharian node
        toch_node = None
        for leaf in tree.get_leaves():
            if 'Tocharian' in leaf.name:
                toch_node = leaf
                break
        
        if not toch_node:
            print("Tocharian not found!")
            return
        
        print(f"Found: {toch_node.name}")
        
        # Traverse up the tree to understand the hierarchy
        current = toch_node
        level = 0
        
        print("\n=== TOCHARIAN HIERARCHY ===")
        
        while current.up:
            parent = current.up
            siblings = [child for child in parent.children if child != current]
            
            print(f"Level {level}:")
            print(f"  Current group size: {len(current.get_leaf_names())}")
            print(f"  Siblings: {len(siblings)}")
            
            for i, sibling in enumerate(siblings):
                sibling_leaves = sibling.get_leaf_names()
                print(f"    Sibling {i+1}: {len(sibling_leaves)} languages")
                if len(sibling_leaves) <= 5:
                    print(f"      Languages: {sibling_leaves}")
                else:
                    print(f"      Sample languages: {sibling_leaves[:5]}...")
            
            # Check if we're at root level
            if parent.up is None:
                print(f"  *** This is ROOT level - Tocharian splits here ***")
                root_children = parent.children
                print(f"  Root has {len(root_children)} main branches:")
                for i, child in enumerate(root_children):
                    child_leaves = child.get_leaf_names()
                    if child == current:
                        print(f"    Branch {i+1}: TOCHARIAN BRANCH ({len(child_leaves)} languages)")
                    else:
                        print(f"    Branch {i+1}: {len(child_leaves)} languages")
                        if 'Hittite' in child_leaves:
                            print(f"      (contains Hittite)")
                break
            
            current = parent
            level += 1
        
        # Let's also check the immediate context around Tocharian
        print(f"\n=== TOCHARIAN IMMEDIATE CONTEXT ===")
        toch_parent = toch_node.up
        if toch_parent:
            parent_leaves = toch_parent.get_leaf_names()
            print(f"Tocharian's immediate group has {len(parent_leaves)} languages:")
            print(f"  {parent_leaves}")
            
            if len(parent_leaves) == 1:
                print("  → Tocharian is isolated in its own group!")
            else:
                print("  → Tocharian is grouped with other languages")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_tocharian_detailed()