"""
Susceptible-Infected-Recovered (SIR) Epidemic Model Module.
Simulates disease transmission, recovery dynamics, peak infection tracking,
and cumulative incidence across network topologies.
"""

from typing import Dict, Any, Optional
import networkx as nx
import numpy as np


class SIRModel:
    """Simulates the SIR compartmental epidemic process on an undirected network."""

    def __init__(
        self,
        beta: float = 0.3,
        gamma: float = 0.1,
        timesteps: int = 50,
        initial_infected_fraction: float = 0.01,
        transmission_mode: str = "independent",
    ):
        """
        Parameters
        ----------
        beta : float
            Infection transmission probability / rate.
        gamma : float
            Recovery rate / probability per timestep.
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
        self.gamma = gamma
        self.timesteps = timesteps
        self.initial_infected_fraction = initial_infected_fraction
        self.transmission_mode = transmission_mode

    def simulate_single_run(
        self, G: nx.Graph, rng: Optional[np.random.Generator] = None
    ) -> Dict[str, Any]:
        """
        Executes one stochastic trajectory of the SIR process.
        
        Returns
        -------
        Dict[str, Any]
            Trajectory arrays and scalar metrics:
            - 'S_counts', 'I_counts', 'R_counts'
            - 'S_proportions', 'I_proportions', 'R_proportions'
            - 'infection_peak' (IP) : maximum concurrent infected nodes
            - 'peak_time' : timestep where maximum concurrent infection occurred
            - 'total_infected' (TI) : cumulative individuals infected over entire run
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
                "R_counts": zeros,
                "S_proportions": np.zeros(self.timesteps + 1, dtype=float),
                "I_proportions": np.zeros(self.timesteps + 1, dtype=float),
                "R_proportions": np.zeros(self.timesteps + 1, dtype=float),
                "infection_peak": 0,
                "peak_time": 0,
                "total_infected": 0,
            }

        num_initial = max(1, int(total_nodes * self.initial_infected_fraction))
        initial_infected = set(rng.choice(nodes, size=num_initial, replace=False))

        # Status: 0 = Susceptible, 1 = Infected, 2 = Recovered
        status = {node: 1 if node in initial_infected else 0 for node in nodes}
        ever_infected = set(initial_infected)

        s_counts = [total_nodes - len(initial_infected)]
        i_counts = [len(initial_infected)]
        r_counts = [0]

        max_w = 5.0

        for t in range(1, self.timesteps + 1):
            new_infections = []
            new_recoveries = []

            for node in nodes:
                st = status[node]
                if st == 0:  # Susceptible
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
                elif st == 1:  # Infected
                    if rng.random() < self.gamma:
                        new_recoveries.append(node)

            for node in new_infections:
                status[node] = 1
                ever_infected.add(node)
            for node in new_recoveries:
                status[node] = 2

            cur_s = sum(1 for v in status.values() if v == 0)
            cur_i = sum(1 for v in status.values() if v == 1)
            cur_r = sum(1 for v in status.values() if v == 2)

            s_counts.append(cur_s)
            i_counts.append(cur_i)
            r_counts.append(cur_r)

        s_arr = np.array(s_counts, dtype=int)
        i_arr = np.array(i_counts, dtype=int)
        r_arr = np.array(r_counts, dtype=int)

        infection_peak = int(np.max(i_arr))
        peak_time = int(np.argmax(i_arr))
        total_infected = len(ever_infected)

        return {
            "S_counts": s_arr,
            "I_counts": i_arr,
            "R_counts": r_arr,
            "S_proportions": s_arr / total_nodes,
            "I_proportions": i_arr / total_nodes,
            "R_proportions": r_arr / total_nodes,
            "infection_peak": infection_peak,
            "peak_time": peak_time,
            "total_infected": total_infected,
        }

    def run_monte_carlo(
        self, G: nx.Graph, num_runs: int = 100, base_seed: int = 42
    ) -> Dict[str, Any]:
        """Runs multiple independent realizations and calculates empirical statistics."""
        s_matrix, i_matrix, r_matrix = [], [], []
        peaks, peak_times, total_infecteds = [], [], []

        for run_idx in range(num_runs):
            rng = np.random.default_rng(base_seed + run_idx)
            res = self.simulate_single_run(G, rng=rng)
            s_matrix.append(res["S_proportions"])
            i_matrix.append(res["I_proportions"])
            r_matrix.append(res["R_proportions"])
            peaks.append(res["infection_peak"])
            peak_times.append(res["peak_time"])
            total_infecteds.append(res["total_infected"])

        s_mat = np.array(s_matrix)
        i_mat = np.array(i_matrix)
        r_mat = np.array(r_matrix)

        return {
            "timesteps": np.arange(self.timesteps + 1),
            "S_mean": np.mean(s_mat, axis=0),
            "S_std": np.std(s_mat, axis=0),
            "I_mean": np.mean(i_mat, axis=0),
            "I_std": np.std(i_mat, axis=0),
            "R_mean": np.mean(r_mat, axis=0),
            "R_std": np.std(r_mat, axis=0),
            "infection_peaks": np.array(peaks),
            "peak_mean": float(np.mean(peaks)),
            "peak_std": float(np.std(peaks)),
            "peak_times": np.array(peak_times),
            "peak_time_mean": float(np.mean(peak_times)),
            "total_infected_runs": np.array(total_infecteds),
            "total_infected_mean": float(np.mean(total_infecteds)),
            "total_infected_std": float(np.std(total_infecteds)),
        }
