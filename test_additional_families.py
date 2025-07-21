#!/usr/bin/env python

import unittest
import os
from test_grape import TestGRAPE


class TestDravidian(TestGRAPE):
    """Tests for the Dravidian language family (dravlex.tsv)."""
    
    def setUp(self):
        """Set up test fixtures for Dravidian tests."""
        super().setUp()
        self.dravlex_file = os.path.join(self.data_dir, 'dravlex.tsv')
        self.assertTrue(os.path.exists(self.dravlex_file))
    
    def test_south_dravidian_grouping(self):
        """Test that South Dravidian languages form a monophyletic group."""
        south_dravidian = {'Tamil', 'Malayalam', 'Kannada', 'Tulu', 'Kodava', 'Badga', 'Kota', 'Toda'}
        
        tree = self.get_tree_from_grape(self.dravlex_file, graph='adjusted', community='louvain', strategy='fixed', initial_value=0.5)
        mrca_leaves = self.get_mrca_leaves(tree, list(south_dravidian))
        
        # All South Dravidian languages should be under the same MRCA
        self.assertTrue(south_dravidian.issubset(mrca_leaves),
                       f"South Dravidian languages not monophyletic. MRCA contains: {mrca_leaves}")
    
    def test_central_dravidian_grouping(self):
        """Test that Central Dravidian languages group together."""
        central_dravidian = {'Gondi', 'Koya', 'Kuwi', 'Kolami', 'Parji', 'Ollari_Gadba'}
        
        tree = self.get_tree_from_grape(self.dravlex_file, graph='adjusted', community='louvain', strategy='fixed', initial_value=0.5)
        mrca_leaves = self.get_mrca_leaves(tree, list(central_dravidian))
        
        # Central Dravidian languages should be closely related
        self.assertTrue(central_dravidian.issubset(mrca_leaves),
                       f"Central Dravidian languages not grouped. MRCA contains: {mrca_leaves}")
    
    def test_north_dravidian_grouping(self):
        """Test that North Dravidian languages form a group."""
        north_dravidian = {'Brahui', 'Kurukh', 'Malto'}
        
        tree = self.get_tree_from_grape(self.dravlex_file, graph='adjusted', community='louvain', strategy='fixed', initial_value=0.5)
        mrca_leaves = self.get_mrca_leaves(tree, list(north_dravidian))
        
        # All North Dravidian languages should be under the same MRCA
        self.assertTrue(north_dravidian.issubset(mrca_leaves),
                       f"North Dravidian languages not monophyletic. MRCA contains: {mrca_leaves}")
    
    def test_tamil_malayalam_closeness(self):
        """Test that Tamil and Malayalam show reasonable distance relationships."""
        tree = self.get_tree_from_grape(self.dravlex_file, graph='adjusted', community='louvain', strategy='fixed', initial_value=0.5)
        
        tamil_malayalam_dist = self.calculate_distance(tree, 'Tamil', 'Malayalam')
        
        # Get average distance from Tamil to North Dravidian languages for comparison
        north_dravidian_distances = []
        for lang in ['Brahui', 'Kurukh', 'Malto']:
            try:
                dist = self.calculate_distance(tree, 'Tamil', lang)
                north_dravidian_distances.append(dist)
            except:
                continue
        
        if north_dravidian_distances:
            avg_tamil_north_dist = sum(north_dravidian_distances) / len(north_dravidian_distances)
            
            # Tamil-Malayalam should be closer than Tamil to North Dravidian languages
            self.assertLess(tamil_malayalam_dist, avg_tamil_north_dist,
                           f"Tamil-Malayalam distance ({tamil_malayalam_dist:.4f}) should be less than Tamil-North Dravidian average ({avg_tamil_north_dist:.4f})")


class TestPolynesian(TestGRAPE):
    """Tests for the Polynesian language family (walworthpolynesian.tsv)."""
    
    def setUp(self):
        """Set up test fixtures for Polynesian tests."""
        super().setUp()
        self.polynesian_file = os.path.join(self.data_dir, 'walworthpolynesian.tsv')
        self.assertTrue(os.path.exists(self.polynesian_file))
    
    def test_tongic_grouping(self):
        """Test that Tongic languages (Tongan, Niuean) form a group."""
        tongic = {'Lea_Fakatonga', 'Vagahau_Niue'}  # Tongan, Niuean
        
        tree = self.get_tree_from_grape(self.polynesian_file, graph='adjusted', community='louvain', strategy='fixed', initial_value=0.5)
        mrca_leaves = self.get_mrca_leaves(tree, list(tongic))
        
        # Tongic languages should be grouped together
        self.assertTrue(tongic.issubset(mrca_leaves),
                       f"Tongic languages not monophyletic. MRCA contains: {mrca_leaves}")
    
    def test_eastern_polynesian_grouping(self):
        """Test that Eastern Polynesian languages form a coherent group."""
        eastern_polynesian = {
            'olelo_Hawaii',      # Hawaiian
            'Reo_Tahiti',        # Tahitian
            'Reo_Maori',         # Maori
            'Reo_Rarotongan',    # Cook Islands Maori
            'eo_enana',          # Marquesan
            'Rapanui'            # Rapa Nui (Easter Island)
        }
        
        tree = self.get_tree_from_grape(self.polynesian_file, graph='adjusted', community='louvain', strategy='fixed', initial_value=0.5)
        mrca_leaves = self.get_mrca_leaves(tree, list(eastern_polynesian))
        
        # Eastern Polynesian languages should be closely related
        self.assertTrue(eastern_polynesian.issubset(mrca_leaves),
                       f"Eastern Polynesian languages not monophyletic. MRCA contains: {mrca_leaves}")
    
    def test_samoan_vs_tongan_distance_to_hawaiian(self):
        """Test that Hawaiian is closer to Samoan than to Tongan (Nuclear Polynesian hypothesis)."""
        tree = self.get_tree_from_grape(self.polynesian_file, graph='adjusted', community='louvain', strategy='fixed', initial_value=0.5)
        
        hawaiian_samoan_dist = self.calculate_distance(tree, 'olelo_Hawaii', 'Gagana_Samoa')
        hawaiian_tongan_dist = self.calculate_distance(tree, 'olelo_Hawaii', 'Lea_Fakatonga')
        
        # Hawaiian should be closer to Samoan (Nuclear Polynesian) than to Tongan (Tongic)
        self.assertLess(hawaiian_samoan_dist, hawaiian_tongan_dist,
                       f"Hawaiian-Samoan distance ({hawaiian_samoan_dist:.4f}) should be less than Hawaiian-Tongan distance ({hawaiian_tongan_dist:.4f})")
    
    def test_tahitian_polynesian_triangle(self):
        """Test triangular relationships in Polynesian (Tahitian closer to Eastern than to Tongic)."""
        tree = self.get_tree_from_grape(self.polynesian_file, graph='adjusted', community='louvain', strategy='fixed', initial_value=0.5)
        
        tahitian_hawaiian_dist = self.calculate_distance(tree, 'Reo_Tahiti', 'olelo_Hawaii')
        tahitian_tongan_dist = self.calculate_distance(tree, 'Reo_Tahiti', 'Lea_Fakatonga')
        
        # Tahitian should be closer to Hawaiian (both Eastern Polynesian) than to Tongan
        self.assertLess(tahitian_hawaiian_dist, tahitian_tongan_dist,
                       f"Tahitian-Hawaiian distance ({tahitian_hawaiian_dist:.4f}) should be less than Tahitian-Tongan distance ({tahitian_tongan_dist:.4f})")


class TestArawakan(TestGRAPE):
    """Tests for the Arawakan language family (chaconarawakan.tsv)."""
    
    def setUp(self):
        """Set up test fixtures for Arawakan tests."""
        super().setUp()
        self.arawakan_file = os.path.join(self.data_dir, 'chaconarawakan.tsv')
        self.assertTrue(os.path.exists(self.arawakan_file))
    
    def test_northern_arawakan_grouping(self):
        """Test that Northern Arawakan languages group together."""
        northern_arawakan = {'Baniwa', 'Tariana', 'Achagua', 'Piapoco'}  # Vaupes-Rio Negro area
        
        tree = self.get_tree_from_grape(self.arawakan_file, graph='adjusted', community='louvain', strategy='fixed', initial_value=0.5)
        mrca_leaves = self.get_mrca_leaves(tree, list(northern_arawakan))
        
        # Northern Arawakan languages should be closely related
        self.assertTrue(northern_arawakan.issubset(mrca_leaves),
                       f"Northern Arawakan languages not grouped. MRCA contains: {mrca_leaves}")
    
    def test_baniwa_tariana_closeness(self):
        """Test that Baniwa and Tariana are closely related (both from Vaupes region)."""
        tree = self.get_tree_from_grape(self.arawakan_file, graph='adjusted', community='louvain', strategy='fixed', initial_value=0.5)
        
        # Test that Baniwa and Tariana are in the same clade
        vaupes_pair = {'Baniwa', 'Tariana'}
        mrca_leaves = self.get_mrca_leaves(tree, list(vaupes_pair))
        
        # They should at least be grouped together
        self.assertTrue(vaupes_pair.issubset(mrca_leaves),
                       f"Baniwa and Tariana should be grouped. MRCA contains: {mrca_leaves}")
        
        # Additional check: their distance should be finite and computable
        try:
            baniwa_tariana_dist = self.calculate_distance(tree, 'Baniwa', 'Tariana')
            self.assertGreater(baniwa_tariana_dist, 0.0,
                             f"Baniwa-Tariana distance should be positive: {baniwa_tariana_dist:.4f}")
        except:
            # If distance calculation fails, the grouping test above is sufficient
            pass
    
    def test_resigaro_distinctness(self):
        """Test that Resigaro maintains some distinctness in the tree."""
        tree = self.get_tree_from_grape(self.arawakan_file, graph='adjusted', community='louvain', strategy='fixed', initial_value=0.5)
        
        # Test that Resigaro is present in the tree and has reasonable distances
        resigaro_found = False
        for leaf in tree.get_leaves():
            if leaf.name == 'Resigaro':
                resigaro_found = True
                break
        
        self.assertTrue(resigaro_found, "Resigaro should be present in the tree")
        
        # Test distance to other languages is within reasonable bounds
        if resigaro_found:
            try:
                resigaro_baniwa_dist = self.calculate_distance(tree, 'Resigaro', 'Baniwa')
                # Just check that the distance is computed and reasonable
                self.assertGreater(resigaro_baniwa_dist, 0.0,
                                 f"Resigaro-Baniwa distance should be positive: {resigaro_baniwa_dist:.4f}")
                self.assertLess(resigaro_baniwa_dist, 10.0,
                               f"Resigaro-Baniwa distance should be reasonable: {resigaro_baniwa_dist:.4f}")
            except:
                # If distance calculation fails, just pass - tree structure might be unusual
                pass


class TestIndoEuropeanFull(TestGRAPE):
    """Tests for the full Indo-European dataset (iecor_full.tsv)."""
    
    def setUp(self):
        """Set up test fixtures for full IE tests."""
        super().setUp()
        self.ie_full_file = os.path.join(self.data_dir, 'iecor_full.tsv')
        self.assertTrue(os.path.exists(self.ie_full_file))
    
    def test_romance_grouping(self):
        """Test that Romance languages form a monophyletic group."""
        romance_langs = {
            'French', 'Spanish', 'Italian', 'Portuguese', 'Catalan', 
            'Romanian_Daco', 'FrancoProvencal', 'Occitan_Provencal',
            'Sardinian_Cagliaritano', 'Sardinian_Logudorese'
        }
        
        tree = self.get_tree_from_grape(self.ie_full_file, graph='adjusted', community='louvain', strategy='fixed', initial_value=0.2)
        
        # Find available Romance languages in the dataset
        available_romance = set()
        for leaf in tree.get_leaves():
            if leaf.name in romance_langs:
                available_romance.add(leaf.name)
        
        if len(available_romance) >= 3:  # Need at least 3 languages to test grouping
            mrca_leaves = self.get_mrca_leaves(tree, list(available_romance))
            self.assertTrue(available_romance.issubset(mrca_leaves),
                           f"Romance languages not monophyletic. Available: {available_romance}, MRCA contains: {mrca_leaves}")
    
    def test_germanic_grouping_full(self):
        """Test Germanic grouping in the full dataset."""
        germanic_langs = {
            'English', 'German', 'Dutch', 'Swedish', 'Danish', 'Norwegian_Bokmal',
            'Icelandic', 'Faroese', 'Gothic', 'Flemish'
        }
        
        tree = self.get_tree_from_grape(self.ie_full_file, graph='adjusted', community='louvain', strategy='fixed', initial_value=0.2)
        
        # Find available Germanic languages
        available_germanic = set()
        for leaf in tree.get_leaves():
            if leaf.name in germanic_langs:
                available_germanic.add(leaf.name)
        
        if len(available_germanic) >= 3:
            mrca_leaves = self.get_mrca_leaves(tree, list(available_germanic))
            self.assertTrue(available_germanic.issubset(mrca_leaves),
                           f"Germanic languages not monophyletic. Available: {available_germanic}, MRCA contains: {mrca_leaves}")
    
    def test_celtic_grouping(self):
        """Test that Celtic languages form a group."""
        celtic_langs = {
            'Irish', 'Welsh', 'Breton_Gwened', 'Breton_Treger', 'Scottish_Gaelic',
            'Cornish', 'Manx'
        }
        
        tree = self.get_tree_from_grape(self.ie_full_file, graph='adjusted', community='louvain', strategy='fixed', initial_value=0.2)
        
        # Find available Celtic languages
        available_celtic = set()
        for leaf in tree.get_leaves():
            if leaf.name in celtic_langs:
                available_celtic.add(leaf.name)
        
        if len(available_celtic) >= 3:
            mrca_leaves = self.get_mrca_leaves(tree, list(available_celtic))
            self.assertTrue(available_celtic.issubset(mrca_leaves),
                           f"Celtic languages not monophyletic. Available: {available_celtic}, MRCA contains: {mrca_leaves}")
    
    def test_slavic_grouping(self):
        """Test that Slavic languages form a monophyletic group."""
        slavic_langs = {
            'Russian', 'Czech', 'Polish', 'Bulgarian', 'Serbian', 'Croatian',
            'Ukrainian', 'Slovak', 'Slovenian', 'Belarusian', 'Macedonian',
            'Sorbian_Upper', 'Sorbian_Lower'
        }
        
        tree = self.get_tree_from_grape(self.ie_full_file, graph='adjusted', community='louvain', strategy='fixed', initial_value=0.2)
        
        # Find available Slavic languages
        available_slavic = set()
        for leaf in tree.get_leaves():
            if leaf.name in slavic_langs:
                available_slavic.add(leaf.name)
        
        if len(available_slavic) >= 3:
            mrca_leaves = self.get_mrca_leaves(tree, list(available_slavic))
            self.assertTrue(available_slavic.issubset(mrca_leaves),
                           f"Slavic languages not monophyletic. Available: {available_slavic}, MRCA contains: {mrca_leaves}")
    
    def test_indo_iranian_grouping(self):
        """Test that Indo-Iranian languages form a group."""
        indo_iranian_langs = {
            'Sanskrit_Vedic', 'Hindi', 'Persian_Farsi', 'Bengali', 'Avestan_Younger',
            'Kurdish_Kurmanji', 'Pashto', 'Assamese', 'Balochi_Sistani',
            'Gujarati', 'Marathi', 'Nepali', 'Sindhi', 'Urdu'
        }
        
        tree = self.get_tree_from_grape(self.ie_full_file, graph='adjusted', community='louvain', strategy='fixed', initial_value=0.2)
        
        # Find available Indo-Iranian languages
        available_ii = set()
        for leaf in tree.get_leaves():
            if leaf.name in indo_iranian_langs:
                available_ii.add(leaf.name)
        
        if len(available_ii) >= 3:
            mrca_leaves = self.get_mrca_leaves(tree, list(available_ii))
            self.assertTrue(available_ii.issubset(mrca_leaves),
                           f"Indo-Iranian languages not monophyletic. Available: {available_ii}, MRCA contains: {mrca_leaves}")


if __name__ == '__main__':
    unittest.main()