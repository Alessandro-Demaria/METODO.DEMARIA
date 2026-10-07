"""
===============================================================================
METODO DEMARIA® — DOUBLE RANDOMIZATION ADVERSARIAL TEST (v3.2 CANONICO)
===============================================================================
Modulo: double_randomization_test.py
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


def run_double_randomization_test(df=None, transition_matrix=None, n_simulations=10000, seed=42):
    """
    Esegue il Test Avversariale Isomorfo di Doppia Randomizzazione.
    Applica sia la permutazione delle sequenze sia lo shuffle casuale isomorfo
    della matrice di transizione (mantenendo fissa la densità delle celle ammesse).
    
    Interpretazione Inferenziale Canonica (Paper v3.2 / Peer-Review Aligned):
    Un p-value neutrale (p >= 0.05) attesta che la matrice casuale sotto permutazione
    non estrae falsa coerenza, fungendo da baseline di controllo neutrale.
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

    # Filtraggio token validi e verifica Composite_Line_Key
    df = df[df['State'] >= 0].copy()
    states = df['State'].to_numpy(dtype=int)
    line_keys = df['Composite_Line_Key'].to_numpy()

    # Maschera di adiacenza rigida su Composite_Line_Key (Zero Leakage)
    same_line_mask = (line_keys[:-1] == line_keys[1:])
    n_transitions = np.sum(same_line_mask)

    c_obs = compute_c_raw_segmented(df, transition_matrix)
    rng = np.random.default_rng(seed)

    tm_flat = transition_matrix.flatten()
    n_ones = np.sum(tm_flat)
    matrix_size = tm_flat.shape[0]

    double_null_scores = np.zeros(n_simulations, dtype=np.float64)

    print("\n>>> ESECUZIONE ISOMORPHIC DOUBLE RANDOMIZATION TEST (N=10000) <<<")
    print(f"[*] Coerenza Reale Osservata (C_obs): {c_obs:.6f}")
    print(f"[*] Densità Matrice Canonica:          {n_ones}/{matrix_size} ({n_ones/matrix_size*100:.1f}%)\n")

    for i in range(n_simulations):
        # 1. Permutazione globale del vettore degli stati
        perm_states = rng.permutation(states)
        
        # 2. Randomizzazione della matrice mantenendo la medesima densità di ammissibilità
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
    
    # Correzione Monte Carlo: p = (r + 1) / (N + 1)
    double_p = float((np.sum(double_null_scores >= c_obs) + 1) / (n_simulations + 1))

    print(f"   - Double Null Mean: {double_mean:.6f} | Std: {double_std:.6f}")
    print(f"   - Double Null Z:    {double_z:+.4f} | p-value: {double_p:.6f}")
    
    if double_p >= 0.05:
        print("   - Esito Inferenziale: Baseline Neutrale di Controllo (Nessuna distorsione artificiale).\n")
    else:
        print("   - Esito Inferenziale: Deviazione Significativa.\n")

    result_summary = {
        "c_obs": c_obs,
        "double_null_mean": double_mean,
        "double_null_std": double_std,
        "double_null_z": double_z,
        "double_null_p": double_p
    }

    return result_summary, double_null_scores


if __name__ == "__main__":
    print("Modulo double_randomization_test.py pronto all'uso e bonificato (v3.2 Canonico).")