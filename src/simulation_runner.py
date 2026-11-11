"""
Simulation Runner Module.
Coordinates Monte Carlo execution across baseline epidemic dynamics (SI, SIR)
and multi-strategy vaccination experiments.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
import networkx as nx
import numpy as np
import pandas as pd

from config.experiment_config import (
    ExperimentConfig,
    SIMULATION_DIR,
    TABLES_DIR,
    default_config,
)
from src.si_model import SIModel
from src.sir_model import SIRModel
from src.vaccination import VaccinationManager
from src.evaluation import Evaluator


class SimulationRunner:
    """Orchestrates comprehensive epidemic and vaccination simulation suites."""

    def __init__(
        self,
        G: nx.Graph,
        centrality_rankings: Dict[str, List[tuple]],
        config: ExperimentConfig = None,
    ):
        self.G = G
        self.config = config or default_config
        self.centrality_rankings = centrality_rankings
        self.vacc_mgr = VaccinationManager(G, centrality_rankings)
        self.sim_dir = Path(SIMULATION_DIR)
        self.tables_dir = Path(TABLES_DIR)
        self.sim_dir.mkdir(parents=True, exist_ok=True)
        self.tables_dir.mkdir(parents=True, exist_ok=True)

    def run_baseline_si(self, num_runs: Optional[int] = None) -> Dict[str, Any]:
        """Runs baseline SI simulations on the unimmunized network."""
        n_runs = num_runs or self.config.vaccination.num_runs
        si = SIModel(
            beta=self.config.epidemic.si_beta,
            timesteps=self.config.epidemic.si_timesteps,
            initial_infected_fraction=self.config.epidemic.si_initial_infected_fraction,
            transmission_mode=self.config.epidemic.transmission_mode,
        )
        results = si.run_monte_carlo(
            self.G, num_runs=n_runs, base_seed=self.config.vaccination.base_seed
        )

        # Save trajectory to CSV
        traj_df = pd.DataFrame({
            "timestep": results["timesteps"],
            "S_mean": results["S_mean"],
            "S_std": results["S_std"],
            "I_mean": results["I_mean"],
            "I_std": results["I_std"],
        })
        traj_file = self.sim_dir / "si_baseline_progression.csv"
        traj_df.to_csv(traj_file, index=False)
        return results

    def run_baseline_sir(self, num_runs: Optional[int] = None) -> Dict[str, Any]:
        """Runs baseline SIR simulations on the unimmunized network."""
        n_runs = num_runs or self.config.vaccination.num_runs
        sir = SIRModel(
            beta=self.config.epidemic.sir_beta,
            gamma=self.config.epidemic.sir_gamma,
            timesteps=self.config.epidemic.sir_timesteps,
            initial_infected_fraction=self.config.epidemic.sir_initial_infected_fraction,
            transmission_mode=self.config.epidemic.transmission_mode,
        )
        results = sir.run_monte_carlo(
            self.G, num_runs=n_runs, base_seed=self.config.vaccination.base_seed
        )

        traj_df = pd.DataFrame({
            "timestep": results["timesteps"],
            "S_mean": results["S_mean"],
            "S_std": results["S_std"],
            "I_mean": results["I_mean"],
            "I_std": results["I_std"],
            "R_mean": results["R_mean"],
            "R_std": results["R_std"],
        })
        traj_file = self.sim_dir / "sir_baseline_progression.csv"
        traj_df.to_csv(traj_file, index=False)
        return results

    def run_vaccination_suite(
        self,
        coverage_levels: Optional[List[float]] = None,
        num_runs: Optional[int] = None,
        suite_name: str = "primary",
    ) -> pd.DataFrame:
        """
        Executes complete multi-strategy vaccination comparison.
        
        Parameters
        ----------
        coverage_levels : Optional[List[float]]
            Fractions of nodes to vaccinate. Defaults to primary (0% to 50% in 10% steps).
        num_runs : Optional[int]
            Independent repetitions per condition (default 100).
        suite_name : str
            Label for output files ('primary' or 'exploratory').
            
        Returns
        -------
        pd.DataFrame
            Aggregated summary table across strategies and coverage levels.
        """
        cov_levels = (
            coverage_levels
            if coverage_levels is not None
            else self.config.vaccination.primary_coverage_levels
        )
        n_runs = num_runs or self.config.vaccination.num_runs
        strategies = self.config.vaccination.strategies
        base_seed = self.config.vaccination.base_seed

        sir = SIRModel(
            beta=self.config.epidemic.sir_beta,
            gamma=self.config.epidemic.sir_gamma,
            timesteps=self.config.epidemic.sir_timesteps,
            initial_infected_fraction=self.config.epidemic.sir_initial_infected_fraction,
            transmission_mode=self.config.epidemic.transmission_mode,
        )

        detailed_records = []
        total_conditions = len(strategies) * len(cov_levels)
        cond_idx = 0

        print(
            f"[SimulationRunner] Starting {suite_name} vaccination suite: "
            f"{len(strategies)} strategies, {len(cov_levels)} coverages, "
            f"{n_runs} runs per condition ({total_conditions * n_runs} simulations total)."
        )

        for strat in strategies:
            for cov in cov_levels:
                cond_idx += 1
                for r in range(n_runs):
                    run_seed = base_seed + 1000 * cond_idx + r
                    rng = np.random.default_rng(run_seed)

                    # Apply vaccination
                    G_vacc, vacc_nodes, lcc_size = self.vacc_mgr.apply_vaccination(
                        strategy=strat, fraction=cov, rng=rng
                    )

                    # Simulate SIR
                    sim_res = sir.simulate_single_run(G_vacc, rng=rng)

                    detailed_records.append({
                        "suite": suite_name,
                        "strategy": strat,
                        "coverage": cov,
                        "run_idx": r,
                        "seed": run_seed,
                        "vaccinated_count": len(vacc_nodes),
                        "lcc": lcc_size,
                        "ti": sim_res["total_infected"],
                        "ip": sim_res["infection_peak"],
                        "peak_time": sim_res["peak_time"],
                    })

        # Save per-run micro-data
        raw_df = pd.DataFrame(detailed_records)
        raw_csv_path = self.sim_dir / f"vaccination_{suite_name}_raw_runs.csv"
        raw_df.to_csv(raw_csv_path, index=False)

        # Aggregate summary table
        summary_df = Evaluator.compile_experiment_summary(detailed_records)
        summary_csv_path = self.tables_dir / f"vaccination_{suite_name}_summary.csv"
        summary_df.to_csv(summary_csv_path, index=False)

        print(f"[SimulationRunner] Saved raw data to {raw_csv_path}")
        print(f"[SimulationRunner] Saved summary table to {summary_csv_path}")
        return summary_df
