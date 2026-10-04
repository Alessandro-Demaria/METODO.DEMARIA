#!/usr/bin/env python3
# METODO DEMARIA® - Out-of-Sample Validation (Release v3.0)
# ------------------------------------------------------------------
# Cross-validation codicologica basata su GroupKFold / GroupShuffleSplit
# per colonna 'Folio_Base' a garanzia dell'assenza di data leakage cross-folio.
# Autore: Avv. Alessandro Demaria | Licenza: CC BY-NC-ND 4.0

import os
import sys
import pandas as pd
import numpy as np
from sklearn.model_selection import GroupShuffleSplit


def run_out_of_sample_validation(csv_path: str = "voynich_eva_tokens_extended.csv",
                                  output_summary_path: str = "out_of_sample_results.csv",
                                  n_splits: int = 5,
                                  test_size: float = 0.20,
                                  seed: int = 42) -> tuple:
    # 0. Verifica presenza del dataset di input
    if not os.path.exists(csv_path):
        print(f"ERRORE CRITICO: File dataset '{csv_path}' non trovato.")
        sys.exit(1)

    df = pd.read_csv(csv_path)

    # Verifica colonne richieste
    if 'Token' not in df.columns or 'Folio_Base' not in df.columns:
        print("ERRORE CRITICO: Il dataset deve contenere le colonne 'Token' e 'Folio_Base'.")
        sys.exit(1)

    # 1. Matrice di adiacenza delle transizioni valide del Computus Magnus (7/16 ammesse)
    transition_matrix = np.array([
        [1, 1, 0, 0],  # alpha -> alpha, beta
        [0, 1, 1, 0],  # beta  -> beta, delta
        [0, 0, 1, 1],  # delta -> delta, gamma
        [1, 0, 0, 1]   # gamma -> gamma, alpha
    ], dtype=float)

    # 2. Mappatura Canonica Demaria® v3.0 (Partizione Rigida 5-5-5-5)
    demaria_map = {
        'o': 0, 'a': 0, 'e': 0, 'c': 0, 'h': 0,  # alpha (0)
        'k': 1, 't': 1, 'p': 1, 'f': 1, 's': 1,  # beta  (1)
        'r': 2, 'l': 2, 'q': 2, 'y': 2, 'd': 2,  # delta (2)
        'x': 3, 'g': 3, 'm': 3, 'n': 3, 'i': 3   # gamma (3)
    }

    tokens = df['Token'].astype(str).to_numpy()
    folios = df['Folio_Base'].astype(str).to_numpy()

    # 3. Conversione del corpus negli stati cibernetici
    corpus_states = np.zeros(len(tokens), dtype=int)
    for idx, token_str in enumerate(tokens):
        mapped_values = [demaria_map[char] for char in token_str if char in demaria_map]
        corpus_states[idx] = mapped_values[0] if len(mapped_values) > 0 else 0

    # 4. Inizializzazione GroupShuffleSplit basato su Folio_Base (Zero Data Leakage)
    gss = GroupShuffleSplit(n_splits=n_splits, test_size=test_size, random_state=seed)

    in_sample_scores = []
    out_of_sample_scores = []

    fold_details = []

    # 5. Iterazione sulle partizioni trasversali di validazione
    for fold_idx, (train_idx, test_idx) in enumerate(gss.split(corpus_states, groups=folios), start=1):
        # In-Sample (Train Fold)
        train_states = corpus_states[train_idx]
        if len(train_states) > 1:
            tr_curr = train_states[:-1]
            tr_next = train_states[1:]
            c_star_in = float(np.mean(transition_matrix[tr_curr, tr_next]))
        else:
            c_star_in = 0.0

        # Out-of-Sample (Test Fold)
        test_states = corpus_states[test_idx]
        if len(test_states) > 1:
            te_curr = test_states[:-1]
            te_next = test_states[1:]
            c_star_out = float(np.mean(transition_matrix[te_curr, te_next]))
        else:
            c_star_out = 0.0

        in_sample_scores.append(c_star_in)
        out_of_sample_scores.append(c_star_out)

        fold_details.append({
            "Fold": fold_idx,
            "Train_Tokens": len(train_idx),
            "Test_Tokens": len(test_idx),
            "C_Star_In_Sample": c_star_in,
            "C_Star_Out_Of_Sample": c_star_out,
            "Delta_Abs": abs(c_star_in - c_star_out)
        })

    # 6. Aggregazione metrica di stabilità Out-of-Sample
    mean_in_sample = float(np.mean(in_sample_scores))
    mean_out_sample = float(np.mean(out_of_sample_scores))
    std_out_sample = float(np.std(out_of_sample_scores))
    max_delta = float(np.max([f["Delta_Abs"] for f in fold_details]))

    # 7. Salvataggio report analitico
    report_df = pd.DataFrame(fold_details)
    report_df.to_csv(output_summary_path, index=False)

    # 8. Stampa formale dell'output di laboratorio
    print("=========================================================")
    print("   METODO DEMARIA® v3.0 — OUT-OF-SAMPLE VALIDATION       ")
    print("=========================================================")
    print(f"Dataset Analizzato:        {csv_path}")
    print(f"Token Totali:              {len(tokens):,}")
    print(f"Folii Unici Raggruppati:   {len(np.unique(folios)):,}")
    print(f"Numero di Partizioni (K):  {n_splits}")
    print(f"Media C* In-Sample:        {mean_in_sample:.6f}")
    print(f"Media C* Out-of-Sample:    {mean_out_sample:.6f}")
    print(f"Dev. Std. Out-of-Sample:   {std_out_sample:.6f}")
    print(f"Scostamento Max (Delta):   {max_delta:.6f}")
    print(f"Report Esportato su:       {output_summary_path}")
    print("=========================================================")

    return mean_in_sample, mean_out_sample, std_out_sample


if __name__ == "__main__":
    run_out_of_sample_validation()
