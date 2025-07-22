#!/usr/bin/env python3

from ete3 import Tree
import sys

def analyze_resolution_5_tree():
    """Analyze the tree generated with resolution 5.0"""
    try:
        with open('improved_ie_tree_clean.newick', 'r') as f:
            newick_str = f.read().strip()
        
        print("=== IMPROVED INDO-EUROPEAN TREE ANALYSIS ===")
        print(f"Newick length: {len(newick_str)}")
        print()
        
        tree = Tree(newick_str)
        all_leaves = tree.get_leaf_names()
        print(f"Total languages: {len(all_leaves)}")
        
        # Check for key languages
        hittite_present = 'Hittite' in all_leaves
        tocharian_present = any('Tocharian' in name for name in all_leaves)
        tocharian_langs = [name for name in all_leaves if 'Tocharian' in name]
        
        print(f"Hittite present: {hittite_present}")  
        print(f"Tocharian present: {tocharian_present}")
        print(f"Tocharian languages: {tocharian_langs}")
        print()
        
        # Analyze root structure
        root = tree.get_tree_root()
        root_children = root.children
        
        print(f"=== ROOT LEVEL ANALYSIS ===")
        print(f"Root has {len(root_children)} main branches")
        
        hittite_found_at_root = False
        tocharian_found_at_root = False
        
        for i, child in enumerate(root_children):
            child_leaves = child.get_leaf_names()
            print(f"\nBranch {i+1}: {len(child_leaves)} languages")
            
            # Check for Hittite  
            if 'Hittite' in child_leaves:
                if len(child_leaves) == 1:
                    print(f"  ✓ ✓ ✓ HITTITE IS ALONE AT ROOT LEVEL! ✓ ✓ ✓")
                    hittite_found_at_root = True
                else:
                    print(f"  ✗ Hittite is with {len(child_leaves)-1} other languages")
                    print(f"  Languages: {child_leaves[:8]}{'...' if len(child_leaves) > 8 else ''}")
            
            # Check for Tocharian
            toch_in_branch = [lang for lang in child_leaves if 'Tocharian' in lang]
            if toch_in_branch:
                if len(child_leaves) == len(toch_in_branch):
                    print(f"  ✓ ✓ ✓ TOCHARIAN IS ALONE AT ROOT LEVEL! ✓ ✓ ✓")
                    print(f"  Tocharian languages: {toch_in_branch}")
                    tocharian_found_at_root = True
                else:
                    print(f"  ✗ Tocharian is with {len(child_leaves) - len(toch_in_branch)} other languages")
                    other_langs = [lang for lang in child_leaves if 'Tocharian' not in lang]
                    print(f"  Other languages: {other_langs[:5]}{'...' if len(other_langs) > 5 else ''}")
        
        print(f"\n=== SUMMARY ===")
        if hittite_found_at_root:
            print("✓ HITTITE: Successfully isolated at root level!")
        else:
            print("✗ HITTITE: Not isolated at root level")
            
        if tocharian_found_at_root:
            print("✓ TOCHARIAN: Successfully isolated at root level!")
        else:
            print("✗ TOCHARIAN: Not isolated at root level")
        
        if hittite_found_at_root and tocharian_found_at_root:
            print("\n★★★ PERFECT! Both outgroups are isolated at root level! ★★★")
            return True
        elif hittite_found_at_root or tocharian_found_at_root:
            print("\n~ PARTIAL SUCCESS: One outgroup isolated ~")
            return False
        else:
            print("\n✗ FAILURE: Neither outgroup isolated")
            return False
            
        # If we didn't get perfect root isolation, let's see the hierarchical structure
        if not (hittite_found_at_root and tocharian_found_at_root):
            print(f"\n=== HIERARCHICAL ANALYSIS ===")
            
            # Find Hittite's position
            if hittite_present:
                hittite_node = None
                for leaf in tree.get_leaves():
                    if leaf.name == 'Hittite':
                        hittite_node = leaf
                        break
                
                if hittite_node:
                    print("Hittite's path to root:")
                    current = hittite_node
                    level = 0
                    while current.up:
                        parent = current.up
                        siblings = parent.children
                        sibling_sizes = [len(s.get_leaf_names()) for s in siblings]
                        print(f"  Level {level}: {len(siblings)} groups, sizes: {sibling_sizes}")
                        
                        if parent.up is None:
                            print("  *** ROOT LEVEL ***")
                        
                        current = parent
                        level += 1
                        
                        if level > 10:  # Prevent infinite loops
                            break
            
            # Find Tocharian's position
            for toch_lang in tocharian_langs:
                toch_node = None
                for leaf in tree.get_leaves():
                    if leaf.name == toch_lang:
                        toch_node = leaf
                        break
                
                if toch_node:
                    print(f"\n{toch_lang}'s path to root:")
                    current = toch_node
                    level = 0
                    while current.up:
                        parent = current.up
                        siblings = parent.children  
                        sibling_sizes = [len(s.get_leaf_names()) for s in siblings]
                        print(f"  Level {level}: {len(siblings)} groups, sizes: {sibling_sizes}")
                        
                        if parent.up is None:
                            print("  *** ROOT LEVEL ***")
                        
                        current = parent
                        level += 1
                        
                        if level > 10:  # Prevent infinite loops
                            break
                    break  # Only analyze one Tocharian language
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    analyze_resolution_5_tree()