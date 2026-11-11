"""
Experiment Script: SI Model Simulation.
Simulates baseline Susceptible-Infected epidemic progression on the friendship network
across 100 independent Monte Carlo realizations.
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.data_loader import DataLoader
from src.network_preprocessing import NetworkPreprocessor
from src.simulation_runner import SimulationRunner
from src.visualization import NetworkVisualizer


def main():
    print("=" * 70)
    print("PHASE 4: SI MODEL EPIDEMIC SIMULATION")
    print("=" * 70)

    loader = DataLoader()
    raw_edges = loader.load_raw_edges()
    preprocessor = NetworkPreprocessor()
    G = preprocessor.build_undirected_graph(raw_edges)

    runner = SimulationRunner(G, centrality_rankings={})
    si_results = runner.run_baseline_si(num_runs=100)

    print(f"SI Simulation complete (100 runs):")
    print(f"  - Initial Infected: 1% (~2 nodes)")
    print(f"  - Beta: {runner.config.epidemic.si_beta}")
    print(f"  - Mean Total Infected at t=50: {si_results['total_infected_mean']:.2f} +/- {si_results['total_infected_std']:.2f}")

    viz = NetworkVisualizer()
    p_si = viz.plot_si_dynamics(si_results)
    print(f"Saved SI plot to: {p_si}\n")
    return si_results


if __name__ == "__main__":
    main()
