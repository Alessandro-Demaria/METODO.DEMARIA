#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
METODO DEMARIA® — COMPUTATIONAL VOYNICH ANALYSIS FRAMEWORK (Release v3.0)
Modulo: null_model_test.py (Test d'Ipotesi Nulla Stocastica Gerarchica N=10.000)
Autore: Avv. Alessandro Demaria | Licenza: CC BY 4.0
Zenodo DOI: 10.5281/zenodo.23119964
===============================================================================
Descrizione:
  Test d'ipotesi nulla stocastica gerarchica (Global Shuffle e Intra-Folio Shuffle).
  Calcola C_trans osservato, il baseline analitico globale e condizionato per folio,
  ed esporta Z-score e p-value distinti per ciascun livello nullo (Null A e Null B).
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
  """Esegue il test d'ipotesi nulla stocastica gerarchica con metriche distinte per Null A e Null B."""
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

  sort_cols = [
      col for col in ["Folio_Base", "line_id", "Record_ID"] if col in df.columns
  ]
  if sort_cols:
    df = df.sort_values(by=sort_cols).reset_index(drop=True)

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

  # 1. Baseline Analitico teorico Globale
  state_counts = np.bincount(corpus_states, minlength=4)
  state_probs = state_counts / len(corpus_states)
  theoretical_global_baseline = float(
      np.sum(transition_matrix * np.outer(state_probs, state_probs))
  )

  # 1b. FIX REVIEWER 2 (Punto 6): Baseline Analitico Condizionato per Folio
  unique_folios = np.unique(folios)
  folio_baselines = []
  folio_weights = []

  for fol in unique_folios:
    fol_mask = folios == fol
    fol_s = corpus_states[fol_mask]
    if len(fol_s) > 1:
      counts_f = np.bincount(fol_s, minlength=4)
      probs_f = counts_f / len(fol_s)
      b_f = float(np.sum(transition_matrix * np.outer(probs_f, probs_f)))
      folio_baselines.append(b_f)
      folio_weights.append(len(fol_s) - 1)

  folio_conditioned_baseline = (
      float(np.average(folio_baselines, weights=folio_weights))
      if folio_weights
      else theoretical_global_baseline
  )

  def calculate_coherence_intra_folio(states_array: np.ndarray) -> float:
    valid_transitions = 0.0
    total_transitions = 0
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

  # 2. Null Model A: Global Shuffle
  null_scores_global = np.zeros(n_iterations, dtype=float)
  shuffled_states_g = corpus_states.copy()
  for i in range(n_iterations):
    rng.shuffle(shuffled_states_g)
    null_scores_global[i] = calculate_coherence_intra_folio(shuffled_states_g)

  mean_null_global = float(np.mean(null_scores_global))
  std_null_global = float(np.std(null_scores_global))
  count_exceed_g = int(np.sum(null_scores_global >= c_trans_obs))
  p_val_global = float((count_exceed_g + 1) / (n_iterations + 1))
  z_score_global = (
      float((c_trans_obs - mean_null_global) / std_null_global)
      if std_null_global > 0
      else 0.0
  )
  p_str_global = (
      f"p <= {p_val_global:.6f}"
      if count_exceed_g == 0
      else f"p = {p_val_global:.6f}"
  )

  # 3. Null Model B: Intra-Folio Shuffle
  null_scores_intra = np.zeros(n_iterations, dtype=float)
  for i in range(n_iterations):
    shuffled_states_f = corpus_states.copy()
    for fol in unique_folios:
      mask = folios == fol
      idx_f = np.flatnonzero(mask)
      shuffled_states_f[idx_f] = rng.permutation(shuffled_states_f[idx_f])
    null_scores_intra[i] = calculate_coherence_intra_folio(shuffled_states_f)

  mean_null_intra = float(np.mean(null_scores_intra))
  std_null_intra = float(np.std(null_scores_intra))

  # FIX REVIEWER 2 (Punto 3): Calcolo distinto di Z-Score e p-value per il Null B (Intra-Folio)
  count_exceed_i = int(np.sum(null_scores_intra >= c_trans_obs))
  p_val_intra = float((count_exceed_i + 1) / (n_iterations + 1))
  z_score_intra = (
      float((c_trans_obs - mean_null_intra) / std_null_intra)
      if std_null_intra > 0
      else 0.0
  )
  p_str_intra = (
      f"p <= {p_val_intra:.6f}"
      if count_exceed_i == 0
      else f"p = {p_val_intra:.6f}"
  )

  analytic_mc_delta = float(
      abs(theoretical_global_baseline - mean_null_global)
  )

  results_df = pd.DataFrame([{
      "Dataset": os.path.basename(csv_path),
      "Total_Tokens": len(tokens),
      "Unique_Folios": len(unique_folios),
      "Iterations": n_iterations,
      "C_Trans_Observed": c_trans_obs,
      "Theoretical_Global_Baseline": theoretical_global_baseline,
      "Folio_Conditioned_Baseline": folio_conditioned_baseline,
      "Global_Null_Mean": mean_null_global,
      "Global_Null_Std": std_null_global,
      "Global_Z_Score": z_score_global,
      "Global_p_value": p_val_global,
      "Global_p_formatted": p_str_global,
      "Intra_Folio_Null_Mean": mean_null_intra,
      "Intra_Folio_Null_Std": std_null_intra,
      "Intra_Folio_Z_Score": z_score_intra,
      "Intra_Folio_p_value": p_val_intra,
      "Intra_Folio_p_formatted": p_str_intra,
      "Analytic_MC_Delta": analytic_mc_delta,
      "Release_Version": "v3.0",
  }])
  results_df.to_csv(output_summary_path, index=False)

  print("=========================================================")
  print("   METODO DEMARIA® v3.0 — NULL MODEL MONTE CARLO TEST    ")
  print("=========================================================")
  print(f"Dataset Analizzato:            {csv_path}")
  print(f"Token Analizzati:              {len(tokens):,}")
  print(f"C_trans Osservato:             {c_trans_obs:.6f}")
  print(f"Baseline Analitico Globale:    {theoretical_global_baseline:.6f}")
  print(f"Baseline Condizionato Folio:   {folio_conditioned_baseline:.6f}")
  print("---------------------------------------------------------")
  print(
      f"Null A (Global Shuffle):       Mean={mean_null_global:.6f} |"
      f" Z={z_score_global:.4f} | {p_str_global}"
  )
  print(
      f"Null B (Intra-Folio Shuffle):  Mean={mean_null_intra:.6f} |"
      f" Z={z_score_intra:.4f} | {p_str_intra}"
  )
  print(f"Analytic vs MC Delta:          {analytic_mc_delta:.6f}")
  print(f"Report Esportato su:           {output_summary_path}")
  print("=========================================================")

  return c_trans_obs, null_scores_global, p_val_global


if __name__ == "__main__":
  run_null_model_test()