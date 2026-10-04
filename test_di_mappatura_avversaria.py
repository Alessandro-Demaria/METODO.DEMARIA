#!/usr/bin/env python3
# METODO DEMARIA® - Test di Mappatura Avversaria (Release v3.0 - Tier B / CR-04)
# ------------------------------------------------------------------
# Test avversario cieco: 10.000 permutazioni stocastiche dell'alfabeto EVA
# su partizione fissa (5, 5, 5, 5) per verificare la selettività stocastica.
# Autore: Avv. Alessandro Demaria | Licenza: CC BY-NC-ND 4.0

import os
import sys
import pandas as pd
import numpy as np


def execute_constrained_adversarial_test(csv_path: str = "voynich_eva_tokens_extended.csv",
                                        output_summary_path: str = "adversarial_test_results.csv",
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

    # Alfabeto EVA di riferimento (20 grafemi)
    eva_graphemes = np.array(['o', 'a', 'e', 'c', 'h',
                              'k', 't', 'p', 'f', 's',
                              'r', 'l', 'q', 'y', 'd',
                              'x', 'g', 'm', 'n', 'i'])

    # Mappatura reale METODO DEMARIA (Partizione fissa 5-5-5-5)
    demaria_map = {
        'o': 0, 'a': 0, 'e': 0, 'c': 0, 'h': 0,
        'k': 1, 't': 1, 'p': 1, 'f': 1, 's': 1,
        'r': 2, 'l': 2, 'q': 2, 'y': 2, 'd': 2,
        'x': 3, 'g': 3, 'm': 3, 'n': 3, 'i': 3
    }

    def compute_states_from_map(mapping_dict: dict) -> np.ndarray:
        states = np.zeros(len(tokens), dtype=int)
        for idx, token_str in enumerate(tokens):
            mapped_values = [mapping_dict[char] for char in token_str if char in mapping_dict]
            if len(mapped_values) > 0:
                counts = np.bincount(mapped_values, minlength=4)
                states[idx] = int(np.argmax(counts))
            else:
                states[idx] = 0
        return states

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

    # 1. Calcolo Coerenza Reale METODO DEMARIA (whole-token)
    real_states = compute_states_from_map(demaria_map)
    c_star_obs = calculate_coherence_intra_folio(real_states)

    # 2. Simulazione Avversaria: 10.000 permutazioni dell'assegnazione dei 20 grafemi con partizione fissa (5,5,5,5)
    fixed_partition_states = np.repeat([0, 1, 2, 3], 5)
    adversarial_scores = np.zeros(n_iterations, dtype=float)

    for i in range(n_iterations):
        shuffled_partition = rng.permutation(fixed_partition_states)
        random_map = dict(zip(eva_graphemes, shuffled_partition))
        rand_states = compute_states_from_map(random_map)
        adversarial_scores[i] = calculate_coherence_intra_folio(rand_states)

    mean_null = float(np.mean(adversarial_scores))
    std_null = float(np.std(adversarial_scores))
    percentile_rank = float(np.mean(adversarial_scores <= c_star_obs) * 100.0)
    p_value = float((np.sum(adversarial_scores >= c_star_obs) + 1) / (n_iterations + 1))
    z_score = float((c_star_obs - mean_null) / std_null) if std_null > 0 else 0.0

    results_summary = {
        "Dataset": os.path.basename(csv_path),
        "Total_Tokens": len(tokens),
        "C_Star_Observed": c_star_obs,
        "Adversarial_Mean": mean_null,
        "Adversarial_Std": std_null,
        "Percentile_Rank": percentile_rank,
        "Z_Score": z_score,
        "p_value": p_value,
        "Release_Version": "v3.0"
    }

    pd.DataFrame([results_summary]).to_csv(output_summary_path, index=False)

    print("=========================================================")
    print("   METODO DEMARIA® v3.0 — TEST MAPPATURA AVVERSARIA     ")
    print("=========================================================")
    print(f"C* Osservato (Mappatura Demaria): {c_star_obs:.6f}")
    print(f"Media Mappature Avversarie:       {mean_null:.6f}")
    print(f"Percentile Posizionamento:       {percentile_rank:.2f}°")
    print(f"Z-Score Significatività:          {z_score:.4f}")
    print(f"p-value (Laplace):                {p_value:.6e}")
    print(f"Report Esportato su:              {output_summary_path}")
    print("=========================================================")

    return results_summary


if __name__ == "__main__":
    execute_constrained_adversarial_test()