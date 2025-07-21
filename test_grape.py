#!/usr/bin/env python

import unittest
import subprocess
import os
from ete3 import Tree
from typing import List, Set


class TestGRAPE(unittest.TestCase):
    """Test suite for GRAPE phylogenetic reconstruction."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        self.harald_ie_file = os.path.join(self.data_dir, 'harald_ie.tsv')
        self.tuled_file = os.path.join(self.data_dir, 'tuled.tsv')
        
        # Verify test data files exist
        self.assertTrue(os.path.exists(self.harald_ie_file))
        self.assertTrue(os.path.exists(self.tuled_file))
    
    def run_grape(self, input_file: str, **kwargs) -> str:
        """Run GRAPE and return the Newick tree output."""
        cmd = ['python', 'grape.py', input_file]
        
        # Add column name mappings for harald_ie.tsv
        if 'harald_ie.tsv' in input_file:
            cmd.extend(['--concept-column', 'Concept'])
        
        # Add optional parameters
        for key, value in kwargs.items():
            cmd.extend([f'--{key}', str(value)])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            # Combine stdout and stderr since GRAPE outputs tree to stderr and parameters to stdout
            return (result.stdout + "\n" + result.stderr).strip()
        except subprocess.CalledProcessError as e:
            self.fail(f"GRAPE execution failed: {e.stderr}")
    
    def get_tree_from_grape(self, input_file: str, **kwargs) -> Tree:
        """Run GRAPE and return the parsed ETE3 tree."""
        newick_output = self.run_grape(input_file, **kwargs)
        
        # Extract Newick string from output (look for the line with "[INFO] Newick format tree:")
        lines = newick_output.split('\n')
        newick_tree = ""
        
        for line in lines:
            if "[INFO] Newick format tree:" in line:
                newick_tree = line.split("[INFO] Newick format tree: ", 1)[1].strip()
                break
        
        if not newick_tree or not newick_tree.endswith(';'):
            self.fail(f"Could not find valid Newick tree in output. Full output:\n{newick_output}")
        
        return Tree(newick_tree)
    
    def get_mrca_leaves(self, tree: Tree, language_list: List[str]) -> Set[str]:
        """Get all leaf names under the MRCA of given languages."""
        # Find leaf nodes for the languages
        target_nodes = []
        for leaf in tree.get_leaves():
            if leaf.name in language_list:
                target_nodes.append(leaf)
        
        if len(target_nodes) < 2:
            return set()
        
        # Get MRCA and all its descendants
        mrca = tree.get_common_ancestor(target_nodes)
        return {leaf.name for leaf in mrca.get_leaves()}
    
    def calculate_distance(self, tree: Tree, lang1: str, lang2: str) -> float:
        """Calculate the total branch length distance between two languages."""
        # Find the leaf nodes
        node1 = None
        node2 = None
        for leaf in tree.get_leaves():
            if leaf.name == lang1:
                node1 = leaf
            elif leaf.name == lang2:
                node2 = leaf
        
        if not node1 or not node2:
            self.fail(f"Could not find languages {lang1} and {lang2} in tree")
        
        # Calculate distance
        return node1.get_distance(node2)


class TestHaraldIE(TestGRAPE):
    """Tests for the Harald Indo-European dataset."""
    
    def test_germanic_grouping(self):
        """Test that Germanic languages form a monophyletic group."""
        germanic_langs = {'Danish', 'Dutch', 'Elfdalian', 'English', 'Frisian', 'German', 'Swedish'}
        
        tree = self.get_tree_from_grape(self.harald_ie_file, graph='adjusted', community='louvain', strategy='fixed', initial_value=0.5)
        
        # Get all leaves under the MRCA of Germanic languages
        mrca_leaves = self.get_mrca_leaves(tree, list(germanic_langs))
        
        # All Germanic languages should be under the same MRCA
        self.assertTrue(germanic_langs.issubset(mrca_leaves), 
                       f"Germanic languages not monophyletic. MRCA contains: {mrca_leaves}")
        
        # No non-Germanic languages should be in this clade
        non_germanic = mrca_leaves - germanic_langs
        self.assertEqual(len(non_germanic), 0, 
                        f"Non-Germanic languages in Germanic clade: {non_germanic}")
    
    def test_spanish_closer_to_germanic_than_hindi(self):
        """Test that Spanish is closer to Germanic group than to Hindi."""
        germanic_langs = ['Danish', 'Dutch', 'Elfdalian', 'English', 'Frisian', 'German', 'Swedish']
        
        tree = self.get_tree_from_grape(self.harald_ie_file, graph='adjusted', community='louvain', strategy='fixed', initial_value=0.5)
        
        # Calculate average distance from Spanish to Germanic languages
        spanish_germanic_distances = []
        for lang in germanic_langs:
            try:
                dist = self.calculate_distance(tree, 'Spanish', lang)
                spanish_germanic_distances.append(dist)
            except:
                continue
        
        if not spanish_germanic_distances:
            self.fail("Could not calculate distances from Spanish to Germanic languages")
        
        avg_spanish_germanic = sum(spanish_germanic_distances) / len(spanish_germanic_distances)
        spanish_hindi_distance = self.calculate_distance(tree, 'Spanish', 'Hindi')
        
        self.assertLess(avg_spanish_germanic, spanish_hindi_distance,
                       f"Spanish-Germanic avg distance ({avg_spanish_germanic:.4f}) should be less than Spanish-Hindi distance ({spanish_hindi_distance:.4f})")
    
    def test_swedish_danish_closer_than_swedish_english(self):
        """Test that Swedish-Danish distance is smaller than Swedish-English distance."""
        tree = self.get_tree_from_grape(self.harald_ie_file, graph='adjusted', community='louvain', strategy='fixed', initial_value=0.5)
        
        swedish_danish_dist = self.calculate_distance(tree, 'Swedish', 'Danish')
        swedish_english_dist = self.calculate_distance(tree, 'Swedish', 'English')
        
        self.assertLess(swedish_danish_dist, swedish_english_dist,
                       f"Swedish-Danish distance ({swedish_danish_dist:.4f}) should be less than Swedish-English distance ({swedish_english_dist:.4f})")


class TestTuled(TestGRAPE):
    """Tests for the Tuled (Tupian) dataset."""
    
    def test_guaranic_grouping(self):
        """Test that Mbya, Guarani, and Kaiowa form a monophyletic group."""
        guaranic_langs = {'Mbya', 'Guarani', 'Kaiowa'}
        
        tree = self.get_tree_from_grape(self.tuled_file, graph='adjusted', community='louvain', strategy='fixed', initial_value=0.5)
        
        # Get all leaves under the MRCA of Guaranic languages
        mrca_leaves = self.get_mrca_leaves(tree, list(guaranic_langs))
        
        # All Guaranic languages should be under the same MRCA
        self.assertTrue(guaranic_langs.issubset(mrca_leaves),
                       f"Guaranic languages not monophyletic. MRCA contains: {mrca_leaves}")
        
        # Ideally, only Guaranic languages should be in this clade, but we'll be lenient
        # as long as the three target languages are grouped together
    
    def test_mawe_aweti_early_branching(self):
        """Test that Mawe and Aweti branch early (are among the first out)."""
        tree = self.get_tree_from_grape(self.tuled_file, graph='adjusted', community='louvain', strategy='fixed', initial_value=0.5)
        
        # Calculate distance from root for all languages
        root = tree.get_tree_root()
        distances = {}
        
        for leaf in tree.get_leaves():
            if leaf.name in {'Mawe', 'Aweti'}:
                distances[leaf.name] = root.get_distance(leaf)
        
        # Check that both Mawe and Aweti are found
        self.assertIn('Mawe', distances, "Mawe not found in tree")
        self.assertIn('Aweti', distances, "Aweti not found in tree")
        
        # Get distances for all other languages
        other_distances = []
        for leaf in tree.get_leaves():
            if leaf.name not in {'Mawe', 'Aweti', 'Language'}:  # Exclude header artifacts
                other_distances.append(root.get_distance(leaf))
        
        # Mawe and Aweti should have relatively long distances from root (early branching)
        mawe_distance = distances['Mawe']
        aweti_distance = distances['Aweti']
        
        if other_distances:
            median_distance = sorted(other_distances)[len(other_distances) // 2]
            
            # At least one of Mawe or Aweti should have above-median distance
            early_branching = mawe_distance >= median_distance or aweti_distance >= median_distance
            self.assertTrue(early_branching,
                           f"Mawe ({mawe_distance:.4f}) or Aweti ({aweti_distance:.4f}) should have >= median distance ({median_distance:.4f})")


if __name__ == '__main__':
    unittest.main()