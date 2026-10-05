#!/usr/bin/env python3
"""
METODO DEMARIA® — TEST AVVERSARIALE DOUBLE NULL (v3.0)
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
N_SIMULATIONS = 1000
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

def run_double_randomization_test():
    print("==================================================================")
    print("METODO DEMARIA® — TEST AVVERSARIALE DOUBLE NULL (v3.0)")
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
    
    c_obs = compute_coherence_matrix(df['State'].values)
    print(f"\n[+] Coerenza Osservata Canonica (C_obs): {c_obs:.6f} ({c_obs*100:.2f}%)")
    
    print(f"[*] Esecuzione Double Randomization Test ({N_SIMULATIONS} sim)...")
    double_null_scores = []
    states_arr = df['State'].values.copy()
    
    for _ in range(N_SIMULATIONS):
        # Passaggio 1: Permutazione Token
        perm_tokens = rng.permutation(states_arr)
        # Passaggio 2: Permutazione Assegnazione Stati
        perm_both = rng.permutation(perm_tokens)
        double_null_scores.append(compute_coherence_matrix(perm_both))
        
    double_null_scores = np.array(double_null_scores)
    dn_mean, dn_std = np.mean(double_null_scores), np.std(double_null_scores)
    z_dn = (c_obs - dn_mean) / dn_std if dn_std > 0 else 0.0
    p_dn = (np.sum(double_null_scores >= c_obs) + 1) / (N_SIMULATIONS + 1)
    
    print("\n[+] RISULTATI DOUBLE RANDOMIZATION TEST:")
    print(f"   - Baseline Double Null Mean: {dn_mean:.6f}")
    print(f"   - Deviazione Standard:      {dn_std:.6f}")
    print(f"   - Z-Score Avversariale:    {z_dn:+.4f}")
    print(f"   - p-value:                  {p_dn:.6f}")
    
    output_csv = 'double_randomization_results.csv'
    res_df = pd.DataFrame([{
        'Timestamp': datetime.datetime.now().isoformat(),
        'Dataset_SHA256': dataset_hash,
        'C_obs_Demaria': c_obs,
        'Double_Null_Mean': dn_mean,
        'Double_Null_Std': dn_std,
        'Z_Score': z_dn,
        'P_Value': p_dn
    }])
    res_df.to_csv(output_csv, index=False)
    print(f"\n[V] Report salvato con successo in: {output_csv}")

if __name__ == '__main__':
    run_double_randomization_test()