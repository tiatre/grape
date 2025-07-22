#!/usr/bin/env python3

import pandas as pd

def analyze_hittite_data():
    """Analyze Hittite cognate patterns in the data"""
    
    # Load the data
    df = pd.read_csv('data/ielex_2022.tsv', sep='\t')
    print(f'Total dataset: {len(df)} rows')
    print(f'Languages: {df["Language"].nunique()}')
    print(f'Concepts: {df["Parameter"].nunique()}') 
    print()

    # Count cognate sets per language
    lang_counts = df['Language'].value_counts()
    print('Language coverage (top 10):')
    print(lang_counts.head(10))
    print()

    # Check Hittite specifically
    hittite_data = df[df['Language'] == 'Hittite']
    print(f'Hittite has {len(hittite_data)} cognate entries')
    
    # Check Tocharian too
    toch_a_data = df[df['Language'] == 'Tocharian_A']
    toch_b_data = df[df['Language'] == 'Tocharian_B']
    print(f'Tocharian A has {len(toch_a_data)} cognate entries')
    print(f'Tocharian B has {len(toch_b_data)} cognate entries')
    print()

    # Check if Hittite has unique cognate sets
    hittite_cognates = set(hittite_data['Cognateset'])
    all_other_data = df[df['Language'] != 'Hittite']
    other_cognates = set(all_other_data['Cognateset'])

    shared_cognates = hittite_cognates.intersection(other_cognates)
    unique_hittite = hittite_cognates - other_cognates

    print(f'Hittite shares {len(shared_cognates)} cognate sets with other languages')
    print(f'Hittite has {len(unique_hittite)} unique cognate sets')
    print(f'Sharing percentage: {len(shared_cognates)/len(hittite_cognates)*100:.1f}%')
    print()
    
    # Compare with other languages for context
    for lang in ['Tocharian_A', 'Latin', 'Sanskrit', 'Gothic']:
        if lang in df['Language'].values:
            lang_data = df[df['Language'] == lang]
            lang_cognates = set(lang_data['Cognateset'])
            lang_shared = lang_cognates.intersection(other_cognates)  # other_cognates is everyone except Hittite
            print(f'{lang}: {len(lang_shared)}/{len(lang_cognates)} shared = {len(lang_shared)/len(lang_cognates)*100:.1f}%')
    
    # Check what concepts Hittite has data for
    print()
    print("Sample Hittite concepts:")
    print(hittite_data['Parameter'].head(10).tolist())

if __name__ == "__main__":
    analyze_hittite_data()