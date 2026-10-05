#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""===============================================================================

METODO DEMARIA® — SUITE DI AUDIT MODELLI NULLI GERARCHICI (v3.0 - Canonico)
Modulo: null_model_test.py
Autore: Avv. Alessandro Demaria | Licenza: CC BY 4.0
===============================================================================
Descrizione:
  Modulo di Audit per Modelli Nulli Gerarchici a Tre Livelli (Global, Folio,
  Line).
  Utilizza esclusivamente method_specification.json come Single Source of Truth.
  Applica la Configurazione A (5-5-5-5) e calcola la metrica primaria C_raw con
  mappatura deterministica pura dello stato del token.
===============================================================================
"""

import datetime
import hashlib
import json
import os
import re
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
  """Mappatura deterministica dello stato dominante senza stocasticità nei pareggi."""
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

  # Priorità deterministica sullo stato dominante (ordine canonico Alpha -> Beta -> Delta -> Gamma)
  return winners[0]


def parse_line_id(val) -> int:
  if pd.isna(val):
    return -1
  digits = re.sub(r'\D', '', str(val))
  return int(digits) if digits else -1


def compute_c_raw_intra_group(
    states_series: np.ndarray, transition_matrix: np.ndarray
) -> float:
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


def run_full_audit_suite():
  print('==================================================================')
  print('METODO DEMARIA® — AUDIT MODELLI NULLI GERARCHICI (v3.0 Canonico)')
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
    elif col.lower() in ['line', 'line_id', 'riga']:
      col_mapping[col] = 'line_raw'
  df.rename(columns=col_mapping, inplace=True)

  # Stripping Folio_Base per evitare conteggio errato dei righi come folii
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

  if 'line_raw' in df.columns:
    df['Line_Num'] = df['line_raw'].apply(parse_line_id)
  else:
    df['Line_Num'] = 1

  c_obs = compute_c_raw_intra_group(df['State'].values, transition_matrix)
  print(
      f'\n[+] Coerenza Osservata Reale (C_raw): {c_obs:.6f} ({c_obs*100:.2f}%)'
  )

  n_simulations = 1000
  states_arr = df['State'].values.copy()

  # 1. MODEL 1: Global Permutation Null
  print(
      f'[*] Esecuzione Model 1 (Global Null Permutation - {n_simulations}'
      ' sim)...'
  )
  m1_scores = []
  for _ in range(n_simulations):
    shuffled = rng.permutation(states_arr)
    m1_scores.append(compute_c_raw_intra_group(shuffled, transition_matrix))

  m1_scores = np.array(m1_scores)
  m1_mean, m1_std = np.mean(m1_scores), np.std(m1_scores)
  z1 = (c_obs - m1_mean) / m1_std if m1_std > 0 else 0.0
  p1 = (np.sum(m1_scores >= c_obs) + 1) / (n_simulations + 1)

  # Pre-calcolo indici di gruppo
  folio_groups = [
      idxs.values for _, idxs in df.groupby('Folio_Base').groups.items()
  ]
  line_groups = [
      idxs.values
      for _, idxs in df.groupby(['Folio_Base', 'Line_Num']).groups.items()
  ]

  # 2. MODEL 2: Intra-Folio Permutation Null
  print(
      f'[*] Esecuzione Model 2 (Intra-Folio Permutation - {n_simulations}'
      ' sim)...'
  )
  m2_scores = []
  for _ in range(n_simulations):
    arr_copy = states_arr.copy()
    for idxs in folio_groups:
      arr_copy[idxs] = rng.permutation(arr_copy[idxs])
    m2_scores.append(compute_c_raw_intra_group(arr_copy, transition_matrix))

  m2_scores = np.array(m2_scores)
  m2_mean, m2_std = np.mean(m2_scores), np.std(m2_scores)
  z2 = (c_obs - m2_mean) / m2_std if m2_std > 0 else 0.0
  p2 = (np.sum(m2_scores >= c_obs) + 1) / (n_simulations + 1)

  # 3. MODEL 3: Intra-Line Permutation Null
  print(
      f'[*] Esecuzione Model 3 (Intra-Line Permutation - {n_simulations}'
      ' sim)...'
  )
  m3_scores = []
  for _ in range(n_simulations):
    arr_copy = states_arr.copy()
    for idxs in line_groups:
      arr_copy[idxs] = rng.permutation(arr_copy[idxs])
    m3_scores.append(compute_c_raw_intra_group(arr_copy, transition_matrix))

  m3_scores = np.array(m3_scores)
  m3_mean, m3_std = np.mean(m3_scores), np.std(m3_scores)
  z3 = (c_obs - m3_mean) / m3_std if m3_std > 0 else 0.0
  p3 = (np.sum(m3_scores >= c_obs) + 1) / (n_simulations + 1)

  print('\n[+] RISULTATI CANONICI MODELLI NULLI GERARCHICI (C_raw):')
  print(
      '   - Model 1 (Global Null):     Mean ='
      f' {m1_mean:.6f} | Z-Score = {z1:+.4f} | p = {p1:.6f}'
  )
  print(
      '   - Model 2 (Intra-Folio Null): Mean ='
      f' {m2_mean:.6f} | Z-Score = {z2:+.4f} | p = {p2:.6f}'
  )
  print(
      '   - Model 3 (Intra-Line Null):  Mean ='
      f' {m3_mean:.6f} | Z-Score = {z3:+.4f} | p = {p3:.6f}'
  )

  output_csv = 'master_batch_execution_summary.csv'
  res_df = pd.DataFrame([{
      'Timestamp': datetime.datetime.now().isoformat(),
      'Dataset_Input': dataset_path,
      'Dataset_SHA256': dataset_hash,
      'Seed': seed,
      'N_Simulations': n_simulations,
      'C_raw_Observed': c_obs,
      'Model1_Global_Mean': m1_mean,
      'Model1_Global_Std': m1_std,
      'Model1_Global_Z': z1,
      'Model1_Global_P': p1,
      'Model2_Folio_Mean': m2_mean,
      'Model2_Folio_Std': m2_std,
      'Model2_Folio_Z': z2,
      'Model2_Folio_P': p2,
      'Model3_Line_Mean': m3_mean,
      'Model3_Line_Std': m3_std,
      'Model3_Line_Z': z3,
      'Model3_Line_P': p3,
  }])
  res_df.to_csv(output_csv, index=False)
  print(f"\n[V] Report di Audit salvato in: {output_csv}")


if __name__ == '__main__':
  run_full_audit_suite()