#!/usr/bin/env python3
"""
METODO DEMARIA® — MODELLO NULLO GERARCHICO A TRE LIVELLI (v3.0 Fast Vectorized)
Autore e Responsabile Scientifico: Avv. Alessandro Demaria
Data Congelamento: 05 Ottobre 2026
"""

import os
import re
import datetime
import hashlib
import numpy as np
import pandas as pd

# ==============================================================================
# CONFIGURAZIONE CANONICA
# ==============================================================================
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

def parse_line_id(val) -> int:
    if pd.isna(val):
        return -1
    digits = re.sub(r'\D', '', str(val))
    return int(digits) if digits else -1

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

def run_full_audit_suite():
    print("==================================================================")
    print("METODO DEMARIA® — SUITE DI AUDIT MODELLI NULLI GERARCHICI (v3.0 - Vettorizzato)")
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
        elif col.lower() in ['line', 'line_id', 'riga']:
            col_mapping[col] = 'line_raw'
    df.rename(columns=col_mapping, inplace=True)
    
    rng = np.random.RandomState(SEED)
    
    df['State'] = df['token'].apply(lambda t: canonical_token_to_state(t, DEMARIA_MAP, rng))
    
    if 'line_raw' in df.columns:
        df['Line_Num'] = df['line_raw'].apply(parse_line_id)
    else:
        df['Line_Num'] = 1
        
    c_obs = compute_coherence_matrix(df['State'].values)
    print(f"\n[+] Coerenza Osservata Canonica (C_obs): {c_obs:.6f} ({c_obs*100:.2f}%)")
    
    # 1. MODEL 1: Global Null
    print(f"[*] Esecuzione Model 1 (Global Permutation - {N_SIMULATIONS} sim)...")
    m1_scores = []
    states_arr = df['State'].values.copy()
    for _ in range(N_SIMULATIONS):
        shuffled = rng.permutation(states_arr)
        m1_scores.append(compute_coherence_matrix(shuffled))
        
    m1_scores = np.array(m1_scores)
    m1_mean, m1_std = np.mean(m1_scores), np.std(m1_scores)
    z1 = (c_obs - m1_mean) / m1_std if m1_std > 0 else 0.0
    p1 = (np.sum(m1_scores >= c_obs) + 1) / (N_SIMULATIONS + 1)
    
    # Pre-calcolo degli indici di gruppo per la massima velocità
    folio_groups = [idxs.values for _, idxs in df.groupby('Folio_Clean').groups.items()]
    line_groups = [idxs.values for _, idxs in df.groupby(['Folio_Clean', 'Line_Num']).groups.items()]
    
    # 2. MODEL 2: Intra-Folio Null (Vettorizzato)
    print(f"[*] Esecuzione Model 2 (Intra-Folio Permutation - {N_SIMULATIONS} sim)...")
    m2_scores = []
    for _ in range(N_SIMULATIONS):
        arr_copy = states_arr.copy()
        for idxs in folio_groups:
            arr_copy[idxs] = rng.permutation(arr_copy[idxs])
        m2_scores.append(compute_coherence_matrix(arr_copy))
        
    m2_scores = np.array(m2_scores)
    m2_mean, m2_std = np.mean(m2_scores), np.std(m2_scores)
    z2 = (c_obs - m2_mean) / m2_std if m2_std > 0 else 0.0
    p2 = (np.sum(m2_scores >= c_obs) + 1) / (N_SIMULATIONS + 1)
    
    # 3. MODEL 3: Intra-Line Null (Vettorizzato)
    print(f"[*] Esecuzione Model 3 (Intra-Line Permutation - {N_SIMULATIONS} sim)...")
    m3_scores = []
    for _ in range(N_SIMULATIONS):
        arr_copy = states_arr.copy()
        for idxs in line_groups:
            arr_copy[idxs] = rng.permutation(arr_copy[idxs])
        m3_scores.append(compute_coherence_matrix(arr_copy))
        
    m3_scores = np.array(m3_scores)
    m3_mean, m3_std = np.mean(m3_scores), np.std(m3_scores)
    z3 = (c_obs - m3_mean) / m3_std if m3_std > 0 else 0.0
    p3 = (np.sum(m3_scores >= c_obs) + 1) / (N_SIMULATIONS + 1)
    
    print("\n[+] SINTESI RISULTATI MODELLI NULLI GERARCHICI:")
    print(f"   - Model 1 (Global Null):     Mean = {m1_mean:.6f} | Z-Score = {z1:+.4f} | p = {p1:.6f}")
    print(f"   - Model 2 (Intra-Folio Null): Mean = {m2_mean:.6f} | Z-Score = {z2:+.4f} | p = {p2:.6f}")
    print(f"   - Model 3 (Intra-Line Null):  Mean = {m3_mean:.6f} | Z-Score = {z3:+.4f} | p = {p3:.6f}")
    
    output_csv = 'master_batch_execution_summary.csv'
    res_df = pd.DataFrame([{
        'Timestamp': datetime.datetime.now().isoformat(),
        'Dataset_Input': INPUT_DATASET_PATH,
        'Dataset_SHA256': dataset_hash,
        'Seed': SEED,
        'N_Simulazioni': N_SIMULATIONS,
        'C_obs_Demaria': c_obs,
        'Model1_Global_Mean': m1_mean, 'Model1_Global_Std': m1_std, 'Model1_Global_Z': z1, 'Model1_Global_P': p1,
        'Model2_Folio_Mean': m2_mean, 'Model2_Folio_Std': m2_std, 'Model2_Folio_Z': z2, 'Model2_Folio_P': p2,
        'Model3_Line_Mean': m3_mean, 'Model3_Line_Std': m3_std, 'Model3_Line_Z': z3, 'Model3_Line_P': p3,
    }])
    res_df.to_csv(output_csv, index=False)
    print(f"\n[V] Summary Report salvato con successo in: {output_csv}")

if __name__ == '__main__':
    run_full_audit_suite()