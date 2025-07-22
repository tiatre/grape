#!/usr/bin/env python3

import os
from ete3 import Tree

def test_sequential_outgroups():
    """Test the sequential outgroup approach"""
    
    tree_file = 'test_sequential_outgroups.txt'
    
    if not os.path.exists(tree_file):
        print("No test file found")
        return False
        
    # Extract Newick tree
    newick_line = None
    with open(tree_file, 'r') as f:
        for line in f:
            if 'Newick format tree:' in line:
                newick_line = line.split('Newick format tree: ')[1].strip()
                break
    
    if not newick_line:
        print("No Newick tree found in file")
        return False
    
    # Save and analyze tree
    with open('test_sequential.newick', 'w') as f:
        f.write(newick_line)
    
    tree = Tree(newick_line)
    
    print('SEQUENTIAL OUTGROUP STRUCTURE TEST:')
    print('='*45)
    
    def analyze_structure(node, depth=0):
        indent = '  ' * depth
        if node.is_leaf():
            print(f'{indent}→ {node.name}')
            return [node.name]
        else:
            print(f'{indent}├─ Internal node ({len(node.children)} children)')
            all_leaves = []
            for i, child in enumerate(node.children):
                child_leaves = analyze_structure(child, depth+1)
                all_leaves.extend(child_leaves)
            return all_leaves
    
    all_languages = analyze_structure(tree)
    
    print(f'\nTotal languages: {len(all_languages)}')
    
    # Check if we have the ideal structure
    root_children = tree.children
    if len(root_children) == 2:
        branch1 = root_children[0].get_leaf_names()
        branch2 = root_children[1].get_leaf_names()
        
        if branch1 == ['Hittite']:
            print('\n✓ SUCCESS: Hittite is the first outgroup!')
            
            # Check if second branch has Tocharian as second outgroup
            if len(root_children[1].children) == 2:
                sub1 = root_children[1].children[0].get_leaf_names()  
                sub2 = root_children[1].children[1].get_leaf_names()
                
                toch_expected = {'Tocharian_A', 'Tocharian_B'}
                if set(sub1) == toch_expected:
                    print('✓ SUCCESS: Tocharian A+B are the second outgroup!')
                    print(f'✓ SUCCESS: Remaining {len(sub2)} languages form the ingroup')
                    return True
                elif set(sub2) == toch_expected:
                    print('✓ SUCCESS: Tocharian A+B are the second outgroup!')
                    print(f'✓ SUCCESS: Remaining {len(sub1)} languages form the ingroup')
                    return True
                else:
                    print('✗ Tocharian structure not as expected')
                    print(f'  Sub-branch 1: {len(sub1)} languages')
                    print(f'  Sub-branch 2: {len(sub2)} languages')
            else:
                print(f'✗ Second branch has {len(root_children[1].children)} sub-branches (expected 2)')
        else:
            print('✗ Hittite not isolated as first outgroup')
    else:
        print(f'✗ Root has {len(root_children)} branches (expected 2)')
    
    return False

if __name__ == "__main__":
    success = test_sequential_outgroups()
    if success:
        print('\n🎯 PERFECT INDO-EUROPEAN STRUCTURE ACHIEVED!')
    else:
        print('\n⚠️  Structure needs more work')