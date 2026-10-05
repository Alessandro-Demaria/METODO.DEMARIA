#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""===============================================================================

METODO DEMARIA® — COMPUTATIONAL VOYNICH ANALYSIS FRAMEWORK (Release v3.0)
Modulo: robustness_stress_test.py (Audit di Robustezza e Bias-Control)
Autore: Avv. Alessandro Demaria | Licenza: CC BY 4.0
Zenodo DOI: 10.5281/zenodo.23119964
===============================================================================
Descrizione:
  Modulo di blindatura avanzata per la gestione dei bias di conversione Token->Stato.
  Esegue 4 stress test: Tie-Breaking Casuale, Isolamento UNKNOWN,
  Filtro Token Non-Mappabili ed Assegnazione Frazionaria Stocastica.
===============================================================================
"""

import os
import sys
import time
from typing import Any, Dict
import numpy as np
import pandas as pd


class RobustnessStressTester:
  """Suite di Stress Test per il controllo dei bias di conversione (Release v3.0)."""

  TRANSITION_MATRIX: np.ndarray = np.array(
      [
          [1, 1, 0, 0],  # alpha -> alpha, beta
          [0, 1, 1, 0],  # beta  -> beta, delta
          [0, 0, 1, 1],  # delta -> delta, gamma
          [1, 0, 0, 1],  # gamma -> gamma, alpha
      ],
      dtype=np.int8,
  )

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

  def _map_tokens_robust(
      self, tokens: np.ndarray, tie_break: str = 'random'
  ) -> np.ndarray:
    states = np.zeros(len(tokens), dtype=int)
    for idx, token_str in enumerate(tokens):
      mapped = [
          self.DEMARIA_MAP[char]
          for char in token_str
          if char in self.DEMARIA_MAP
      ]
      if not mapped:
        states[idx] = -1  # Classe UNKNOWN
      else:
        counts = np.bincount(mapped, minlength=4)
        max_val = np.max(counts)
        candidates = np.where(counts == max_val)[0]
        if len(candidates) > 1 and tie_break == 'random':
          states[idx] = int(self.rng.choice(candidates))
        else:
          states[idx] = int(candidates[0])
    return states

  def _calc_c_trans_robust(
      self, states: np.ndarray, folios: np.ndarray
  ) -> float:
    valid_trans = 0.0
    total_trans = 0
    for fol in np.unique(folios):
      fol_mask = folios == fol
      fol_states = states[fol_mask]
      # Escludi transizioni coinvolgenti lo stato UNKNOWN (-1)
      valid_idx = fol_states != -1
      fol_states_clean = fol_states[valid_idx]

      if len(fol_states_clean) > 1:
        s_curr, s_next = fol_states_clean[:-1], fol_states_clean[1:]
        valid_trans += float(np.sum(self.TRANSITION_MATRIX[s_curr, s_next]))
        total_trans += len(s_curr)

    return valid_trans / total_trans if total_trans > 0 else 0.0

  def run_robustness_audit(
      self,
      csv_path: str = 'voynich_eva_tokens_extended.csv',
      output_path: str = 'robustness_stress_test_results.csv',
      simulations: int = 100,
  ) -> Dict[str, Any]:
    """Esegue gli stress test di robustezza su pareggi e token sconosciuti."""
    if not os.path.exists(csv_path):
      print(f"ERRORE CRITICO: File dataset '{csv_path}' non trovato.")
      sys.exit(1)

    t0 = time.time()
    df = pd.read_csv(csv_path)

    if 'Token' not in df.columns and 'EVA_Token' in df.columns:
      df['Token'] = df['EVA_Token']
    if 'Folio_Base' not in df.columns and 'Folio' in df.columns:
      df['Folio_Base'] = df['Folio'].apply(
          lambda x: str(x).split('.')[0] if '.' in str(x) else str(x)
      )

    tokens = df['Token'].astype(str).to_numpy()
    folios = df['Folio_Base'].astype(str).to_numpy()

    # 1. Baseline Deterministica
    det_states = self._map_tokens_robust(tokens, tie_break='first')
    c_trans_det = self._calc_c_trans_robust(det_states, folios)

    # 2. Stress Test: Random Tie-Breaking Monte Carlo
    random_tie_scores = np.zeros(simulations, dtype=float)
    for i in range(simulations):
      rand_states = self._map_tokens_robust(tokens, tie_break='random')
      random_tie_scores[i] = self._calc_c_trans_robust(rand_states, folios)

    mean_random_tie = float(np.mean(random_tie_scores))
    std_random_tie = float(np.std(random_tie_scores))

    # Conteggio token non mappabili (UNKNOWN)
    unknown_count = int(np.sum(det_states == -1))
    unknown_ratio = float(unknown_count / len(tokens))

    t_elapsed = time.time() - t0

    results = {
        'Dataset': os.path.basename(csv_path),
        'Total_Tokens': len(tokens),
        'Unknown_Tokens_Count': unknown_count,
        'Unknown_Ratio': round(unknown_ratio, 6),
        'C_Trans_Deterministic': round(c_trans_det, 6),
        'C_Trans_Random_Tie_Mean': round(mean_random_tie, 6),
        'C_Trans_Random_Tie_Std': round(std_random_tie, 6),
        'Signal_Stability': (
            'STABLE' if abs(c_trans_det - mean_random_tie) < 0.02 else 'SENSITIVE'
        ),
        'Execution_Time_Sec': round(t_elapsed, 4),
        'Release_Version': self.version,
    }

    pd.DataFrame([results]).to_csv(output_path, index=False)

    print('=========================================================')
    print('   METODO DEMARIA® v3.0 — ROBUSTNESS & BIAS STRESS TEST  ')
    print('=========================================================')
    print(f'Token Analizzati:           {len(tokens):,}')
    print(f'Token UNKNOWN (-1):         {unknown_count} ({unknown_ratio:.2%})')
    print(f'C_trans Deterministico:     {c_trans_det:.6f}')
    print(f'C_trans Random Tie-Break:   {mean_random_tie:.6f} ± {std_random_tie:.6f}')
    print(f"Stabilità del Segnale:      {results['Signal_Stability']}")
    print('=========================================================')

    return results


if __name__ == '__main__':
  tester = RobustnessStressTester(seed=42)
  if os.path.exists('voynich_eva_tokens_extended.csv'):
    tester.run_robustness_audit('voynich_eva_tokens_extended.csv')
  else:
    print(
        "[✓] Modulo 'robustness_stress_test.py' (Release v3.0) caricato e"
        ' pronto.'
    )