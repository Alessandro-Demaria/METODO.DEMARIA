"""
===============================================================================
METODO DEMARIA® — ROBUSTNESS & STRESS TEST (v3.0 CANONICO)
===============================================================================
Modulo: robustness_stress_test.py
Autore: Avv. Alessandro Demaria | Licenza: CC BY 4.0
===============================================================================
"""

import json
import numpy as np
import pandas as pd
from voynich_parser import parse_and_clean_dataset, load_method_specification, SPEC_FILE


def _load_inputs():
    spec = load_method_specification(SPEC_FILE)
    raw_matrix = spec.get("transition_matrix_validity", {}).get("allowed_transitions", None)
    
    if raw_matrix is None:
        raw_matrix = [
            [1, 1, 0, 0],
            [0, 1, 1, 0],
            [0, 0, 1, 1],
            [1, 0, 0, 1]
        ]

    transition_matrix = np.array(raw_matrix, dtype=bool)
    df = parse_and_clean_dataset(SPEC_FILE)
    df = df[df['State'] >= 0].copy()  # Filtra token non riconosciuti
    return df, transition_matrix


def _compute_c_raw_fast(states, line_ids, transition_matrix):
    same_line_mask = (line_ids[:-1] == line_ids[1:])
    n_transitions = np.sum(same_line_mask)
    if n_transitions == 0:
        return 0.0
    src = states[:-1][same_line_mask]
    dst = states[1:][same_line_mask]
    tm_array = np.array(transition_matrix, dtype=bool)
    return float(np.sum(tm_array[src, dst]) / n_transitions)


def run_robustness_stress_test(df=None, transition_matrix=None, noise_levels=None, n_iterations=100, seed=42):
    """
    Simula l'iniezione graduale di rumore/errore di trascrizione (sostituzione stocastica degli stati)
    e valuta la degradazione della coerenza osservata C_raw.
    """
    if df is None or transition_matrix is None:
        df, transition_matrix = _load_inputs()

    if noise_levels is None:
        noise_levels = [0.0, 0.01, 0.05, 0.10, 0.20, 0.30]

    rng = np.random.default_rng(seed)
    
    states_orig = df['State'].to_numpy(dtype=int, copy=True)
    line_ids = df['Line_Num'].to_numpy(dtype=int, copy=True)
    
    c_base = _compute_c_raw_fast(states_orig, line_ids, transition_matrix)

    print("=" * 70)
    print("METODO DEMARIA® — ROBUSTNESS & STRESS TEST (FASE 3)")
    print("=" * 70)
    print(f"\n[+] Coerenza Base Nominale (0% Rumore):     {c_base:.6f} ({c_base*100:.2f}%)")
    print(f"[*] Livelli di Rumore Testati:             {[f'{int(n*100)}%' for n in noise_levels]}")
    print(f"[*] Iterazioni per Livello (Monte Carlo):   {n_iterations}")
    print(f"[*] Seed del Generatore Pseudo-Casuale:     {seed}\n")
    print("-" * 70)
    print(f"{'Rumore (%)':<12} | {'C_raw Medio':<14} | {'Std Dev':<10} | {'Ritenzione Coerenza (%)':<24}")
    print("-" * 70)

    results = []
    n_tokens = len(states_orig)

    for noise in noise_levels:
        if noise == 0.0:
            c_mean = c_base
            c_std = 0.0
            retention = 100.0
        else:
            scores = np.zeros(n_iterations, dtype=np.float64)
            n_corrupt = int(n_tokens * noise)

            for i in range(n_iterations):
                corrupted_states = states_orig.copy()
                corrupt_indices = rng.choice(n_tokens, size=n_corrupt, replace=False)
                # Sostituisce i token selezionati con uno dei 4 stati possibili a caso (0, 1, 2, 3)
                random_states = rng.integers(0, 4, size=n_corrupt)
                corrupted_states[corrupt_indices] = random_states
                
                scores[i] = _compute_c_raw_fast(corrupted_states, line_ids, transition_matrix)

            c_mean = float(np.mean(scores))
            c_std = float(np.std(scores, ddof=1))
            retention = (c_mean / c_base) * 100.0

        print(f"{noise*100:>10.1f}% | {c_mean:>14.6f} | {c_std:>10.6f} | {retention:>22.2f}%")

        results.append({
            "noise_level": noise,
            "noise_percentage": f"{int(noise*100)}%",
            "c_raw_mean": c_mean,
            "c_raw_std": c_std,
            "coherence_retention_pct": retention
        })

    print("-" * 70)
    print("[+] TEST DI ROBUSTEZZA COMPLETATO CON SUCCESSO.")
    print("=" * 70 + "\n")

    results_df = pd.DataFrame(results)
    return results_df


if __name__ == "__main__":
    run_robustness_stress_test()