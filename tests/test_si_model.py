"""
Unit tests for SIModel.
"""

import unittest
from pathlib import Path
import sys
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.data_loader import DataLoader
from src.network_preprocessing import NetworkPreprocessor
from src.si_model import SIModel


class TestSIModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        loader = DataLoader()
        raw_df = loader.load_raw_edges()
        preprocessor = NetworkPreprocessor()
        cls.G = preprocessor.build_undirected_graph(raw_df)

    def test_si_monotonically_non_decreasing(self):
        si = SIModel(beta=0.3, timesteps=50, initial_infected_fraction=0.01)
        res = si.simulate_single_run(self.G, rng=np.random.default_rng(123))

        i_counts = res["I_counts"]
        # Infected count can never decrease in an SI model
        for t in range(len(i_counts) - 1):
            self.assertGreaterEqual(
                i_counts[t + 1],
                i_counts[t],
                f"Infected count decreased at step {t} in SI model!",
            )

    def test_si_initial_conditions(self):
        si = SIModel(beta=0.3, timesteps=50, initial_infected_fraction=0.01)
        res = si.simulate_single_run(self.G, rng=np.random.default_rng(42))

        # 1% of 217 is ~2 nodes
        self.assertEqual(res["I_counts"][0], 2)
        self.assertEqual(res["S_counts"][0], 215)
        self.assertEqual(res["S_counts"][0] + res["I_counts"][0], 217)

    def test_si_monte_carlo(self):
        si = SIModel(beta=0.3, timesteps=30, initial_infected_fraction=0.01)
        mc_res = si.run_monte_carlo(self.G, num_runs=10, base_seed=42)
        self.assertEqual(len(mc_res["I_mean"]), 31)
        self.assertGreater(mc_res["total_infected_mean"], 100)


if __name__ == "__main__":
    unittest.main()
