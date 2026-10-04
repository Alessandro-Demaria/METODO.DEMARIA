#!/usr/bin/env python3
# METODO DEMARIA® - Out-of-Sample Validation (Release v3.0)
# ------------------------------------------------------------------
# Cross-validation codicologica basata su GroupShuffleSplit per colonna 'Folio_Base'
# a garanzia dell'assenza di data leakage e con isolamento dei confini di folio.
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
    # 0. Verifica e caricamento dataset
    if not os.path.exists(csv_path):
        print(f"ERRORE CRITICO: File dataset '{csv_path}' non trovato.")
        sys.exit(1)

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

    def calculate_coherence_intra_folio_subset(subset_indices: np.ndarray) -> float:
        # Calcolo di C* isolato entro ciascun folio contenuto nel sottoinsieme selezionato
        sub_folios = folios[subset_indices]
        sub_states = corpus_states[subset_indices]
        
        valid_transitions = 0.0
        total_transitions = 0
        unique_sub_folios = np.unique(sub_folios)

        for fol in unique_sub_folios:
            fol_mask = (sub_folios == fol)
            fol_states = sub_states[fol_mask]
            if len(fol_states) > 1:
                s_curr = fol_states[:-1]
                s_next = fol_states[1:]
                valid_transitions += float(np.sum(transition_matrix[s_curr, s_next]))
                total_transitions += len(s_curr)

        return valid_transitions / total_transitions if total_transitions > 0 else 0.0

    # 4. GroupShuffleSplit basato su Folio_Base (Zero Data Leakage)
    gss = GroupShuffleSplit(n_splits=n_splits, test_size=test_size, random_state=seed)

    in_sample_scores = []
    out_of_sample_scores = []
    fold_details = []

    # 5. Iterazione sulle partizioni trasversali di validazione
    for fold_idx, (train_idx, test_idx) in enumerate(gss.split(corpus_states, groups=folios), start=1):
        c_star_in = calculate_coherence_intra_folio_subset(train_idx)
        c_star_out = calculate_coherence_intra_folio_subset(test_idx)

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

    # 6. Aggregazione metrica di stabilita Out-of-Sample
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
