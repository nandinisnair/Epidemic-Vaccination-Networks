"""
Visualization Module.
Generates publication-quality figures for network structures, degree distributions,
centrality rankings, epidemic trajectories, and multi-strategy vaccination evaluations.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
import networkx as nx
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from config.experiment_config import PLOTS_DIR, TABLES_DIR


class NetworkVisualizer:
    """Creates publication-ready visualizations conforming to IEEE conference standards."""

    def __init__(self, plots_dir: Path = None, tables_dir: Path = None):
        self.plots_dir = Path(plots_dir or PLOTS_DIR)
        self.tables_dir = Path(tables_dir or TABLES_DIR)
        self.plots_dir.mkdir(parents=True, exist_ok=True)
        self.tables_dir.mkdir(parents=True, exist_ok=True)

        # Matplotlib global style settings for clean publication aesthetics
        plt.rcParams["font.sans-serif"] = "DejaVu Sans"
        plt.rcParams["font.family"] = "sans-serif"
        plt.rcParams["axes.edgecolor"] = "#333333"
        plt.rcParams["axes.linewidth"] = 1.0

    def plot_network(
        self,
        G: nx.Graph,
        title: str = "Social Network Visualization",
        filename: str = "01_network_visualization.png",
        seed: int = 42,
    ) -> Path:
        """Visualizes the network topology with weighted edge alpha and spring layout."""
        fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
        pos = nx.spring_layout(G, seed=seed, k=0.18, iterations=60)

        # Draw edges with intensity mapped to width and transparency
        weights = [d.get("weight", 1.0) for _, _, d in G.edges(data=True)]
        max_w = max(weights) if weights else 1.0
        normalized_weights = [0.4 + 1.2 * (w / max_w) for w in weights]

        nx.draw_networkx_edges(
            G, pos, ax=ax, width=normalized_weights, alpha=0.35, edge_color="#2b2b2b"
        )
        nx.draw_networkx_nodes(
            G, pos, ax=ax, node_size=35, node_color="#1f77b4", edgecolors="#0f3d60", linewidths=0.6
        )

        ax.set_title(title, fontsize=14, fontweight="bold", pad=12)
        ax.axis("off")
        fig.tight_layout()

        out_path = self.plots_dir / filename
        fig.savefig(out_path, dpi=300)
        plt.close(fig)
        return out_path

    def plot_largest_component(
        self,
        G_lcc: nx.Graph,
        title: str = "Largest Connected Component (LCC)",
        filename: str = "02_largest_connected_component.png",
        seed: int = 42,
    ) -> Path:
        """Visualizes the isolated primary connected cluster."""
        fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
        pos = nx.spring_layout(G_lcc, seed=seed, k=0.18, iterations=60)

        weights = [d.get("weight", 1.0) for _, _, d in G_lcc.edges(data=True)]
        max_w = max(weights) if weights else 1.0
        normalized_widths = [0.4 + 1.2 * (w / max_w) for w in weights]

        nx.draw_networkx_edges(
            G_lcc, pos, ax=ax, width=normalized_widths, alpha=0.35, edge_color="#333333"
        )
        nx.draw_networkx_nodes(
            G_lcc, pos, ax=ax, node_size=35, node_color="#2ca02c", edgecolors="#1b611b", linewidths=0.6
        )

        ax.set_title(
            f"{title} ({G_lcc.number_of_nodes()} nodes, {G_lcc.number_of_edges()} edges)",
            fontsize=14,
            fontweight="bold",
            pad=12,
        )
        ax.axis("off")
        fig.tight_layout()

        out_path = self.plots_dir / filename
        fig.savefig(out_path, dpi=300)
        plt.close(fig)
        return out_path

    def plot_degree_distribution(
        self,
        G: nx.Graph,
        filename_hist: str = "03_degree_distribution_histogram.png",
        filename_plot: str = "03b_degree_distribution_curve.png",
    ) -> Tuple[Path, Path]:
        """Plots degree distribution histogram and frequency curve."""
        degrees = [d for _, d in G.degree()]

        # Histogram (matching Figure 2 in paper)
        fig1, ax1 = plt.subplots(figsize=(8, 6), dpi=300)
        ax1.hist(degrees, bins=30, color="#414ff0", alpha=0.85, edgecolor="#1c25a0")
        ax1.set_xlabel("Degree", fontsize=12)
        ax1.set_ylabel("Frequency", fontsize=12)
        ax1.set_title("Degree Distribution", fontsize=14, fontweight="bold")
        ax1.set_xlim(left=0)
        ax1.grid(True, linestyle="--", alpha=0.4)
        fig1.tight_layout()
        hist_path = self.plots_dir / filename_hist
        fig1.savefig(hist_path, dpi=300)
        plt.close(fig1)

        # 2. Probability Mass / Frequency Curve
        deg_counts = pd.Series(degrees).value_counts().sort_index()
        fig2, ax2 = plt.subplots(figsize=(8, 6), dpi=300)
        ax2.plot(deg_counts.index, deg_counts.values, marker="o", color="#1f77b4", linewidth=1.8, markersize=5)
        ax2.set_xlabel("Node Degree (k)", fontsize=12)
        ax2.set_ylabel("Number of Nodes P(k)", fontsize=12)
        ax2.set_title("Degree Distribution Frequency Curve", fontsize=14, fontweight="bold")
        ax2.grid(True, linestyle="--", alpha=0.4)
        fig2.tight_layout()
        curve_path = self.plots_dir / filename_plot
        fig2.savefig(curve_path, dpi=300)
        plt.close(fig2)

        # Save underlying numerical data
        dist_df = pd.DataFrame({"degree": deg_counts.index, "count": deg_counts.values})
        dist_df["probability"] = dist_df["count"] / len(degrees)
        dist_df.to_csv(self.tables_dir / "degree_distribution_data.csv", index=False)

        return hist_path, curve_path

    def plot_centrality_comparisons(
        self,
        centrality_df: pd.DataFrame,
        filename: str = "04_centrality_comparison.png",
    ) -> Path:
        """Generates pairwise correlation subplots between the four centrality measures."""
        fig, axes = plt.subplots(2, 2, figsize=(11, 9), dpi=300)

        # Panel A: Degree vs Strength
        axes[0, 0].scatter(
            centrality_df["degree"], centrality_df["strength"], color="#1f77b4", alpha=0.7, edgecolors="none"
        )
        axes[0, 0].set_xlabel("Degree Centrality", fontsize=11)
        axes[0, 0].set_ylabel("Strength Centrality", fontsize=11)
        axes[0, 0].set_title("A. Degree vs. Strength", fontsize=12, fontweight="bold")
        axes[0, 0].grid(True, linestyle="--", alpha=0.4)

        # Panel B: Degree vs Betweenness
        axes[0, 1].scatter(
            centrality_df["degree"], centrality_df["betweenness"], color="#2ca02c", alpha=0.7, edgecolors="none"
        )
        axes[0, 1].set_xlabel("Degree Centrality", fontsize=11)
        axes[0, 1].set_ylabel("Betweenness Centrality", fontsize=11)
        axes[0, 1].set_title("B. Degree vs. Betweenness", fontsize=12, fontweight="bold")
        axes[0, 1].grid(True, linestyle="--", alpha=0.4)

        # Panel C: Betweenness vs Weighted Betweenness (Inverse)
        axes[1, 0].scatter(
            centrality_df["betweenness"],
            centrality_df["weighted_betweenness_inverse"],
            color="#d62728",
            alpha=0.7,
            edgecolors="none",
        )
        axes[1, 0].set_xlabel("Betweenness Centrality", fontsize=11)
        axes[1, 0].set_ylabel("Weighted Betweenness (Inverse)", fontsize=11)
        axes[1, 0].set_title("C. Betweenness vs. Weighted Betweenness", fontsize=12, fontweight="bold")
        axes[1, 0].grid(True, linestyle="--", alpha=0.4)

        # Panel D: Strength vs Weighted Betweenness
        axes[1, 1].scatter(
            centrality_df["strength"],
            centrality_df["weighted_betweenness_inverse"],
            color="#9467bd",
            alpha=0.7,
            edgecolors="none",
        )
        axes[1, 1].set_xlabel("Strength Centrality", fontsize=11)
        axes[1, 1].set_ylabel("Weighted Betweenness (Inverse)", fontsize=11)
        axes[1, 1].set_title("D. Strength vs. Weighted Betweenness", fontsize=12, fontweight="bold")
        axes[1, 1].grid(True, linestyle="--", alpha=0.4)

        fig.suptitle("Comparison of Centrality Measures in Friendship Network", fontsize=14, fontweight="bold", y=0.98)
        fig.tight_layout()
        out_path = self.plots_dir / filename
        fig.savefig(out_path, dpi=300)
        plt.close(fig)
        return out_path

    def plot_si_dynamics(
        self,
        si_results: Dict[str, Any],
        filename: str = "05_si_epidemic_dynamics.png",
    ) -> Path:
        """Plots mean Susceptible and Infected population trajectories for SI model."""
        fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
        t = si_results["timesteps"]
        s_mean, s_std = si_results["S_mean"], si_results["S_std"]
        i_mean, i_std = si_results["I_mean"], si_results["I_std"]

        ax.plot(t, i_mean, label="Infected (I)", color="#1f77b4", linewidth=2.2)
        ax.fill_between(t, np.maximum(0, i_mean - i_std), np.minimum(1, i_mean + i_std), color="#1f77b4", alpha=0.18)

        ax.set_xlabel("Time (steps)", fontsize=12)
        ax.set_ylabel("Proportion of Population", fontsize=12)
        ax.set_title("SI Model Dynamics (β = 0.3)", fontsize=14, fontweight="bold")
        ax.set_ylim(-0.05, 1.05)
        ax.grid(True, linestyle="--", alpha=0.4)
        ax.legend(fontsize=11, loc="center right")
        fig.tight_layout()

        out_path = self.plots_dir / filename
        fig.savefig(out_path, dpi=300)
        plt.close(fig)
        return out_path

    def plot_sir_dynamics(
        self,
        sir_results: Dict[str, Any],
        filename: str = "06_sir_epidemic_dynamics.png",
    ) -> Path:
        """Plots S, I, and R curves (matching Figure 4 in the IEEE paper)."""
        fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
        t = sir_results["timesteps"]
        s_m = sir_results["S_mean"]
        i_m = sir_results["I_mean"]
        r_m = sir_results["R_mean"]

        ax.plot(t, s_m, label="Susceptible", color="#1f77b4", linewidth=2.0)
        ax.plot(t, i_m, label="Infected", color="#ff7f0e", linewidth=2.0)
        ax.plot(t, r_m, label="Recovered", color="#2ca02c", linewidth=2.0)

        # Highlight peak
        peak_idx = int(np.argmax(i_m))
        ax.scatter([t[peak_idx]], [i_m[peak_idx]], color="#d62728", s=45, zorder=5)
        ax.annotate(
            f"Peak: {i_m[peak_idx]:.2f} (t={t[peak_idx]})",
            (t[peak_idx], i_m[peak_idx]),
            xytext=(t[peak_idx] + 3, i_m[peak_idx] + 0.05),
            arrowprops=dict(facecolor="#d62728", arrowstyle="->", lw=1.2),
            fontweight="bold",
            fontsize=10,
        )

        ax.set_xlabel("Time", fontsize=12)
        ax.set_ylabel("Proportion", fontsize=12)
        ax.set_title("SIR Model Dynamics", fontsize=14, fontweight="bold")
        ax.set_ylim(-0.02, 1.05)
        ax.grid(True, linestyle="--", alpha=0.4)
        ax.legend(fontsize=11, loc="center right")
        fig.tight_layout()

        out_path = self.plots_dir / filename
        fig.savefig(out_path, dpi=300)
        plt.close(fig)
        return out_path

    def plot_si_vs_sir_comparison(
        self,
        si_results: Dict[str, Any],
        sir_results: Dict[str, Any],
        filename: str = "07_si_vs_sir_comparison.png",
    ) -> Path:
        """Compares infection trajectory between unconstrained SI and recovering SIR models."""
        fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
        t = si_results["timesteps"]

        ax.plot(t, si_results["I_mean"], label="SI Model (No Recovery)", color="#d62728", linewidth=2.2)
        ax.plot(t, sir_results["I_mean"], label="SIR Model (γ = 0.1)", color="#1f77b4", linewidth=2.2)

        ax.set_xlabel("Time (steps)", fontsize=12)
        ax.set_ylabel("Infected Proportion of Population", fontsize=12)
        ax.set_title("SI vs. SIR Epidemic Progression Comparison", fontsize=14, fontweight="bold")
        ax.set_ylim(-0.02, 1.05)
        ax.grid(True, linestyle="--", alpha=0.4)
        ax.legend(fontsize=11)
        fig.tight_layout()

        out_path = self.plots_dir / filename
        fig.savefig(out_path, dpi=300)
        plt.close(fig)
        return out_path

    def plot_individual_vaccination_metrics(
        self,
        summary_df: pd.DataFrame,
    ) -> Dict[str, Path]:
        """Plots standalone curves for Total Infected, Infection Peak, and LCC vs Vaccination."""
        color_map = {
            "Degree": "#1f77b4",
            "Strength": "#ff7f0e",
            "Betweenness": "#2ca02c",
            "Weighted Betweenness": "#d62728",
            "Random": "#9467bd",
        }
        marker_map = {
            "Degree": "o",
            "Strength": "s",
            "Betweenness": "^",
            "Weighted Betweenness": "D",
            "Random": "v",
        }

        paths = {}

        # 1. Total Infected (TI)
        fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
        for strat in summary_df["strategy"].unique():
            sub = summary_df[summary_df["strategy"] == strat]
            ax.plot(
                sub["coverage"],
                sub["TI_mean"],
                marker=marker_map.get(strat, "o"),
                label=strat,
                color=color_map.get(strat, "#333333"),
                linewidth=1.8,
            )
        ax.set_xlabel("Vaccination Fraction", fontsize=12)
        ax.set_ylabel("Total Infected (TI)", fontsize=12)
        ax.set_title("Effect of Vaccination on Total Infections", fontsize=14, fontweight="bold")
        ax.grid(True, linestyle="--", alpha=0.4)
        ax.legend(fontsize=10)
        fig.tight_layout()
        ti_path = self.plots_dir / "08_total_infected_vs_coverage.png"
        fig.savefig(ti_path, dpi=300)
        plt.close(fig)
        paths["ti"] = ti_path

        # 2. Infection Peak (IP)
        fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
        for strat in summary_df["strategy"].unique():
            sub = summary_df[summary_df["strategy"] == strat]
            ax.plot(
                sub["coverage"],
                sub["IP_mean"],
                marker=marker_map.get(strat, "o"),
                label=strat,
                color=color_map.get(strat, "#333333"),
                linewidth=1.8,
            )
        ax.set_xlabel("Vaccination Fraction", fontsize=12)
        ax.set_ylabel("Infection Peak (IP)", fontsize=12)
        ax.set_title("Effect of Vaccination on Infection Peak", fontsize=14, fontweight="bold")
        ax.grid(True, linestyle="--", alpha=0.4)
        ax.legend(fontsize=10)
        fig.tight_layout()
        ip_path = self.plots_dir / "09_infection_peak_vs_coverage.png"
        fig.savefig(ip_path, dpi=300)
        plt.close(fig)
        paths["ip"] = ip_path

        # 3. Largest Connected Component (LCC)
        fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
        for strat in summary_df["strategy"].unique():
            sub = summary_df[summary_df["strategy"] == strat]
            ax.plot(
                sub["coverage"],
                sub["LCC"],
                marker=marker_map.get(strat, "o"),
                label=strat,
                color=color_map.get(strat, "#333333"),
                linewidth=1.8,
            )
        ax.set_xlabel("Vaccination Fraction", fontsize=12)
        ax.set_ylabel("Size of Largest Connected Component (LCC)", fontsize=12)
        ax.set_title("Effect of Vaccination on Network Connectivity", fontsize=14, fontweight="bold")
        ax.grid(True, linestyle="--", alpha=0.4)
        ax.legend(fontsize=10)
        fig.tight_layout()
        lcc_path = self.plots_dir / "10_lcc_vs_coverage.png"
        fig.savefig(lcc_path, dpi=300)
        plt.close(fig)
        paths["lcc"] = lcc_path

        return paths

    def plot_ieee_multipanel_comparison(
        self,
        summary_df: pd.DataFrame,
        filename: str = "11_ieee_multipanel_comparison.png",
    ) -> Path:
        """
        Replicates Figure 8 from the IEEE paper:
        A three-panel stacked layout displaying:
        - Panel 1: Largest Connected Component (LCC)
        - Panel 2: Total Infected (TI)
        - Panel 3: Infection Peak (IP)
        """
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(9, 12), dpi=300, sharex=True)

        color_map = {
            "Degree": "#1f77b4",
            "Strength": "#ff7f0e",
            "Betweenness": "#2ca02c",
            "Weighted Betweenness": "#d62728",
            "Random": "#9467bd",
        }
        marker_map = {
            "Degree": "o",
            "Strength": "o",
            "Betweenness": "o",
            "Weighted Betweenness": "o",
            "Random": "s",
        }

        strategies = [s for s in summary_df["strategy"].unique() if s != "Random"]
        if "Random" in summary_df["strategy"].unique():
            strategies.append("Random")

        for strat in strategies:
            sub = summary_df[summary_df["strategy"] == strat]
            cov = sub["coverage"]
            c = color_map.get(strat, "#333333")
            m = marker_map.get(strat, "o")

            # 1. LCC
            ax1.plot(cov, sub["LCC"], marker=m, label=strat, color=c, linewidth=1.8, markersize=5)

            # 2. Total Infected
            ax2.plot(cov, sub["TI_mean"], marker=m, label=strat, color=c, linewidth=1.8, markersize=5)

            # 3. Infection Peak
            ax3.plot(cov, sub["IP_mean"], marker=m, label=strat, color=c, linewidth=1.8, markersize=5)

        ax1.set_title("Largest Connected Component (LCC)", fontsize=13, fontweight="bold")
        ax1.set_ylabel("LCC", fontsize=11)
        ax1.grid(True, linestyle="-", alpha=0.5)
        ax1.legend(loc="upper right", fontsize=9)

        ax2.set_title("Total Infected (TI)", fontsize=13, fontweight="bold")
        ax2.set_ylabel("TI", fontsize=11)
        ax2.grid(True, linestyle="-", alpha=0.5)
        ax2.legend(loc="upper right", fontsize=9)

        ax3.set_title("Infection Peak (IP)", fontsize=13, fontweight="bold")
        ax3.set_ylabel("IP", fontsize=11)
        ax3.set_xlabel("Vaccination Fraction", fontsize=11)
        ax3.grid(True, linestyle="-", alpha=0.5)
        ax3.legend(loc="upper right", fontsize=9)

        fig.tight_layout()
        out_path = self.plots_dir / filename
        fig.savefig(out_path, dpi=300)
        plt.close(fig)
        return out_path

    def plot_comparative_barchart(
        self,
        summary_df: pd.DataFrame,
        filename: str = "12_comparative_barchart.png",
    ) -> Path:
        """Comparative grouped bar charts at primary coverage percentages (10%, 20%, 30%, 40%, 50%)."""
        # Filter for coverage > 0
        df_sub = summary_df[summary_df["coverage"] > 0.0].copy()
        coverages = sorted(df_sub["coverage"].unique())
        strategies = df_sub["strategy"].unique()

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)

        x = np.arange(len(coverages))
        width = 0.8 / len(strategies)

        color_map = {
            "Degree": "#1f77b4",
            "Strength": "#ff7f0e",
            "Betweenness": "#2ca02c",
            "Weighted Betweenness": "#d62728",
            "Random": "#9467bd",
        }

        for idx, strat in enumerate(strategies):
            strat_data = df_sub[df_sub["strategy"] == strat]
            offsets = x + (idx - len(strategies) / 2 + 0.5) * width
            
            # Left: Total Infected Mean
            ax1.bar(
                offsets,
                strat_data["TI_mean"],
                width=width,
                label=strat,
                color=color_map.get(strat, None),
                edgecolor="#222222",
                linewidth=0.6,
            )
            # Right: Infection Peak Mean
            ax2.bar(
                offsets,
                strat_data["IP_mean"],
                width=width,
                label=strat,
                color=color_map.get(strat, None),
                edgecolor="#222222",
                linewidth=0.6,
            )

        cov_labels = [f"{int(c * 100)}%" for c in coverages]
        ax1.set_xticks(x)
        ax1.set_xticklabels(cov_labels, fontsize=11)
        ax1.set_xlabel("Vaccination Coverage", fontsize=12)
        ax1.set_ylabel("Mean Total Infected (TI)", fontsize=12)
        ax1.set_title("Total Infected by Strategy and Coverage", fontsize=13, fontweight="bold")
        ax1.grid(True, axis="y", linestyle="--", alpha=0.4)
        ax1.legend(fontsize=9)

        ax2.set_xticks(x)
        ax2.set_xticklabels(cov_labels, fontsize=11)
        ax2.set_xlabel("Vaccination Coverage", fontsize=12)
        ax2.set_ylabel("Mean Infection Peak (IP)", fontsize=12)
        ax2.set_title("Infection Peak by Strategy and Coverage", fontsize=13, fontweight="bold")
        ax2.grid(True, axis="y", linestyle="--", alpha=0.4)
        ax2.legend(fontsize=9)

        fig.tight_layout()
        out_path = self.plots_dir / filename
        fig.savefig(out_path, dpi=300)
        plt.close(fig)
        return out_path
