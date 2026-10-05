#!/usr/bin/env python3
"""
METODO DEMARIA® — HOLDOUT CROSS-VALIDATION SUITE (v3.0)
Autore e Responsabile Scientifico: Avv. Alessandro Demaria
Data Congelamento: 05 Ottobre 2026
"""

import os
import re
import datetime
import hashlib
import numpy as np
import pandas as pd

SEED = 42
INPUT_DATASET_PATH = 'voynich_eva_tokens_extended.csv'

DEMARIA_MAP = {
    'o': 0, 'k': 0, 't': 0, 'p': 0, 'f': 0,
    'a': 1, 'e': 1, 'i': 1, 'c': 1, 'h': 1,
    'd': 2, 's': 2, 'y': 2, 'q': 2, 'l': 2,
    'r': 3, 'm': 3, 'g': 3, 'x': 3, 'z': 3
}

def get_file_sha256(filepath: str) -> str:
    if not os.path.exists(filepath):
        return "FILE_NOT_FOUND"
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        hasher.update(f.read())
    return hasher.hexdigest()

def canonical_token_to_state(token: str, demaria_map: dict, rng: np.random.RandomState) -> int:
    counts = [0, 0, 0, 0]
    has_known_char = False
    
    for char in str(token):
        if char in demaria_map:
            state = demaria_map[char]
            counts[state] += 1
            has_known_char = True
            
    if not has_known_char:
        return -1
        
    max_val = max(counts)
    winners = [i for i, c in enumerate(counts) if c == max_val]
    
    if len(winners) == 1:
        return winners[0]
    else:
        return int(rng.choice(winners))

def compute_coherence_matrix(states_series: np.ndarray) -> float:
    valid_states = states_series[states_series >= 0]
    if len(valid_states) < 2:
        return 0.0
    
    s1 = valid_states[:-1]
    s2 = valid_states[1:]
    
    matrix = np.zeros((4, 4), dtype=int)
    for a, b in zip(s1, s2):
        matrix[a, b] += 1
        
    total_transitions = matrix.sum()
    if total_transitions == 0:
        return 0.0
        
    diag_sum = np.trace(matrix)
    max_row_sum = matrix.sum(axis=1).max()
    
    return float((diag_sum + max_row_sum) / (2.0 * total_transitions))

def run_train_test_validation():
    print("==================================================================")
    print("METODO DEMARIA® — HOLDOUT CROSS-VALIDATION SUITE (v3.0)")
    print("==================================================================")
    
    dataset_hash = get_file_sha256(INPUT_DATASET_PATH)
    print(f"[*] Dataset Input: {INPUT_DATASET_PATH}")
    print(f"[*] SHA-256 Provenance Hash: {dataset_hash}")
    
    if not os.path.exists(INPUT_DATASET_PATH):
        print(f"[!] ERRORE CRITICO: File {INPUT_DATASET_PATH} non trovato.")
        return
        
    df = pd.read_csv(INPUT_DATASET_PATH)
    
    # NORMALIZZAZIONE COLONNE
    df.columns = df.columns.str.strip()
    col_mapping = {}
    for col in df.columns:
        if col.lower() == 'folio':
            col_mapping[col] = 'Folio_Clean'
        elif col.lower() in ['eva_token', 'token']:
            col_mapping[col] = 'token'
    df.rename(columns=col_mapping, inplace=True)
    
    rng = np.random.RandomState(SEED)
    
    df['State'] = df['token'].apply(lambda t: canonical_token_to_state(t, DEMARIA_MAP, rng))
    
    # Split 50/50 Train / Test
    folios = df['Folio_Clean'].unique()
    rng.shuffle(folios)
    
    split_idx = len(folios) // 2
    train_folios = set(folios[:split_idx])
    test_folios = set(folios[split_idx:])
    
    train_df = df[df['Folio_Clean'].isin(train_folios)]
    test_df = df[df['Folio_Clean'].isin(test_folios)]
    
    c_train = compute_coherence_matrix(train_df['State'].values)
    c_test = compute_coherence_matrix(test_df['State'].values)
    delta_abs = abs(c_train - c_test)
    
    print("\n[+] RISULTATI HOLDOUT SPLIT VALIDATION (50/50):")
    print(f"   - Train Coherence (C_train): {c_train:.6f} ({c_train*100:.2f}%)")
    print(f"   - Test Coherence  (C_test):  {c_test:.6f} ({c_test*100:.2f}%)")
    print(f"   - Delta Assoluto:             {delta_abs:.6f}")
    
    output_csv = 'train_test_validation_results.csv'
    res_df = pd.DataFrame([{
        'Timestamp': datetime.datetime.now().isoformat(),
        'Dataset_SHA256': dataset_hash,
        'N_Folios_Train': len(train_folios),
        'N_Folios_Test': len(test_folios),
        'C_Train': c_train,
        'C_Test': c_test,
        'Delta_Abs': delta_abs
    }])
    res_df.to_csv(output_csv, index=False)
    print(f"\n[V] Report salvato con successo in: {output_csv}")

if __name__ == '__main__':
    run_train_test_validation()