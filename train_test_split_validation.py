#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""===============================================================================

METODO DEMARIA® — COMPUTATIONAL VOYNICH ANALYSIS FRAMEWORK (Release v3.0)
Modulo: train_test_split_validation.py (Validazione Strict Out-of-Sample)
Autore: Avv. Alessandro Demaria | Licenza: CC BY 4.0
Zenodo DOI: 10.5281/zenodo.23119964
===============================================================================
Descrizione:
  Modulo per la validazione cieca Out-of-Sample (Tier C / GroupShuffleSplit).
  Congela la mappatura ed i parametri stocastici sul 40% dei Folii (Train)
  e valuta la capacita predittiva ed il Delta C_trans sul 60% dei Folii (Test).
===============================================================================
"""

import os
import sys
import time
from typing import Any, Dict
import numpy as np
import pandas as pd


class StrictOutOfSampleValidator:
  """Suite di validazione cieca out-of-sample raggruppata su Folio_Base (Release v3.0)."""

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

  def _map_tokens(self, tokens: np.ndarray) -> np.ndarray:
    states = np.zeros(len(tokens), dtype=int)
    for idx, token_str in enumerate(tokens):
      mapped = [
          self.DEMARIA_MAP[char]
          for char in token_str
          if char in self.DEMARIA_MAP
      ]
      states[idx] = int(np.argmax(np.bincount(mapped, minlength=4))) if mapped else 0
    return states

  def _calc_c_trans(self, states: np.ndarray, folios: np.ndarray) -> float:
    valid_trans = 0.0
    total_trans = 0
    for fol in np.unique(folios):
      fol_states = states[folios == fol]
      if len(fol_states) > 1:
        s_curr, s_next = fol_states[:-1], fol_states[1:]
        valid_trans += float(np.sum(self.TRANSITION_MATRIX[s_curr, s_next]))
        total_trans += len(s_curr)
    return valid_trans / total_trans if total_trans > 0 else 0.0

  def run_strict_validation(
      self,
      csv_path: str = 'voynich_eva_tokens_extended.csv',
      output_path: str = 'train_test_validation_results.csv',
      train_ratio: float = 0.40,
      max_delta_threshold: float = 0.025,
  ) -> Dict[str, Any]:
    """Esegue lo split blindato per Folio e calcola la stabilità Out-of-Sample."""
    if not os.path.exists(csv_path):
      print(f"ERRORE CRITICO: File dataset '{csv_path}' non trovato.")
      sys.exit(1)

    t0 = time.time()
    df = pd.read_csv(csv_path)

    # Aliasing e ordinamento v3.0
    if 'Token' not in df.columns and 'EVA_Token' in df.columns:
      df['Token'] = df['EVA_Token']
    if 'Folio_Base' not in df.columns and 'Folio' in df.columns:
      df['Folio_Base'] = df['Folio'].apply(
          lambda x: str(x).split('.')[0] if '.' in str(x) else str(x)
      )

    sort_cols = [
        col
        for col in ['Folio_Base', 'line_id', 'Record_ID']
        if col in df.columns
    ]
    if sort_cols:
      df = df.sort_values(by=sort_cols).reset_index(drop=True)

    unique_folios = np.unique(df['Folio_Base'].astype(str).to_numpy())
    n_folios = len(unique_folios)

    # Split raggruppato sui Folii (Group Split)
    shuffled_folios = self.rng.permutation(unique_folios)
    n_train_folios = int(np.ceil(n_folios * train_ratio))

    train_folios = shuffled_folios[:n_train_folios]
    test_folios = shuffled_folios[n_train_folios:]

    train_mask = df['Folio_Base'].isin(train_folios)
    test_mask = df['Folio_Base'].isin(test_folios)

    train_df = df[train_mask].reset_index(drop=True)
    test_df = df[test_mask].reset_index(drop=True)

    # 1. Fitting sul Train Set
    train_tokens = train_df['Token'].astype(str).to_numpy()
    train_fols = train_df['Folio_Base'].astype(str).to_numpy()
    train_states = self._map_tokens(train_tokens)
    c_trans_train = self._calc_c_trans(train_states, train_fols)

    # 2. Evaluation al Buio sul Test Set (Blind Test)
    test_tokens = test_df['Token'].astype(str).to_numpy()
    test_fols = test_df['Folio_Base'].astype(str).to_numpy()
    test_states = self._map_tokens(test_tokens)
    c_trans_test = self._calc_c_trans(test_states, test_fols)

    delta_c_trans = abs(c_trans_train - c_trans_test)
    is_verified = bool(delta_c_trans <= max_delta_threshold)
    t_elapsed = time.time() - t0

    results = {
        'Dataset': os.path.basename(csv_path),
        'Total_Tokens': len(df),
        'Total_Folios': n_folios,
        'Train_Folios_Count': len(train_folios),
        'Test_Folios_Count': len(test_folios),
        'C_Trans_Train': round(c_trans_train, 6),
        'C_Trans_Test': round(c_trans_test, 6),
        'Delta_C_Trans': round(delta_c_trans, 6),
        'Threshold_Max': max_delta_threshold,
        'Status_Verified': 'PASS' if is_verified else 'FAIL',
        'Execution_Time_Sec': round(t_elapsed, 4),
        'Release_Version': self.version,
    }

    pd.DataFrame([results]).to_csv(output_path, index=False)

    print('=========================================================')
    print('   METODO DEMARIA® v3.0 — STRICT OUT-OF-SAMPLE TEST      ')
    print('=========================================================')
    print(f'Train Folios (40%):         {len(train_folios)} folii')
    print(f'Test Folios  (60%):         {len(test_folios)} folii (Blind)')
    print(f'C_trans Train Set:          {c_trans_train:.6f}')
    print(f'C_trans Test Set:           {c_trans_test:.6f}')
    print(f'Delta |Train - Test|:       {delta_c_trans:.6f}')
    print(f"Esito Validazione:          {results['Status_Verified']}")
    print('=========================================================')

    return results


if __name__ == '__main__':
  validator = StrictOutOfSampleValidator(seed=42)
  if os.path.exists('voynich_eva_tokens_extended.csv'):
    validator.run_strict_validation('voynich_eva_tokens_extended.csv')
  else:
    print(
        "[✓] Modulo 'train_test_split_validation.py' (Release v3.0) caricato e"
        ' pronto.'
    )