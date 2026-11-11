"""
Susceptible-Infected (SI) Epidemic Model Module.
Implements stochastic transmission over network contact topologies.
"""

from typing import Dict, List, Optional, Any
import networkx as nx
import numpy as np


class SIModel:
    """Simulates the SI compartmental epidemic process on an undirected network."""

    def __init__(
        self,
        beta: float = 0.3,
        timesteps: int = 50,
        initial_infected_fraction: float = 0.01,
        transmission_mode: str = "independent",
    ):
        """
        Parameters
        ----------
        beta : float
            Infection transmission probability / rate.
        timesteps : int
            Number of discrete simulation steps.
        initial_infected_fraction : float
            Fraction of the initial network randomly selected as infected seeds.
        transmission_mode : str
            'independent' : P(inf) = 1 - prod_{j in I}(1 - beta)
            'weighted_contact': P(inf) = 1 - prod_{j in I}(1 - beta * w_j / w_max)
            'linear_additive': P(inf) = min(1.0, beta * |I|)
        """
        self.beta = beta
        self.timesteps = timesteps
        self.initial_infected_fraction = initial_infected_fraction
        self.transmission_mode = transmission_mode

    def simulate_single_run(
        self, G: nx.Graph, rng: Optional[np.random.Generator] = None
    ) -> Dict[str, np.ndarray]:
        """
        Executes one independent stochastic realization of the SI epidemic.
        
        Returns
        -------
        Dict[str, np.ndarray]
            Dictionary containing:
            - 'S_counts': count of susceptible nodes at each timestep
            - 'I_counts': count of infected nodes at each timestep
            - 'S_proportions': proportion of susceptible nodes at each timestep
            - 'I_proportions': proportion of infected nodes at each timestep
            - 'total_infected': total number of individuals infected
        """
        if rng is None:
            rng = np.random.default_rng()

        nodes = list(G.nodes())
        total_nodes = len(nodes)
        
        if total_nodes == 0:
            zeros = np.zeros(self.timesteps + 1, dtype=int)
            return {
                "S_counts": zeros,
                "I_counts": zeros,
                "S_proportions": np.zeros(self.timesteps + 1, dtype=float),
                "I_proportions": np.zeros(self.timesteps + 1, dtype=float),
                "total_infected": 0,
            }

        num_initial = max(1, int(total_nodes * self.initial_infected_fraction))
        initial_infected = set(rng.choice(nodes, size=num_initial, replace=False))

        # Node states: 0 = Susceptible, 1 = Infected
        status = {node: 1 if node in initial_infected else 0 for node in nodes}

        s_counts = [total_nodes - len(initial_infected)]
        i_counts = [len(initial_infected)]

        max_w = 5.0  # Maximum friendship weight in Moreno ANU dataset

        for _ in range(self.timesteps):
            new_infections = []
            for node in nodes:
                if status[node] == 0:  # Susceptible
                    infected_neighbors = [
                        nbr for nbr in G.neighbors(node) if status[nbr] == 1
                    ]
                    k_inf = len(infected_neighbors)
                    if k_inf > 0:
                        if self.transmission_mode == "independent":
                            prob = 1.0 - (1.0 - self.beta) ** k_inf
                        elif self.transmission_mode == "weighted_contact":
                            prod_term = 1.0
                            for nbr in infected_neighbors:
                                w = G[node][nbr].get("weight", 1.0)
                                prod_term *= (1.0 - self.beta * (w / max_w))
                            prob = 1.0 - prod_term
                        elif self.transmission_mode == "linear_additive":
                            prob = min(1.0, self.beta * k_inf)
                        else:
                            prob = 1.0 - (1.0 - self.beta) ** k_inf

                        if rng.random() < prob:
                            new_infections.append(node)

            for node in new_infections:
                status[node] = 1

            current_i = sum(status.values())
            current_s = total_nodes - current_i
            s_counts.append(current_s)
            i_counts.append(current_i)

        s_arr = np.array(s_counts, dtype=int)
        i_arr = np.array(i_counts, dtype=int)

        return {
            "S_counts": s_arr,
            "I_counts": i_arr,
            "S_proportions": s_arr / total_nodes,
            "I_proportions": i_arr / total_nodes,
            "total_infected": int(i_arr[-1]),
        }

    def run_monte_carlo(
        self, G: nx.Graph, num_runs: int = 100, base_seed: int = 42
    ) -> Dict[str, Any]:
        """Runs multiple independent stochastic simulations and aggregates results."""
        s_matrix = []
        i_matrix = []
        total_infected_list = []

        for run_idx in range(num_runs):
            rng = np.random.default_rng(base_seed + run_idx)
            res = self.simulate_single_run(G, rng=rng)
            s_matrix.append(res["S_proportions"])
            i_matrix.append(res["I_proportions"])
            total_infected_list.append(res["total_infected"])

        s_mat = np.array(s_matrix)
        i_mat = np.array(i_matrix)

        return {
            "timesteps": np.arange(self.timesteps + 1),
            "S_mean": np.mean(s_mat, axis=0),
            "S_std": np.std(s_mat, axis=0),
            "I_mean": np.mean(i_mat, axis=0),
            "I_std": np.std(i_mat, axis=0),
            "total_infected_runs": np.array(total_infected_list),
            "total_infected_mean": float(np.mean(total_infected_list)),
            "total_infected_std": float(np.std(total_infected_list)),
        }
