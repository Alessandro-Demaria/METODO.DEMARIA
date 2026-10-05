#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""===============================================================================

METODO DEMARIA® — PARSER E NORMALIZZATORE DI CORPUS (v3.0 - Canonico)
Modulo: voynich_parser.py
Autore: Avv. Alessandro Demaria | Licenza: CC BY 4.0
===============================================================================
Descrizione:
  Modulo di ingestion e parsing del dataset EVA. Normalizza le colonne,
  esegue lo stripping di Folio_Base per evitare inflazione dei gruppi ed
  assegna lo stato topologico deterministico leggendo unicamente da
  method_specification.json.
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


def canonical_token_to_state(token: str, char_map: dict, rng=None) -> int:
  """Mappatura deterministica dello stato dominante del token senza tie-breaking stocastico."""
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


def parse_and_clean_dataset(spec_path: str = SPEC_FILE) -> pd.DataFrame:
  spec = load_method_specification(spec_path)
  dataset_path = spec['master_dataset']['filename']

  if not os.path.exists(dataset_path):
    raise FileNotFoundError(
        f"[!] ERRORE CRITICO: Dataset '{dataset_path}' non trovato."
    )

  df = pd.read_csv(dataset_path)
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

  # Stripping esplicito Folio_Base per eliminare inflazione di righi
  df['Folio_Base'] = df['Folio_Clean'].apply(
      lambda x: str(x).split('.')[0] if '.' in str(x) else str(x)
  )

  char_map = build_demaria_map_from_spec(spec)

  df['State'] = df['token'].apply(
      lambda t: canonical_token_to_state(t, char_map)
  )

  if 'line_raw' in df.columns:
    df['Line_Num'] = df['line_raw'].apply(parse_line_id)
  else:
    df['Line_Num'] = 1

  return df


def run_parser_test():
  print('==================================================================')
  print('METODO DEMARIA® — PARSER E NORMALIZZATORE DATASET (v3.0 Canonico)')
  print('==================================================================')

  df = parse_and_clean_dataset()
  print(f'[*] Registri totali processati: {len(df)}')
  print(f"[*] Folii unici identificati:  {df['Folio_Base'].nunique()}")
  print(f"[*] Distribuzione Stati:\n{df['State'].value_counts(normalize=True)}")
  print('\n[V] Parsing completato con successo.')


if __name__ == '__main__':
  run_parser_test()