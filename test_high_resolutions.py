#!/usr/bin/env python3

import sys
sys.path.append('.')
from grape import *
from common import read_cognate_file
import networkx as nx

def test_high_resolutions():
    """Test much higher resolution parameters"""
    
    print("=== TESTING HIGH RESOLUTION VALUES ===")
    
    # Read data and build graph
    cognates = read_cognate_file(
        "data/ielex_2022.tsv", "auto", "utf-8", "Language", "Parameter", "Cognateset"
    )
    
    G = build_graph("cognateset_graph", data=cognates)
    print(f"Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    
    # Test much higher resolution parameters
    resolutions_to_test = [1.0, 2.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0]
    
    for resolution in resolutions_to_test:
        print(f"\n=== Resolution: {resolution} ===")
        
        # Apply Louvain community detection
        communities_dict = nx.community.louvain_communities(G, resolution=resolution, seed=42)
        communities_list = [frozenset(community) for community in communities_dict]
        
        print(f"Number of communities: {len(communities_list)}")
        
        # Track key language positions
        hittite_community = None
        tocharian_community = None
        
        for i, community in enumerate(communities_list):
            community_list = list(community)
            
            if 'Hittite' in community:
                hittite_community = i
                print(f"Hittite community {i} (size {len(community)}): {community_list[:8]}{'...' if len(community) > 8 else ''}")
                
                if len(community) == 1:
                    print("  ✓ ✓ ✓ HITTITE IS ISOLATED! ✓ ✓ ✓")
            
            toch_langs = [lang for lang in community if 'Tocharian' in lang]
            if toch_langs:
                tocharian_community = i  
                print(f"Tocharian community {i} (size {len(community)}): {community_list[:8]}{'...' if len(community) > 8 else ''}")
                print(f"  Tocharian languages: {toch_langs}")
                
                if len(community) == len(toch_langs):
                    print("  ✓ ✓ ✓ TOCHARIAN LANGUAGES ARE ISOLATED TOGETHER! ✓ ✓ ✓")
        
        # Check if they're separated
        if hittite_community is not None and tocharian_community is not None:
            if hittite_community != tocharian_community:
                print("✓ Hittite and Tocharian are in SEPARATE communities!")
            else:
                print("✗ Hittite and Tocharian are still together")
        
        # Show a summary of major communities
        print(f"Community size distribution: {sorted([len(c) for c in communities_list], reverse=True)}")
        
        # Try to build actual tree and see what happens
        try:
            # Run the full GRAPE pipeline with this resolution
            print("  Running full GRAPE pipeline...")
            
            # Use same parameters as current best
            community_method = LouvainCommunities(G, "weight")  
            strategy = FixedParameterStrategy(resolution)
            
            history = build_history(G, community_method, strategy)
            
            if history and len(history) > 1:
                tree = communities_to_tree(history)
                
                # Analyze tree structure
                root_children = tree.children
                print(f"  Tree has {len(root_children)} main branches")
                
                hittite_found = False
                tocharian_found = False
                
                for i, child in enumerate(root_children):
                    leaves = child.get_leaf_names()
                    
                    if 'Hittite' in leaves:
                        if len(leaves) == 1:
                            print(f"    Branch {i+1}: ✓ HITTITE ALONE!")
                            hittite_found = True
                        else:
                            print(f"    Branch {i+1}: Hittite + {len(leaves)-1} others")
                    
                    toch_langs = [lang for lang in leaves if 'Tocharian' in lang]
                    if toch_langs:
                        if len(leaves) == len(toch_langs):
                            print(f"    Branch {i+1}: ✓ TOCHARIAN ALONE! ({toch_langs})")
                            tocharian_found = True
                        else:
                            print(f"    Branch {i+1}: Tocharian + {len(leaves)-len(toch_langs)} others")
                
                if hittite_found and tocharian_found:
                    print(f"  ★★★ RESOLUTION {resolution} ACHIEVES PERFECT OUTGROUP ISOLATION! ★★★")
                    
                    # Save this tree for inspection
                    with open(f'test_tree_resolution_{resolution}.newick', 'w') as f:
                        f.write(tree.write())
                    print(f"  Saved tree to: test_tree_resolution_{resolution}.newick")
                    
            else:
                print("  No valid history generated")
                
        except Exception as e:
            print(f"  Error in pipeline: {e}")

if __name__ == "__main__":
    test_high_resolutions()