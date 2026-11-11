"""
Unit tests for SIRModel.
"""

import unittest
from pathlib import Path
import sys
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.data_loader import DataLoader
from src.network_preprocessing import NetworkPreprocessor
from src.sir_model import SIRModel


class TestSIRModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        loader = DataLoader()
        raw_df = loader.load_raw_edges()
        preprocessor = NetworkPreprocessor()
        cls.G = preprocessor.build_undirected_graph(raw_df)

    def test_population_conservation(self):
        sir = SIRModel(beta=0.3, gamma=0.1, timesteps=50, initial_infected_fraction=0.01)
        res = sir.simulate_single_run(self.G, rng=np.random.default_rng(99))

        s = res["S_counts"]
        i = res["I_counts"]
        r = res["R_counts"]
        n = self.G.number_of_nodes()

        for t in range(len(s)):
            self.assertEqual(
                s[t] + i[t] + r[t],
                n,
                f"Population conservation violated at timestep {t}: {s[t]} + {i[t]} + {r[t]} != {n}",
            )
            self.assertGreaterEqual(s[t], 0)
            self.assertGreaterEqual(i[t], 0)
            self.assertGreaterEqual(r[t], 0)

    def test_recovered_monotonically_non_decreasing(self):
        sir = SIRModel(beta=0.3, gamma=0.1, timesteps=50, initial_infected_fraction=0.01)
        res = sir.simulate_single_run(self.G, rng=np.random.default_rng(101))
        r = res["R_counts"]
        for t in range(len(r) - 1):
            self.assertGreaterEqual(
                r[t + 1], r[t], f"Recovered count decreased at timestep {t}!"
            )

    def test_metrics_consistency(self):
        sir = SIRModel(beta=0.3, gamma=0.1, timesteps=50, initial_infected_fraction=0.01)
        res = sir.simulate_single_run(self.G, rng=np.random.default_rng(202))

        # Peak must equal maximum value of I_counts
        self.assertEqual(res["infection_peak"], int(np.max(res["I_counts"])))
        # Total infected must equal 217 - final susceptible
        final_s = res["S_counts"][-1]
        self.assertEqual(res["total_infected"], 217 - final_s)


if __name__ == "__main__":
    unittest.main()
