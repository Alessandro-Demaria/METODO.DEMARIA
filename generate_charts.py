"""
===============================================================================
METODO DEMARIA® — GENERATORE DI GRAFICI EMPIRICI AD ALTA RISOLUZIONE (v3.2)
===============================================================================
Modulo: generate_charts.py
Autore e Inventore: Avv. Alessandro Demaria
PEC: avv.alessandrodemaria@pec.it
DOI UFFICIALE: 10.5281/zenodo.23199718
Licenza: CC BY 4.0
===============================================================================
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def generate_empirical_charts(
    c_obs,
    global_scores,
    line_scores,
    double_scores,
    robustness_df,
    output_prefix="audit_master",
):
  """Genera i 3 grafici empirici ad alta risoluzione (300 DPI) basati esclusivamente sui punteggi reali calcolati dalle 10.000 simulazioni Monte Carlo."""
  plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

  # ---------------------------------------------------------------------------
  # GRAFICO 1: Modelli Nulli Gerarchici (Global vs Intra-Line vs Observed)
  # ---------------------------------------------------------------------------
  fig, ax = plt.subplots(figsize=(10, 6), dpi=300)

  ax.hist(
      global_scores,
      bins=50,
      alpha=0.6,
      color="#1f77b4",
      label="Global Null Model (Corpus Permutation)",
      edgecolor="black",
      linewidth=0.5,
  )
  ax.hist(
      line_scores,
      bins=50,
      alpha=0.6,
      color="#2ca02c",
      label="Intra-Line Null Model (Within-Line Permutation)",
      edgecolor="black",
      linewidth=0.5,
  )

  ax.axvline(
      c_obs,
      color="#d62728",
      linestyle="--",
      linewidth=2.5,
      label=f"Observed Real Coherence (C_obs = {c_obs:.6f})",
  )

  ax.set_title(
      "METODO DEMARIA® v3.2 — Hierarchical Null Models Distribution (Empirical"
      " N=10000)",
      fontsize=12,
      fontweight="bold",
  )
  ax.set_xlabel("Syntactic Coherence (C_raw)", fontsize=11)
  ax.set_ylabel("Frequency", fontsize=11)
  ax.legend(loc="upper left", frameon=True)
  plt.tight_layout()

  chart1_path = f"{output_prefix}_null_models_empirical.png"
  plt.savefig(chart1_path)
  plt.close()
  print(f"[CHART] Grafico Null Models generato: {chart1_path}")

  # ---------------------------------------------------------------------------
  # GRAFICO 2: Isomorphic Double Randomization Test
  # ---------------------------------------------------------------------------
  fig, ax = plt.subplots(figsize=(10, 6), dpi=300)

  ax.hist(
      double_scores,
      bins=50,
      alpha=0.7,
      color="#9467bd",
      label="Isomorphic Double Randomization Null",
      edgecolor="black",
      linewidth=0.5,
  )
  ax.axvline(
      c_obs,
      color="#d62728",
      linestyle="--",
      linewidth=2.5,
      label=f"Observed Real Coherence (C_obs = {c_obs:.6f})",
  )

  double_mean = np.mean(double_scores)
  ax.axvline(
      double_mean,
      color="#8c564b",
      linestyle=":",
      linewidth=2.0,
      label=f"Double Null Mean ({double_mean:.6f})",
  )

  ax.set_title(
      "METODO DEMARIA® v3.2 — Double Randomization Adversarial Test (Empirical"
      " N=10000)",
      fontsize=12,
      fontweight="bold",
  )
  ax.set_xlabel("Syntactic Coherence (C_raw)", fontsize=11)
  ax.set_ylabel("Frequency", fontsize=11)
  ax.legend(loc="upper right", frameon=True)
  plt.tight_layout()

  chart2_path = f"{output_prefix}_double_randomization_empirical.png"
  plt.savefig(chart2_path)
  plt.close()
  print(f"[CHART] Grafico Double Randomization generato: {chart2_path}")

  # ---------------------------------------------------------------------------
  # GRAFICO 3: Robustness & Noise Stress Test
  # ---------------------------------------------------------------------------
  fig, ax = plt.subplots(figsize=(10, 6), dpi=300)

  noise_pcts = [int(x * 100) for x in robustness_df["noise_level"]]
  retentions = robustness_df["retention_pct"]

  ax.plot(
      noise_pcts,
      retentions,
      marker="o",
      linewidth=2.5,
      color="#ff7f0e",
      label="Coherence Retention %",
  )

  for x, y in zip(noise_pcts, retentions):
    ax.annotate(
        f"{y:.2f}%",
        (x, y),
        textcoords="offset points",
        xytext=(0, 8),
        ha="center",
        fontsize=9,
        fontweight="bold",
    )

  ax.set_title(
      "METODO DEMARIA® v3.2 — Noise Stress Test & Sensor Resilience Curve",
      fontsize=12,
      fontweight="bold",
  )
  ax.set_xlabel("Injected Transcription Noise (%)", fontsize=11)
  ax.set_ylabel("Coherence Retention (%)", fontsize=11)
  ax.set_ylim(75, 105)
  ax.legend(loc="lower left", frameon=True)
  plt.tight_layout()

  chart3_path = f"{output_prefix}_robustness_stress_test.png"
  plt.savefig(chart3_path)
  plt.close()
  print(f"[CHART] Grafico Stress Test generato: {chart3_path}")


if __name__ == "__main__":
  print("Modulo generate_charts.py pronto all'uso e bonificato (v3.2 Canonico).")