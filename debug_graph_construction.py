#!/usr/bin/env python3

import sys
sys.path.append('.')
from grape import *
from common import read_cognate_file
import networkx as nx

def debug_graph_construction():
    """Debug the graph construction process to understand connectivity patterns"""
    
    print("=== DEBUGGING GRAPH CONSTRUCTION ===")
    
    # Read the cognate data using proper parameters
    cognates = read_cognate_file(
        "data/ielex_2022.tsv",
        "auto",  # dialect
        "utf-8",  # encoding
        "Language",  # language column
        "Parameter",  # concept column  
        "Cognateset"  # cognateset column
    )
    
    # Extract languages and concepts
    languages = sorted(set(lang for lang, concept in cognates.keys()))
    concepts = sorted(set(concept for lang, concept in cognates.keys()))
    
    print(f"Total languages: {len(languages)}")
    print(f"Total concepts: {len(concepts)}")
    
    # Check if Hittite and Tocharian are present
    hittite_present = 'Hittite' in languages
    tocharian_langs = [lang for lang in languages if 'Tocharian' in lang]
    
    print(f"Hittite present: {hittite_present}")
    print(f"Tocharian languages: {tocharian_langs}")
    
    if not hittite_present or not tocharian_langs:
        print("Missing key languages!")
        return
    
    # Build the graph using the same parameters as our current best tree
    print("\n=== BUILDING GRAPH ===")
    graph_type = "unadjusted"  # Current best parameters
    
    if graph_type == "unadjusted":
        G = build_graph(
            "cognateset_graph", 
            data=cognates
        )
    else:
        # For adjusted graph (not used in current best, but available)
        distance_matrix = common.compute_distance_matrix(
            cognates, synonyms="average", missing_data="max_dist"
        )
        G = build_graph(
            "adjusted_cognateset_graph",
            data=cognates,
            distance_matrix=distance_matrix,
            sorted_languages=languages,
            proximity_weight=0.5,
            sharing_factor=0.5
        )
    
    print(f"Graph has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    
    # Analyze connectivity of key languages
    print(f"\n=== CONNECTIVITY ANALYSIS ===")
    
    if hittite_present:
        hittite_edges = list(G.edges('Hittite', data=True))
        print(f"Hittite has {len(hittite_edges)} connections")
        
        # Sort by weight to see strongest connections
        hittite_edges.sort(key=lambda x: x[2]['weight'], reverse=True)
        print("Hittite's strongest connections:")
        for i, (src, dst, data) in enumerate(hittite_edges[:10]):
            other = dst if src == 'Hittite' else src
            print(f"  {i+1:2d}. {other:<25} (weight: {data['weight']:.3f})")
    
    for toch_lang in tocharian_langs:
        if toch_lang in G:
            toch_edges = list(G.edges(toch_lang, data=True))
            print(f"\n{toch_lang} has {len(toch_edges)} connections")
            
            toch_edges.sort(key=lambda x: x[2]['weight'], reverse=True)
            print(f"{toch_lang}'s strongest connections:")
            for i, (src, dst, data) in enumerate(toch_edges[:10]):
                other = dst if src == toch_lang else src
                print(f"  {i+1:2d}. {other:<25} (weight: {data['weight']:.3f})")
    
    # Check connectivity between key language groups
    print(f"\n=== INTER-GROUP CONNECTIVITY ===")
    
    # Define some major groups to test
    germanic = ['English', 'German', 'Gothic', 'Danish', 'Swedish', 'Norwegian']
    romance = ['French', 'Spanish', 'Italian', 'Portuguese', 'Latin']
    celtic = ['Welsh', 'Irish', 'Breton', 'Cornish']
    hellenic = ['Ancient_Greek', 'Modern_Greek']
    armenian = ['Classical_Armenian', 'Adapazar/Eastern_Armenian']
    
    groups = {
        'Germanic': [lang for lang in germanic if lang in G],
        'Romance': [lang for lang in romance if lang in G], 
        'Celtic': [lang for lang in celtic if lang in G],
        'Hellenic': [lang for lang in hellenic if lang in G],
        'Armenian': [lang for lang in armenian if lang in G]
    }
    
    print("Group sizes found in graph:")
    for group_name, group_langs in groups.items():
        print(f"  {group_name}: {len(group_langs)} languages")
    
    # Check how strongly Tocharian connects to these groups
    if tocharian_langs and tocharian_langs[0] in G:
        toch_lang = tocharian_langs[0]
        print(f"\n{toch_lang} connectivity to major groups:")
        
        for group_name, group_langs in groups.items():
            if not group_langs:
                continue
                
            group_weights = []
            for lang in group_langs:
                if G.has_edge(toch_lang, lang):
                    weight = G[toch_lang][lang]['weight']
                    group_weights.append((lang, weight))
            
            if group_weights:
                group_weights.sort(key=lambda x: x[1], reverse=True)
                avg_weight = sum(w[1] for w in group_weights) / len(group_weights)
                max_weight = max(w[1] for w in group_weights)
                print(f"  {group_name:<10}: {len(group_weights)}/{len(group_langs)} connections, avg={avg_weight:.3f}, max={max_weight:.3f}")
                print(f"    Strongest: {group_weights[0][0]} ({group_weights[0][1]:.3f})")
            else:
                print(f"  {group_name:<10}: No connections")
    
    # Check how strongly Hittite connects to these groups  
    if hittite_present:
        print(f"\nHittite connectivity to major groups:")
        
        for group_name, group_langs in groups.items():
            if not group_langs:
                continue
                
            group_weights = []
            for lang in group_langs:
                if G.has_edge('Hittite', lang):
                    weight = G['Hittite'][lang]['weight']
                    group_weights.append((lang, weight))
            
            if group_weights:
                group_weights.sort(key=lambda x: x[1], reverse=True)
                avg_weight = sum(w[1] for w in group_weights) / len(group_weights)
                max_weight = max(w[1] for w in group_weights)
                print(f"  {group_name:<10}: {len(group_weights)}/{len(group_langs)} connections, avg={avg_weight:.3f}, max={max_weight:.3f}")
            else:
                print(f"  {group_name:<10}: No connections")

if __name__ == "__main__":
    debug_graph_construction()