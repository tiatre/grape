#!/usr/bin/env python

import unittest
from test_additional_families import TestDravidian, TestPolynesian, TestArawakan, TestIndoEuropeanFull


class TestDravidianExtended(TestDravidian):
    """Extended tests for Dravidian with different parameters."""
    
    def test_south_dravidian_grouping_greedy(self):
        """Test South Dravidian grouping with greedy modularity."""
        south_dravidian = {'Tamil', 'Malayalam', 'Kannada', 'Tulu'}  # Core South Dravidian
        
        tree = self.get_tree_from_grape(self.dravlex_file, graph='adjusted', community='greedy', strategy='fixed', initial_value=0.5)
        mrca_leaves = self.get_mrca_leaves(tree, list(south_dravidian))
        
        self.assertTrue(south_dravidian.issubset(mrca_leaves),
                       f"South Dravidian languages not monophyletic with greedy. MRCA contains: {mrca_leaves}")
    
    def test_north_dravidian_grouping_unadjusted(self):
        """Test North Dravidian grouping with unadjusted graph."""
        north_dravidian = {'Brahui', 'Kurukh', 'Malto'}
        
        tree = self.get_tree_from_grape(self.dravlex_file, graph='unadjusted', community='louvain', strategy='fixed', initial_value=0.5)
        mrca_leaves = self.get_mrca_leaves(tree, list(north_dravidian))
        
        self.assertTrue(north_dravidian.issubset(mrca_leaves),
                       f"North Dravidian languages not monophyletic with unadjusted graph. MRCA contains: {mrca_leaves}")
    
    def test_dravidian_dynamic_strategy(self):
        """Test Dravidian grouping with dynamic parameter strategy."""
        central_dravidian = {'Gondi', 'Koya', 'Kuwi'}  # Core Central Dravidian
        
        tree = self.get_tree_from_grape(self.dravlex_file, graph='adjusted', community='louvain', strategy='dynamic', initial_value=0.5)
        mrca_leaves = self.get_mrca_leaves(tree, list(central_dravidian))
        
        self.assertTrue(central_dravidian.issubset(mrca_leaves),
                       f"Central Dravidian languages not grouped with dynamic strategy. MRCA contains: {mrca_leaves}")


class TestPolynesianExtended(TestPolynesian):
    """Extended tests for Polynesian with different parameters."""
    
    def test_tongic_grouping_greedy(self):
        """Test Tongic grouping with greedy modularity."""
        tongic = {'Lea_Fakatonga', 'Vagahau_Niue'}
        
        tree = self.get_tree_from_grape(self.polynesian_file, graph='adjusted', community='greedy', strategy='fixed', initial_value=0.5)
        mrca_leaves = self.get_mrca_leaves(tree, list(tongic))
        
        self.assertTrue(tongic.issubset(mrca_leaves),
                       f"Tongic languages not monophyletic with greedy. MRCA contains: {mrca_leaves}")
    
    def test_eastern_polynesian_unadjusted(self):
        """Test Eastern Polynesian grouping with unadjusted graph."""
        eastern_polynesian = {'olelo_Hawaii', 'Reo_Tahiti', 'Reo_Maori'}  # Core Eastern Polynesian
        
        tree = self.get_tree_from_grape(self.polynesian_file, graph='unadjusted', community='louvain', strategy='fixed', initial_value=0.5)
        mrca_leaves = self.get_mrca_leaves(tree, list(eastern_polynesian))
        
        self.assertTrue(eastern_polynesian.issubset(mrca_leaves),
                       f"Eastern Polynesian languages not monophyletic with unadjusted graph. MRCA contains: {mrca_leaves}")
    
    def test_polynesian_adaptive_strategy(self):
        """Test Polynesian grouping with adaptive parameter strategy."""
        nuclear_polynesian_sample = {'Gagana_Samoa', 'olelo_Hawaii', 'Reo_Tahiti'}
        
        tree = self.get_tree_from_grape(self.polynesian_file, graph='adjusted', community='louvain', strategy='adaptive', initial_value=0.5)
        mrca_leaves = self.get_mrca_leaves(tree, list(nuclear_polynesian_sample))
        
        self.assertTrue(nuclear_polynesian_sample.issubset(mrca_leaves),
                       f"Nuclear Polynesian sample not grouped with adaptive strategy. MRCA contains: {mrca_leaves}")


class TestArawakanExtended(TestArawakan):
    """Extended tests for Arawakan with different parameters."""
    
    def test_northern_arawakan_greedy(self):
        """Test Northern Arawakan grouping with greedy modularity."""
        northern_arawakan = {'Baniwa', 'Tariana', 'Achagua'}  # Core Northern Arawakan
        
        tree = self.get_tree_from_grape(self.arawakan_file, graph='adjusted', community='greedy', strategy='fixed', initial_value=0.5)
        mrca_leaves = self.get_mrca_leaves(tree, list(northern_arawakan))
        
        self.assertTrue(northern_arawakan.issubset(mrca_leaves),
                       f"Northern Arawakan languages not grouped with greedy. MRCA contains: {mrca_leaves}")
    
    def test_arawakan_unadjusted_graph(self):
        """Test Arawakan grouping with unadjusted graph weights."""
        vaupes_group = {'Baniwa', 'Tariana'}  # Geographically close pair
        
        tree = self.get_tree_from_grape(self.arawakan_file, graph='unadjusted', community='louvain', strategy='fixed', initial_value=0.5)
        mrca_leaves = self.get_mrca_leaves(tree, list(vaupes_group))
        
        self.assertTrue(vaupes_group.issubset(mrca_leaves),
                       f"Vaupes Arawakan languages not grouped with unadjusted graph. MRCA contains: {mrca_leaves}")
    
    def test_arawakan_dynamic_strategy(self):
        """Test Arawakan with dynamic parameter strategy."""
        core_group = {'Baniwa', 'Tariana', 'Piapoco'}
        
        tree = self.get_tree_from_grape(self.arawakan_file, graph='adjusted', community='louvain', strategy='dynamic', initial_value=0.5)
        mrca_leaves = self.get_mrca_leaves(tree, list(core_group))
        
        self.assertTrue(core_group.issubset(mrca_leaves),
                       f"Core Arawakan languages not grouped with dynamic strategy. MRCA contains: {mrca_leaves}")


class TestIndoEuropeanFullExtended(TestIndoEuropeanFull):
    """Extended tests for full Indo-European with different parameters."""
    
    def test_romance_grouping_greedy(self):
        """Test Romance grouping with greedy modularity."""
        core_romance = {'French', 'Spanish', 'Italian'}  # Well-documented Romance languages
        
        tree = self.get_tree_from_grape(self.ie_full_file, graph='adjusted', community='greedy', strategy='fixed', initial_value=0.2)
        
        # Find available languages
        available_romance = set()
        for leaf in tree.get_leaves():
            if leaf.name in core_romance:
                available_romance.add(leaf.name)
        
        if len(available_romance) >= 2:
            mrca_leaves = self.get_mrca_leaves(tree, list(available_romance))
            self.assertTrue(available_romance.issubset(mrca_leaves),
                           f"Core Romance languages not monophyletic with greedy. Available: {available_romance}, MRCA contains: {mrca_leaves}")
    
    def test_germanic_grouping_unadjusted(self):
        """Test Germanic grouping with unadjusted graph."""
        core_germanic = {'English', 'German', 'Dutch'}
        
        tree = self.get_tree_from_grape(self.ie_full_file, graph='unadjusted', community='louvain', strategy='fixed', initial_value=0.2)
        
        # Find available languages
        available_germanic = set()
        for leaf in tree.get_leaves():
            if leaf.name in core_germanic:
                available_germanic.add(leaf.name)
        
        if len(available_germanic) >= 2:
            mrca_leaves = self.get_mrca_leaves(tree, list(available_germanic))
            self.assertTrue(available_germanic.issubset(mrca_leaves),
                           f"Core Germanic languages not monophyletic with unadjusted graph. Available: {available_germanic}, MRCA contains: {mrca_leaves}")
    
    def test_ie_adaptive_strategy(self):
        """Test Indo-European groupings with adaptive parameter strategy."""
        slavic_sample = {'Russian', 'Czech', 'Polish'}
        
        tree = self.get_tree_from_grape(self.ie_full_file, graph='adjusted', community='louvain', strategy='adaptive', initial_value=0.2)
        
        # Find available languages
        available_slavic = set()
        for leaf in tree.get_leaves():
            if leaf.name in slavic_sample:
                available_slavic.add(leaf.name)
        
        if len(available_slavic) >= 2:
            mrca_leaves = self.get_mrca_leaves(tree, list(available_slavic))
            self.assertTrue(available_slavic.issubset(mrca_leaves),
                           f"Slavic sample not monophyletic with adaptive strategy. Available: {available_slavic}, MRCA contains: {mrca_leaves}")


if __name__ == '__main__':
    unittest.main()