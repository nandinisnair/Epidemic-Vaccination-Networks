"""
Evaluation Metrics Module.
Computes and aggregates Total Infected (TI), Infection Peak (IP), and
Largest Connected Component (LCC) across experimental simulation runs.
"""

from typing import List, Dict, Any
import numpy as np
import pandas as pd


class Evaluator:
    """Calculates statistical summary tables, confidence intervals, and metrics."""

    @staticmethod
    def calculate_statistics(values: np.ndarray, confidence: float = 0.95) -> Dict[str, float]:
        """
        Computes mean, standard deviation, min, max, and parametric confidence interval.
        """
        vals = np.array(values, dtype=float)
        n = len(vals)
        if n == 0:
            return {
                "mean": 0.0,
                "std": 0.0,
                "min": 0.0,
                "max": 0.0,
                "ci_lower": 0.0,
                "ci_upper": 0.0,
            }

        mean = float(np.mean(vals))
        std = float(np.std(vals, ddof=1)) if n > 1 else 0.0
        vmin = float(np.min(vals))
        vmax = float(np.max(vals))

        # 95% CI half-width
        z = 1.96
        margin = z * (std / np.sqrt(n)) if n > 0 else 0.0
        return {
            "mean": mean,
            "std": std,
            "min": vmin,
            "max": vmax,
            "ci_lower": max(0.0, mean - margin),
            "ci_upper": mean + margin,
        }

    @staticmethod
    def compile_experiment_summary(
        results_records: List[Dict[str, Any]]
    ) -> pd.DataFrame:
        """
        Converts raw per-run records into an aggregated summary DataFrame.
        Expected keys in each record:
        ['strategy', 'coverage', 'run_idx', 'ti', 'ip', 'lcc']
        """
        df = pd.DataFrame(results_records)
        grouped = df.groupby(["strategy", "coverage"])

        summary_rows = []
        for (strategy, coverage), group in grouped:
            ti_stats = Evaluator.calculate_statistics(group["ti"].values)
            ip_stats = Evaluator.calculate_statistics(group["ip"].values)
            lcc_val = group["lcc"].iloc[0]  # deterministic for targeted, or mean for random

            summary_rows.append({
                "strategy": strategy,
                "coverage": coverage,
                "LCC": lcc_val,
                "TI_mean": round(ti_stats["mean"], 2),
                "TI_std": round(ti_stats["std"], 2),
                "TI_ci_lower": round(ti_stats["ci_lower"], 2),
                "TI_ci_upper": round(ti_stats["ci_upper"], 2),
                "IP_mean": round(ip_stats["mean"], 2),
                "IP_std": round(ip_stats["std"], 2),
                "IP_ci_lower": round(ip_stats["ci_lower"], 2),
                "IP_ci_upper": round(ip_stats["ci_upper"], 2),
                "runs_count": len(group),
            })

        summary_df = pd.DataFrame(summary_rows)
        # Sort by strategy and coverage
        summary_df.sort_values(by=["strategy", "coverage"], inplace=True)
        return summary_df
