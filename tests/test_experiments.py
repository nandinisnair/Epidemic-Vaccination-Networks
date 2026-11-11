"""
Integration tests for experiment configurations, evaluation statistics, and parameter consistency.
"""

import unittest
from pathlib import Path
import sys
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from config.experiment_config import default_config
from src.evaluation import Evaluator


class TestExperimentPipeline(unittest.TestCase):
    def test_configuration_integrity(self):
        cfg = default_config
        # Primary coverage levels must be 0% to 50% in 10% steps
        expected_cov = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
        self.assertEqual(cfg.vaccination.primary_coverage_levels, expected_cov)
        self.assertEqual(len(cfg.vaccination.strategies), 5)
        self.assertIn("Random", cfg.vaccination.strategies)
        self.assertIn("Degree", cfg.vaccination.strategies)
        self.assertIn("Strength", cfg.vaccination.strategies)
        self.assertIn("Betweenness", cfg.vaccination.strategies)
        self.assertIn("Weighted Betweenness", cfg.vaccination.strategies)

        # Epidemic parameters
        self.assertEqual(cfg.epidemic.si_beta, 0.3)
        self.assertEqual(cfg.epidemic.sir_beta, 0.3)
        self.assertEqual(cfg.epidemic.sir_gamma, 0.1)
        self.assertEqual(cfg.epidemic.si_timesteps, 50)
        self.assertEqual(cfg.epidemic.sir_timesteps, 50)

    def test_evaluator_statistics(self):
        vals = np.array([10.0, 12.0, 14.0, 16.0, 18.0])
        stats = Evaluator.calculate_statistics(vals)
        self.assertEqual(stats["mean"], 14.0)
        self.assertEqual(stats["min"], 10.0)
        self.assertEqual(stats["max"], 18.0)
        self.assertTrue(stats["ci_lower"] < stats["mean"] < stats["ci_upper"])

    def test_summary_compilation(self):
        mock_runs = [
            {"strategy": "Degree", "coverage": 0.1, "run_idx": 0, "ti": 180, "ip": 60, "lcc": 196},
            {"strategy": "Degree", "coverage": 0.1, "run_idx": 1, "ti": 190, "ip": 70, "lcc": 196},
            {"strategy": "Random", "coverage": 0.1, "run_idx": 0, "ti": 200, "ip": 80, "lcc": 210},
            {"strategy": "Random", "coverage": 0.1, "run_idx": 1, "ti": 205, "ip": 85, "lcc": 210},
        ]
        summary_df = Evaluator.compile_experiment_summary(mock_runs)
        self.assertEqual(len(summary_df), 2)
        self.assertIn("TI_mean", summary_df.columns)
        self.assertIn("IP_mean", summary_df.columns)
        self.assertIn("LCC", summary_df.columns)


if __name__ == "__main__":
    unittest.main()
