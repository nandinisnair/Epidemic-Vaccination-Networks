"""
Experiment Configuration Module.
Defines parameters for dataset paths, network preprocessing, centrality metrics,
epidemic models (SI, SIR), vaccination strategies, and simulation runs.
"""

from pathlib import Path
from dataclasses import dataclass, field
from typing import List


# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
RESULTS_DIR = BASE_DIR / "results"
TABLES_DIR = RESULTS_DIR / "tables"
PLOTS_DIR = RESULTS_DIR / "plots"
CENTRALITY_DIR = RESULTS_DIR / "centrality_rankings"
SIMULATION_DIR = RESULTS_DIR / "simulation_outputs"


@dataclass
class DatasetConfig:
    raw_archive_name: str = "download.tsv.moreno_oz.tar.bz2"
    konect_url: str = "http://konect.cc/files/download.tsv.moreno_oz.tar.bz2"
    raw_data_file: Path = RAW_DATA_DIR / "moreno_oz" / "out.moreno_oz_oz"
    meta_data_file: Path = RAW_DATA_DIR / "moreno_oz" / "meta.moreno_oz_oz"
    readme_file: Path = RAW_DATA_DIR / "moreno_oz" / "README.moreno_oz"
    processed_edge_file: Path = PROCESSED_DATA_DIR / "moreno_oz_edges.csv"
    processed_graph_file: Path = PROCESSED_DATA_DIR / "moreno_oz_graph.graphml"
    
    # Expected KONECT dataset properties
    expected_total_nodes: int = 217
    # Reciprocal edge resolution: 'last' (as in raw sequential add_edge), 'max', 'mean', or 'sum'
    reciprocal_weight_mode: str = "last"
    remove_self_loops: bool = True


@dataclass
class CentralityConfig:
    # Distance transformation for weighted shortest paths:
    # 'inverse': distance = 1.0 / weight (strong friendship = low distance)
    # 'direct': distance = weight (historical raw notebook weight interpretation)
    weighted_betweenness_distance_mode: str = "inverse"
    top_k_nodes: int = 10


@dataclass
class EpidemicConfig:
    # SI Model parameters
    si_beta: float = 0.3
    si_timesteps: int = 50
    si_initial_infected_fraction: float = 0.01

    # SIR Model parameters
    sir_beta: float = 0.3
    sir_gamma: float = 0.1
    sir_timesteps: int = 50
    sir_initial_infected_fraction: float = 0.01

    # Transmission mode:
    # 'independent': p = 1 - prod_{j in Inf}(1 - beta) (per-edge independent contagion)
    # 'weighted_contact': p = 1 - prod_{j in Inf}(1 - beta * (w_j / w_max))
    # 'linear_additive': p = min(1.0, beta * len(infected_neighbors)) (notebook early prototype)
    transmission_mode: str = "independent"


@dataclass
class VaccinationConfig:
    # Primary IEEE publication coverage levels (0% to 50% in 10% steps)
    primary_coverage_levels: List[float] = field(
        default_factory=lambda: [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
    )
    # Exploratory fine-grained coverage levels (0% to 50% in 5% steps)
    exploratory_coverage_levels: List[float] = field(
        default_factory=lambda: [
            0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50
        ]
    )
    strategies: List[str] = field(
        default_factory=lambda: [
            "Random",
            "Degree",
            "Strength",
            "Betweenness",
            "Weighted Betweenness",
        ]
    )
    # Simulation repetition count
    num_runs: int = 100
    base_seed: int = 42


@dataclass
class ExperimentConfig:
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    centrality: CentralityConfig = field(default_factory=CentralityConfig)
    epidemic: EpidemicConfig = field(default_factory=EpidemicConfig)
    vaccination: VaccinationConfig = field(default_factory=VaccinationConfig)


default_config = ExperimentConfig()
