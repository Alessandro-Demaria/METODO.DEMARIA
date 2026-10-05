#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""===============================================================================

METODO DEMARIA® — COMPUTATIONAL VOYNICH ANALYSIS FRAMEWORK (Release v3.0)
Modulo: null_model_test.py (Test d'Ipotesi Nulla Stocastica Monte Carlo N=10.000)
Autore: Avv. Alessandro Demaria | Licenza: CC BY 4.0
Zenodo DOI: 10.5281/zenodo.23119964
===============================================================================
Descrizione:
  Test d'ipotesi nulla stocastica (Monte Carlo N=10.000) su sequenza shufflata.
  Calcola C_trans osservato, il baseline analitico condizionato dalle frequenze
  marginali degli stati, ed applica la correzione di Laplace per il p-value.
===============================================================================
"""

import os
import sys
from typing import Tuple
import numpy as np
import pandas as pd


def run_null_model_test(
    csv_path: str = "voynich_eva_tokens_extended.csv",
    output_summary_path: str = "null_model_test_results.csv",
    n_iterations: int = 10000,
    seed: int = 42,
) -> Tuple[float, np.ndarray, float]:
  """Esegue il test d'ipotesi nulla Monte Carlo (N=10.000) sul dataset per C_trans."""
  if not os.path.exists(csv_path):
    print(f"ERRORE CRITICO: File dataset '{csv_path}' non trovato.")
    sys.exit(1)

  rng = np.random.default_rng(seed)
  df = pd.read_csv(csv_path)

  # Aliasing e normalizzazione v3.0
  if "Token" not in df.columns and "EVA_Token" in df.columns:
    df["Token"] = df["EVA_Token"]
  if "Folio_Base" not in df.columns and "Folio" in df.columns:
    df["Folio_Base"] = df["Folio"].apply(
        lambda x: str(x).split(".")[0] if "." in str(x) else str(x)
    )

  if "Token" not in df.columns or "Folio_Base" not in df.columns:
    print("ERRORE CRITICO: Colonne necessarie non trovate nel dataset.")
    sys.exit(1)

  # Ordinamento sequenziale codicologico
  sort_cols = [
      col for col in ["Folio_Base", "line_id", "Record_ID"] if col in df.columns
  ]
  if sort_cols:
    df = df.sort_values(by=sort_cols).reset_index(drop=True)

  # Matrice di adiacenza delle transizioni valide (8/16 ammesse, Densità = 0.50)
  transition_matrix = np.array(
      [
          [1, 1, 0, 0],  # alpha -> alpha, beta
          [0, 1, 1, 0],  # beta  -> beta, delta
          [0, 0, 1, 1],  # delta -> delta, gamma
          [1, 0, 0, 1],  # gamma -> gamma, alpha
      ],
      dtype=float,
  )

  tokens = df["Token"].astype(str).to_numpy()
  folios = df["Folio_Base"].astype(str).to_numpy()

  demaria_map = {
      "o": 0,
      "a": 0,
      "e": 0,
      "c": 0,
      "h": 0,  # alpha (0)
      "k": 1,
      "t": 1,
      "p": 1,
      "f": 1,
      "s": 1,  # beta  (1)
      "r": 2,
      "l": 2,
      "q": 2,
      "y": 2,
      "d": 2,  # delta (2)
      "x": 3,
      "g": 3,
      "m": 3,
      "n": 3,
      "i": 3,  # gamma (3)
  }

  corpus_states = np.zeros(len(tokens), dtype=int)
  for idx, token_str in enumerate(tokens):
    mapped_values = [
        demaria_map[char] for char in token_str if char in demaria_map
    ]
    if len(mapped_values) > 0:
      counts = np.bincount(mapped_values, minlength=4)
      corpus_states[idx] = int(np.argmax(counts))
    else:
      corpus_states[idx] = 0

  # P0.3 FIX: Calcolo del Baseline Analitico teorico condizionato dalle Frequenze Marginali degli stati
  state_counts = np.bincount(corpus_states, minlength=4)
  state_probs = state_counts / len(corpus_states)
  theoretical_baseline_c_trans = float(
      np.sum(transition_matrix * np.outer(state_probs, state_probs))
  )

  def calculate_coherence_intra_folio(states_array: np.ndarray) -> float:
    valid_transitions = 0.0
    total_transitions = 0
    unique_folios = np.unique(folios)

    for fol in unique_folios:
      fol_mask = folios == fol
      fol_states = states_array[fol_mask]
      if len(fol_states) > 1:
        s_curr = fol_states[:-1]
        s_next = fol_states[1:]
        valid_transitions += float(np.sum(transition_matrix[s_curr, s_next]))
        total_transitions += len(s_curr)

    return (
        valid_transitions / total_transitions if total_transitions > 0 else 0.0
    )

  c_trans_obs = calculate_coherence_intra_folio(corpus_states)

  # Simulazione Monte Carlo
  null_scores = np.zeros(n_iterations, dtype=float)
  shuffled_states = corpus_states.copy()

  for i in range(n_iterations):
    rng.shuffle(shuffled_states)
    null_scores[i] = calculate_coherence_intra_folio(shuffled_states)

  mean_null = float(np.mean(null_scores))
  std_null = float(np.std(null_scores))
  max_null = float(np.max(null_scores))
  min_null = float(np.min(null_scores))

  count_exceed = int(np.sum(null_scores >= c_trans_obs))
  p_value = float((count_exceed + 1) / (n_iterations + 1))
  z_score = float((c_trans_obs - mean_null) / std_null) if std_null > 0 else 0.0
  p_str = f"p <= {p_value:.6f}" if count_exceed == 0 else f"p = {p_value:.6f}"

  results_df = pd.DataFrame([{
      "Dataset": os.path.basename(csv_path),
      "Total_Tokens": len(tokens),
      "Unique_Folios": len(np.unique(folios)),
      "Iterations": n_iterations,
      "C_Trans_Observed": c_trans_obs,
      "Theoretical_Marginal_Baseline": theoretical_baseline_c_trans,
      "Null_Mean": mean_null,
      "Null_Std": std_null,
      "Null_Min": min_null,
      "Null_Max": max_null,
      "Z_Score": z_score,
      "p_value": p_value,
      "p_value_formatted": p_str,
      "Release_Version": "v3.0",
  }])
  results_df.to_csv(output_summary_path, index=False)

  print("=========================================================")
  print("   METODO DEMARIA® v3.0 — NULL MODEL MONTE CARLO TEST    ")
  print("=========================================================")
  print(f"Dataset Analizzato:            {csv_path}")
  print(f"Token Analizzati:              {len(tokens):,}")
  print(f"C_trans Osservato:             {c_trans_obs:.6f}")
  print(f"Baseline Analitico Teorico:    {theoretical_baseline_c_trans:.6f}")
  print(f"Media Modello Nullo Stocastico:{mean_null:.6f}")
  print(f"Z-Score Significativita:       {z_score:.4f}")
  print(f"p-value Significativita:       {p_str}")
  print(f"Report Esportato su:           {output_summary_path}")
  print("=========================================================")

  return c_trans_obs, null_scores, p_value


if __name__ == "__main__":
  run_null_model_test()