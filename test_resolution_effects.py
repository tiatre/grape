#!/usr/bin/env python3

import sys
sys.path.append('.')
from grape import *
from common import read_cognate_file
import networkx as nx

def test_resolution_effects():
    """Test different resolution parameters to understand their effect on hierarchical structure"""
    
    print("=== TESTING RESOLUTION EFFECTS ===")
    
    # Read data and build graph
    cognates = read_cognate_file(
        "data/ielex_2022.tsv", "auto", "utf-8", "Language", "Parameter", "Cognateset"
    )
    
    languages = sorted(set(lang for lang, concept in cognates.keys()))
    G = build_graph("cognateset_graph", data=cognates)
    
    print(f"Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    
    # Test a range of resolution parameters
    resolutions_to_test = [0.001, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
    
    print(f"\n=== RESOLUTION PARAMETER TESTING ===")
    
    for resolution in resolutions_to_test:
        print(f"\nResolution: {resolution}")
        
        # Apply Louvain community detection
        communities_dict = nx.community.louvain_communities(G, resolution=resolution, seed=42)
        communities_list = [frozenset(community) for community in communities_dict]
        
        print(f"  Number of communities: {len(communities_list)}")
        
        # Check if Hittite and Tocharian are isolated
        hittite_community = None
        tocharian_community = None
        
        for i, community in enumerate(communities_list):
            if 'Hittite' in community:
                hittite_community = i
                hittite_size = len(community)
                print(f"  Hittite in community {i} (size: {hittite_size})")
                if hittite_size == 1:
                    print("    ✓ Hittite is ISOLATED!")
                else:
                    sample_langs = list(community)[:5]
                    print(f"    ✗ Hittite grouped with: {sample_langs}...")
            
            if any('Tocharian' in lang for lang in community):
                tocharian_community = i
                tocharian_langs = [lang for lang in community if 'Tocharian' in lang]
                tocharian_size = len(community)
                print(f"  Tocharian in community {i} (size: {tocharian_size})")
                print(f"    Tocharian languages: {tocharian_langs}")
                if tocharian_size == len(tocharian_langs):
                    print("    ✓ Tocharian languages are ISOLATED together!")
                else:
                    sample_langs = [lang for lang in community if 'Tocharian' not in lang][:3]
                    print(f"    ✗ Tocharian grouped with: {sample_langs}...")
        
        # Check separation
        if hittite_community is not None and tocharian_community is not None:
            if hittite_community != tocharian_community:
                print("  ✓ Hittite and Tocharian are in SEPARATE communities!")
            else:
                print("  ✗ Hittite and Tocharian are in the SAME community")
        
        # Build tree from communities to see actual structure
        try:
            method = LouvainCommunities()
            strategy = FixedParameterStrategy(resolution)
            
            # Build history 
            history = build_history(G, method, strategy)
            
            if history:
                tree = communities_to_tree(history)
                
                # Quick analysis of tree structure 
                root_children = tree.children
                print(f"  Tree: {len(root_children)} main branches at root")
                
                # Check if any branch has only Hittite
                for i, child in enumerate(root_children):
                    leaves = child.get_leaf_names()
                    if len(leaves) == 1 and leaves[0] == 'Hittite':
                        print(f"    ✓ Branch {i+1}: Hittite alone!")
                    elif len(leaves) <= 5:
                        print(f"    Branch {i+1}: {leaves}")
                
        except Exception as e:
            print(f"  Error building tree: {e}")

if __name__ == "__main__":
    test_resolution_effects()