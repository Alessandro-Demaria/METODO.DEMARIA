"""
===============================================================================
METODO DEMARIA® — SPATIAL STRUCTURAL STABILITY ANALYSIS (v3.2 CANONICO)
===============================================================================
Modulo 5: 5_train_test_split_validation.py
Autore e Inventore: Avv. Alessandro Demaria
PEC: avv.alessandrodemaria@pec.it
DOI UFFICIALE: 10.5281/zenodo.23199718
Licenza: CC BY 4.0
===============================================================================
"""

import json
import numpy as np
import pandas as pd
import importlib.util

spec_p1 = importlib.util.spec_from_file_location("voynich_parser_1", "1_voynich_parser.py")
vp1 = importlib.util.module_from_spec(spec_p1)
spec_p1.loader.exec_module(vp1)

SPEC_FILE = 'method_specification.json'


def _load_default_inputs():
    spec = vp1.load_method_specification(SPEC_FILE)
    raw_matrix = spec.get("transition_matrix_validity", {}).get("allowed_transitions", None)
    
    if raw_matrix is None:
        raw_matrix = [
            [True, True, False, False],
            [False, True, True, False],
            [False, False, True, True],
            [True, False, False, True]
        ]

    transition_matrix = np.array(raw_matrix, dtype=bool)
    df = vp1.parse_and_clean_dataset(SPEC_FILE)
    return df, transition_matrix


def run_holdout_validation(df=None, transition_matrix=None, split_ratio=0.5, seed=42):
    """
    Esegue l'Analisi di Stabilità Strutturale Spaziale mediante Singolo Holdout Split 50/50 sui Folii Canonici.
    Integrazione NOTA SAVERIO (Punto 3.1 / P1.1): Misurazione della stabilità descrittiva tra sottoinsiemi.
    """
    if df is None or transition_matrix is None:
        df, transition_matrix = _load_default_inputs()

    df = df[df['State'] >= 0].copy()

    unique_folios = df['Folio_Base'].unique()
    n_folios = len(unique_folios)

    rng = np.random.default_rng(seed)
    shuffled_folios = rng.permutation(unique_folios)

    split_point = int(n_folios * split_ratio)
    train_folios = shuffled_folios[:split_point]
    test_folios = shuffled_folios[split_point:]

    df_train = df[df['Folio_Base'].isin(train_folios)].copy()
    df_test = df[df['Folio_Base'].isin(test_folios)].copy()

    c_train = vp1.compute_c_raw_segmented(df_train, transition_matrix)
    c_test = vp1.compute_c_raw_segmented(df_test, transition_matrix)

    delta_c_abs = abs(c_train - c_test)
    delta_c_pct = (delta_c_abs / c_train) * 100.0 if c_train > 0 else 0.0

    print("\n>>> ESECUZIONE SPATIAL STRUCTURAL STABILITY ANALYSIS (HOLDOUT SINGLE SPLIT 50/50) <<<")
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


def run_repeated_holdout_validation(df=None, transition_matrix=None, n_iterations=1000, split_ratio=0.5, seed=42):
    """
    Esegue l'Analisi di Stabilità Strutturale Spaziale mediante REPEATED MONTE CARLO HOLDOUT (1.000 Iterazioni).
    Integrazione NOTA SAVERIO (Punto 3.2 / P1.2): Calcola media, deviazione standard, errore standard
    e Intervalli di Confidenza (IC) al 95% per Delta C e Delta C %.
    """
    if df is None or transition_matrix is None:
        df, transition_matrix = _load_default_inputs()

    df = df[df['State'] >= 0].copy()
    unique_folios = df['Folio_Base'].unique()
    n_folios = len(unique_folios)
    split_point = int(n_folios * split_ratio)

    rng = np.random.default_rng(seed)

    delta_c_abs_list = np.zeros(n_iterations, dtype=np.float64)
    delta_c_pct_list = np.zeros(n_iterations, dtype=np.float64)
    c_train_list = np.zeros(n_iterations, dtype=np.float64)
    c_test_list = np.zeros(n_iterations, dtype=np.float64)

    for i in range(n_iterations):
        shuffled_folios = rng.permutation(unique_folios)
        train_folios = shuffled_folios[:split_point]
        test_folios = shuffled_folios[split_point:]

        df_train = df[df['Folio_Base'].isin(train_folios)]
        df_test = df[df['Folio_Base'].isin(test_folios)]

        c_tr = vp1.compute_c_raw_segmented(df_train, transition_matrix)
        c_te = vp1.compute_c_raw_segmented(df_test, transition_matrix)

        d_abs = abs(c_tr - c_te)
        d_pct = (d_abs / c_tr) * 100.0 if c_tr > 0 else 0.0

        c_train_list[i] = c_tr
        c_test_list[i] = c_te
        delta_c_abs_list[i] = d_abs
        delta_c_pct_list[i] = d_pct

    mean_delta_abs = float(np.mean(delta_c_abs_list))
    std_delta_abs = float(np.std(delta_c_abs_list, ddof=1))
    ci95_abs_low = float(np.percentile(delta_c_abs_list, 2.5))
    ci95_abs_high = float(np.percentile(delta_c_abs_list, 97.5))

    mean_delta_pct = float(np.mean(delta_c_pct_list))
    std_delta_pct = float(np.std(delta_c_pct_list, ddof=1))
    ci95_pct_low = float(np.percentile(delta_c_pct_list, 2.5))
    ci95_pct_high = float(np.percentile(delta_c_pct_list, 97.5))

    print(f"\n>>> ESECUZIONE REPEATED MONTE CARLO HOLDOUT VALIDATION (N={n_iterations}) <<<")
    print(f"[*] Media Delta C Assoluto: {mean_delta_abs:.6f} | Std: {std_delta_abs:.6f}")
    print(f"[*] IC 95% Delta C Assoluto: [{ci95_abs_low:.6f}, {ci95_abs_high:.6f}]")
    print(f"[*] Media Delta C %:        {mean_delta_pct:.2f}% | Std: {std_delta_pct:.2f}%")
    print(f"[*] IC 95% Delta C %:       [{ci95_pct_low:.2f}%, {ci95_pct_high:.2f}%]\n")

    summary_repeated = {
        "n_iterations": n_iterations,
        "mean_c_train": float(np.mean(c_train_list)),
        "mean_c_test": float(np.mean(c_test_list)),
        "mean_delta_c_abs": mean_delta_abs,
        "std_delta_c_abs": std_delta_abs,
        "ci95_abs_low": ci95_abs_low,
        "ci95_abs_high": ci95_abs_high,
        "mean_delta_c_pct": mean_delta_pct,
        "std_delta_c_pct": std_delta_pct,
        "ci95_pct_low": ci95_pct_low,
        "ci95_pct_high": ci95_pct_high
    }

    return summary_repeated


if __name__ == "__main__":
    print("Modulo 5_train_test_split_validation.py pronto all'uso e bonificato (v3.2 Canonico).")