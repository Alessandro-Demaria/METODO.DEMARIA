#!/usr/bin/env python3
# METODO DEMARIA® - Validazione Fuori Campione / Out-of-Sample (Release v3.0)
# ------------------------------------------------------------------
# Validazione Out-of-Sample al buio (GroupShuffleSplit: 40% Train / 60% Test)
# raggruppata per Folio_Base per evitare Data Leakage tra transizioni.
# Autore: Avv. Alessandro Demaria | Licenza: CC BY-NC-ND 4.0

import os
import sys
import pandas as pd
import numpy as np


def execute_out_of_sample_validation(csv_path: str = "voynich_eva_tokens_extended.csv",
                                     output_summary_path: str = "out_of_sample_results.csv",
                                     train_ratio: float = 0.40,
                                     seed: int = 42) -> dict:
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

    def calculate_coherence_for_folio_subset(selected_folios: np.ndarray) -> float:
        valid_transitions = 0.0
        total_transitions = 0
        
        for fol in selected_folios:
            fol_mask = (folios == fol)
            fol_states = corpus_states[fol_mask]
            if len(fol_states) > 1:
                s_curr = fol_states[:-1]
                s_next = fol_states[1:]
                valid_transitions += float(np.sum(transition_matrix[s_curr, s_next]))
                total_transitions += len(s_curr)
                
        return valid_transitions / total_transitions if total_transitions > 0 else 0.0

    # Group Shuffle Split su Folio_Base per evitare Data Leakage
    unique_folios = np.unique(folios)
    rng.shuffle(unique_folios)

    n_train_folios = int(len(unique_folios) * train_ratio)
    train_folios = unique_folios[:n_train_folios]
    test_folios = unique_folios[n_train_folios:]

    c_star_train = calculate_coherence_for_folio_subset(train_folios)
    c_star_test = calculate_coherence_for_folio_subset(test_folios)
    delta_c_star = float(abs(c_star_train - c_star_test))

    results_summary = {
        "Dataset": os.path.basename(csv_path),
        "Total_Tokens": len(tokens),
        "Total_Folios": len(unique_folios),
        "Train_Folios": len(train_folios),
        "Test_Folios": len(test_folios),
        "C_Star_Train": c_star_train,
        "C_Star_Test": c_star_test,
        "Delta_C_Star": delta_c_star,
        "Pass_Stability": bool(delta_c_star < 0.0015),
        "Release_Version": "v3.0"
    }

    pd.DataFrame([results_summary]).to_csv(output_summary_path, index=False)

    print("=========================================================")
    print("   METODO DEMARIA® v3.0 — VALIDAZIONE FUORI CAMPIONE     ")
    print("=========================================================")
    print(f"Folii Totali:             {len(unique_folios):,}")
    print(f"Folii Train (40%):         {len(train_folios):,}")
    print(f"Folii Test  (60%):         {len(test_folios):,}")
    print(f"C* Train (Addestramento):  {c_star_train:.6f}")
    print(f"C* Test  (Validazione):    {c_star_test:.6f}")
    print(f"Scostamento |ΔC*|:        {delta_c_star:.6f}")
    print(f"Esito Stabilita (<0.0015): {'SUPERATO (PASS)' if delta_c_star < 0.0015 else 'FALLITO'}")
    print(f"Report Esportato su:       {output_summary_path}")
    print("=========================================================")

    return results_summary


if __name__ == "__main__":
    execute_out_of_sample_validation()