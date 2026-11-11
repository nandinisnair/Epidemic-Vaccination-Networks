"""
Unit tests for CentralityAnalyzer.
"""

import unittest
from pathlib import Path
import sys
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.data_loader import DataLoader
from src.network_preprocessing import NetworkPreprocessor
from src.centrality_analysis import CentralityAnalyzer


class TestCentralityAnalysis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        loader = DataLoader()
        raw_df = loader.load_raw_edges()
        preprocessor = NetworkPreprocessor()
        cls.G = preprocessor.build_undirected_graph(raw_df)
        cls.analyzer = CentralityAnalyzer()
        cls.centralities = cls.analyzer.compute_all_centralities(cls.G)
        cls.rankings = cls.analyzer.get_rankings(cls.centralities)

    def test_all_nodes_scored(self):
        for name, scores in self.centralities.items():
            self.assertEqual(
                len(scores), 217, f"Metric '{name}' must score all 217 nodes."
            )
            # Scores must be finite and non-negative
            vals = list(scores.values())
            self.assertTrue(all(np.isfinite(v) and v >= 0 for v in vals))

    def test_rankings_sorted_descending(self):
        for name, ranked_list in self.rankings.items():
            scores = [s for _, s in ranked_list]
            self.assertTrue(
                all(scores[i] >= scores[i + 1] for i in range(len(scores) - 1)),
                f"Rankings for '{name}' must be sorted in non-increasing order.",
            )

    def test_top_nodes_match_expected(self):
        # Top degree node is 70
        top_deg_node, _ = self.rankings["degree"][0]
        self.assertEqual(top_deg_node, 70)
        # Top strength node is 70
        top_str_node, _ = self.rankings["strength"][0]
        self.assertEqual(top_str_node, 70)
        # Top unweighted betweenness node is 70
        top_bet_node, _ = self.rankings["betweenness"][0]
        self.assertEqual(top_bet_node, 70)


if __name__ == "__main__":
    unittest.main()
