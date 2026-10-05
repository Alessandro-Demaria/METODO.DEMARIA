#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""===============================================================================

METODO DEMARIA® — COMPUTATIONAL VOYNICH ANALYSIS FRAMEWORK (Release v3.0)
Modulo: null_model_test.py (Test d'Ipotesi Nulla Stocastica Gerarchica a 3
Livelli N=10.000)
Autore: Avv. Alessandro Demaria | Licenza: CC BY 4.0
Zenodo DOI: 10.5281/zenodo.23119964
===============================================================================
Descrizione:
  Test d'ipotesi nulla stocastica gerarchica a 3 livelli (Global, Intra-Folio e
  Intra-Line Shuffle). Calcola C_trans osservato, baseline analitiche ed
  esporta
  Z-score, p-value e delta Monte Carlo per ciascun livello nullo.
===============================================================================
"""

import os
import sys
from typing import Any, Dict
import numpy as np
import pandas as pd


def run_null_model_test(
    csv_path: str = "voynich_eva_tokens_extended.csv",
    output_summary_path: str = "null_model_test_results.csv",
    n_iterations: int = 10000,
    seed: int = 42,
) -> Dict[str, Any]:
  """Esegue il test gerarchico a 3 livelli (Global, Intra-Folio, Intra-Line) e restituisce il dizionario completo."""
  if not os.path.exists(csv_path):
    print(f"ERRORE CRITICO: File dataset '{csv_path}' non trovato.")
    sys.exit(1)

  rng = np.random.default_rng(seed)
  df = pd.read_csv(csv_path)

  # Normalizzazione colonne v3.0
  if "Token" not in df.columns and "EVA_Token" in df.columns:
    df["Token"] = df["EVA_Token"]
  if "Folio_Base" not in df.columns and "Folio" in df.columns:
    df["Folio_Base"] = df["Folio"].apply(
        lambda x: str(x).split(".")[0] if "." in str(x) else str(x)
    )
  if "line_id" not in df.columns and "Line" in df.columns:
    df["line_id"] = df["Line"]

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
  lines = (
      df["line_id"].astype(str).to_numpy()
      if "line_id" in df.columns
      else np.zeros(len(tokens), dtype=str)
  )

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

  # 1. Null A: Global Shuffle
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

  # 2. Null B: Intra-Folio Shuffle
  null_scores_intra_folio = np.zeros(n_iterations, dtype=float)
  for i in range(n_iterations):
    shuffled_states_f = corpus_states.copy()
    for fol in unique_folios:
      mask = folios == fol
      idx_f = np.flatnonzero(mask)
      shuffled_states_f[idx_f] = rng.permutation(shuffled_states_f[idx_f])
    null_scores_intra_folio[i] = calculate_coherence_intra_folio(
        shuffled_states_f
    )

  mean_null_folio = float(np.mean(null_scores_intra_folio))
  std_null_folio = float(np.std(null_scores_intra_folio))
  count_exceed_f = int(np.sum(null_scores_intra_folio >= c_trans_obs))
  p_val_folio = float((count_exceed_f + 1) / (n_iterations + 1))
  z_score_folio = (
      float((c_trans_obs - mean_null_folio) / std_null_folio)
      if std_null_folio > 0
      else 0.0
  )

  # 3. Null C: Intra-Line Shuffle (SOLUZIONE P0.1)
  null_scores_intra_line = np.zeros(n_iterations, dtype=float)
  folio_line_ids = np.array([f"{f}_{l}" for f, l in zip(folios, lines)])
  unique_lines = np.unique(folio_line_ids)

  for i in range(n_iterations):
    shuffled_states_l = corpus_states.copy()
    for l_id in unique_lines:
      mask = folio_line_ids == l_id
      idx_l = np.flatnonzero(mask)
      if len(idx_l) > 1:
        shuffled_states_l[idx_l] = rng.permutation(shuffled_states_l[idx_l])
    null_scores_intra_line[i] = calculate_coherence_intra_folio(
        shuffled_states_l
    )

  mean_null_line = float(np.mean(null_scores_intra_line))
  std_null_line = float(np.std(null_scores_intra_line))
  count_exceed_l = int(np.sum(null_scores_intra_line >= c_trans_obs))
  p_val_line = float((count_exceed_l + 1) / (n_iterations + 1))
  z_score_line = (
      float((c_trans_obs - mean_null_line) / std_null_line)
      if std_null_line > 0
      else 0.0
  )

  global_analytic_mc_delta = float(
      abs(theoretical_global_baseline - mean_null_global)
  )
  folio_analytic_mc_delta = float(
      abs(folio_conditioned_baseline - mean_null_folio)
  )

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
      "Global_Analytic_MC_Delta": global_analytic_mc_delta,
      "Folio_Analytic_MC_Delta": folio_analytic_mc_delta,
      "Release_Version": "v3.0",
  }

  pd.DataFrame([metrics]).to_csv(output_summary_path, index=False)
  return metrics