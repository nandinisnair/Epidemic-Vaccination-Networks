"""
Validation suite for core scientific requirements:
1. Weighted betweenness and shortest-path distance transformation.
2. 100 independent stochastic runs with verifiable empirical variance.
3. Node removal vaccination and complete immunity guarantee.
4. Separation of SI and SIR models and exact state transition validity.
5. Research accuracy and authentic empirical computation (no fabrication).
"""

import unittest
from pathlib import Path
import sys
import networkx as nx
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.data_loader import DataLoader
from src.network_preprocessing import NetworkPreprocessor
from src.centrality_analysis import CentralityAnalyzer
from src.si_model import SIModel
from src.sir_model import SIRModel
from src.vaccination import VaccinationManager
from src.simulation_runner import SimulationRunner


class TestResearchGuarantees(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        loader = DataLoader()
        raw_df = loader.load_raw_edges()
        preprocessor = NetworkPreprocessor()
        cls.G = preprocessor.build_undirected_graph(raw_df)
        cls.analyzer = CentralityAnalyzer()
        cls.centralities = cls.analyzer.compute_all_centralities(cls.G)
        cls.rankings = cls.analyzer.get_rankings(cls.centralities)

    def test_requirement_1_weighted_betweenness_distance_transformation(self):
        """
        Friendship intensity must not be treated as physical distance.
        Stronger ties (w=5) must have shorter distances (d=0.2),
        meaning shortest-path algorithms prioritize high-intensity ties.
        """
        for u, v, d in self.G.edges(data=True):
            w = d["weight"]
            expected_dist = 1.0 / w
            self.assertAlmostEqual(
                d["distance"],
                expected_dist,
                places=5,
                msg=f"Edge ({u}, {v}) has weight {w} but distance {d['distance']} != {expected_dist}",
            )

        # Verify on a 3-node path: A - B (w=5) vs A - C - B (w=1 each)
        test_G = nx.Graph()
        test_G.add_edge("A", "B", weight=1.0, distance=1.0 / 1.0)  # Weak direct tie: dist = 1.0
        test_G.add_edge("A", "C", weight=5.0, distance=1.0 / 5.0)  # Strong tie: dist = 0.2
        test_G.add_edge("C", "B", weight=5.0, distance=1.0 / 5.0)  # Strong tie: dist = 0.2
        # Path A-C-B total distance = 0.2 + 0.2 = 0.4 < 1.0
        shortest_path = nx.shortest_path(test_G, source="A", target="B", weight="distance")
        self.assertEqual(shortest_path, ["A", "C", "B"])

        # Compare inverse vs direct weighted betweenness on Moreno OZ
        wb_inv = self.centralities["weighted_betweenness_inverse"]
        wb_dir = self.centralities["weighted_betweenness_direct"]
        # The rankings must NOT be identical because distance inversion reverses edge priorities
        top_inv_nodes = [n for n, _ in self.rankings["weighted_betweenness_inverse"][:10]]
        top_dir_nodes = [n for n, _ in self.rankings["weighted_betweenness_direct"][:10]]
        self.assertNotEqual(
            top_inv_nodes,
            top_dir_nodes,
            "Inverse distance and direct weight must yield distinct centrality rankings.",
        )

    def test_requirement_2_100_independent_runs_stochasticity(self):
        """
        Simulations must execute genuinely independent stochastic realizations
        with non-zero variance across runs, not static repeated outputs.
        """
        sir = SIRModel(beta=0.3, gamma=0.1, timesteps=50, initial_infected_fraction=0.01)
        mc_results = sir.run_monte_carlo(self.G, num_runs=100, base_seed=42)

        peak_runs = mc_results["infection_peaks"]
        ti_runs = mc_results["total_infected_runs"]

        self.assertEqual(len(peak_runs), 100)
        self.assertEqual(len(ti_runs), 100)

        # Standard deviation must be strictly positive (stochastic variance)
        self.assertGreater(
            np.std(peak_runs),
            0.5,
            "100 runs must exhibit genuine stochastic variation in infection peaks.",
        )
        self.assertGreater(
            len(set(peak_runs)),
            5,
            "There must be multiple distinct peak infection values across 100 runs.",
        )

    def test_requirement_3_vaccination_node_removal_and_immunity(self):
        """
        Vaccinated nodes must be removed from the network and must never
        become infected or recovered. Original network must remain intact.
        """
        vacc_mgr = VaccinationManager(self.G, self.rankings)
        original_nodes_count = self.G.number_of_nodes()
        original_edges_count = self.G.number_of_edges()

        fraction = 0.30
        G_vacc, vacc_nodes, lcc = vacc_mgr.apply_vaccination("Degree", fraction)
        num_vacc = len(vacc_nodes)
        self.assertEqual(num_vacc, int(round(fraction * original_nodes_count)))

        # 1. Vaccinated nodes must NOT be present in G_vacc
        for v in vacc_nodes:
            self.assertNotIn(v, G_vacc.nodes)

        # 2. Residual graph size must equal N - num_vacc
        self.assertEqual(G_vacc.number_of_nodes(), original_nodes_count - num_vacc)

        # 3. Simulate SIR on G_vacc and verify no vaccinated node is ever touched
        sir = SIRModel(beta=0.3, gamma=0.1, timesteps=50, initial_infected_fraction=0.01)
        for seed in [1, 2, 3, 4, 5]:
            rng = np.random.default_rng(seed)
            res = sir.simulate_single_run(G_vacc, rng=rng)
            # Total infected can never exceed residual graph size
            self.assertLessEqual(res["total_infected"], G_vacc.number_of_nodes())
            self.assertLessEqual(res["infection_peak"], G_vacc.number_of_nodes())

        # 4. Original graph remains completely unaltered
        self.assertEqual(self.G.number_of_nodes(), original_nodes_count)
        self.assertEqual(self.G.number_of_edges(), original_edges_count)

    def test_requirement_4_si_and_sir_strict_separation_and_transitions(self):
        """
        SI and SIR models must remain strictly distinct compartmental models:
        - SI: only S -> I; I is monotonic non-decreasing; S + I = N.
        - SIR: S -> I -> R; R is monotonic non-decreasing; S + I + R = N; R is absorbing.
        """
        # Test SI Model
        si = SIModel(beta=0.3, timesteps=50, initial_infected_fraction=0.01)
        si_res = si.simulate_single_run(self.G, rng=np.random.default_rng(1234))

        self.assertNotIn("R_counts", si_res, "SI model must NOT contain Recovered state.")
        s_si = si_res["S_counts"]
        i_si = si_res["I_counts"]

        for t in range(len(i_si) - 1):
            # Monotonicity of infection in SI
            self.assertGreaterEqual(
                i_si[t + 1], i_si[t], f"SI infected count decreased at timestep {t}!"
            )
            # Monotonicity of susceptibility in SI
            self.assertLessEqual(
                s_si[t + 1], s_si[t], f"SI susceptible count increased at timestep {t}!"
            )
            # Population conservation in SI
            self.assertEqual(s_si[t] + i_si[t], 217)

        # Test SIR Model
        sir = SIRModel(beta=0.3, gamma=0.1, timesteps=50, initial_infected_fraction=0.01)
        sir_res = sir.simulate_single_run(self.G, rng=np.random.default_rng(5678))

        s_sir = sir_res["S_counts"]
        i_sir = sir_res["I_counts"]
        r_sir = sir_res["R_counts"]

        for t in range(len(r_sir) - 1):
            # Monotonicity of recovery (R is an absorbing state)
            self.assertGreaterEqual(
                r_sir[t + 1], r_sir[t], f"SIR recovered count decreased at timestep {t}!"
            )
            # Population conservation
            self.assertEqual(
                s_sir[t] + i_sir[t] + r_sir[t],
                217,
                f"SIR conservation violated at timestep {t}!",
            )

    def test_requirement_5_research_accuracy_no_fabrication(self):
        """
        Verify that summary CSV metrics are exactly computed from raw simulation outputs,
        and not fabricated or artificially forced.
        """
        raw_path = BASE_DIR / "results" / "simulation_outputs" / "vaccination_primary_raw_runs.csv"
        summary_path = BASE_DIR / "results" / "tables" / "vaccination_primary_summary.csv"

        self.assertTrue(raw_path.exists(), "Raw simulation runs file must exist.")
        self.assertTrue(summary_path.exists(), "Summary table file must exist.")

        raw_df = pd.read_csv(raw_path)
        summary_df = pd.read_csv(summary_path)

        # Verify that for every strategy and coverage, summary mean matches raw mean
        for _, row in summary_df.iterrows():
            strat = row["strategy"]
            cov = row["coverage"]
            subset = raw_df[(raw_df["strategy"] == strat) & (raw_df["coverage"] == cov)]
            self.assertEqual(len(subset), 100, f"Expected 100 runs for {strat} at {cov}.")

            computed_ti_mean = subset["ti"].mean()
            computed_ip_mean = subset["ip"].mean()

            self.assertAlmostEqual(
                computed_ti_mean,
                row["TI_mean"],
                places=1,
                msg=f"Discrepancy in TI_mean for {strat} at {cov}: {computed_ti_mean} vs {row['TI_mean']}",
            )
            self.assertAlmostEqual(
                computed_ip_mean,
                row["IP_mean"],
                places=1,
                msg=f"Discrepancy in IP_mean for {strat} at {cov}: {computed_ip_mean} vs {row['IP_mean']}",
            )


if __name__ == "__main__":
    unittest.main()
