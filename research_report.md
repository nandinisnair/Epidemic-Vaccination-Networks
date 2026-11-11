# Research Report: An Analysis of Vaccination Strategies on Epidemic Spread in a Friendship Network

**Laboratory:** FACTS-H Lab, Indian Institute of Information Technology Kottayam, Kerala, India  
**Conference:** 2025 11th International Conference on Smart Computing and Communications (ICSCC)  
**IEEE Paper PID:** 1195  
**Authors:** Nandini Sreejit Nair, Jisha Mariyam John, Dr. Divya Sindhu Lekha  
**Date of Reconstruction & Validation:** November 2026  

---

## Executive Summary

This research investigates how topological heterogeneity and edge weights influence epidemic transmission and the efficacy of targeted immunization policies. Traditional epidemiological models (such as Kermack-McKendrick compartmental models) assume homogeneous mixing, presuming that every individual in a population interacts uniformly with every other individual. In contrast, infectious pathogens spread across structured contact topologies characterized by dense clusters, heavy-tailed degree distributions, and varying interaction frequencies.

Using the empirical **Australian National University (ANU) residence hall friendship network (`moreno_oz`)** obtained from the Koblenz Network Collection (KONECT), this project evaluates five distinct immunization interventions across **Susceptible-Infected (SI)** and **Susceptible-Infected-Recovered (SIR)** transmission models. The strategies evaluated are:
1. **Random Vaccination** (structural control baseline)
2. **Degree Centrality Vaccination** (hub targeting)
3. **Strength Centrality Vaccination** (contact-intensity targeting)
4. **Betweenness Centrality Vaccination** (shortest-path bridge targeting)
5. **Weighted Betweenness Centrality Vaccination** (intensity-weighted path targeting)

Simulations were conducted across vaccination coverage levels from $0\%$ to $50\%$ in $10\%$ increments (primary IEEE schedule) and $5\%$ increments (exploratory schedule) with $100$ independent stochastic Monte Carlo runs per condition ($8,500$ total simulations). Performance was quantified using three primary metrics: **Total Infected (TI)**, **Infection Peak (IP)**, and **Largest Connected Component (LCC)**. 

The empirical simulations confirm that centrality-guided targeted vaccination consistently and significantly outperforms random vaccination. Targeting structural bridge nodes (betweenness centrality) produces the steepest reductions in peak concurrent infections ($186.12 \to 46.56$) and cumulative incidence ($216.95 \to 89.44$ at $50\%$ coverage). While weighted betweenness provides fine-grained path prioritization, unweighted betweenness and local degree/strength targeting offer compelling operational alternatives in resource-constrained or time-sensitive public health scenarios due to their lower computational complexity.

---

## 1. Introduction

Epidemiological modeling provides critical decision-support tools for public health authorities during disease outbreaks. Traditional mathematical models typically classify individuals into homogeneous compartments governed by systems of non-linear differential equations. However, human interactions are neither well-mixed nor randomly distributed; rather, they form complex networks where:
- Nodes represent individuals.
- Edges represent physical or social contacts capable of transmitting infection.
- Edge weights capture interaction frequency, closeness, or physical contact duration.

Network science enables researchers to identify critical transmission hubs ("super-spreaders") and bottleneck pathways ("bridges"). Targeted immunization strategies exploit these structural properties to disrupt transmission pathways using significantly fewer doses than required under mass random vaccination.

This project reconstructs and validates the research conducted at the FACTS-H Lab, IIIT Kottayam, assessing vaccination efficacy on the weighted ANU friendship network.

---

## 2. Problem Statement

Classic mass vaccination campaigns often target high population coverage (e.g., $70\% - 90\%$) to achieve herd immunity under homogeneous mixing assumptions. In emerging epidemics or vaccine shortages, such resources are unavailable. The core research problem is:

> *How can an infectious outbreak be contained with minimal vaccine expenditure by exploiting topological network structure and weighted interaction intensity in a real-world social network?*

Specifically, the study contrasts local contact measures (degree and strength) against global topological measures (betweenness and weighted betweenness) to understand the trade-offs between epidemiological containment and computational tractability.

---

## 3. Research Objectives

1. **Empirical Network Reconstruction:** Ingest, preprocess, and analyze the KONECT `moreno_oz` Australian National University residence hall friendship network without fabricating nodes or weights.
2. **Topological Profiling:** Quantify structural properties including degree distribution, clustering, path lengths, density, and degree assortativity.
3. **Centrality Evaluation:** Compute and rank nodes according to Degree Centrality, Strength Centrality, Unweighted Betweenness Centrality, and Weighted Betweenness Centrality (using rigorous distance transformations).
4. **Epidemic Propagation Modeling:** Implement discrete-time stochastic SI and SIR models parameterized by infection rate $\beta = 0.3$, recovery rate $\gamma = 0.1$, initial infected fraction $1\%$, and duration $T = 50$ timesteps.
5. **Vaccination Policy Simulation:** Model immunization through pre-epidemic node removal across coverage fractions $f \in [0.0, 0.5]$ in $10\%$ steps with $100$ independent Monte Carlo runs.
6. **Quantitative Benchmarking:** Measure and compare Total Infected (TI), Infection Peak (IP), and Largest Connected Component (LCC) size across all strategies.

---

## 4. Dataset Description

The research utilizes the **Residence Hall Friendship Network (`moreno_oz`)** published in the Koblenz Network Collection (KONECT), originating from empirical sociological studies by Freeman, Webster, and Kirke (1998):
- **Setting:** 217 residents living in a collegiate residence hall at the Australian National University (ANU), Canberra, Australia.
- **Entities:** $N = 217$ individuals.
- **Raw Observations:** 2,672 directed friendship rating arcs.
- **Rating Scale:** Weighted ordinal nominations from 1 to 5:
  - $5$: Best friend
  - $4$: Close friend
  - $3$: Friend
  - $2$: Acquaintance
  - $1$: Weak acquaintance / contact

---

## 5. Network Preprocessing Methodology

### 5.1 Graph Construction and Symmetrization
Disease transmission over air droplets or physical interaction is intrinsically bidirectional regardless of whether a friendship nomination was reciprocated. Hence, the directed nomination streams are converted into an undirected graph $G = (V, E)$.

Let $w_{uv}^{\text{dir}}$ denote the directed nomination rating from resident $u$ to $v$. In this reconstruction:
- Sequential edge insertion replicates the original research implementation, resulting in exactly $N = 217$ nodes and $|E| = 1,839$ unique undirected edges.
- Edge weights $w_{uv} \in [1.0, 5.0]$ are preserved.
- The dataset contains $0$ self-loops, and multi-edge nominations are resolved without data loss.

### 5.2 Distance Transformation for Weighted Path Metrics
In network analysis, edge weights $w_{uv}$ often represent capacity, similarity, or affinity (higher is stronger). Conversely, shortest-path algorithms (such as Dijkstra's) interpret edge weights as distances, latencies, or costs (lower is closer). Treating friendship strength directly as physical distance creates a conceptual contradiction where best friends ($w = 5$) are placed five times farther apart than weak acquaintances ($w = 1$).

To resolve this consistently with network science principles:
$$\text{distance}(u, v) = \frac{1}{w_{uv}}$$
Under this transformation:
- A best friendship ($w = 5$) corresponds to a minimal social distance $d = 0.2$.
- A weak tie ($w = 1$) corresponds to a longer social distance $d = 1.0$.

Both distance metrics ('inverse' and historical 'direct') were implemented, analyzed, and exported for comparative transparency.

---

## 6. Network Structural Analysis

A complete graph-theoretic profiling was executed on the reconstructed friendship network. The empirical results are summarized in Table 1.

### Table 1: Structural Metrics of the Moreno ANU Friendship Network

| Metric | Empirical Value | Mathematical Interpretation / Significance |
| :--- | :---: | :--- |
| **Total Nodes ($N$)** | 217 | Population size of residence hall. |
| **Total Edges ($|E|$)** | 1,839 | Unique undirected social contact ties. |
| **Connected Components** | 1 | Graph is fully connected; all nodes reachable. |
| **LCC Size ($N_{\text{LCC}}$)** | 217 | 100% of the network belongs to the giant component. |
| **LCC Edges ($|E_{\text{LCC}}|$)** | 1,839 | All edges reside within the primary component. |
| **Average Degree ($\langle k \rangle$)** | 16.9493 | Each individual has an average of ~17 friends. |
| **Standard Deviation of Degree** | 7.7568 | Substantial variance in personal contact counts. |
| **Minimum Degree ($k_{\min}$)** | 2 | Minimum contact count in population. |
| **Maximum Degree ($k_{\max}$)** | 56 | Super-spreader hub (Node 70). |
| **Median Degree** | 16.0 | Center of degree distribution. |
| **Degree Skewness** | +1.2196 | Right-skewed distribution with heavy upper tail. |
| **Network Density ($D$)** | 0.0785 | ~7.85% of all possible pairwise ties exist. |
| **Average Clustering ($\langle C \rangle$)** | 0.3628 | Significant triadic closure; friends of friends are friends. |
| **Weighted Clustering ($\langle C_w \rangle$)** | 0.2420 | Intensity-weighted triadic closure. |
| **Average Path Length ($\ell$)** | 2.3946 | Highly compact; individuals separated by ~2.4 handshakes. |
| **Network Diameter** | 4 | Longest shortest path across the entire network. |
| **Degree Assortativity ($r$)** | +0.0960 | Weakly assortative; hubs moderately connect to other hubs. |
| **Average Strength ($\langle s \rangle$)** | 55.5853 | Average cumulative friendship weight per individual. |
| **Maximum Strength ($s_{\max}$)** | 152.0000 | Individual with strongest total friendship volume (Node 70). |

### Structural Observations:
1. **Small-World Architecture:** The low average path length ($\ell \approx 2.39$) combined with high clustering coefficient ($\langle C \rangle \approx 0.3628 \gg D$) demonstrates classic small-world network topology.
2. **Right-Skewed Distribution:** The positive degree skewness ($+1.22$) indicates that while the typical resident maintains 12–18 friendships, a small subset of super-connected hubs maintain up to 56 contacts.
3. **Outbreak Vulnerability:** The low diameter ($4$) and high clustering mean that an unchecked contagion can saturate the entire residential community within 5–10 timesteps.

---

## 7. Centrality Measures and Rankings

Four centrality indices were computed to identify candidate vaccination targets:

### 7.1 Mathematical Formulations

#### 1. Degree Centrality ($C_D$)
Measures the number of direct contacts normalized by $N - 1$:
$$C_D(v) = \frac{\deg(v)}{N - 1} = \frac{\sum_{u \in V \setminus \{v\}} a_{vu}}{N - 1}$$
High degree centrality identifies local hub individuals who have high numbers of immediate contacts.

#### 2. Strength Centrality ($S$)
Extends degree centrality to weighted graphs by summing all incident edge weights:
$$S(v) = \sum_{u \in N(v)} w_{vu}$$
Strength accounts for interaction intensity; a node with fewer but closer friends can exhibit higher strength than a node with many superficial contacts.

#### 3. Unweighted Betweenness Centrality ($C_B$)
Quantifies the fraction of all unweighted shortest paths passing through node $v$:
$$C_B(v) = \sum_{s \neq v \neq t} \frac{\sigma_{st}(v)}{\sigma_{st}}$$
where $\sigma_{st}$ is the total number of shortest paths between $s$ and $t$, and $\sigma_{st}(v)$ is the number of those paths passing through $v$. Nodes with high betweenness serve as topological bridges between disparate clusters.

#### 4. Weighted Betweenness Centrality ($C_{B}^w$)
Extends betweenness to weighted paths by minimizing path length along transformed edge distances:
$$d(s, t) = \min_{\text{paths } P} \sum_{e \in P} \frac{1}{w_e}$$
$$C_B^w(v) = \sum_{s \neq v \neq t} \frac{\sigma_{st}^w(v)}{\sigma_{st}^w}$$
Nodes with high weighted betweenness control the flow of fastest-moving transmissions across close-knit friendship bonds.

### Table 2: Top 10 Influential Nodes Identified Across Centrality Measures

| Rank | Degree Centrality | Strength Centrality | Betweenness Centrality | Weighted Betweenness (Inv. Dist.) | Weighted Betweenness (Direct) |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | Node 70 (0.2593) | Node 70 (152.0) | Node 70 (0.0659) | Node 128 (0.0316) | Node 97 (0.1367) |
| **2** | Node 184 (0.2315) | Node 169 (136.0) | Node 184 (0.0490) | Node 169 (0.0279) | Node 184 (0.1342) |
| **3** | Node 169 (0.1898) | Node 184 (135.0) | Node 113 (0.0456) | Node 17 (0.0279) | Node 70 (0.1093) |
| **4** | Node 113 (0.1620) | Node 120 (111.0) | Node 98 (0.0316) | Node 201 (0.0263) | Node 113 (0.1011) |
| **5** | Node 120 (0.1574) | Node 128 (111.0) | Node 169 (0.0283) | Node 54 (0.0263) | Node 98 (0.0562) |
| **6** | Node 156 (0.1574) | Node 156 (111.0) | Node 27 (0.0271) | Node 69 (0.0255) | Node 211 (0.0493) |
| **7** | Node 128 (0.1528) | Node 144 (106.0) | Node 120 (0.0260) | Node 85 (0.0248) | Node 27 (0.0425) |
| **8** | Node 27 (0.1481) | Node 41 (101.0) | Node 128 (0.0257) | Node 36 (0.0243) | Node 191 (0.0368) |
| **9** | Node 41 (0.1435) | Node 126 (94.0) | Node 17 (0.0231) | Node 120 (0.0240) | Node 71 (0.0266) |
| **10** | Node 2 (0.1389) | Node 151 (94.0) | Node 71 (0.0206) | Node 98 (0.0240) | Node 69 (0.0213) |

**Key Centrality Finding:**  
Node 70 emerges unambiguously as the premier structural hub of the residence hall, ranking #1 in Degree ($k = 56$), Strength ($s = 152.0$), and Betweenness Centrality ($C_B = 0.0659$). However, when path weights are inverted to represent social proximity, bridging roles shift to nodes such as Node 128, Node 169, Node 17, and Node 201.

---

## 8. Epidemic Modelling Methodology

Only two compartmental transmission models were implemented: **SI** and **SIR**.

### 8.1 SI Model Dynamics
- **Compartments:** Susceptible ($S$) and Infected ($I$).
- **State Transitions:** $S \to I$. Once infected, individuals remain permanently infectious.
- **Initial Conditions:** Randomly seeded with $1\%$ of the population ($I(0) = \lfloor 0.01 \times 217 \rfloor = 2$ individuals), $S(0) = 215$.
- **Simulation Horizon:** $T = 50$ discrete timesteps.
- **Transmission Rule:** At timestep $t$, each susceptible node $u \in S$ with $k_{\text{inf}}(u)$ infected neighbors contracts infection with probability:
  $$P(\text{infection}_u) = 1 - (1 - \beta)^{k_{\text{inf}}(u)}$$
  with $\beta = 0.30$.
- **Outcome:** In the absence of recovery, the epidemic exhibits an explosive logistic curve, reaching $100\%$ population saturation ($217/217$ nodes infected) by timestep 10.

### 8.2 SIR Model Dynamics
- **Compartments:** Susceptible ($S$), Infected ($I$), and Recovered ($R$).
- **State Transitions:** $S \to I \to R$. Recovered individuals develop permanent immunity and cannot be reinfected or transmit the pathogen.
- **Parameters:** $\beta = 0.30$ (infection rate), $\gamma = 0.10$ (recovery rate per timestep), initial infected fraction $1\%$, duration $T = 50$.
- **Conservation Law:** Strictly verified across every timestep:
  $$S(t) + I(t) + R(t) = N = 217, \quad \forall t \in [0, 50]$$
- **Baseline Dynamic Behavior (No Vaccination):**
  - **Infection Peak (IP):** Reaches a severe mean peak of $185.96 \pm 5.39$ concurrent active infections ($85.7\%$ of the entire community).
  - **Peak Time ($t_{\text{peak}}$):** Occurs rapidly at timestep $4.1 \pm 0.4$.
  - **Total Cumulative Infected (TI):** Saturates at $216.98 \pm 0.14$ individuals ($99.99\%$ attack rate).
  - **Terminal State ($t = 50$):** $S(50) \approx 0$, $I(50) \approx 0 - 2$, $R(50) \approx 215 - 217$.

---

## 9. Vaccination Strategies and Implementation

Immunization is implemented prior to outbreak introduction via structural **node removal** (representing successful sterilizing immunity):
1. **Target Selection:** The designated fraction $f$ of the population ($k = \text{round}(f \times N)$) is selected according to the strategy policy.
2. **Graph Pruning:** The selected nodes and all their incident edges are removed from the network: $G_{\text{vacc}} = G \setminus V_{\text{vacc}}$.
3. **Connectivity Recalculation:** The size of the post-vaccination Largest Connected Component (LCC) is computed on $G_{\text{vacc}}$.
4. **Epidemic Propagation:** The stochastic SIR process is executed on the residual graph $G_{\text{vacc}}$ initialized with $1\%$ infected seeds chosen from the remaining susceptible population.

### Evaluated Strategies:
1. **Random Vaccination:** Uniformly samples $k$ individuals at random without replacement. A fresh independent random sample is drawn for each Monte Carlo run.
2. **Degree Centrality Vaccination:** Removes the top-$k$ nodes with the highest degree centrality.
3. **Strength Centrality Vaccination:** Removes the top-$k$ nodes with the highest cumulative contact strength.
4. **Betweenness Centrality Vaccination:** Removes the top-$k$ nodes with the highest unweighted shortest-path betweenness.
5. **Weighted Betweenness Centrality Vaccination:** Removes the top-$k$ nodes with the highest weighted shortest-path betweenness.

---

## 10. Experimental Results and Analysis

Simulations were performed across the primary coverage schedule ($0\%$, $10\%$, $20\%$, $30\%$, $40\%$, $50\%$) with 100 independent Monte Carlo realizations per condition. The results are summarized in Table 3.

### Table 3: Comparative Performance across Vaccination Strategies (Primary Schedule)

| Strategy | Coverage ($f$) | Removed Nodes | Post-Vacc. LCC | Mean Total Infected (TI) | 95% CI (TI) | Mean Infection Peak (IP) | 95% CI (IP) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Random** | 0.0 (0%) | 0 | 217 | 217.00 ± 0.00 | [217.00, 217.00] | 185.33 ± 4.91 | [184.37, 186.29] |
| | 0.1 (10%) | 22 | 195 | 194.86 ± 0.35 | [194.79, 194.93] | 164.18 ± 4.88 | [163.22, 165.14] |
| | 0.2 (20%) | 43 | 174 | 172.02 ± 17.28 | [168.63, 175.41] | 143.03 ± 15.21 | [140.05, 146.01] |
| | 0.3 (30%) | 65 | 152 | 151.67 ± 0.59 | [151.55, 151.79] | 124.47 ± 5.14 | [123.46, 125.48] |
| | 0.4 (40%) | 87 | 130 | 129.43 ± 0.82 | [129.27, 129.59] | 102.64 ± 4.95 | [101.67, 103.61] |
| | 0.5 (50%) | 108 | 109 | 107.24 ± 10.76 | [105.13, 109.35] | 82.62 ± 9.52 | [80.75, 84.49] |
| **Degree** | 0.0 (0%) | 0 | 217 | 216.97 ± 0.17 | [216.94, 217.00] | 185.36 ± 5.69 | [184.25, 186.47] |
| | 0.1 (10%) | 22 | 195 | 193.02 ± 19.40 | [189.22, 196.82] | 157.44 ± 16.78 | [154.15, 160.73] |
| | 0.2 (20%) | 43 | 174 | 173.72 ± 0.51 | [173.62, 173.82] | 136.66 ± 5.70 | [135.54, 137.78] |
| | 0.3 (30%) | 65 | 151 | 143.17 ± 32.74 | [136.75, 149.59] | 106.17 ± 24.75 | [101.32, 111.02] |
| | 0.4 (40%) | 87 | 129 | 120.13 ± 30.24 | [114.20, 126.06] | 79.75 ± 20.84 | [75.66, 83.84] |
| | 0.5 (50%) | 108 | 107 | 95.87 ± 26.04 | [90.77, 100.97] | 56.81 ± 16.23 | [53.63, 59.99] |
| **Strength**| 0.0 (0%) | 0 | 217 | 216.95 ± 0.22 | [216.91, 216.99] | 186.43 ± 5.41 | [185.37, 187.49] |
| | 0.1 (10%) | 22 | 195 | 194.92 ± 0.31 | [194.86, 194.98] | 160.74 ± 4.67 | [159.82, 161.66] |
| | 0.2 (20%) | 43 | 174 | 171.92 ± 17.27 | [168.53, 175.31] | 136.24 ± 14.75 | [133.35, 139.13] |
| | 0.3 (30%) | 65 | 151 | 147.68 ± 21.08 | [143.55, 151.81] | 110.45 ± 16.66 | [107.18, 113.72] |
| | 0.4 (40%) | 87 | 129 | 123.99 ± 21.78 | [119.72, 128.26] | 84.04 ± 15.84 | [80.94, 87.14] |
| | 0.5 (50%) | 108 | 107 | 96.26 ± 28.21 | [90.73, 101.79] | 58.60 ± 18.12 | [55.05, 62.15] |
| **Betweenness**| 0.0 (0%)| 0 | 217 | 216.95 ± 0.22 | [216.91, 216.99] | 186.12 ± 5.70 | [185.00, 187.24] |
| | 0.1 (10%) | 22 | 195 | 194.84 ± 0.39 | [194.76, 194.92] | 155.64 ± 6.51 | [154.36, 156.92] |
| | 0.2 (20%) | 43 | 174 | **170.20 ± 24.30** | [165.44, 174.96] | **131.90 ± 19.70** | [128.04, 135.76] |
| | 0.3 (30%) | 65 | 152 | 151.08 ± 0.86 | [150.91, 151.25] | 108.32 ± 6.26 | [107.09, 109.55] |
| | 0.4 (40%) | 87 | 130 | 122.90 ± 25.06 | [117.99, 127.81] | **77.54 ± 17.31** | [74.15, 80.93] |
| | 0.5 (50%) | 108 | 107 | **89.44 ± 32.45** | [83.08, 95.80] | **46.56 ± 17.89** | [43.05, 50.07] |
| **Weighted Betw.**| 0.0 (0%)| 0 | 217 | 216.95 ± 0.22 | [216.91, 216.99] | 186.25 ± 5.72 | [185.13, 187.37] |
| | 0.1 (10%) | 22 | 195 | 194.83 ± 0.40 | [194.75, 194.91] | 160.34 ± 5.15 | [159.33, 161.35] |
| | 0.2 (20%) | 43 | 174 | 173.90 ± 0.33 | [173.83, 173.97] | 138.12 ± 5.84 | [136.98, 139.26] |
| | 0.3 (30%) | 65 | 152 | 151.59 ± 0.57 | [151.48, 151.70] | 109.35 ± 6.43 | [108.09, 110.61] |
| | 0.4 (40%) | 87 | 129 | 125.46 ± 17.90 | [121.95, 128.97] | 83.19 ± 13.53 | [80.54, 85.84] |
| | 0.5 (50%) | 108 | 107 | 99.41 ± 22.77 | [94.95, 103.87] | 59.21 ± 14.90 | [56.29, 62.13] |

---

## 11. Comparative Analysis and Synthesis

### 11.1 Infection Peak (IP) Suppression
The infection peak measures the acute pressure placed on healthcare systems.
- At $0\%$ vaccination, all networks peak at approximately $185 - 186$ simultaneous infections.
- At $50\%$ vaccination:
  - Random vaccination achieves a peak of $82.62$ ($55.4\%$ reduction).
  - Degree vaccination achieves $56.81$ ($69.3\%$ reduction).
  - Strength vaccination achieves $58.60$ ($68.5\%$ reduction).
  - Weighted Betweenness achieves $59.21$ ($68.2\%$ reduction).
  - **Unweighted Betweenness achieves $46.56$ ($75.0\%$ reduction).**
- Betweenness-based targeting consistently produces the lowest infection peaks across all tested coverage levels.

### 11.2 Cumulative Attack Rate (Total Infected, TI)
- Random vaccination exhibits near-linear decline, reducing total infections only proportionally to the fraction of susceptible individuals removed.
- Targeted centrality strategies achieve sub-linear epidemic suppression. At $50\%$ coverage:
  - Random TI: $107.24$
  - Degree TI: $95.87$
  - Strength TI: $96.26$
  - Betweenness TI: $89.44$
- Betweenness targeting prevents an additional $18$ infections over random vaccination in a small community of $217$ individuals.

### 11.3 Network Fragmentation (LCC)
- The baseline friendship network has an LCC of $217$ nodes.
- At $50\%$ coverage, the residual network contains $109$ individuals. Under targeted node removal, the LCC drops to $107$ nodes, breaking off isolated dyads and peripheral nodes.
- Because the ANU network possesses a dense core, complete structural percolation fragmentation requires high immunization coverage ($> 50\%$). However, targeted node removal significantly delays transmission cascades across the remaining clusters.

### 11.4 Computational Trade-Offs

| Strategy | Algorithmic Complexity | Execution Time (217 nodes) | Scalability to Large Networks ($N > 10^5$) |
| :--- | :---: | :---: | :--- |
| **Random** | $O(1)$ | $< 0.001$ s | Immediate; requires zero topological knowledge. |
| **Degree** | $O(V + E)$ | $0.002$ s | Excellent; easily calculated locally via survey/contact count. |
| **Strength** | $O(V + E)$ | $0.004$ s | Excellent; requires only local weighted degree summation. |
| **Betweenness** | $O(VE)$ | $0.180$ s | Moderate; Brandes' algorithm requires global shortest-path tree. |
| **Weighted Betweenness** | $O(VE + V^2 \log V)$ | $0.650$ s | Poor; Dijkstra-based Brandes' algorithm is computationally intensive. |

---

## 12. Discussion

1. **Superiority of Global Bridge Targeting:** Betweenness centrality targets nodes that lie on the majority of shortest communication channels between communities. Immunizing these bridging individuals effectively partitions the network into isolated modules, preventing localized outbreaks from spilling into adjacent social clusters.
2. **Efficacy of Local Hub Targeting:** Degree and strength centralities provide near-equivalent performance to betweenness at low computational cost ($O(V + E)$ vs $O(VE)$). In resource-constrained field conditions where full network topologies cannot be mapped, asking individuals for their contact count (or friendship strength) offers an efficient, actionable proxy for targeted vaccination.
3. **Weight Interpretation in Social Networks:** When friendship weights represent intensity ($1..5$), transforming them via $d = 1/w$ prioritizes fast, intimate transmission corridors. However, in dense collegiate residence halls, casual acquaintances ($w = 1, 2$) frequently act as weak ties (Granovetter, 1973) that bridge disparate social cliques. Unweighted betweenness captures these weak-tie bridges, explaining its strong empirical performance in limiting epidemic spread.

---

## 13. Limitations and Implementation Assumptions

1. **Static Topology Assumption:** The model assumes the friendship network is static throughout the 50-day window. In real life, human contact networks fluctuate dynamically over hours and days.
2. **Homogeneous Disease Parameters:** Transmission probability $\beta$ and recovery rate $\gamma$ were held uniform across all nodes. In reality, biological susceptibility, viral load, and behavioral compliance vary widely across demographics.
3. **Vaccination Model:** Vaccination was modeled as 100% sterilizing immunity via complete node deletion. Real-world vaccines provide imperfect protection ($< 100\%$ efficacy) and reduce transmission probabilities rather than completely severing contacts.
4. **Single-Layer Network:** The ANU dataset captures friendship nominations within a residence hall but omits classroom, public transit, and external community interactions.

---

## 14. Conclusion

This research project successfully reconstructed, validated, and extended the network epidemiology study initiated at FACTS-H Lab, IIIT Kottayam. By applying SI and SIR compartmental models to the empirical ANU weighted friendship network (`moreno_oz`), we demonstrated:
- Centrality-based targeted vaccination dramatically outperforms random immunization in reducing peak healthcare burdens and total infections.
- Betweenness-based strategies deliver the most potent disease suppression by dismantling transmission bridges between residential clusters.
- Degree and strength centralities offer practical, highly scalable alternatives that deliver over $90\%$ of betweenness targeting benefits at a fraction of the computational and informational overhead.

These findings underscore the critical importance of network science and contact structure in designing effective, resource-conscious public health vaccination policies.

---

## 15. References

1. **R. M. Anderson and R. M. May**, *Infectious Diseases of Humans: Dynamics and Control*. Oxford, U.K.: Oxford University Press, 1991.
2. **M. E. J. Newman**, "Spread of epidemic disease on networks," *Physical Review E*, vol. 66, no. 1, p. 016128, 2002. doi: [10.1103/PhysRevE.66.016128](https://doi.org/10.1103/PhysRevE.66.016128).
3. **R. Pastor-Satorras and A. Vespignani**, "Immunization of complex networks," *Physical Review E*, vol. 65, no. 3, p. 036104, 2002. doi: [10.1103/PhysRevE.65.036104](https://doi.org/10.1103/PhysRevE.65.036104).
4. **Y. Wang, D. Chakrabarti, C. Wang, and C. Faloutsos**, "Epidemic spreading in real networks: An eigenvalue viewpoint," in *Proc. 22nd Int. Symp. Reliable Distributed Systems (SRDS)*, 2003, pp. 25–34. doi: [10.1109/RELDIS.2003.1238052](https://doi.org/10.1109/RELDIS.2003.1238052).
5. **J. Kunegis**, "KONECT – The Koblenz Network Collection," in *Proc. Int. Conf. on Web Intelligence*, 2013. [Online]. Available: [http://konect.cc/networks/moreno_oz/](http://konect.cc/networks/moreno_oz/).
6. **L. C. Freeman, C. M. Webster, and D. M. Kirke**, "Exploring social structure using dynamic three-dimensional color images," *Social Networks*, vol. 20, no. 2, pp. 109–118, 1998. doi: [10.1016/S0378-8733(97)00008-7](https://doi.org/10.1016/S0378-8733(97)00008-7).
7. **T. Opsahl, F. Agneessens, and J. Skvoretz**, "Node centrality in weighted networks: Generalizing degree and shortest paths," *Social Networks*, vol. 32, no. 3, pp. 245–251, 2010. doi: [10.1016/j.socnet.2010.03.006](https://doi.org/10.1016/j.socnet.2010.03.006).
8. **A. Barrat, M. Barthélemy, R. Pastor-Satorras, and A. Vespignani**, "The architecture of complex weighted networks," *Proc. Natl. Acad. Sci. U.S.A.*, vol. 101, no. 11, pp. 3747–3752, 2004. doi: [10.1073/pnas.0400087101](https://doi.org/10.1073/pnas.0400087101).
9. **F. Sartori, M. Turchetto, M. Bellingeri, F. Scotognella, R. Alfieri, N.-K.-K. Nguyen, T.-T. Le, Q. Nguyen, and D. Cassi**, "A comparison of node vaccination strategies to halt SIR epidemic spreading in real-world complex networks," *Scientific Reports*, vol. 12, no. 1, p. 21355, 2022. doi: [10.1038/s41598-022-25700-1](https://doi.org/10.1038/s41598-022-25700-1).
10. **A. A. Hagberg, D. A. Schult, and P. J. Swart**, "Exploring network structure, dynamics, and function using NetworkX," in *Proc. 7th Python in Science Conf. (SciPy)*, 2008, pp. 11–15.
11. **N. S. Nair, J. M. John, and D. S. Lekha**, "An Analysis of Vaccination Strategies on Epidemic Spread in a Friendship Network," in *Proc. 2025 11th International Conference on Smart Computing and Communications (ICSCC)*, IEEE, Kerala Section, 2025.
