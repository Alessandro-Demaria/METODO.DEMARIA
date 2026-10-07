#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
METODO DEMARIA® — PARSER E NORMALIZZATORE DI CORPUS (v3.0 - Canonico)
Modulo: voynich_parser.py
Autore: Avv. Alessandro Demaria | Licenza: CC BY 4.0
===============================================================================
Descrizione:
  Modulo di ingestion, parsing e scoring segmentato del dataset EVA.
  Esegue lo stripping esplicito via RegEx di Folio_Base e Line_Num per eliminare
  qualsiasi leakage inter-folio o inter-linea.
  Implementa la funzione canonica compute_c_raw_segmented().
===============================================================================
"""

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


def build_demaria_map_from_spec(spec: dict) -> dict:
  states_dict = spec['canonical_mapping']['states']
  indices_dict = spec['canonical_mapping']['state_indices']

  char_map = {}
  for state_name, chars in states_dict.items():
    state_idx = indices_dict[state_name]
    for c in chars:
      char_map[c] = state_idx
  return char_map


def canonical_token_to_state(token: str, char_map: dict) -> int:
  """Mappatura deterministica dello stato dominante del token senza tie-breaking stocastico.

  Priorità deterministica: Alpha (0) -> Beta (1) -> Delta (2) -> Gamma (3).
  """
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
  return winners[0]


def parse_and_clean_dataset(spec_path: str = SPEC_FILE) -> pd.DataFrame:
  """Parsing esplicito con RegEx per derivare Folio_Base e Line_Num dal campo originale.

  Arresta l'esecuzione (Fail-Fast) se la struttura del dataset risulta invalida.
  """
  spec = load_method_specification(spec_path)
  dataset_path = spec['master_dataset']['filename']

  if not os.path.exists(dataset_path):
    raise FileNotFoundError(
        f"[!] ERRORE CRITICO: Dataset '{dataset_path}' non trovato."
    )

  df = pd.read_csv(dataset_path)
  df.columns = df.columns.str.strip()

  folio_col = None
  for col in df.columns:
    if col.lower() in ['folio', 'folio_clean']:
      folio_col = col
      break

  if folio_col is None:
    raise KeyError('[!] ERRORE CRITICO: Colonna Folio non trovata nel dataset.')

  def extract_folio_base(val):
    match = re.search(r'f\d+[rv]', str(val).lower())
    return match.group(0) if match else str(val).split('.')[0]

  def extract_line_num(val):
    match = re.search(r'\.(\d+)', str(val))
    if match:
      return int(match.group(1))
    match_alt = re.search(r'f\d+[rv](\d+)', str(val).lower())
    if match_alt:
      return int(match_alt.group(1))
    return -1

  df['Folio_Clean'] = df[folio_col].astype(str)
  df['Folio_Base'] = df['Folio_Clean'].apply(extract_folio_base)
  df['Line_Num'] = df['Folio_Clean'].apply(extract_line_num)

  # Fail-Fast se privo di Line_Num
  if (df['Line_Num'] == -1).any():
    invalid_count = (df['Line_Num'] == -1).sum()
    raise ValueError(
        f'[!] ERRORE CRITICO (P0.4): Trovati {invalid_count} record privi di'
        ' Line_Num identificabile!'
    )

  token_col = None
  for col in df.columns:
    if col.lower() in ['token', 'eva_token']:
      token_col = col
      break
  if token_col is None:
    raise KeyError(
        '[!] ERRORE CRITICO: Colonna Token non trovata nel dataset.'
    )

  df['token'] = df[token_col].astype(str)

  char_map = build_demaria_map_from_spec(spec)
  df['State'] = df['token'].apply(
      lambda t: canonical_token_to_state(t, char_map)
  )

  return df


def compute_c_raw_segmented(
    df: pd.DataFrame,
    transition_matrix: np.ndarray,
    group_by=['Folio_Base', 'Line_Num'],
) -> float:
  """Funzione Canonica Universale (P0.1): Calcola C_raw escludendo qualsiasi

  transizione a cavallo di righi o folii diversi.
  """
  valid_transitions_total = 0
  total_transitions_total = 0

  grouped = df.groupby(group_by, sort=False)

  for _, group in grouped:
    states = group['State'].values
    valid_states = states[states >= 0]

    if len(valid_states) >= 2:
      s1 = valid_states[:-1]
      s2 = valid_states[1:]

      valid_trans = np.sum(transition_matrix[s1, s2])
      total_trans = len(s1)

      valid_transitions_total += valid_trans
      total_transitions_total += total_trans

  return (
      float(valid_transitions_total / total_transitions_total)
      if total_transitions_total > 0
      else 0.0
  )


if __name__ == '__main__':
  print('==================================================================')
  print('METODO DEMARIA® — PARSER E SCORED SEGMENTATO (v3.0 Canonico)')
  print('==================================================================')
  spec = load_method_specification(SPEC_FILE)
  transition_matrix = np.array(
      spec['transition_matrix_validity']['allowed_transitions'], dtype=float
  )

  df = parse_and_clean_dataset(SPEC_FILE)
  c_raw = compute_c_raw_segmented(df, transition_matrix)
  print(f'[*] Registri Processati:     {len(df)}')
  print(f"[*] Folii Unici Isolati:     {df['Folio_Base'].nunique()}")
  print(
      '[*] Righe Uniche Isolate:    '
      f" {df.groupby(['Folio_Base', 'Line_Num']).ngroups}"
  )
  print(f'[+] Coerenza C_raw Segmentata: {c_raw:.6f} ({c_raw*100:.2f}%)')