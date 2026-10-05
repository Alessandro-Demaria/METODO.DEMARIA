#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""===============================================================================

METODO DEMARIA® — COMPUTATIONAL VOYNICH ANALYSIS FRAMEWORK (Release v3.0)
Modulo: double_randomization_test.py (Test di Doppia Randomizzazione
Avversariale)
Autore: Avv. Alessandro Demaria | Licenza: CC BY 4.0
Zenodo DOI: 10.5281/zenodo.23119964
===============================================================================
Descrizione:
  Suite per il test di doppia randomizzazione avversariale (Tier B / CR-05).
  Esegue la ricanalizzazione combinata del corpus:
  1. Permutazione stocastica della sequenza dei token entro ciascun folio.
  2. Rimescolamento casuale delle rigide partizioni alfabetiche (5-5-5-5).
  Calcola il p-value con correzione di Laplace e la significatività Z-Score.
===============================================================================
"""

import os
import sys
import time
from typing import Any, Dict
import numpy as np
import pandas as pd


class DoubleRandomizationTester:
  """Suite per il test di doppia randomizzazione avversariale su dati reali (Release v3.0).

  Garantisce l'assenza di inter-folio leakage ed applica l'ordinamento
  codicologico esplicito.
  """

  TRANSITION_MATRIX: np.ndarray = np.array(
      [
          [1, 1, 0, 0],  # alpha -> alpha, beta
          [0, 1, 1, 0],  # beta  -> beta, delta
          [0, 0, 1, 1],  # delta -> delta, gamma
          [1, 0, 0, 1],  # gamma -> gamma, alpha
      ],
      dtype=np.int8,
  )

  EVA_20_ALPHABET: np.ndarray = np.array([
      'o',
      'a',
      'e',
      'c',
      'h',
      'k',
      't',
      'p',
      'f',
      's',
      'r',
      'l',
      'q',
      'y',
      'd',
      'x',
      'g',
      'm',
      'n',
      'i',
  ])

  DEMARIA_MAP: Dict[str, int] = {
      'o': 0,
      'a': 0,
      'e': 0,
      'c': 0,
      'h': 0,  # alpha (0)
      'k': 1,
      't': 1,
      'p': 1,
      'f': 1,
      's': 1,  # beta  (1)
      'r': 2,
      'l': 2,
      'q': 2,
      'y': 2,
      'd': 2,  # delta (2)
      'x': 3,
      'g': 3,
      'm': 3,
      'n': 3,
      'i': 3,  # gamma (3)
  }

  def __init__(self, seed: int = 42) -> None:
    self.seed = seed
    self.rng = np.random.default_rng(self.seed)
    self.version = 'v3.0'

  def _map_tokens_to_states(
      self, tokens: np.ndarray, mapping_dict: Dict[str, int]
  ) -> np.ndarray:
    corpus_states = np.zeros(len(tokens), dtype=int)
    for idx, token_str in enumerate(tokens):
      mapped_values = [
          mapping_dict[char] for char in token_str if char in mapping_dict
      ]
      if len(mapped_values) > 0:
        counts = np.bincount(mapped_values, minlength=4)
        corpus_states[idx] = int(np.argmax(counts))
      else:
        corpus_states[idx] = 0
    return corpus_states

  def _calculate_coherence_intra_folio(
      self, states_array: np.ndarray, folios: np.ndarray
  ) -> float:
    valid_transitions = 0.0
    total_transitions = 0
    unique_folios = np.unique(folios)

    for fol in unique_folios:
      fol_mask = folios == fol
      fol_states = states_array[fol_mask]
      if len(fol_states) > 1:
        s_curr = fol_states[:-1]
        s_next = fol_states[1:]
        valid_transitions += float(
            np.sum(self.TRANSITION_MATRIX[s_curr, s_next])
        )
        total_transitions += len(s_curr)

    return (
        valid_transitions / total_transitions if total_transitions > 0 else 0.0
    )

  def run_double_randomization(
      self,
      csv_path: str = 'voynich_eva_tokens_extended.csv',
      output_summary_path: str = 'double_randomization_results.csv',
      iterations: int = 1000,
  ) -> Dict[str, Any]:
    """Esegue il test di doppia randomizzazione (strutturale e alfabetica) sul dataset."""
    if not os.path.exists(csv_path):
      print(f"ERRORE CRITICO: File dataset '{csv_path}' non trovato.")
      sys.exit(1)

    t0 = time.time()
    df = pd.read_csv(csv_path)

    # Aliasing automatico colonne (v3.0)
    if 'Token' not in df.columns and 'EVA_Token' in df.columns:
      df['Token'] = df['EVA_Token']
    if 'Folio_Base' not in df.columns and 'Folio' in df.columns:
      df['Folio_Base'] = df['Folio'].apply(
          lambda x: str(x).split('.')[0] if '.' in str(x) else str(x)
      )

    if 'Token' not in df.columns or 'Folio_Base' not in df.columns:
      print(
          "ERRORE CRITICO: Colonne 'Token'/'EVA_Token' e 'Folio_Base'/'Folio'"
          ' necessarie.'
      )
      sys.exit(1)

    # Ordinamento sequenziale codicologico esplicito
    sort_cols = [
        col
        for col in ['Folio_Base', 'line_id', 'Record_ID']
        if col in df.columns
    ]
    if sort_cols:
      df = df.sort_values(by=sort_cols).reset_index(drop=True)

    tokens = df['Token'].astype(str).to_numpy()
    folios = df['Folio_Base'].astype(str).to_numpy()
    n_tokens = len(tokens)

    # 1. Baseline reale osservata (Metodo Demaria)
    real_states = self._map_tokens_to_states(tokens, self.DEMARIA_MAP)
    c_star_obs = self._calculate_coherence_intra_folio(real_states, folios)

    # 2. Simulazione Monte Carlo a Doppia Randomizzazione
    double_null_scores = np.zeros(iterations, dtype=np.float64)
    fixed_partition_states = np.repeat([0, 1, 2, 3], 5)

    for k in range(iterations):
      # Randomizzazione 1: Permutazione della mappatura alfabetica (5-5-5-5)
      shuffled_partition = self.rng.permutation(fixed_partition_states)
      random_map = dict(zip(self.EVA_20_ALPHABET, shuffled_partition))
      rand_states = self._map_tokens_to_states(tokens, random_map)

      # Randomizzazione 2: Permutazione della sequenza dei token intra-folio
      shuffled_states = rand_states.copy()
      for fol in np.unique(folios):
        fol_mask = folios == fol
        # FIXING CRITICO REVIEWER 2: Indicizzazione via np.flatnonzero
        idx = np.flatnonzero(fol_mask)
        shuffled_states[idx] = self.rng.permutation(shuffled_states[idx])

      double_null_scores[k] = self._calculate_coherence_intra_folio(
          shuffled_states, folios
      )

    mean_null = float(np.mean(double_null_scores))
    std_null = float(np.std(double_null_scores))
    min_null = float(np.min(double_null_scores))
    max_null = float(np.max(double_null_scores))

    p_value = float(
        (np.sum(double_null_scores >= c_star_obs) + 1) / (iterations + 1)
    )
    z_score = float((c_star_obs - mean_null) / std_null) if std_null > 0 else 0.0
    t_elapsed = time.time() - t0

    results = {
        'Dataset': os.path.basename(csv_path),
        'Total_Tokens': n_tokens,
        'Unique_Folios': len(np.unique(folios)),
        'Iterations': iterations,
        'C_Star_Observed': round(c_star_obs, 6),
        'Double_Null_Mean': round(mean_null, 6),
        'Double_Null_Std': round(std_null, 6),
        'Double_Null_Min': round(min_null, 6),
        'Double_Null_Max': round(max_null, 6),
        'Z_Score': round(z_score, 4),
        'p_value_laplace': round(p_value, 6),
        'execution_time_sec': round(t_elapsed, 4),
        'release_version': self.version,
    }

    pd.DataFrame([results]).to_csv(output_summary_path, index=False)
    return results


if __name__ == '__main__':
  print('=' * 80)
  print('METODO DEMARIA® v3.0 — TEST DI DOPPIA RANDOMIZZAZIONE AVVERSARIALE')
  print('=' * 80)

  tester = DoubleRandomizationTester(seed=42)
  if os.path.exists('voynich_eva_tokens_extended.csv'):
    res = tester.run_double_randomization(
        'voynich_eva_tokens_extended.csv', iterations=1000
    )
    print(f"\n  • Token Totali Processati     : {res['Total_Tokens']:,}")
    print(f"  • Folii Distinti Analizzati   : {res['Unique_Folios']:,}")
    print(f"  • Coerenza Osservata (C*)     : {res['C_Star_Observed']:.6f}")
    print(
        '  • Coerenza Doppia Nulla Media :'
        f" {res['Double_Null_Mean']:.6f} ± {res['Double_Null_Std']:.6f}"
    )
    print(
        '  • Intervallo Nullo [Min - Max]:'
        f" [{res['Double_Null_Min']:.6f} - {res['Double_Null_Max']:.6f}]"
    )
    print(f"  • Z-Score di Significatività  : {res['Z_Score']:.4f}")
    print(f"  • p-value (Laplace)           : {res['p_value_laplace']:.6e}")
    print(f"  • Tempo di Esecuzione         : {res['execution_time_sec']} s")
    print('  • Report Esportato su         : double_randomization_results.csv')
  else:
    print(
        "\n  [INFO] Dataset 'voynich_eva_tokens_extended.csv' non rilevato in"
        ' locale.'
    )
    print(
        "  [✓] Modulo 'double_randomization_test.py' (Release v3.0) caricato e"
        ' pronto.'
    )
  print('=' * 80)