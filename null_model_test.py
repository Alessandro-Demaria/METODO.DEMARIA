#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
METODO DEMARIA® — COMPUTATIONAL VOYNICH ANALYSIS FRAMEWORK (Release v3.0 Ultra-Fast)
Modulo: null_model_test.py (Test d'Ipotesi Nulla Gerarchica Vettorizzata N=10.000)
Autore: Avv. Alessandro Demaria | Licenza: CC BY 4.0
Zenodo DOI: 10.5281/zenodo.23119964
===============================================================================
"""

import os
import sys
import time
from typing import Dict, Any
import numpy as np
import pandas as pd


def run_null_model_test(
    csv_path: str = "voynich_eva_tokens_extended.csv",
    output_summary_path: str = "null_model_test_results.csv",
    n_iterations: int = 10000,
    seed: int = 42,
) -> Dict[str, Any]:
  if not os.path.exists(csv_path):
    print(f"ERRORE CRITICO: File dataset '{csv_path}' non trovato.", flush=True)
    sys.exit(1)

  rng = np.random.default_rng(seed)
  df = pd.read_csv(csv_path)

  # Standardizzazione Token ed Estrazione Folio / Riga Reale EVA
  if "Token" not in df.columns and "EVA_Token" in df.columns:
    df["Token"] = df["EVA_Token"]

  if "Folio" in df.columns:
    # Estrazione del folio base (es. 'f1r.1,@P0' -> 'f1r')
    df["Folio_Base"] = df["Folio"].apply(
        lambda x: str(x).split(".")[0] if "." in str(x) else str(x)
    )
    # Estrazione della VERA riga EVA originale (es. 'f1r.1,@P0' -> '1')
    df["line_id"] = df["Folio"].apply(
        lambda x: str(x).split(".")[1].split(",")[0]
        if "." in str(x) and len(str(x).split(".")) > 1
        else "1"
    )
  else:
    print("ERRORE CRITICO: Colonna 'Folio' mancante nel CSV.", flush=True)
    sys.exit(1)

  sort_cols = [
      col for col in ["Folio_Base", "line_id", "Record_ID"] if col in df.columns
  ]
  if sort_cols:
    df = df.sort_values(by=sort_cols).reset_index(drop=True)

  transition_matrix = np.array(
      [
          [1, 1, 0, 0],
          [0, 1, 1, 0],
          [0, 0, 1, 1],
          [1, 0, 0, 1],
      ],
      dtype=float,
  )

  tokens = df["Token"].astype(str).to_numpy()
  folios = df["Folio_Base"].astype(str).to_numpy()
  lines = df["line_id"].astype(str).to_numpy()

  demaria_map = {
      "o": 0, "a": 0, "e": 0, "c": 0, "h": 0,
      "k": 1, "t": 1, "p": 1, "f": 1, "s": 1,
      "r": 2, "l": 2, "q": 2, "y": 2, "d": 2,
      "x": 3, "g": 3, "m": 3, "n": 3, "i": 3,
  }

  corpus_states = np.zeros(len(tokens), dtype=int)
  for idx, token_str in enumerate(tokens):
    mapped_values = [
        demaria_map[char] for char in token_str if char in demaria_map
    ]
    if len(mapped_values) > 0:
      counts = np.bincount(mapped_values, minlength=4)
      corpus_states[idx] = int(np.argmax(counts))

  same_folio_mask = folios[:-1] == folios[1:]

  def calc_fast(states_arr: np.ndarray) -> float:
    s_curr = states_arr[:-1][same_folio_mask]
    s_next = states_arr[1:][same_folio_mask]
    return float(np.mean(transition_matrix[s_curr, s_next]))

  c_trans_obs = calc_fast(corpus_states)

  # Baseline analitiche
  state_counts = np.bincount(corpus_states, minlength=4)
  state_probs = state_counts / len(corpus_states)
  theoretical_global_baseline = float(
      np.sum(transition_matrix * np.outer(state_probs, state_probs))
  )

  unique_folios = np.unique(folios)
  folio_baselines, folio_weights = [], []
  for fol in unique_folios:
    fol_mask = folios == fol
    fol_s = corpus_states[fol_mask]
    if len(fol_s) > 1:
      counts_f = np.bincount(fol_s, minlength=4)
      probs_f = counts_f / len(fol_s)
      folio_baselines.append(float(np.sum(transition_matrix * np.outer(probs_f, probs_f))))
      folio_weights.append(len(fol_s) - 1)

  folio_conditioned_baseline = (
      float(np.average(folio_baselines, weights=folio_weights))
      if folio_weights
      else theoretical_global_baseline
  )

  folio_indices = [np.flatnonzero(folios == fol) for fol in unique_folios]
  folio_line_ids = np.array([f"{f}_{l}" for f, l in zip(folios, lines)])
  unique_lines = np.unique(folio_line_ids)
  line_indices = [np.flatnonzero(folio_line_ids == lid) for lid in unique_lines if np.sum(folio_line_ids == lid) > 1]

  # 1. Null A: Global Shuffle
  print("      -> Esecuzione Null A (Global Shuffle)...", flush=True)
  null_scores_global = np.zeros(n_iterations, dtype=float)
  shuffled_g = corpus_states.copy()
  for i in range(n_iterations):
    rng.shuffle(shuffled_g)
    null_scores_global[i] = calc_fast(shuffled_g)

  mean_null_global = float(np.mean(null_scores_global))
  std_null_global = float(np.std(null_scores_global))
  p_val_global = float((np.sum(null_scores_global >= c_trans_obs) + 1) / (n_iterations + 1))
  z_score_global = float((c_trans_obs - mean_null_global) / std_null_global) if std_null_global > 0 else 0.0

  # 2. Null B: Intra-Folio Shuffle
  print("      -> Esecuzione Null B (Intra-Folio Shuffle)...", flush=True)
  null_scores_folio = np.zeros(n_iterations, dtype=float)
  for i in range(n_iterations):
    shuffled_f = corpus_states.copy()
    for idxs in folio_indices:
      shuffled_f[idxs] = rng.permutation(shuffled_f[idxs])
    null_scores_folio[i] = calc_fast(shuffled_f)

  mean_null_folio = float(np.mean(null_scores_folio))
  std_null_folio = float(np.std(null_scores_folio))
  p_val_folio = float((np.sum(null_scores_folio >= c_trans_obs) + 1) / (n_iterations + 1))
  z_score_folio = float((c_trans_obs - mean_null_folio) / std_null_folio) if std_null_folio > 0 else 0.0

  # 3. Null C: Intra-Line Shuffle (Sulle VERE linee EVA)
  print("      -> Esecuzione Null C (Intra-Line Shuffle su linee reali EVA)...", flush=True)
  null_scores_line = np.zeros(n_iterations, dtype=float)
  for i in range(n_iterations):
    shuffled_l = corpus_states.copy()
    for idxs in line_indices:
      shuffled_l[idxs] = rng.permutation(shuffled_l[idxs])
    null_scores_line[i] = calc_fast(shuffled_l)

  mean_null_line = float(np.mean(null_scores_line))
  std_null_line = float(np.std(null_scores_line))
  p_val_line = float((np.sum(null_scores_line >= c_trans_obs) + 1) / (n_iterations + 1))
  z_score_line = float((c_trans_obs - mean_null_line) / std_null_line) if std_null_line > 0 else 0.0

  metrics = {
      "Dataset": os.path.basename(csv_path),
      "Total_Tokens": len(tokens),
      "Unique_Folios": len(unique_folios),
      "Iterations": n_iterations,
      "C_Trans_Observed": c_trans_obs,
      "Theoretical_Global_Baseline": theoretical_global_baseline,
      "Folio_Conditioned_Baseline": folio_conditioned_baseline,
      "Global_Null_Mean": mean_null_global,
      "Global_Z_Score": z_score_global,
      "Global_p_value": p_val_global,
      "Intra_Folio_Null_Mean": mean_null_folio,
      "Intra_Folio_Z_Score": z_score_folio,
      "Intra_Folio_p_value": p_val_folio,
      "Intra_Line_Null_Mean": mean_null_line,
      "Intra_Line_Z_Score": z_score_line,
      "Intra_Line_p_value": p_val_line,
      "Global_Analytic_MC_Delta": float(abs(theoretical_global_baseline - mean_null_global)),
      "Folio_Analytic_MC_Delta": float(abs(folio_conditioned_baseline - mean_null_folio)),
      "Release_Version": "v3.0",
  }

  pd.DataFrame([metrics]).to_csv(output_summary_path, index=False)
  return metrics

if __name__ == "__main__":
  run_null_model_test()