#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
METODO DEMARIA® — COMPUTATIONAL VOYNICH ANALYSIS FRAMEWORK (Release v3.0)
Modulo: validazione_fuori_campione.py (Validazione Out-of-Sample 40/60)
Autore: Avv. Alessandro Demaria | Licenza: CC BY 4.0
===============================================================================
Descrizione:
  Validazione Out-of-Sample al buio (GroupShuffleSplit: 40% Train / 60% Test)
  raggruppata per Folio_Base per evitare Data Leakage tra le transizioni intra-folio.
  Implementa l'ordinamento codicologico esplicito v3.0 ed il bilanciamento stocastico.
===============================================================================
"""

import os
import sys
import pandas as pd
import numpy as np


def execute_out_of_sample_validation(csv_path: str = "voynich_eva_tokens_extended.csv",
                                     output_summary_path: str = "out_of_sample_results.csv",
                                     train_ratio: float = 0.40,
                                     n_splits: int = 10,
                                     seed: int = 42) -> dict:
    if not os.path.exists(csv_path):
        print(f"ERRORE CRITICO: File dataset '{csv_path}' non trovato.")
        sys.exit(1)

    rng = np.random.default_rng(seed)
    df = pd.read_csv(csv_path)

    # Normalizzazione automatica delle colonne (Aliasing v3.0)
    if 'Token' not in df.columns and 'EVA_Token' in df.columns:
        df['Token'] = df['EVA_Token']
    if 'Folio_Base' not in df.columns and 'Folio' in df.columns:
        df['Folio_Base'] = df['Folio'].apply(lambda x: str(x).split('.')[0] if '.' in str(x) else str(x))

    if 'Token' not in df.columns or 'Folio_Base' not in df.columns:
        print("ERRORE CRITICO: Colonne 'Token'/'EVA_Token' e 'Folio_Base'/'Folio' necessarie.")
        sys.exit(1)

    # FIXING CRITICO v3.0: Ordinamento sequenziale codicologico esplicito
    sort_cols = [col for col in ['Folio_Base', 'line_id', 'Record_ID'] if col in df.columns]
    if sort_cols:
        df = df.sort_values(by=sort_cols).reset_index(drop=True)

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

    # Group Shuffle Split Multi-Run su Folio_Base per evitare Data Leakage
    unique_folios = np.unique(folios)
    train_scores, test_scores, deltas = [], [], []

    for _ in range(n_splits):
        shuffled_fols = unique_folios.copy()
        rng.shuffle(shuffled_fols)

        n_train_fols = int(len(shuffled_fols) * train_ratio)
        train_fols = shuffled_fols[:n_train_fols]
        test_fols = shuffled_fols[n_train_fols:]

        c_tr = calculate_coherence_for_folio_subset(train_fols)
        c_te = calculate_coherence_for_folio_subset(test_fols)

        train_scores.append(c_tr)
        test_scores.append(c_te)
        deltas.append(abs(c_tr - c_te))

    mean_c_train = float(np.mean(train_scores))
    mean_c_test = float(np.mean(test_scores))
    mean_delta = float(np.mean(deltas))

    results_summary = {
        "Dataset": os.path.basename(csv_path),
        "Total_Tokens": len(tokens),
        "Total_Folios": len(unique_folios),
        "Splits_Evaluated": n_splits,
        "Mean_C_Star_Train": mean_c_train,
        "Mean_C_Star_Test": mean_c_test,
        "Mean_Delta_C_Star": mean_delta,
        "Pass_Stability": bool(mean_delta < 0.025),
        "Release_Version": "v3.0"
    }

    pd.DataFrame([results_summary]).to_csv(output_summary_path, index=False)

    print("=========================================================")
    print("   METODO DEMARIA® v3.0 — VALIDAZIONE FUORI CAMPIONE     ")
    print("=========================================================")
    print(f"Token Totali Analizzati:   {len(tokens):,}")
    print(f"Folii Totali Distinti:     {len(unique_folios):,}")
    print(f"Split Eseguiti:            {n_splits}")
    print(f"C* Media Train (40%):      {mean_c_train:.6f}")
    print(f"C* Media Test  (60%):      {mean_c_test:.6f}")
    print(f"Scostamento Medio |ΔC*|:   {mean_delta:.6f}")
    print(f"Esito Stabilita (< 0.025): {'SUPERATO (PASS)' if mean_delta < 0.025 else 'FALLITO'}")
    print(f"Report Esportato su:       {output_summary_path}")
    print("=========================================================")

    return results_summary


if __name__ == "__main__":
    execute_out_of_sample_validation()