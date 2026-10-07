"""
===============================================================================
METODO DEMARIA® — SPATIAL STRUCTURAL STABILITY ANALYSIS (v3.2 CANONICO)
===============================================================================
Modulo: train_test_split_validation.py
Autore e Inventore: Avv. Alessandro Demaria
PEC: avv.alessandrodemaria@pec.it
DOI UFFICIALE: 10.5281/zenodo.23199718
Licenza: CC BY 4.0
===============================================================================
"""

import json
import numpy as np
import pandas as pd
from voynich_parser import parse_and_clean_dataset, load_method_specification, compute_c_raw_segmented, SPEC_FILE


def run_holdout_validation(df=None, transition_matrix=None, split_ratio=0.5, seed=42):
    """
    Esegue l'Analisi di Stabilità Strutturale Spaziale mediante Holdout Split 50/50 sui 227 Folii Canonici.
    Valuta lo scarto percentuale Delta C % tra sottoinsiemi indipendenti di folii.
    """
    spec = load_method_specification(SPEC_FILE)

    if df is None:
        df = parse_and_clean_dataset(SPEC_FILE)

    if transition_matrix is None:
        raw_matrix = spec.get("transition_matrix_validity", {}).get("allowed_transitions", None)
        if raw_matrix is None:
            raw_matrix = [
                [1, 1, 0, 0],
                [0, 1, 1, 0],
                [0, 0, 1, 1],
                [1, 0, 0, 1]
            ]
        transition_matrix = np.array(raw_matrix, dtype=bool)

    df = df[df['State'] >= 0].copy()

    # Estrazione folii unici isolati (227 Folii Canonici)
    unique_folios = df['Folio_Base'].unique()
    n_folios = len(unique_folios)

    rng = np.random.default_rng(seed)
    shuffled_folios = rng.permutation(unique_folios)

    split_point = int(n_folios * split_ratio)
    train_folios = shuffled_folios[:split_point]
    test_folios = shuffled_folios[split_point:]

    df_train = df[df['Folio_Base'].isin(train_folios)].copy()
    df_test = df[df['Folio_Base'].isin(test_folios)].copy()

    c_train = compute_c_raw_segmented(df_train, transition_matrix)
    c_test = compute_c_raw_segmented(df_test, transition_matrix)

    delta_c_abs = abs(c_train - c_test)
    delta_c_pct = (delta_c_abs / c_train) * 100.0 if c_train > 0 else 0.0

    print("\n>>> ESECUZIONE SPATIAL STRUCTURAL STABILITY ANALYSIS (HOLDOUT 50/50) <<<")
    print(f"[*] Total Unique Folios: {n_folios}")
    print(f"[*] Training Folios:     {len(train_folios)} | Test Folios: {len(test_folios)}")
    print(f"   - Coerenza Train (C_train): {c_train:.6f}")
    print(f"   - Coerenza Test  (C_test):  {c_test:.6f}")
    print(f"   - Delta C %:                {delta_c_pct:.2f}%\n")

    result_summary = {
        "n_total_folios": n_folios,
        "n_train_folios": len(train_folios),
        "n_test_folios": len(test_folios),
        "c_train": c_train,
        "c_test": c_test,
        "delta_c_abs": delta_c_abs,
        "delta_c_pct": delta_c_pct
    }

    return result_summary


if __name__ == "__main__":
    print("Modulo train_test_split_validation.py pronto all'uso e bonificato (v3.2 Canonico).")