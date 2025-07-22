#!/usr/bin/env python3

from ete3 import Tree
import os

def test_outgroup_modification():
    """Test if the outgroup modification worked"""
    
    if os.path.exists('test_hittite_outgroup.newick'):
        tree = Tree(open('test_hittite_outgroup.newick').read().strip())
        print('TESTING HITTITE OUTGROUP MODIFICATION:')
        print('='*40)
        
        root_children = tree.children
        print(f'Root has {len(root_children)} main branches')
        
        if len(root_children) == 2:
            branch1_langs = root_children[0].get_leaf_names()
            branch2_langs = root_children[1].get_leaf_names()
            
            if branch1_langs == ['Hittite']:
                print('✓ SUCCESS! Hittite is alone in first branch')
                return True
            elif branch2_langs == ['Hittite']:
                print('✓ SUCCESS! Hittite is alone in second branch')
                return True
            else:
                print('✗ Still not working')
                print(f'  Branch 1: {len(branch1_langs)} languages')
                print(f'  Branch 2: {len(branch2_langs)} languages')
                if 'Hittite' in branch1_langs:
                    others = [l for l in branch1_langs if l != 'Hittite']
                    print(f'  Hittite in branch 1 with: {others[:5]}...')
                if 'Hittite' in branch2_langs:
                    others = [l for l in branch2_langs if l != 'Hittite']
                    print(f'  Hittite in branch 2 with: {others[:5]}...')
                return False
        else:
            print(f'✗ Wrong root structure: {len(root_children)} branches')
            return False
    else:
        print('✗ No tree file generated')
        return False

if __name__ == "__main__":
    test_outgroup_modification()