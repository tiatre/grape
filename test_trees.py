#!/usr/bin/env python3

from ete3 import Tree
import sys

def analyze_tree_structure(tree_file, description):
    """Analyze if a tree has correct Hittite/Tocharian positioning"""
    
    try:
        tree = Tree(open(tree_file).read().strip())
        
        print(f"=== {description} ===")
        
        # Check root structure
        root_children = tree.children
        print(f"Root has {len(root_children)} main branches")
        
        # Look for the ideal structure: Hittite alone vs rest
        hittite_alone = False
        tocharian_second = False
        
        if len(root_children) == 2:
            branch1_langs = root_children[0].get_leaf_names()
            branch2_langs = root_children[1].get_leaf_names()
            
            # Check if one branch has only Hittite
            if branch1_langs == ['Hittite']:
                print("✓ PERFECT! Hittite is alone in first branch")
                hittite_alone = True
                other_branch = root_children[1]
            elif branch2_langs == ['Hittite']:
                print("✓ PERFECT! Hittite is alone in second branch") 
                hittite_alone = True
                other_branch = root_children[0]
            else:
                print(f"✗ No branch contains only Hittite")
                print(f"  Branch 1: {len(branch1_langs)} langs: {branch1_langs[:3]}...")
                print(f"  Branch 2: {len(branch2_langs)} langs: {branch2_langs[:3]}...")
                other_branch = None
        
            # If Hittite is correctly positioned, check Tocharian in the rest
            if hittite_alone and other_branch:
                # Check if the other branch splits Tocharian early
                if len(other_branch.children) == 2:
                    sub_branch1 = other_branch.children[0].get_leaf_names()
                    sub_branch2 = other_branch.children[1].get_leaf_names()
                    
                    toch_in_1 = any('Tocharian' in lang for lang in sub_branch1)
                    toch_in_2 = any('Tocharian' in lang for lang in sub_branch2)
                    
                    if toch_in_1 and not toch_in_2:
                        print(f"✓ Tocharian group in first sub-branch ({len(sub_branch1)} langs)")
                        tocharian_second = True
                    elif toch_in_2 and not toch_in_1:
                        print(f"✓ Tocharian group in second sub-branch ({len(sub_branch2)} langs)")
                        tocharian_second = True
                    else:
                        print("✗ Tocharian positioning unclear in sub-branches")
        else:
            print(f"✗ Root has {len(root_children)} branches (need 2)")
        
        # Score this tree
        if hittite_alone and tocharian_second:
            score = "PERFECT ★★★"
        elif hittite_alone:
            score = "GOOD ★★☆"
        else:
            score = "POOR ★☆☆"
            
        print(f"Score: {score}")
        print()
        return score
        
    except Exception as e:
        print(f"ERROR analyzing {tree_file}: {e}")
        print()
        return "ERROR"

def main():
    """Test all generated trees"""
    
    trees_to_test = [
        ("test_0001.newick", "LOUVAIN UNADJUSTED 0.001"),
        ("test_adj_0005.newick", "LOUVAIN ADJUSTED 0.005"), 
        ("test_greedy_adj_0001.newick", "GREEDY ADJUSTED 0.001")
    ]
    
    results = []
    
    for tree_file, description in trees_to_test:
        score = analyze_tree_structure(tree_file, description)
        results.append((tree_file, description, score))
    
    print("SUMMARY RANKING:")
    print("-" * 50)
    for tree_file, description, score in results:
        print(f"{score:<12} {description}")

if __name__ == "__main__":
    main()