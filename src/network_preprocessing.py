"""
Network Preprocessing Module.
Transforms raw edge interactions into an undirected, weighted NetworkX graph,
handles reciprocity and self-loops, and prepares the largest connected component.
"""

from pathlib import Path
from typing import Tuple, Dict, Any
import networkx as nx
import pandas as pd

from config.experiment_config import DatasetConfig, PROCESSED_DATA_DIR


class NetworkPreprocessor:
    """Preprocesses raw edge streams into analyzed graph structures."""

    def __init__(self, config: DatasetConfig = None):
        self.config = config or DatasetConfig()
        self.processed_dir = Path(PROCESSED_DATA_DIR)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def build_undirected_graph(self, raw_edges_df: pd.DataFrame) -> nx.Graph:
        """
        Constructs an undirected weighted network from raw directed interactions.
        
        Parameters
        ----------
        raw_edges_df : pd.DataFrame
            DataFrame with columns ['source', 'target', 'weight']
            
        Returns
        -------
        nx.Graph
            Undirected graph with edge attributes:
            - 'weight': original friendship intensity
            - 'distance': transformed path length (1.0 / weight)
        """
        mode = self.config.reciprocal_weight_mode.lower()
        
        # Identify all unique nodes across source and target
        unique_nodes = sorted(
            list(set(raw_edges_df["source"]).union(set(raw_edges_df["target"])))
        )
        
        G = nx.Graph()
        G.add_nodes_from(unique_nodes)

        # Handle reciprocal edges
        if mode == "last":
            # Direct replication of the research notebook sequential insertion
            for _, row in raw_edges_df.iterrows():
                u, v, w = int(row["source"]), int(row["target"]), float(row["weight"])
                if self.config.remove_self_loops and u == v:
                    continue
                G.add_edge(u, v, weight=w)
        elif mode in ("max", "min", "mean", "sum"):
            # Aggregate symmetric ties
            edge_weights: Dict[Tuple[int, int], list] = {}
            for _, row in raw_edges_df.iterrows():
                u, v, w = int(row["source"]), int(row["target"]), float(row["weight"])
                if self.config.remove_self_loops and u == v:
                    continue
                pair = tuple(sorted((u, v)))
                if pair not in edge_weights:
                    edge_weights[pair] = []
                edge_weights[pair].append(w)

            for (u, v), w_list in edge_weights.items():
                if mode == "max":
                    agg_w = max(w_list)
                elif mode == "min":
                    agg_w = min(w_list)
                elif mode == "mean":
                    agg_w = sum(w_list) / len(w_list)
                else:  # sum
                    agg_w = sum(w_list)
                G.add_edge(u, v, weight=agg_w)
        else:
            raise ValueError(f"Unsupported reciprocal_weight_mode: '{mode}'")

        # Assign distance attribute for weighted shortest path computations
        for u, v, d in G.edges(data=True):
            w = d.get("weight", 1.0)
            # Distance inversely proportional to friendship intensity:
            # Stronger connection -> shorter social distance
            d["distance"] = 1.0 / w if w > 0 else 1.0

        return G

    def get_largest_connected_component(self, G: nx.Graph) -> Tuple[nx.Graph, int, int]:
        """
        Identifies and extracts the largest connected component of graph G.
        
        Returns
        -------
        Tuple[nx.Graph, int, int]
            (Sub-graph of LCC, number of components, total nodes in LCC)
        """
        components = list(nx.connected_components(G))
        num_components = len(components)
        if not components:
            return G.copy(), 0, 0
        largest_set = max(components, key=len)
        G_lcc = G.subgraph(largest_set).copy()
        return G_lcc, num_components, len(largest_set)

    def export_processed_data(self, G: nx.Graph) -> Tuple[Path, Path]:
        """Exports processed graph edges to CSV and GraphML for reproducibility."""
        edge_records = []
        for u, v, d in G.edges(data=True):
            edge_records.append({
                "source": u,
                "target": v,
                "weight": d["weight"],
                "distance": d["distance"],
            })
        edges_df = pd.DataFrame(edge_records)
        edge_file = Path(self.config.processed_edge_file)
        edges_df.to_csv(edge_file, index=False)

        graph_file = Path(self.config.processed_graph_file)
        nx.write_graphml(G, str(graph_file))
        return edge_file, graph_file
