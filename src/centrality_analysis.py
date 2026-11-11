"""
Centrality Analysis Module.
Computes Degree, Strength, Betweenness, and Weighted Betweenness centralities,
generates rankings, compares top-k influential individuals, and exports structured CSVs.
"""

from pathlib import Path
from typing import Dict, List, Tuple
import networkx as nx
import pandas as pd

from config.experiment_config import CENTRALITY_DIR, TABLES_DIR, CentralityConfig


class CentralityAnalyzer:
    """Computes and ranks network nodes across unweighted and weighted centrality indices."""

    def __init__(self, config: CentralityConfig = None, out_dir: Path = None):
        self.config = config or CentralityConfig()
        self.out_dir = Path(out_dir or CENTRALITY_DIR)
        self.tables_dir = Path(TABLES_DIR)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.tables_dir.mkdir(parents=True, exist_ok=True)

    def compute_all_centralities(self, G: nx.Graph) -> Dict[str, Dict[int, float]]:
        """
        Computes all four primary centrality measures:
        1. Degree Centrality: C_D(v) = deg(v) / (N - 1)
        2. Strength Centrality: S(v) = sum_{u in N(v)} w_{vu}
        3. Betweenness Centrality: C_B(v) = sum_{s != v != t} (sigma_{st}(v) / sigma_{st})
        4. Weighted Betweenness Centrality:
           - inverse distance: shortest paths minimized by d_e = 1 / w_e
           - direct weight: shortest paths evaluated with d_e = w_e (historical comparison)
        """
        # 1. Degree Centrality (normalized by N-1)
        deg_centrality = nx.degree_centrality(G)

        # 2. Strength Centrality (unnormalized cumulative edge weight)
        strength_centrality = {
            node: float(sum(d.get("weight", 1.0) for _, _, d in G.edges(node, data=True)))
            for node in G.nodes()
        }

        # 3. Unweighted Betweenness Centrality
        bet_centrality = nx.betweenness_centrality(G, weight=None, normalized=True)

        # 4. Weighted Betweenness Centrality with inverse distance
        # Ensuring each edge has 'distance' = 1.0 / weight
        for _, _, d in G.edges(data=True):
            w = d.get("weight", 1.0)
            d["distance"] = 1.0 / w if w > 0 else 1.0

        weighted_bet_inv = nx.betweenness_centrality(
            G, weight="distance", normalized=True
        )

        # Direct weight betweenness (historical notebook reference)
        weighted_bet_direct = nx.betweenness_centrality(
            G, weight="weight", normalized=True
        )

        return {
            "degree": deg_centrality,
            "strength": strength_centrality,
            "betweenness": bet_centrality,
            "weighted_betweenness_inverse": weighted_bet_inv,
            "weighted_betweenness_direct": weighted_bet_direct,
        }

    def get_rankings(
        self, centralities: Dict[str, Dict[int, float]]
    ) -> Dict[str, List[Tuple[int, float]]]:
        """Returns sorted lists of (node, score) tuples in descending order."""
        rankings = {}
        for metric_name, scores in centralities.items():
            rankings[metric_name] = sorted(
                scores.items(), key=lambda item: item[1], reverse=True
            )
        return rankings

    def export_rankings(
        self, centralities: Dict[str, Dict[int, float]]
    ) -> Dict[str, Path]:
        """Saves individual and consolidated centrality rankings to CSV files."""
        saved_paths = {}
        rankings = self.get_rankings(centralities)

        # Individual files
        for metric_name, ranked_list in rankings.items():
            df = pd.DataFrame(ranked_list, columns=["node_id", "score"])
            df["rank"] = range(1, len(df) + 1)
            file_path = self.out_dir / f"{metric_name}_centrality_ranking.csv"
            df[["rank", "node_id", "score"]].to_csv(file_path, index=False)
            saved_paths[metric_name] = file_path

        # Consolidated table
        all_nodes = sorted(list(centralities["degree"].keys()))
        master_df = pd.DataFrame({"node_id": all_nodes})
        for metric_name, scores in centralities.items():
            master_df[metric_name] = master_df["node_id"].map(scores)
        master_file = self.out_dir / "all_centrality_measures.csv"
        master_df.to_csv(master_file, index=False)
        saved_paths["all"] = master_file

        # Top 10 Influential Nodes Table
        top_k = self.config.top_k_nodes
        top_records = []
        for rank_idx in range(top_k):
            row = {"Rank": rank_idx + 1}
            for metric in [
                "degree",
                "strength",
                "betweenness",
                "weighted_betweenness_inverse",
                "weighted_betweenness_direct",
            ]:
                node_id, val = rankings[metric][rank_idx]
                row[f"{metric}_node"] = node_id
                row[f"{metric}_score"] = round(val, 4)
            top_records.append(row)

        top_df = pd.DataFrame(top_records)
        top_file = self.tables_dir / f"top_{top_k}_influential_nodes.csv"
        top_df.to_csv(top_file, index=False)
        saved_paths["top_k"] = top_file

        return saved_paths
