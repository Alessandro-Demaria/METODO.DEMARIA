#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""===============================================================================

METODO DEMARIA® — HOLDOUT CROSS-VALIDATION SUITE (v3.0 - Canonico)
Modulo: train_test_split_validation.py
Autore: Avv. Alessandro Demaria | Licenza: CC BY 4.0
===============================================================================
Descrizione:
  Holdout Cross-Validation al buio su raggruppamento rigido per Folio_Base.
  Applica lo stripping del campo folio per prevenire l'inflazione dei gruppi e
  utilizza la mappatura deterministica dello stato del token.
  Legge la configurazione esclusivamente da method_specification.json.
===============================================================================
"""

import datetime
import hashlib
import json
import os
import numpy as np
import pandas as pd

SPEC_FILE = 'method_specification.json'


def load_method_specification(spec_path: str = SPEC_FILE) -> dict:
  if not os.path.exists(spec_path):
    raise FileNotFoundError(
        f"[!] ERRORE CRITICO: File di specifica '{spec_path}' non trovato."
    )
  with open(spec_path, 'r', encoding='utf-8') as f:
    return json.load(f)


def get_file_sha256(filepath: str) -> str:
  if not os.path.exists(filepath):
    return 'FILE_NOT_FOUND'
  hasher = hashlib.sha256()
  with open(filepath, 'rb') as f:
    hasher.update(f.read())
  return hasher.hexdigest()


def build_demaria_map_from_spec(spec: dict) -> dict:
  states_dict = spec['canonical_mapping']['states']
  indices_dict = spec['canonical_mapping']['state_indices']

  char_map = {}
  for state_name, chars in states_dict.items():
    state_idx = indices_dict[state_name]
    for c in chars:
      char_map[c] = state_idx
  return char_map


def canonical_token_to_state(token: str, char_map: dict, rng=None) -> int:
  """Mappatura deterministica dello stato del token senza tie-breaking stocastico."""
  counts = [0, 0, 0, 0]
  has_known_char = False

  for char in str(token).lower():
    if char in char_map:
      state = char_map[char]
      counts[state] += 1
      has_known_char = True

  if not has_known_char:
    return -1

  max_val = max(counts)
  winners = [i for i, c in enumerate(counts) if c == max_val]

  # Priorità deterministica sullo stato dominante (Alpha -> Beta -> Delta -> Gamma)
  return winners[0]


def compute_c_raw_subset(
    df_subset: pd.DataFrame, transition_matrix: np.ndarray
) -> float:
  states_series = df_subset['State'].values
  valid_states = states_series[states_series >= 0]
  if len(valid_states) < 2:
    return 0.0

  s1 = valid_states[:-1]
  s2 = valid_states[1:]

  valid_transitions = np.sum(transition_matrix[s1, s2])
  total_transitions = len(s1)

  return (
      float(valid_transitions / total_transitions)
      if total_transitions > 0
      else 0.0
  )


def run_train_test_validation():
  print('==================================================================')
  print('METODO DEMARIA® — HOLDOUT CROSS-VALIDATION SUITE (v3.0 Canonico)')
  print('==================================================================')

  spec = load_method_specification(SPEC_FILE)
  dataset_path = spec['master_dataset']['filename']
  expected_hash = spec['master_dataset']['sha256_hash']
  seed = spec['system_parameters']['seed']

  dataset_hash = get_file_sha256(dataset_path)
  print(f'[*] Single Source of Truth: {SPEC_FILE}')
  print(f'[*] Dataset Input:          {dataset_path}')
  print(f'[*] SHA-256 Measured:       {dataset_hash}')

  if dataset_hash.lower() != expected_hash.lower():
    print(
        "[!] WARNING: SHA-256 non corrisponde all'hash congelato in specifica!"
    )

  if not os.path.exists(dataset_path):
    print(f"[!] ERRORE CRITICO: Dataset '{dataset_path}' non trovato.")
    return

  df = pd.read_csv(dataset_path)

  # Normalizzazione Colonne
  df.columns = df.columns.str.strip()
  col_mapping = {}
  for col in df.columns:
    if col.lower() == 'folio':
      col_mapping[col] = 'Folio_Clean'
    elif col.lower() in ['eva_token', 'token']:
      col_mapping[col] = 'token'
  df.rename(columns=col_mapping, inplace=True)

  # Stripping esplicito per isolare il vero Folio_Base (es. f1r)
  df['Folio_Base'] = df['Folio_Clean'].apply(
      lambda x: str(x).split('.')[0] if '.' in str(x) else str(x)
  )

  rng = np.random.RandomState(seed)
  char_map = build_demaria_map_from_spec(spec)
  transition_matrix = np.array(
      spec['transition_matrix_validity']['allowed_transitions'], dtype=float
  )

  df['State'] = df['token'].apply(
      lambda t: canonical_token_to_state(t, char_map)
  )

  # Raggruppamento per veri folii unici
  unique_folios = df['Folio_Base'].unique()
  rng.shuffle(unique_folios)

  split_idx = len(unique_folios) // 2
  train_folios = set(unique_folios[:split_idx])
  test_folios = set(unique_folios[split_idx:])

  train_df = df[df['Folio_Base'].isin(train_folios)]
  test_df = df[df['Folio_Base'].isin(test_folios)]

  c_train = compute_c_raw_subset(train_df, transition_matrix)
  c_test = compute_c_raw_subset(test_df, transition_matrix)
  delta_abs = abs(c_train - c_test)

  print(
      '\n[+] RISULTATI HOLDOUT SPLIT VALIDATION (50/50 Grouped on Folio_Base):'
  )
  print(f'   - Folii Unici Train:      {len(train_folios)}')
  print(f'   - Folii Unici Test:       {len(test_folios)}')
  print(f'   - Train Coherence (C_raw): {c_train:.6f} ({c_train*100:.2f}%)')
  print(f'   - Test Coherence  (C_raw): {c_test:.6f} ({c_test*100:.2f}%)')
  print(f'   - Delta Assoluto (|ΔC|):   {delta_abs:.6f}')

  output_csv = 'train_test_validation_results.csv'
  res_df = pd.DataFrame([{
      'Timestamp': datetime.datetime.now().isoformat(),
      'Dataset_SHA256': dataset_hash,
      'N_Folios_Train': len(train_folios),
      'N_Folios_Test': len(test_folios),
      'C_Train_Raw': c_train,
      'C_Test_Raw': c_test,
      'Delta_Abs': delta_abs,
  }])
  res_df.to_csv(output_csv, index=False)
  print(f"\n[V] Report di Audit salvato in: {output_csv}")


if __name__ == '__main__':
  run_train_test_validation()