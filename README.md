# An Analysis of Vaccination Strategies on Epidemic Spread in a Friendship Network

**Research Internship Project Reconstruction**  
**Laboratory:** FACTS-H Lab, Indian Institute of Information Technology Kottayam  
**Conference Publication:** *2025 11th International Conference on Smart Computing and Communications (ICSCC)*  
**IEEE PID:** 1195  
**Authors:** Nandini Sreejit Nair, Jisha Mariyam John, Dr. Divya Sindhu Lekha  

---

## 1. Project Overview

Epidemiological modeling has historically relied on homogeneous mixing assumptions, wherein every individual possesses an equal probability of contacting every other individual. In real human populations, however, transmission is governed by structured, heterogeneous social contact networks.

This project investigates disease transmission and targeted immunization across a real-world, weighted social network: the **Australian National University (ANU) residence hall friendship network (`moreno_oz`)** from the KONECT repository (217 individuals). In this network:
- **Nodes** represent individuals (residents).
- **Edges** represent friendship ties.
- **Edge weights** reflect friendship intensity ($w \in \{1, 2, 3, 4, 5\}$).

We implement compartmental **SI (Susceptible-Infected)** and **SIR (Susceptible-Infected-Recovered)** models and rigorously evaluate five vaccination strategies:
1. **Random Vaccination** (baseline non-targeted control).
2. **Degree Centrality Vaccination** (targeting highly connected hubs).
3. **Strength Centrality Vaccination** (targeting high cumulative contact intensity).
4. **Betweenness Centrality Vaccination** (targeting topological bridge nodes).
5. **Weighted Betweenness Centrality Vaccination** (targeting shortest-path bottlenecks incorporating interaction weights).

Interventions are evaluated across vaccination coverage fractions from **0% to 50%** (primary IEEE schedule: 10% steps; exploratory schedule: 5% steps) with **100 independent Monte Carlo realizations** per experimental condition. Outcomes are evaluated along three primary indicators:
- **Total Infected (TI):** Cumulative incidence across the outbreak.
- **Infection Peak (IP):** Maximum concurrent active infections.
- **Largest Connected Component (LCC):** Residual structural connectivity post-vaccination.

---

## 2. Repository Architecture

```text
Epidemic Simulation/
│
├── data/
│   ├── raw/
│   │   └── moreno_oz/
│   │       ├── meta.moreno_oz_oz       # Official KONECT metadata
│   │       ├── out.moreno_oz_oz        # Whitespace-delimited edge streams (2,672 directed arcs)
│   │       └── README.moreno_oz        # Dataset documentation and citations
│   └── processed/
│       ├── moreno_oz_edges.csv         # Processed undirected edge list with weights & distances
│       └── moreno_oz_graph.graphml     # Exported NetworkX GraphML network representation
│
├── config/
│   └── experiment_config.py            # Centralized parameter definitions, paths, and model hyperparams
│
├── src/
│   ├── __init__.py                     # Package initialization
│   ├── data_loader.py                  # Automated acquisition, decompression, and parsing
│   ├── network_preprocessing.py        # Graph construction, reciprocal edge handling, LCC extraction
│   ├── network_analysis.py             # Global topological and structural graph metrics
│   ├── centrality_analysis.py          # Degree, Strength, Betweenness, and Weighted Betweenness metrics
│   ├── si_model.py                     # Susceptible-Infected stochastic epidemic model
│   ├── sir_model.py                    # Susceptible-Infected-Recovered stochastic epidemic model
│   ├── vaccination.py                  # Immunization strategy implementations via node removal
│   ├── simulation_runner.py            # Monte Carlo experiment harness and batch orchestrator
│   ├── evaluation.py                   # Statistical aggregation (Mean, Std, 95% CI) for TI, IP, LCC
│   └── visualization.py                # Publication-quality Matplotlib figures (300 DPI)
│
├── experiments/
│   ├── run_network_analysis.py         # Phase 1 & 2: Structural analysis & degree distribution plots
│   ├── run_si_simulation.py            # Phase 4: Baseline SI simulation and trajectory plot
│   ├── run_sir_simulation.py           # Phase 5: Baseline SIR simulation and trajectory plots
│   ├── run_vaccination_experiments.py  # Phases 3, 6-9: Multi-strategy vaccination evaluation
│   └── run_complete_pipeline.py        # Master entry point: executes complete research pipeline
│
├── results/
│   ├── tables/
│   │   ├── network_summary_statistics.csv  # 20+ graph-theoretic metrics
│   │   ├── top_10_influential_nodes.csv    # Consolidated top-10 rankings by centrality
│   │   ├── degree_distribution_data.csv    # Degree counts and empirical probabilities
│   │   ├── vaccination_primary_summary.csv # Mean, Std, CI for 0%-50% (10% increments)
│   │   └── vaccination_exploratory_summary.csv # Fine-grained 5% coverage schedule
│   ├── plots/
│   │   ├── 01_network_visualization.png         # Weighted friendship network graph
│   │   ├── 02_largest_connected_component.png   # Isolated primary component (217 nodes)
│   │   ├── 03_degree_distribution_histogram.png # Right-skewed degree distribution histogram
│   │   ├── 03b_degree_distribution_curve.png    # Empirical frequency curve
│   │   ├── 04_centrality_comparison.png         # Pairwise scatter correlations
│   │   ├── 05_si_epidemic_dynamics.png          # SI population progression
│   │   ├── 06_sir_epidemic_dynamics.png         # SIR population progression
│   │   ├── 07_si_vs_sir_comparison.png          # Comparative SI vs SIR dynamics
│   │   ├── 08_total_infected_vs_coverage.png    # TI reduction curve by strategy
│   │   ├── 09_infection_peak_vs_coverage.png    # IP suppression curve by strategy
│   │   ├── 10_lcc_vs_coverage.png               # Network fragmentation (LCC) curve
│   │   ├── 11_ieee_multipanel_comparison.png    # Replicated 3-panel IEEE Fig. 8 (LCC, TI, IP)
│   │   ├── 11b_ieee_multipanel_exploratory_5pct.png # Fine-grained 11-point 3-panel comparison
│   │   └── 12_comparative_barchart.png          # Grouped comparative bar chart
│   ├── centrality_rankings/
│   │   ├── degree_centrality_ranking.csv
│   │   ├── strength_centrality_ranking.csv
│   │   ├── betweenness_centrality_ranking.csv
│   │   ├── weighted_betweenness_inverse_centrality_ranking.csv
│   │   ├── weighted_betweenness_direct_centrality_ranking.csv
│   │   └── all_centrality_measures.csv
│   └── simulation_outputs/
│       ├── si_baseline_progression.csv
│       ├── sir_baseline_progression.csv
│       ├── vaccination_primary_raw_runs.csv     # 3,000 individual Monte Carlo runs
│       └── vaccination_exploratory_raw_runs.csv # 5,500 individual Monte Carlo runs
│
├── tests/
│   ├── test_data_loader.py             # Validates raw record counts and graph loading
│   ├── test_network_analysis.py        # Validates structural metrics and bounds
│   ├── test_centrality.py              # Validates centrality validity and sorting
│   ├── test_si_model.py                # Validates monotonicity and initial states
│   ├── test_sir_model.py               # Validates conservation: S(t) + I(t) + R(t) = N
│   ├── test_vaccination.py             # Validates node removal and residual graph integrity
│   └── test_experiments.py            # Validates pipeline parameters and aggregator
│
├── requirements.txt
├── research_report.md                  # Comprehensive formal research report
└── README.md
```

---

## 3. Setup and Installation

### Prerequisites
- Python 3.9+ (tested on Python 3.10)
- Standard scientific stack: `networkx`, `numpy`, `pandas`, `matplotlib`, `scipy`

### Installation
Clone or navigate to the workspace directory:
```bash
cd "Epidemic Simulation"
```

Install dependencies:
```bash
pip install -r requirements.txt
```

---

## 4. Execution Guide

### Option A: Complete Master Pipeline (Recommended)
To execute the entire end-to-end research workflow from data validation to structural analysis, centrality computation, SI/SIR baseline dynamics, 8,500 vaccination simulations, and full plot generation:
```bash
python experiments/run_complete_pipeline.py
```

### Option B: Modular Execution
Each stage can be independently executed and verified:

1. **Network Structural Analysis & Topology Plots:**
   ```bash
   python experiments/run_network_analysis.py
   ```
2. **SI Epidemic Dynamics:**
   ```bash
   python experiments/run_si_simulation.py
   ```
3. **SIR Epidemic Dynamics & SI vs. SIR Comparison:**
   ```bash
   python experiments/run_sir_simulation.py
   ```
4. **Vaccination Experiments & Centrality Rankings:**
   ```bash
   python experiments/run_vaccination_experiments.py
   ```

### Option C: Automated Test Suite
To execute the automated regression suite (22 unit & integration tests):
```bash
python -m unittest discover tests
```

---

## 5. Summary of Key Experimental Results

| Metric | Random | Degree Centrality | Strength Centrality | Betweenness Centrality | Weighted Betweenness |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **LCC Reduction (at 50% cov.)** | 217 $\to$ 109 | 217 $\to$ 107 | 217 $\to$ 107 | 217 $\to$ 107 | 217 $\to$ 107 |
| **Total Infected (TI at 0%)** | 217.00 | 216.97 | 216.95 | 216.95 | 216.95 |
| **Total Infected (TI at 20%)**| 172.02 | 173.72 | 171.92 | **170.20** | 173.90 |
| **Total Infected (TI at 50%)**| 107.24 | 95.87 | 96.26 | **89.44** | 99.41 |
| **Infection Peak (IP at 0%)**  | 185.33 | 185.36 | 186.43 | 186.12 | 186.25 |
| **Infection Peak (IP at 20%)** | 143.03 | 136.66 | 136.24 | **131.90** | 138.12 |
| **Infection Peak (IP at 50%)** | 82.62 | 56.81 | 58.60 | **46.56** | 59.21 |
| **Computational Complexity**  | $O(1)$ | $O(V + E)$ | $O(V + E)$ | $O(VE)$ | $O(VE + V^2 \log V)$ |

Detailed analytical discussions, mathematical derivations, and limitations are provided in `research_report.md`.
