"""
Unit tests for DataLoader and NetworkPreprocessor.
"""

import unittest
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.data_loader import DataLoader
from src.network_preprocessing import NetworkPreprocessor


class TestDataLoaderAndPreprocessing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loader = DataLoader()
        cls.raw_df = cls.loader.load_raw_edges()
        cls.preprocessor = NetworkPreprocessor()
        cls.G = cls.preprocessor.build_undirected_graph(cls.raw_df)

    def test_raw_edges_loaded(self):
        self.assertFalse(self.raw_df.empty, "Raw edges DataFrame should not be empty.")
        self.assertEqual(len(self.raw_df), 2672, "Expected 2,672 directed arcs in KONECT moreno_oz.")
        self.assertIn("source", self.raw_df.columns)
        self.assertIn("target", self.raw_df.columns)
        self.assertIn("weight", self.raw_df.columns)

    def test_node_and_edge_counts(self):
        self.assertEqual(self.G.number_of_nodes(), 217, "Expected exactly 217 nodes.")
        self.assertEqual(self.G.number_of_edges(), 1839, "Expected 1,839 undirected edges.")

    def test_graph_properties(self):
        self.assertFalse(self.G.is_directed(), "Graph must be undirected.")
        # Check edge weights are preserved within 1..5
        weights = [d["weight"] for _, _, d in self.G.edges(data=True)]
        self.assertTrue(all(1.0 <= w <= 5.0 for w in weights), "Weights must be in [1.0, 5.0].")
        # Check distance attribute exists
        distances = [d["distance"] for _, _, d in self.G.edges(data=True)]
        self.assertTrue(all(d > 0 for d in distances), "Distance must be strictly positive.")

    def test_connected_component_calculation(self):
        G_lcc, num_comp, lcc_size = self.preprocessor.get_largest_connected_component(self.G)
        self.assertEqual(num_comp, 1, "The friendship graph should form 1 connected component.")
        self.assertEqual(lcc_size, 217, "LCC size must equal total nodes (217).")


if __name__ == "__main__":
    unittest.main()
