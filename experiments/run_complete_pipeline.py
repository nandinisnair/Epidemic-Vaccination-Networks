"""
Main Entry-Point Pipeline Script.
Executes the entire research workflow from dataset loading to multi-strategy
vaccination simulation, evaluation, table generation, and plotting.
"""

import sys
import time
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.data_loader import DataLoader
from src.network_preprocessing import NetworkPreprocessor
from src.network_analysis import NetworkAnalyzer
from src.centrality_analysis import CentralityAnalyzer
from src.simulation_runner import SimulationRunner
from src.visualization import NetworkVisualizer
from config.experiment_config import default_config


def run_pipeline():
    start_time = time.time()
    print("=" * 75)
    print("RESEARCH PIPELINE: NETWORK EPIDEMIC SIMULATION & VACCINATION EVALUATION")
    print("FACTS-H Lab, Indian Institute of Information Technology Kottayam")
    print("=" * 75)

    # 1. Dataset Loading & Preprocessing
    print("\n[Step 1/6] Loading and Preprocessing KONECT moreno_oz Dataset...")
    loader = DataLoader(default_config.dataset)
    raw_edges = loader.load_raw_edges()
    preprocessor = NetworkPreprocessor(default_config.dataset)
    G = preprocessor.build_undirected_graph(raw_edges)
    edge_file, graph_file = preprocessor.export_processed_data(G)
    G_lcc, num_comp, lcc_size = preprocessor.get_largest_connected_component(G)
    print(f"Network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges, {num_comp} component(s), LCC={lcc_size} nodes.")

    # 2. Structural Analysis
    print("\n[Step 2/6] Performing Network Structural Analysis...")
    analyzer = NetworkAnalyzer()
    metrics = analyzer.analyze_network(G)
    summary_path = analyzer.save_summary_table(metrics)
    print(f"Saved structural metrics to {summary_path}")

    # 3. Centrality Computations
    print("\n[Step 3/6] Computing Centrality Measures & Top Influential Rankings...")
    cent_analyzer = CentralityAnalyzer(default_config.centrality)
    centralities = cent_analyzer.compute_all_centralities(G)
    rankings = cent_analyzer.get_rankings(centralities)
    saved_ranks = cent_analyzer.export_rankings(centralities)
    print(f"Saved rankings to {saved_ranks['all']}")

    # 4. Visualizations: Topology, Distribution & Centrality
    print("\n[Step 4/6] Generating Structural and Centrality Visualizations...")
    viz = NetworkVisualizer()
    viz.plot_network(G)
    viz.plot_largest_component(G_lcc)
    viz.plot_degree_distribution(G)
    master_cent_df = analyzer.tables_dir.parent / "centrality_rankings" / "all_centrality_measures.csv"
    viz.plot_centrality_comparisons(pd.read_csv(master_cent_df))

    # 5. Baseline SI & SIR Epidemic Simulations
    print("\n[Step 5/6] Simulating Baseline SI and SIR Epidemic Dynamics (100 runs each)...")
    runner = SimulationRunner(G, rankings, config=default_config)
    si_res = runner.run_baseline_si(num_runs=100)
    sir_res = runner.run_baseline_sir(num_runs=100)
    viz.plot_si_dynamics(si_res)
    viz.plot_sir_dynamics(sir_res)
    viz.plot_si_vs_sir_comparison(si_res, sir_res)

    # 6. Vaccination Suites (Primary 10% schedule & Exploratory 5% schedule)
    print("\n[Step 6/6] Executing Vaccination Strategy Experiments (100 runs per condition)...")
    primary_summary = runner.run_vaccination_suite(
        coverage_levels=default_config.vaccination.primary_coverage_levels,
        num_runs=100,
        suite_name="primary",
    )
    exploratory_summary = runner.run_vaccination_suite(
        coverage_levels=default_config.vaccination.exploratory_coverage_levels,
        num_runs=100,
        suite_name="exploratory",
    )

    # Visualizations for vaccination
    viz.plot_individual_vaccination_metrics(primary_summary)
    viz.plot_ieee_multipanel_comparison(primary_summary, "11_ieee_multipanel_comparison.png")
    viz.plot_ieee_multipanel_comparison(exploratory_summary, "11b_ieee_multipanel_exploratory_5pct.png")
    viz.plot_comparative_barchart(primary_summary)

    elapsed = time.time() - start_time
    print("\n" + "=" * 75)
    print(f"COMPLETE PIPELINE EXECUTION SUCCESSFUL! Elapsed Time: {elapsed:.2f} seconds.")
    print("=" * 75)


if __name__ == "__main__":
    run_pipeline()
