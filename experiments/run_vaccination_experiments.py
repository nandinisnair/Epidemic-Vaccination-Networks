"""
Experiment Script: Vaccination Strategies Evaluation.
Computes centrality metrics, executes 100 Monte Carlo runs per strategy and coverage,
evaluates TI, IP, and LCC, and generates publication plots and summary tables.
"""

import sys
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.data_loader import DataLoader
from src.network_preprocessing import NetworkPreprocessor
from src.centrality_analysis import CentralityAnalyzer
from src.simulation_runner import SimulationRunner
from src.visualization import NetworkVisualizer
from config.experiment_config import default_config


def main():
    print("=" * 70)
    print("PHASES 3, 6, 7, 8, 9: CENTRALITY & VACCINATION EXPERIMENTS")
    print("=" * 70)

    # 1. Load network
    loader = DataLoader()
    raw_edges = loader.load_raw_edges()
    preprocessor = NetworkPreprocessor()
    G = preprocessor.build_undirected_graph(raw_edges)

    # 2. Centrality analysis
    cent_analyzer = CentralityAnalyzer()
    centralities = cent_analyzer.compute_all_centralities(G)
    rankings = cent_analyzer.get_rankings(centralities)
    saved_centrality_paths = cent_analyzer.export_rankings(centralities)

    print("Computed Centrality Measures. Saved rankings:")
    for k, p in saved_centrality_paths.items():
        print(f"  - {k}: {p}")

    # Plot centralities comparison
    master_cent_df = pd.read_csv(saved_centrality_paths["all"])
    viz = NetworkVisualizer()
    p_cent = viz.plot_centrality_comparisons(master_cent_df)
    print(f"Saved centrality comparison plot to: {p_cent}")

    # Display Top 10 nodes table
    top_10_df = pd.read_csv(saved_centrality_paths["top_k"])
    print("\nTop 10 Influential Nodes Table:")
    print(top_10_df.to_string(index=False))

    # 3. Primary Vaccination Experiment (0% to 50% in 10% steps, 100 runs)
    runner = SimulationRunner(G, rankings, config=default_config)
    print("\nExecuting Primary Published IEEE Experiment Suite (0%-50% in 10% steps)...")
    primary_summary_df = runner.run_vaccination_suite(
        coverage_levels=default_config.vaccination.primary_coverage_levels,
        num_runs=100,
        suite_name="primary",
    )

    # 4. Exploratory Vaccination Experiment (0% to 50% in 5% steps, 100 runs)
    print("\nExecuting Exploratory Fine-Grained Experiment Suite (0%-50% in 5% steps)...")
    exploratory_summary_df = runner.run_vaccination_suite(
        coverage_levels=default_config.vaccination.exploratory_coverage_levels,
        num_runs=100,
        suite_name="exploratory",
    )

    # 5. Visualizations
    print("\nGenerating Vaccination Evaluation Figures...")
    ind_paths = viz.plot_individual_vaccination_metrics(primary_summary_df)
    multi_path = viz.plot_ieee_multipanel_comparison(primary_summary_df)
    bar_path = viz.plot_comparative_barchart(primary_summary_df)

    print(f"Generated Plots:\n  - TI: {ind_paths['ti']}\n  - IP: {ind_paths['ip']}\n  - LCC: {ind_paths['lcc']}")
    print(f"  - IEEE Multi-panel: {multi_path}\n  - Bar Chart: {bar_path}")

    # Also plot the exploratory fine-grained multi-panel
    viz.plot_ieee_multipanel_comparison(
        exploratory_summary_df, filename="11b_ieee_multipanel_exploratory_5pct.png"
    )

    print("\nVaccination Experiments Complete!\n")
    return primary_summary_df, exploratory_summary_df


if __name__ == "__main__":
    main()
