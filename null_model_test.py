#!/usr/bin/env python3
# METODO DEMARIA® - Null Model Test (Tier A Validation v3.0)
# ------------------------------------------------------------------
# Test d'ipotesi nulla stocastica (Monte Carlo N=10.000) su sequenza shufflata.
# Calcolo dinamico e simmetrico di C* con isolamento dei confini di folio.
# Autore: Avv. Alessandro Demaria | Licenza: CC BY-NC-ND 4.0

import os
import sys
import pandas as pd
import numpy as np


def run_null_model_test(csv_path: str = "voynich_eva_tokens_extended.csv", 
                        output_summary_path: str = "null_model_test_results.csv",
                        n_iterations: int = 10000, 
                        seed: int = 42) -> tuple:
    # 0. Verifica e caricamento dataset
    if not os.path.exists(csv_path):
        print(f"ERRORE CRITICO: File dataset '{csv_path}' non trovato.")
        sys.exit(1)

    rng = np.random.default_rng(seed)
    df = pd.read_csv(csv_path)

    # Normalizzazione automatica delle colonne (Aliasing)
    if 'Token' not in df.columns and 'EVA_Token' in df.columns:
        df['Token'] = df['EVA_Token']
    if 'Folio_Base' not in df.columns and 'Folio' in df.columns:
        df['Folio_Base'] = df['Folio']

    if 'Token' not in df.columns or 'Folio_Base' not in df.columns:
        print("ERRORE CRITICO: Colonne 'Token'/'EVA_Token' e 'Folio_Base'/'Folio' necessarie.")
        sys.exit(1)

    # 1. Matrice di adiacenza delle transizioni valide del Computus Magnus (7/16 ammesse)
    transition_matrix = np.array([
        [1, 1, 0, 0],  # alpha -> alpha, beta
        [0, 1, 1, 0],  # beta  -> beta, delta
        [0, 0, 1, 1],  # delta -> delta, gamma
        [1, 0, 0, 1]   # gamma -> gamma, alpha
    ], dtype=float)

    tokens = df['Token'].astype(str).to_numpy()
    folios = df['Folio_Base'].astype(str).to_numpy()

    # 2. Mappatura Canonica Demaria® v3.0 (Partizione Rigida 5-5-5-5)
    demaria_map = {
        'o': 0, 'a': 0, 'e': 0, 'c': 0, 'h': 0,  # alpha (0)
        'k': 1, 't': 1, 'p': 1, 'f': 1, 's': 1,  # beta  (1)
        'r': 2, 'l': 2, 'q': 2, 'y': 2, 'd': 2,  # delta (2)
        'x': 3, 'g': 3, 'm': 3, 'n': 3, 'i': 3   # gamma (3)
    }

    # 3. Conversione dell'intero corpus negli stati cibernetici dominanti per token
    corpus_states = np.zeros(len(tokens), dtype=int)
    for idx, token_str in enumerate(tokens):
        mapped_values = [demaria_map[char] for char in token_str if char in demaria_map]
        if len(mapped_values) > 0:
            counts = np.bincount(mapped_values, minlength=4)
            corpus_states[idx] = int(np.argmax(counts))
        else:
            corpus_states[idx] = 0

    def calculate_coherence_intra_folio(states_array: np.ndarray) -> float:
        # Calcolo di C* isolato entro i confini di ciascun folio (Zero transizioni inter-folio)
        valid_transitions = 0.0
        total_transitions = 0
        unique_folios = np.unique(folios)
        
        for fol in unique_folios:
            fol_mask = (folios == fol)
            fol_states = states_array[fol_mask]
            if len(fol_states) > 1:
                s_curr = fol_states[:-1]
                s_next = fol_states[1:]
                valid_transitions += float(np.sum(transition_matrix[s_curr, s_next]))
                total_transitions += len(s_curr)
                
        return valid_transitions / total_transitions if total_transitions > 0 else 0.0

    # 4. Calcolo REALE e DINAMICO di C* osservato
    c_star_obs = calculate_coherence_intra_folio(corpus_states)

    # 5. Simulazione Monte Carlo dell'Ipotesi Nulla (Shuffling della sequenza di stati)
    null_scores = np.zeros(n_iterations, dtype=float)
    shuffled_states = corpus_states.copy()

    for i in range(n_iterations):
        rng.shuffle(shuffled_states)
        null_scores[i] = calculate_coherence_intra_folio(shuffled_states)

    # 6. Calcolo metriche stocastiche e p-value rigoroso con correzione di Laplace
    mean_null = float(np.mean(null_scores))
    std_null = float(np.std(null_scores))
    max_null = float(np.max(null_scores))
    min_null = float(np.min(null_scores))
    p_value = float((np.sum(null_scores >= c_star_obs) + 1) / (n_iterations + 1))
    z_score = float((c_star_obs - mean_null) / std_null) if std_null > 0 else 0.0

    # 7. Esportazione automatica della relazione dei risultati
    results_df = pd.DataFrame([{
        "Dataset": os.path.basename(csv_path),
        "Total_Tokens": len(tokens),
        "Unique_Folios": len(np.unique(folios)),
        "Iterations": n_iterations,
        "C_Star_Observed": c_star_obs,
        "Null_Mean": mean_null,
        "Null_Std": std_null,
        "Null_Min": min_null,
        "Null_Max": max_null,
        "Z_Score": z_score,
        "p_value": p_value,
        "Release_Version": "v3.0"
    }])
    results_df.to_csv(output_summary_path, index=False)

    # 8. Stampa formale dell'output di laboratorio
    print("=========================================================")
    print("   METODO DEMARIA® v3.0 — NULL MODEL MONTE CARLO TEST    ")
    print("=========================================================")
    print(f"Dataset Analizzato:        {csv_path}")
    print(f"Token Analizzati:          {len(tokens):,}")
    print(f"Folii Distinti:            {len(np.unique(folios)):,}")
    print(f"Iterazioni Monte Carlo:    {n_iterations:,}")
    print(f"C* Osservato (Dinamico):   {c_star_obs:.6f}")
    print(f"Media Modello Nullo:       {mean_null:.6f}")
    print(f"Dev. Std. Modello Nullo:   {std_null:.6f}")
    print(f"Range Nullo [Min - Max]:   [{min_null:.6f} - {max_null:.6f}]")
    print(f"Z-Score Significativita:   {z_score:.4f}")
    print(f"p-value Significativita:   {p_value:.6e}")
    print(f"Report Esportato su:       {output_summary_path}")
    print("=========================================================")

    return c_star_obs, null_scores, p_value


if __name__ == "__main__":
    run_null_model_test()
