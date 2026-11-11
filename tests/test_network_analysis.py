"""
Unit tests for NetworkAnalyzer.
"""

import unittest
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.data_loader import DataLoader
from src.network_preprocessing import NetworkPreprocessor
from src.network_analysis import NetworkAnalyzer


class TestNetworkAnalysis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        loader = DataLoader()
        raw_df = loader.load_raw_edges()
        preprocessor = NetworkPreprocessor()
        cls.G = preprocessor.build_undirected_graph(raw_df)
        cls.analyzer = NetworkAnalyzer()
        cls.metrics = cls.analyzer.analyze_network(cls.G)

    def test_metrics_presence_and_bounds(self):
        m = self.metrics
        self.assertEqual(m["num_nodes"], 217)
        self.assertEqual(m["num_edges"], 1839)
        self.assertEqual(m["lcc_nodes"], 217)
        self.assertAlmostEqual(m["avg_shortest_path_length_unweighted"], 2.3946, places=2)
        self.assertEqual(m["diameter_unweighted"], 4)
        self.assertAlmostEqual(m["avg_clustering_coefficient_unweighted"], 0.3628, places=2)
        self.assertAlmostEqual(m["network_density"], 0.0785, places=3)
        self.assertGreater(m["average_degree"], 0)
        self.assertTrue(m["degree_skewness"] > 0, "Degree distribution must be right-skewed.")

    def test_summary_table_saving(self):
        saved = self.analyzer.save_summary_table(self.metrics, "test_summary.csv")
        self.assertTrue(saved.exists())
        saved.unlink()


if __name__ == "__main__":
    unittest.main()
