"""
Experiment Script: Network Structural Analysis.
Loads the KONECT moreno_oz dataset, builds the undirected weighted graph,
extracts the largest connected component, computes all metrics, and produces visualizations.
"""

import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.data_loader import DataLoader
from src.network_preprocessing import NetworkPreprocessor
from src.network_analysis import NetworkAnalyzer
from src.visualization import NetworkVisualizer


def main():
    print("=" * 70)
    print("PHASE 1 & 2: DATASET LOADING AND NETWORK STRUCTURAL ANALYSIS")
    print("=" * 70)

    # 1. Load raw data
    loader = DataLoader()
    raw_edges = loader.load_raw_edges()
    print(f"Loaded {len(raw_edges)} raw edge records.")

    # 2. Preprocess into undirected graph
    preprocessor = NetworkPreprocessor()
    G = preprocessor.build_undirected_graph(raw_edges)
    edge_file, graph_file = preprocessor.export_processed_data(G)
    print(f"Constructed undirected graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges.")
    print(f"Saved processed graph to {graph_file} and edges to {edge_file}")

    # 3. Extract Largest Connected Component
    G_lcc, num_comp, lcc_size = preprocessor.get_largest_connected_component(G)
    print(f"Identified {num_comp} connected component(s). LCC size: {lcc_size} nodes.")

    # 4. Structural analysis
    analyzer = NetworkAnalyzer()
    metrics = analyzer.analyze_network(G)
    table_path = analyzer.save_summary_table(metrics)
    print(f"Structural Metrics Summary saved to {table_path}:")
    for k, v in metrics.items():
        if isinstance(v, float):
            print(f"  - {k}: {v:.4f}")
        else:
            print(f"  - {k}: {v}")

    # 5. Visualizations
    viz = NetworkVisualizer()
    p1 = viz.plot_network(G)
    p2 = viz.plot_largest_component(G_lcc)
    p3a, p3b = viz.plot_degree_distribution(G)

    print(f"Generated network visualizations:\n  - {p1}\n  - {p2}\n  - {p3a}\n  - {p3b}")
    print("Network Structural Analysis Complete!\n")
    return G, metrics


if __name__ == "__main__":
    main()
