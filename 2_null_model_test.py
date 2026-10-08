"""
===============================================================================
METODO DEMARIA® — SUITE DI AUDIT MODELLI NULLI GERARCHICI (v3.2 CANONICO)
===============================================================================
Modulo 2: 2_null_model_test.py
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


def _prepare_dataframe(df):
    if 'State' not in df.columns or 'Folio_Base' not in df.columns or 'Composite_Line_Key' not in df.columns:
        df = vp1.parse_and_clean_dataset(SPEC_FILE)
    
    df = df[df['State'] >= 0].copy()
    df['State'] = df['State'].astype(int)
    return df


def run_global_null(df, transition_matrix, n_simulations=10000, rng=None):
    if rng is None:
        rng = np.random.default_rng(42)

    df = _prepare_dataframe(df)
    states = df['State'].to_numpy(dtype=int, copy=True)
    line_keys = df['Composite_Line_Key'].to_numpy()
    
    same_line_mask = (line_keys[:-1] == line_keys[1:])
    n_transitions = np.sum(same_line_mask)
    tm_array = np.array(transition_matrix, dtype=bool)

    null_scores = np.zeros(n_simulations, dtype=np.float64)

    for i in range(n_simulations):
        perm_states = rng.permutation(states)
        src = perm_states[:-1][same_line_mask]
        dst = perm_states[1:][same_line_mask]
        null_scores[i] = np.sum(tm_array[src, dst]) / n_transitions

    return null_scores


def run_intra_folio_null(df, transition_matrix, n_simulations=10000, rng=None):
    if rng is None:
        rng = np.random.default_rng(42)

    df = _prepare_dataframe(df)
    states = df['State'].to_numpy(dtype=int, copy=True)
    folio_ids = df['Folio_Base'].to_numpy()
    line_keys = df['Composite_Line_Key'].to_numpy()

    unique_folios, folio_inverse = np.unique(folio_ids, return_inverse=True)
    folio_indices = [np.where(folio_inverse == i)[0] for i in range(len(unique_folios))]

    same_line_mask = (line_keys[:-1] == line_keys[1:])
    n_transitions = np.sum(same_line_mask)
    tm_array = np.array(transition_matrix, dtype=bool)

    null_scores = np.zeros(n_simulations, dtype=np.float64)

    for i in range(n_simulations):
        perm_states = states.copy()
        for idxs in folio_indices:
            if len(idxs) > 1:
                perm_states[idxs] = rng.permutation(perm_states[idxs])

        src = perm_states[:-1][same_line_mask]
        dst = perm_states[1:][same_line_mask]
        null_scores[i] = np.sum(tm_array[src, dst]) / n_transitions

    return null_scores


def run_intra_line_null(df, transition_matrix, n_simulations=10000, rng=None):
    if rng is None:
        rng = np.random.default_rng(42)

    df = _prepare_dataframe(df)
    states = df['State'].to_numpy(dtype=int, copy=True)
    line_keys = df['Composite_Line_Key'].to_numpy()

    unique_lines, line_inverse = np.unique(line_keys, return_inverse=True)
    line_indices = [np.where(line_inverse == i)[0] for i in range(len(unique_lines))]

    same_line_mask = (line_keys[:-1] == line_keys[1:])
    n_transitions = np.sum(same_line_mask)
    tm_array = np.array(transition_matrix, dtype=bool)

    null_scores = np.zeros(n_simulations, dtype=np.float64)

    for i in range(n_simulations):
        perm_states = states.copy()
        for idxs in line_indices:
            if len(idxs) > 1:
                perm_states[idxs] = rng.permutation(perm_states[idxs])

        src = perm_states[:-1][same_line_mask]
        dst = perm_states[1:][same_line_mask]
        null_scores[i] = np.sum(tm_array[src, dst]) / n_transitions

    return null_scores


def run_full_audit_suite(df=None, transition_matrix=None, n_simulations=10000, seed=42):
    if df is None or transition_matrix is None:
        df, transition_matrix = _load_default_inputs()

    df = _prepare_dataframe(df)
    rng = np.random.default_rng(seed)
    
    c_obs = vp1.compute_c_raw_segmented(df, transition_matrix)

    print(f"\n[+] Coerenza Osservata Reale (C_raw Segmentata): {c_obs:.6f} ({c_obs*100:.2f}%)")
    print(f"[*] Simulazioni Monte Carlo (N):             {n_simulations}")
    print(f"[*] Seed del Generatore Pseudo-Casuale:     {seed}\n")
    print("-" * 70)

    # 1. Global Null
    global_scores = run_global_null(df, transition_matrix, n_simulations, rng)
    g_mean = float(np.mean(global_scores))
    g_std = float(np.std(global_scores, ddof=1))
    g_z = float((c_obs - g_mean) / g_std) if g_std > 0 else 0.0
    g_p = float((np.sum(global_scores >= c_obs) + 1) / (n_simulations + 1))

    # 2. Intra-Folio Null
    folio_scores = run_intra_folio_null(df, transition_matrix, n_simulations, rng)
    f_mean = float(np.mean(folio_scores))
    f_std = float(np.std(folio_scores, ddof=1))
    f_z = float((c_obs - f_mean) / f_std) if f_std > 0 else 0.0
    f_p = float((np.sum(folio_scores >= c_obs) + 1) / (n_simulations + 1))

    # 3. Intra-Line Null
    line_scores = run_intra_line_null(df, transition_matrix, n_simulations, rng)
    l_mean = float(np.mean(line_scores))
    l_std = float(np.std(line_scores, ddof=1))
    l_z = float((c_obs - l_mean) / l_std) if l_std > 0 else 0.0
    l_p = float((np.sum(line_scores >= c_obs) + 1) / (n_simulations + 1))

    results_df = pd.DataFrame([
        {"model": "Global Null", "c_obs": c_obs, "mean": g_mean, "std": g_std, "z_score": g_z, "p_value": g_p},
        {"model": "Intra-Folio Null", "c_obs": c_obs, "mean": f_mean, "std": f_std, "z_score": f_z, "p_value": f_p},
        {"model": "Intra-Line Null", "c_obs": c_obs, "mean": l_mean, "std": l_std, "z_score": l_z, "p_value": l_p}
    ])

    return results_df, global_scores, folio_scores, line_scores


if __name__ == "__main__":
    print("Modulo 2_null_model_test.py pronto all'uso e bonificato (v3.2 Canonico).")