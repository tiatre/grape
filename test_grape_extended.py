#!/usr/bin/env python

import unittest
from test_grape import TestHaraldIE, TestTuled


class TestHaraldIEExtended(TestHaraldIE):
    """Extended tests for Harald IE dataset with different parameters."""
    
    def test_germanic_grouping_greedy_modularity(self):
        """Test Germanic grouping with greedy modularity community detection."""
        germanic_langs = {'Danish', 'Dutch', 'Elfdalian', 'English', 'Frisian', 'German', 'Swedish'}
        
        tree = self.get_tree_from_grape(self.harald_ie_file, graph='adjusted', community='greedy', strategy='fixed', initial_value=0.5)
        mrca_leaves = self.get_mrca_leaves(tree, list(germanic_langs))
        
        self.assertTrue(germanic_langs.issubset(mrca_leaves), 
                       f"Germanic languages not monophyletic with greedy modularity. MRCA contains: {mrca_leaves}")
        
        non_germanic = mrca_leaves - germanic_langs
        self.assertEqual(len(non_germanic), 0, 
                        f"Non-Germanic languages in Germanic clade: {non_germanic}")
    
    def test_germanic_grouping_unadjusted_graph(self):
        """Test Germanic grouping with unadjusted graph weights."""
        germanic_langs = {'Danish', 'Dutch', 'Elfdalian', 'English', 'Frisian', 'German', 'Swedish'}
        
        tree = self.get_tree_from_grape(self.harald_ie_file, graph='unadjusted', community='louvain', strategy='fixed', initial_value=0.5)
        mrca_leaves = self.get_mrca_leaves(tree, list(germanic_langs))
        
        self.assertTrue(germanic_langs.issubset(mrca_leaves), 
                       f"Germanic languages not monophyletic with unadjusted graph. MRCA contains: {mrca_leaves}")


class TestTuledExtended(TestTuled):
    """Extended tests for Tuled dataset with different parameters."""
    
    def test_guaranic_grouping_greedy_modularity(self):
        """Test Guaranic grouping with greedy modularity community detection."""
        guaranic_langs = {'Mbya', 'Guarani', 'Kaiowa'}
        
        tree = self.get_tree_from_grape(self.tuled_file, graph='adjusted', community='greedy', strategy='fixed', initial_value=0.5)
        mrca_leaves = self.get_mrca_leaves(tree, list(guaranic_langs))
        
        self.assertTrue(guaranic_langs.issubset(mrca_leaves),
                       f"Guaranic languages not monophyletic with greedy modularity. MRCA contains: {mrca_leaves}")
    
    def test_guaranic_grouping_unadjusted_graph(self):
        """Test Guaranic grouping with unadjusted graph weights."""
        guaranic_langs = {'Mbya', 'Guarani', 'Kaiowa'}
        
        tree = self.get_tree_from_grape(self.tuled_file, graph='unadjusted', community='louvain', strategy='fixed', initial_value=0.5)
        mrca_leaves = self.get_mrca_leaves(tree, list(guaranic_langs))
        
        self.assertTrue(guaranic_langs.issubset(mrca_leaves),
                       f"Guaranic languages not monophyletic with unadjusted graph. MRCA contains: {mrca_leaves}")


if __name__ == '__main__':
    unittest.main()