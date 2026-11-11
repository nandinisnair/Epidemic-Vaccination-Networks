"""
Unit tests for VaccinationManager.
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
from src.vaccination import VaccinationManager


class TestVaccination(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        loader = DataLoader()
        raw_df = loader.load_raw_edges()
        preprocessor = NetworkPreprocessor()
        cls.G = preprocessor.build_undirected_graph(raw_df)
        cls.cent = CentralityAnalyzer()
        cls.centralities = cls.cent.compute_all_centralities(cls.G)
        cls.rankings = cls.cent.get_rankings(cls.centralities)
        cls.mgr = VaccinationManager(cls.G, cls.rankings)

    def test_original_graph_unaltered(self):
        initial_nodes = self.G.number_of_nodes()
        initial_edges = self.G.number_of_edges()

        # Apply 30% degree vaccination
        G_vacc, vacc_nodes, lcc = self.mgr.apply_vaccination("Degree", 0.3)
        self.assertEqual(self.G.number_of_nodes(), initial_nodes)
        self.assertEqual(self.G.number_of_edges(), initial_edges)

    def test_vaccination_node_count_and_removal(self):
        fraction = 0.2
        expected_count = int(round(0.2 * 217))  # 43 nodes
        for strat in ["Random", "Degree", "Strength", "Betweenness", "Weighted Betweenness"]:
            rng = np.random.default_rng(42)
            G_vacc, vacc_nodes, lcc = self.mgr.apply_vaccination(strat, fraction, rng=rng)
            self.assertEqual(
                len(vacc_nodes),
                expected_count,
                f"Strategy '{strat}' vaccinated {len(vacc_nodes)} nodes, expected {expected_count}.",
            )
            self.assertEqual(
                G_vacc.number_of_nodes(),
                217 - expected_count,
                f"Residual graph node count mismatch for '{strat}'.",
            )
            # Verify no vaccinated node remains in G_vacc
            for node in vacc_nodes:
                self.assertNotIn(node, G_vacc)

    def test_degree_targeted_nodes_are_highest_degree(self):
        fraction = 0.1  # 22 nodes
        expected_nodes = [n for n, _ in self.rankings["degree"][:22]]
        G_vacc, vacc_nodes, lcc = self.mgr.apply_vaccination("Degree", fraction)
        self.assertEqual(vacc_nodes, expected_nodes)

    def test_lcc_decreases_with_coverage(self):
        lccs = []
        for cov in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]:
            _, _, lcc = self.mgr.apply_vaccination("Degree", cov)
            lccs.append(lcc)
        for i in range(len(lccs) - 1):
            self.assertGreaterEqual(lccs[i], lccs[i + 1])


if __name__ == "__main__":
    unittest.main()
