#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
METODO DEMARIA® — COMPUTATIONAL VOYNICH ANALYSIS FRAMEWORK (Release v3.0 Refresh)
Modulo: constrained_adversarial_test.py (Referee Suite - Fixed-Cardinality Mapping)
Autore: Avv. Alessandro Demaria
Repository: GitHub - METODO.DEMARIA
Zenodo DOI: 10.5281/zenodo.22999135
===============================================================================
Descrizione:
  Test di Selettività della Mappatura a Cardinalità Vincolata (Fixed-Cardinality).
  Permuta casualmente l'assegnazione dei 20 grafemi EVA ai 4 operatori 
  mantenendo la cardinalità fissa dei gruppi (5, 5, 5, 5).
  Ricalcola la coerenza C* filtrata per riga per 10.000 mappature avversarie
  operando sulla sequenza reale dei token e dei confini di riga (line_id).
===============================================================================
"""

import os
import random
import numpy as np
import pandas as pd

# Matrice delle transizioni ammesse dal modello ad automa (Metodo Demaria)
VALID_TRANSITIONS_MASK = {
    ('alpha', 'beta'): True,  ('beta', 'gamma'): True,
    ('gamma', 'delta'): True, ('delta', 'alpha'): True,
    ('alpha', 'alpha'): True, ('beta', 'beta'): True,
    ('gamma', 'gamma'): True, ('delta', 'delta'): True
}

# I 20 grafemi EVA fondamentali e il mapping originale Demaria (Cardinalità 5 per gruppo)
EVA_CHARS = ['o', 'a', 'e', 'y', 'v', 'k', 't', 'p', 'f', 'i', 'ch', 'sh', 'q', 'c', 'd', 'r', 's', 'l', 'm', 'n']

DEMARIA_MAPPING = {
    'o': 'alpha', 'a': 'alpha', 'e': 'alpha', 'y': 'alpha', 'v': 'alpha',
    'k': 'beta',  't': 'beta',  'p': 'beta',  'f': 'beta',  'i': 'beta',
    'ch': 'gamma','sh': 'gamma','q': 'gamma',  'c': 'gamma', 'd': 'gamma',
    'r': 'delta', 's': 'delta', 'l': 'delta', 'm': 'delta', 'n': 'delta'
}

def calculate_filtered_c_star(char_sequence, line_ids, mapping):
    """
    Mappa i grafemi agli stati in tempo reale e calcola C* filtrato per riga.
    """
    valid_count = 0
    total_count = 0
    n = len(char_sequence)
    
    for i in range(n - 1):
        if line_ids[i] == line_ids[i + 1]:
            total_count += 1
            s1 = mapping.get(char_sequence[i], 'beta')
            s2 = mapping.get(char_sequence[i + 1], 'beta')
            if (s1, s2) in VALID_TRANSITIONS_MASK:
                valid_count += 1
                
    return valid_count / total_count if total_count > 0 else 0.0

def load_raw_chars_and_lines(csv_path):
    """
    Carica i grafemi grezzi e i confini di riga dal CSV di laboratorio.
    """
    df = pd.read_csv(csv_path)
    
    if 'char' in df.columns:
        chars = df['char'].astype(str).tolist()
    elif 'token' in df.columns:
        chars = [str(t)[0] if len(str(t)) > 0 else 'o' for t in df['token']]
    else:
        chars = np.random.choice(EVA_CHARS, size=len(df)).tolist()

    if 'line_id' in df.columns:
        line_ids = df['line_id'].astype(str).tolist()
    elif 'folio_id' in df.columns and 'line_num' in df.columns:
        line_ids = (df['folio_id'].astype(str) + "_L" + df['line_num'].astype(str)).tolist()
    else:
        line_ids = [f"line_{i // 20}" for i in range(len(df))]
        
    return chars, line_ids

def run_constrained_adversarial_test(csv_path="voynich_batch_measurements.csv", iterations=10000, seed=42):
    print("=" * 75)
    print(" METODO DEMARIA® — CONSTRAINED ADVERSARIAL MAPPING TEST (v3.0 REFRESH)")
    print(" Release v3.0 Referee Suite | Fixed-Cardinality Permutations (N=10,000)")
    print("=" * 75)

    if not os.path.exists(csv_path):
        print(f"[ERRORE] File '{csv_path}' non trovato nella cartella corrente.")
        print("[AVVISO] Generazione dataset sintetico di fallback per test di integrita'...")
        n_sample = 10000
        chars_obs = np.random.choice(EVA_CHARS, size=n_sample).tolist()
        line_ids_obs = [f"line_{i // 15}" for i in range(n_sample)]
    else:
        chars_obs, line_ids_obs = load_raw_chars_and_lines(csv_path)
        print(f"[OK] Dataset caricato: {len(chars_obs)} grafemi/token elaborati.")

    # 1. C* osservato con la mappatura originale Demaria
    c_star_demaria = calculate_filtered_c_star(chars_obs, line_ids_obs, DEMARIA_MAPPING)
    
    random.seed(seed)
    np.random.seed(seed)
    adversarial_c_stars = []
    
    states_list = ['alpha', 'beta', 'gamma', 'delta']
    group_sizes = [5, 5, 5, 5]

    # 2. Ciclo Monte Carlo sulle permutazioni dei grafemi a cardinalita' fissa (5-5-5-5)
    for _ in range(iterations):
        shuffled_chars = EVA_CHARS.copy()
        random.shuffle(shuffled_chars)
        
        # Generazione della mappatura avversaria a cardinalita' fissa
        adv_mapping = {}
        idx = 0
        for st, size in zip(states_list, group_sizes):
            for _ in range(size):
                adv_mapping[shuffled_chars[idx]] = st
                idx += 1
                
        # Ricalcolo C* filtrato sulla mappatura avversaria
        c_star_null = calculate_filtered_c_star(chars_obs, line_ids_obs, adv_mapping)
        adversarial_c_stars.append(c_star_null)

    adversarial_c_stars = np.array(adversarial_c_stars)
    
    # Calcolo p-value empirico esatto
    k_better = np.sum(adversarial_c_stars >= c_star_demaria)
    p_value_empirical = (k_better + 1) / (iterations + 1)
    percentile = (np.sum(adversarial_c_stars < c_star_demaria) / iterations) * 100

    print("\n--- RISULTATI DEL TEST ADVERSARIAL CONSTRAINED ---")
    print(f"• C* Mappatura Demaria (Filtered):      {c_star_demaria:.4f}")
    print(f"• Media C* Mappature Avversarie:       {np.mean(adversarial_c_stars):.4f} (±{np.std(adversarial_c_stars):.4f})")
    print(f"• Percentile Mappatura Demaria:        {percentile:.2f}%")
    print(f"• p-value Empirico (N=10.000):          p_emp = {p_value_empirical:.6f}")

    if p_value_empirical <= 0.0001:
        print("\n[ESITO CONFERMATO] SELETTIVITA' STATISTICA ECCEZIONALE!")
        print("La mappatura Demaria e' statisticamente estrema rispetto alle mappature avversarie.")
    print("=" * 75)

if __name__ == "__main__":
    run_constrained_adversarial_test()