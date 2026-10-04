#!/usr/bin/env python3
# METODO DEMARIA® - Null Model Master Runner (Release v3.0)
# ------------------------------------------------------------------
# Orchestratore per l'esecuzione simmetrica e dinamica dei test stocastici Tier A.
# Gestione automatica aliasing colonne e isolamento intra-folio.
# Autore: Avv. Alessandro Demaria | Licenza: CC BY-NC-ND 4.0

import os
import sys
import pandas as pd
import numpy as np


def execute_master_null_model(csv_path: str = "voynich_eva_tokens_extended.csv",
                              output_summary_path: str = "null_model_runner_results.csv",
                              n_iterations: int = 10000,
                              seed: int = 42) -> dict:
    if not os.path.exists(csv_path):
        print(f"ERRORE CRITICO: File dataset '{csv_path}' non trovato.")
        sys.exit(1)

    rng = np.random.default_rng(seed)
    df = pd.read_csv(csv_path)

    # Aliasing automatico delle colonne
    if 'Token' not in df.columns and 'EVA_Token' in df.columns:
        df['Token'] = df['EVA_Token']
    if 'Folio_Base' not in df.columns and 'Folio' in df.columns:
        df['Folio_Base'] = df['Folio']

    if 'Token' not in df.columns or 'Folio_Base' not in df.columns:
        print("ERRORE CRITICO: Colonne 'Token'/'EVA_Token' e 'Folio_Base'/'Folio' necessarie.")
        sys.exit(1)

    transition_matrix = np.array([
        [1, 1, 0, 0],
        [0, 1, 1, 0],
        [0, 0, 1, 1],
        [1, 0, 0, 1]
    ], dtype=float)

    tokens = df['Token'].astype(str).to_numpy()
    folios = df['Folio_Base'].astype(str).to_numpy()

    demaria_map = {
        'o': 0, 'a': 0, 'e': 0, 'c': 0, 'h': 0,
        'k': 1, 't': 1, 'p': 1, 'f': 1, 's': 1,
        'r': 2, 'l': 2, 'q': 2, 'y': 2, 'd': 2,
        'x': 3, 'g': 3, 'm': 3, 'n': 3, 'i': 3
    }

    corpus_states = np.zeros(len(tokens), dtype=int)
    for idx, token_str in enumerate(tokens):
        mapped_values = [demaria_map[char] for char in token_str if char in demaria_map]
        if len(mapped_values) > 0:
            counts = np.bincount(mapped_values, minlength=4)
            corpus_states[idx] = int(np.argmax(counts))
        else:
            corpus_states[idx] = 0

    def calculate_coherence_intra_folio(states_array: np.ndarray) -> float:
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

    c_star_obs = calculate_coherence_intra_folio(corpus_states)

    null_scores = np.zeros(n_iterations, dtype=float)
    shuffled_states = corpus_states.copy()

    for i in range(n_iterations):
        rng.shuffle(shuffled_states)
        null_scores[i] = calculate_coherence_intra_folio(shuffled_states)

    mean_null = float(np.mean(null_scores))
    std_null = float(np.std(null_scores))
    max_null = float(np.max(null_scores))
    min_null = float(np.min(null_scores))
    p_value = float((np.sum(null_scores >= c_star_obs) + 1) / (n_iterations + 1))
    z_score = float((c_star_obs - mean_null) / std_null) if std_null > 0 else 0.0

    results_summary = {
        "Dataset": os.path.basename(csv_path),
        "Total_Tokens": len(tokens),
        "Unique_Folios": len(np.unique(folios)),
        "C_Star_Observed": c_star_obs,
        "Null_Mean": mean_null,
        "Null_Std": std_null,
        "Z_Score": z_score,
        "p_value": p_value,
        "Release_Version": "v3.0"
    }

    pd.DataFrame([results_summary]).to_csv(output_summary_path, index=False)

    print("=========================================================")
    print("   METODO DEMARIA® v3.0 — NULL MODEL MASTER RUNNER       ")
    print("=========================================================")
    print(f"C* Osservato (Dinamico):   {c_star_obs:.6f}")
    print(f"Media Modello Nullo:       {mean_null:.6f}")
    print(f"Z-Score Significativita:   {z_score:.4f}")
    print(f"p-value (Laplace):         {p_value:.6e}")
    print(f"Report Esportato su:       {output_summary_path}")
    print("=========================================================")

    return results_summary


if __name__ == "__main__":
    execute_master_null_model()
