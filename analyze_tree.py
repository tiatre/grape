#!/usr/bin/env python3

from ete3 import Tree

def analyze_indo_european_tree():
    """Properly analyze the Indo-European tree topology"""
    
    # Load the current tree
    tree = Tree(open('docs/images/trees/indo_european.newick').read().strip())
    
    print('PROPER TREE TOPOLOGY ANALYSIS')
    print('='*50)
    
    # Find all leaves
    leaves = tree.get_leaf_names()
    print(f'Total languages: {len(leaves)}')
    print()
    
    # Check what's actually at the root level splits
    root = tree
    print('ROOT LEVEL ANALYSIS:')
    print(f'Root has {len(root.children)} main branches')
    
    for i, child in enumerate(root.children):
        child_leaves = child.get_leaf_names()
        print(f'Branch {i+1}: {len(child_leaves)} languages')
        
        # Show first few languages in each branch to understand structure
        if 'Hittite' in child_leaves:
            print(f'  -> Contains HITTITE (along with {len(child_leaves)-1} others)')
            if len(child_leaves) <= 10:
                print(f'    Languages: {child_leaves}')
        elif any('Tocharian' in lang for lang in child_leaves):
            print(f'  -> Contains TOCHARIAN (along with {len(child_leaves)-1} others)')
            if len(child_leaves) <= 10:
                print(f'    Languages: {child_leaves}')
        else:
            print(f'  -> Languages include: {child_leaves[:5]}...')
    
    print()
    print('HITTITE POSITION CHECK:')
    hittite = tree.search_nodes(name='Hittite')[0]
    print(f'Hittite node found: {hittite.name}')
    
    # Walk up from Hittite to find the split levels
    current = hittite
    level = 0
    while current.up is not None:
        level += 1
        parent = current.up
        siblings = [child for child in parent.children if child is not current]
        
        print(f'Level {level}: Hittite group vs {len(siblings)} sibling group(s)')
        
        total_sibling_languages = []
        for sibling in siblings:
            sibling_langs = sibling.get_leaf_names()
            total_sibling_languages.extend(sibling_langs)
            
        print(f'  Sibling groups contain {len(total_sibling_languages)} total languages')
        
        # Check if this is the root split (Hittite vs all others)
        if parent.up is None:  # This is the root
            if len(siblings) == 1 and len(total_sibling_languages) == len(leaves) - 1:
                print(f'  ✓ HITTITE IS THE FIRST OUTGROUP!')
                print(f'    Hittite vs all other {len(total_sibling_languages)} IE languages')
                break
            else:
                print(f'  ✗ Hittite is NOT the first outgroup')
                print(f'    At root level, Hittite shares the tree with other groups')
        
        current = parent
    
    print()
    print('TOCHARIAN POSITION CHECK:')
    tocharian_nodes = [n for n in tree.get_leaves() if 'Tocharian' in n.name]
    if tocharian_nodes:
        toch = tocharian_nodes[0]  # Use first Tocharian node found
        print(f'Found Tocharian: {toch.name}')
        
        # Walk up from Tocharian to find splits
        current = toch.up  # Start from Tocharian parent (since they're grouped)
        level = 0
        while current.up is not None:
            level += 1
            parent = current.up
            siblings = [child for child in parent.children if child is not current]
            
            total_sibling_languages = []
            for sibling in siblings:
                sibling_langs = sibling.get_leaf_names() 
                total_sibling_languages.extend(sibling_langs)
            
            print(f'Level {level}: Tocharian group vs {len(total_sibling_languages)} other languages')
            
            # Check if Hittite is in the sibling group
            if 'Hittite' not in total_sibling_languages:
                print(f'  ✓ Found Tocharian split without Hittite!')
                print(f'    This suggests Tocharian is the second outgroup')
                break
            else:
                print(f'  -> Hittite is still in sibling group, going up...')
            
            current = parent
    else:
        print('✗ Tocharian not found')
    
    print()
    print('CONCLUSION:')
    print('-' * 20)
    
    # Final assessment
    root_children = tree.children
    if len(root_children) == 2:
        branch1_langs = root_children[0].get_leaf_names()
        branch2_langs = root_children[1].get_leaf_names()
        
        if 'Hittite' in branch1_langs and len(branch1_langs) == 1:
            print('✓ HITTITE is the first outgroup (alone in one root branch)')
        elif 'Hittite' in branch2_langs and len(branch2_langs) == 1:
            print('✓ HITTITE is the first outgroup (alone in one root branch)')
        else:
            print('✗ HITTITE is NOT the first outgroup')
            print(f'  Branch 1 has {len(branch1_langs)} languages: {branch1_langs[:5]}...')
            print(f'  Branch 2 has {len(branch2_langs)} languages: {branch2_langs[:5]}...')
    else:
        print(f'✗ Tree has {len(root_children)} main branches (should be 2 for proper outgroup)')

if __name__ == "__main__":
    analyze_indo_european_tree()