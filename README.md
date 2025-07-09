<h1 align="center">🧠 Vaccination Strategies in Epidemic Networks</h1>

<p align="center">
  <strong>Code & Results for ICSCC 2025 Research Paper</strong><br>
  <em>“An Analysis of Vaccination Strategies on Epidemic Spread in a Friendship Network”</em>
</p>

---

### 📄 Abstract

This project explores the use of centrality-based vaccination strategies in reducing epidemic spread over a social network.  
Using the SIR model, we analyze and compare Degree, Closeness, and Betweenness centrality measures to identify the most effective strategy for immunizing key nodes in a network.

> ❗ Full paper not included due to copyright restrictions.  
> 📌 [Link to official paper will be provided once published]

---

### 📁 Repository Structure

| Folder/File        | Description                                                  |
|--------------------|--------------------------------------------------------------|
| `code/`            | Python scripts and Jupyter notebooks for simulation          |
| `data/`            | Network dataset (e.g., friendship graph in CSV format)       |
| `results/`         | Visuals and CSVs generated from simulation                   |
| `citation.bib`     | BibTeX citation for referencing this research                |
| `README.md`        | Project documentation and instructions                       |

---

### 📊 Results Summary

The `results/` folder includes output plots and statistics from experiments:

| File Name                    | Description                                                                 |
|-----------------------------|-----------------------------------------------------------------------------|
| `infection_curve.png`       | Line graph showing infection over time for each strategy                    |
| `centrality_comparison.png` | Bar chart comparing effectiveness of Degree, Closeness, and Betweenness     |
| `sir_output.csv`            | Tabular SIR values per timestep                                             |
| `network_visual.png`        | Graph of the network with vaccinated nodes highlighted                      |
| `summary_stats.txt`         | Final stats: peak infection day, total infected, strategy used              |

---

### 🛠️ Tools & Libraries

- **Python 3**
- **NetworkX** for graph modeling
- **Matplotlib** for plotting
- **Pandas** for CSV and data analysis
- **Jupyter Notebooks**

---

### 📚 Citation

```bibtex
@inproceedings{nair2025vaccination,
  title={An Analysis of Vaccination Strategies on Epidemic Spread in a Friendship Network},
  author={Nandini Sreejit Nair},
  booktitle={International Conference on Smart Computing and Communication (ICSCC)},
  year={2025}
}
