"""
Experiment Script: SIR Model Simulation.
Simulates baseline Susceptible-Infected-Recovered epidemic progression on the friendship network
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
    print("PHASE 5: SIR MODEL EPIDEMIC SIMULATION")
    print("=" * 70)

    loader = DataLoader()
    raw_edges = loader.load_raw_edges()
    preprocessor = NetworkPreprocessor()
    G = preprocessor.build_undirected_graph(raw_edges)

    runner = SimulationRunner(G, centrality_rankings={})
    si_results = runner.run_baseline_si(num_runs=100)
    sir_results = runner.run_baseline_sir(num_runs=100)

    print(f"SIR Simulation complete (100 runs):")
    print(f"  - Beta: {runner.config.epidemic.sir_beta}")
    print(f"  - Gamma: {runner.config.epidemic.sir_gamma}")
    print(f"  - Mean Peak Infected (IP): {sir_results['peak_mean']:.2f} +/- {sir_results['peak_std']:.2f}")
    print(f"  - Mean Peak Time: step {sir_results['peak_time_mean']:.1f}")
    print(f"  - Mean Total Infected (TI): {sir_results['total_infected_mean']:.2f} +/- {sir_results['total_infected_std']:.2f}")

    viz = NetworkVisualizer()
    p_sir = viz.plot_sir_dynamics(sir_results)
    p_comp = viz.plot_si_vs_sir_comparison(si_results, sir_results)
    print(f"Saved SIR plots:\n  - {p_sir}\n  - {p_comp}\n")
    return sir_results


if __name__ == "__main__":
    main()
