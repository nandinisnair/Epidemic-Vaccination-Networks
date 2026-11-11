"""
Vaccination Strategies Module.
Implements Random, Degree, Strength, Betweenness, and Weighted Betweenness
immunization interventions via structural node removal.
"""

from typing import List, Tuple, Dict, Any, Optional
import networkx as nx
import numpy as np


class VaccinationManager:
    """Manages node immunization selection and residual network generation."""

    def __init__(self, G: nx.Graph, centrality_rankings: Optional[Dict[str, List[Tuple[int, float]]]] = None):
        """
        Parameters
        ----------
        G : nx.Graph
            Original pre-intervention friendship network.
        centrality_rankings : Optional[Dict[str, List[Tuple[int, float]]]]
            Pre-computed node rankings for targeted strategies.
        """
        self.original_graph = G.copy()
        self.total_nodes = G.number_of_nodes()
        self.rankings = centrality_rankings or {}

    def get_vaccinated_nodes(
        self,
        strategy: str,
        fraction: float,
        rng: Optional[np.random.Generator] = None,
    ) -> List[int]:
        """
        Selects individuals for vaccination under the specified policy.
        
        Parameters
        ----------
        strategy : str
            One of: 'Random', 'Degree', 'Strength', 'Betweenness', 'Weighted Betweenness'
        fraction : float
            Proportion of total network nodes to vaccinate [0.0, 1.0].
        rng : Optional[np.random.Generator]
            Random number generator for random vaccination.
            
        Returns
        -------
        List[int]
            List of node identifiers selected for vaccination.
        """
        num_vaccinate = int(round(fraction * self.total_nodes))
        if num_vaccinate <= 0:
            return []
        if num_vaccinate >= self.total_nodes:
            return list(self.original_graph.nodes())

        strat_clean = strategy.lower().strip()

        if strat_clean == "random":
            if rng is None:
                rng = np.random.default_rng()
            nodes = list(self.original_graph.nodes())
            return list(rng.choice(nodes, size=num_vaccinate, replace=False))

        # Mapping for targeted rankings
        key_map = {
            "degree": "degree",
            "strength": "strength",
            "betweenness": "betweenness",
            "weighted betweenness": "weighted_betweenness_inverse",
            "weighted_betweenness": "weighted_betweenness_inverse",
            "weighted betweenness (direct)": "weighted_betweenness_direct",
        }

        ranking_key = key_map.get(strat_clean, strat_clean)
        if ranking_key in self.rankings:
            ranked_nodes = [node for node, score in self.rankings[ranking_key]]
            return ranked_nodes[:num_vaccinate]
        else:
            raise ValueError(
                f"Unknown vaccination strategy '{strategy}'. "
                f"Available in rankings: {list(self.rankings.keys())}"
            )

    def apply_vaccination(
        self,
        strategy: str,
        fraction: float,
        rng: Optional[np.random.Generator] = None,
    ) -> Tuple[nx.Graph, List[int], int]:
        """
        Applies vaccination by removing immunized nodes and incident edges.
        
        Returns
        -------
        Tuple[nx.Graph, List[int], int]
            (G_vaccinated, vaccinated_nodes, lcc_size)
        """
        vaccinated_nodes = self.get_vaccinated_nodes(strategy, fraction, rng=rng)
        G_vaccinated = self.original_graph.copy()
        G_vaccinated.remove_nodes_from(vaccinated_nodes)

        # Compute largest connected component size after node removal
        components = list(nx.connected_components(G_vaccinated))
        lcc_size = len(max(components, key=len)) if components else 0

        return G_vaccinated, vaccinated_nodes, lcc_size
