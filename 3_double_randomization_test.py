"""
===============================================================================
METODO DEMARIA® — DOUBLE RANDOMIZATION & MATRIX SWEEP TEST (v3.2 CANONICO)
===============================================================================
Modulo 3: 3_double_randomization_test.py
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


def run_double_randomization_test(df=None, transition_matrix=None, n_simulations=10000, seed=42):
    """
    TEST AVVERSARIALE 1: Isomorphic Double Randomization Test.
    Applica la permutazione simultanea sia del corpus sia della matrice di transizione
    a pari densità (8/16 celle ammesse). Serve da baseline neutrale di controllo generale.
    """
    if df is None or transition_matrix is None:
        df, transition_matrix = _load_default_inputs()

    df = df[df['State'] >= 0].copy()
    states = df['State'].to_numpy(dtype=int)
    line_keys = df['Composite_Line_Key'].to_numpy()

    same_line_mask = (line_keys[:-1] == line_keys[1:])
    n_transitions = np.sum(same_line_mask)

    c_obs = vp1.compute_c_raw_segmented(df, transition_matrix)
    rng = np.random.default_rng(seed)

    tm_flat = transition_matrix.flatten()
    n_ones = np.sum(tm_flat)
    matrix_size = tm_flat.shape[0]

    double_null_scores = np.zeros(n_simulations, dtype=np.float64)

    for i in range(n_simulations):
        perm_states = rng.permutation(states)
        shuffled_flat = np.zeros(matrix_size, dtype=bool)
        ones_indices = rng.choice(matrix_size, size=n_ones, replace=False)
        shuffled_flat[ones_indices] = True
        random_tm = shuffled_flat.reshape(4, 4)

        src = perm_states[:-1][same_line_mask]
        dst = perm_states[1:][same_line_mask]

        double_null_scores[i] = np.sum(random_tm[src, dst]) / n_transitions

    double_mean = float(np.mean(double_null_scores))
    double_std = float(np.std(double_null_scores, ddof=1))
    double_z = float((c_obs - double_mean) / double_std) if double_std > 0 else 0.0
    double_p = float((np.sum(double_null_scores >= c_obs) + 1) / (n_simulations + 1))

    result_summary = {
        "c_obs": c_obs,
        "double_null_mean": double_mean,
        "double_null_std": double_std,
        "double_null_z": double_z,
        "double_null_p": double_p
    }

    return result_summary, double_null_scores


def run_fixed_corpus_matrix_sweep(df=None, transition_matrix=None, n_simulations=10000, seed=42):
    """
    TEST AVVERSARIALE 2 (PUNTO P0.3 NOTA SAVERIO): Fixed-Corpus Matrix Sweep.
    Mantiene il corpus reale del Voynich FISSO e NON permutato, facendo scorrere N matrici
    casuali 4x4 a pari densità (8/16 celle ammesse).
    Isola e dimostra la specificità ed efficacia causale della matrice canonica del Metodo Demaria.
    """
    if df is None or transition_matrix is None:
        df, transition_matrix = _load_default_inputs()

    df = df[df['State'] >= 0].copy()
    states = df['State'].to_numpy(dtype=int)
    line_keys = df['Composite_Line_Key'].to_numpy()

    same_line_mask = (line_keys[:-1] == line_keys[1:])
    n_transitions = np.sum(same_line_mask)

    c_obs = vp1.compute_c_raw_segmented(df, transition_matrix)
    rng = np.random.default_rng(seed)

    tm_flat = transition_matrix.flatten()
    n_ones = np.sum(tm_flat)
    matrix_size = tm_flat.shape[0]

    matrix_sweep_scores = np.zeros(n_simulations, dtype=np.float64)

    src = states[:-1][same_line_mask]
    dst = states[1:][same_line_mask]

    for i in range(n_simulations):
        shuffled_flat = np.zeros(matrix_size, dtype=bool)
        ones_indices = rng.choice(matrix_size, size=n_ones, replace=False)
        shuffled_flat[ones_indices] = True
        random_tm = shuffled_flat.reshape(4, 4)

        matrix_sweep_scores[i] = np.sum(random_tm[src, dst]) / n_transitions

    sweep_mean = float(np.mean(matrix_sweep_scores))
    sweep_std = float(np.std(matrix_sweep_scores, ddof=1))
    sweep_z = float((c_obs - sweep_mean) / sweep_std) if sweep_std > 0 else 0.0
    sweep_p = float((np.sum(matrix_sweep_scores >= c_obs) + 1) / (n_simulations + 1))

    result_summary = {
        "c_obs": c_obs,
        "fixed_corpus_sweep_mean": sweep_mean,
        "fixed_corpus_sweep_std": sweep_std,
        "fixed_corpus_sweep_z": sweep_z,
        "fixed_corpus_sweep_p": sweep_p
    }

    return result_summary, matrix_sweep_scores


if __name__ == "__main__":
    print("Modulo 3_double_randomization_test.py pronto all'uso e bonificato (v3.2 Canonico).")