"""
Network Structural Analysis Module.
Calculates topological, structural, and connectivity metrics on both the complete
network and its largest connected component.
"""

from pathlib import Path
from typing import Dict, Any
import networkx as nx
import numpy as np
import pandas as pd
from scipy import stats

from config.experiment_config import TABLES_DIR


class NetworkAnalyzer:
    """Computes comprehensive graph-theoretic and structural metrics."""

    def __init__(self, tables_dir: Path = None):
        self.tables_dir = Path(tables_dir or TABLES_DIR)
        self.tables_dir.mkdir(parents=True, exist_ok=True)

    def analyze_network(self, G: nx.Graph) -> Dict[str, Any]:
        """
        Computes all primary and secondary topological metrics of graph G.
        
        Parameters
        ----------
        G : nx.Graph
            Input undirected, weighted network.
            
        Returns
        -------
        Dict[str, Any]
            Dictionary of computed structural metrics.
        """
        num_nodes = G.number_of_nodes()
        num_edges = G.number_of_edges()

        # Connected components
        components = list(nx.connected_components(G))
        num_components = len(components)
        largest_comp_nodes = max(components, key=len) if components else set()
        lcc_size = len(largest_comp_nodes)
        
        G_lcc = G.subgraph(largest_comp_nodes).copy() if lcc_size > 0 else nx.Graph()
        lcc_edges = G_lcc.number_of_edges()

        # Path metrics computed on LCC (well-defined on connected graph)
        if lcc_size > 1:
            avg_path_length_unweighted = float(nx.average_shortest_path_length(G_lcc))
            diameter_unweighted = int(nx.diameter(G_lcc))
            # Weighted path metrics using distance (1/w)
            avg_path_length_weighted = float(
                nx.average_shortest_path_length(G_lcc, weight="distance")
            )
        else:
            avg_path_length_unweighted = 0.0
            diameter_unweighted = 0
            avg_path_length_weighted = 0.0

        # Clustering coefficients
        avg_clustering_unweighted = float(nx.average_clustering(G))
        avg_clustering_weighted = float(nx.average_clustering(G, weight="weight"))

        # Density and Assortativity
        density = float(nx.density(G))
        degree_assortativity = float(nx.degree_assortativity_coefficient(G))

        # Degree statistics
        degrees = [d for _, d in G.degree()]
        avg_degree = float(np.mean(degrees))
        std_degree = float(np.std(degrees))
        min_degree = int(np.min(degrees))
        max_degree = int(np.max(degrees))
        median_degree = float(np.median(degrees))
        skew_degree = float(stats.skew(degrees)) if len(degrees) > 2 else 0.0

        # Strength statistics
        strengths = [
            sum(d.get("weight", 1.0) for _, _, d in G.edges(n, data=True))
            for n in G.nodes()
        ]
        avg_strength = float(np.mean(strengths))
        std_strength = float(np.std(strengths))
        min_strength = float(np.min(strengths))
        max_strength = float(np.max(strengths))

        metrics = {
            "num_nodes": num_nodes,
            "num_edges": num_edges,
            "num_connected_components": num_components,
            "lcc_nodes": lcc_size,
            "lcc_edges": lcc_edges,
            "avg_shortest_path_length_unweighted": avg_path_length_unweighted,
            "avg_shortest_path_length_weighted": avg_path_length_weighted,
            "diameter_unweighted": diameter_unweighted,
            "avg_clustering_coefficient_unweighted": avg_clustering_unweighted,
            "avg_clustering_coefficient_weighted": avg_clustering_weighted,
            "network_density": density,
            "average_degree": avg_degree,
            "std_degree": std_degree,
            "min_degree": min_degree,
            "max_degree": max_degree,
            "median_degree": median_degree,
            "degree_skewness": skew_degree,
            "degree_assortativity_coefficient": degree_assortativity,
            "average_strength": avg_strength,
            "std_strength": std_strength,
            "min_strength": min_strength,
            "max_strength": max_strength,
        }
        return metrics

    def save_summary_table(self, metrics: Dict[str, Any], filename: str = "network_summary_statistics.csv") -> Path:
        """Saves metric dictionary as structured summary table."""
        out_path = self.tables_dir / filename
        df = pd.DataFrame([
            {"Metric": k, "Value": v} for k, v in metrics.items()
        ])
        df.to_csv(out_path, index=False)
        return out_path
