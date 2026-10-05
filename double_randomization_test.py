#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""===============================================================================

METODO DEMARIA® — TEST AVVERSARIALE DOUBLE NULL (v3.0 - Canonico)
Modulo: double_randomization_test.py
Autore: Avv. Alessandro Demaria | Licenza: CC BY 4.0
===============================================================================
Descrizione:
  Test Avversariale Double Null a due livelli indipendenti di randomizzazione:
    1. Randomizzazione della sequenza dei token.
    2. Randomizzazione dell'assegnazione grafema -> stato dell'alfabeto EVA.
  Legge la configurazione esclusivamente da method_specification.json e applica
  la mappatura deterministica dello stato del token.
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


def map_tokens_to_states(
    tokens: np.ndarray, char_map: dict, rng: np.random.RandomState = None
) -> np.ndarray:
  """Mappatura deterministica dello stato del token senza tie-breaking stocastico."""
  states = np.zeros(len(tokens), dtype=int)
  for idx, tok in enumerate(tokens):
    counts = [0, 0, 0, 0]
    has_char = False
    for char in str(tok).lower():
      if char in char_map:
        s = char_map[char]
        counts[s] += 1
        has_char = True
    if not has_char:
      states[idx] = -1
    else:
      max_v = max(counts)
      winners = [i for i, c in enumerate(counts) if c == max_v]
      # Priorità deterministica sullo stato dominante (Alpha -> Beta -> Delta -> Gamma)
      states[idx] = winners[0]
  return states


def compute_c_raw(
    states_arr: np.ndarray, transition_matrix: np.ndarray
) -> float:
  valid_states = states_arr[states_arr >= 0]
  if len(valid_states) < 2:
    return 0.0
  s1 = valid_states[:-1]
  s2 = valid_states[1:]
  valid_trans = np.sum(transition_matrix[s1, s2])
  total_trans = len(s1)
  return float(valid_trans / total_trans) if total_trans > 0 else 0.0


def run_double_randomization_test():
  print('==================================================================')
  print('METODO DEMARIA® — TEST AVVERSARIALE DOUBLE NULL (v3.0 Canonico)')
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
    if col.lower() in ['eva_token', 'token']:
      col_mapping[col] = 'token'
  df.rename(columns=col_mapping, inplace=True)

  rng = np.random.RandomState(seed)
  char_map = build_demaria_map_from_spec(spec)
  transition_matrix = np.array(
      spec['transition_matrix_validity']['allowed_transitions'], dtype=float
  )

  tokens = df['token'].astype(str).values
  obs_states = map_tokens_to_states(tokens, char_map)
  c_obs = compute_c_raw(obs_states, transition_matrix)
  print(
      f'\n[+] Coerenza Osservata Reale (C_raw): {c_obs:.6f} ({c_obs*100:.2f}%)'
  )

  n_simulations = 1000
  all_eva_chars = list(char_map.keys())

  print(f'[*] Esecuzione Double Randomization Test ({n_simulations} sim)...')
  double_null_scores = []

  for _ in range(n_simulations):
    # LEVEL 1: Randomizzazione della sequenza dei token
    perm_tokens = rng.permutation(tokens)

    # LEVEL 2: Randomizzazione indipendente della mappatura alfabetica
    shuffled_chars = rng.permutation(all_eva_chars)
    random_map = {}
    for state_idx in range(4):
      group = shuffled_chars[state_idx * 5 : (state_idx + 1) * 5]
      for c in group:
        random_map[c] = state_idx

    # Calcolo dello stato sulle sequenze e mappature congiuntamente permutate
    perm_states = map_tokens_to_states(perm_tokens, random_map)
    double_null_scores.append(compute_c_raw(perm_states, transition_matrix))

  double_null_scores = np.array(double_null_scores)
  dn_mean = float(np.mean(double_null_scores))
  dn_std = float(np.std(double_null_scores))
  z_dn = float((c_obs - dn_mean) / dn_std) if dn_std > 0 else 0.0
  p_dn = float((np.sum(double_null_scores >= c_obs) + 1) / (n_simulations + 1))

  print('\n[+] RISULTATI DOUBLE RANDOMIZATION TEST (C_raw):')
  print(f'   - Baseline Double Null Mean: {dn_mean:.6f}')
  print(f'   - Deviazione Standard:       {dn_std:.6f}')
  print(f'   - Z-Score Avversariale:     {z_dn:+.4f}')
  print(f'   - p-value:                  {p_dn:.6f}')

  output_csv = 'double_randomization_results.csv'
  res_df = pd.DataFrame([{
      'Timestamp': datetime.datetime.now().isoformat(),
      'Dataset_SHA256': dataset_hash,
      'C_raw_Observed': c_obs,
      'Double_Null_Mean': dn_mean,
      'Double_Null_Std': dn_std,
      'Z_Score': z_dn,
      'P_Value': p_dn,
  }])
  res_df.to_csv(output_csv, index=False)
  print(f"\n[V] Report di Audit salvato in: {output_csv}")


if __name__ == '__main__':
  run_double_randomization_test()