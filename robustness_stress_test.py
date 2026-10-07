"""
===============================================================================
METODO DEMARIA® — ROBUSTNESS & STRESS TEST (v3.2 CANONICO)
===============================================================================
Modulo: robustness_stress_test.py
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


def run_robustness_stress_test(df=None, transition_matrix=None, noise_levels=[0.0, 0.01, 0.05, 0.10, 0.20, 0.30], n_iterations=100, seed=42):
    """
    Esegue lo Stress Test di Resilienza al Rumore di Trascrizione (EVA Noise Stress Test).
    Inietta livelli crescenti di rumore scompaginando casualmente una quota di token
    e misura la ritenzione di coerenza sintattica C_raw.
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
    c_obs_baseline = compute_c_raw_segmented(df, transition_matrix)

    rng = np.random.default_rng(seed)
    results = []

    print("\n>>> ESECUZIONE ROBUSTNESS & NOISE STRESS TEST <<<")
    print(f"[*] Coerenza Baseline (Rumore 0%): {c_obs_baseline:.6f} (100.00%)\n")

    for noise in noise_levels:
        if noise == 0.0:
            c_mean = c_obs_baseline
            c_std = 0.0
            retention = 100.0
        else:
            scores = np.zeros(n_iterations, dtype=np.float64)
            n_tokens = len(df)
            n_corrupt = int(n_tokens * noise)

            for i in range(n_iterations):
                df_noisy = df.copy()
                corrupt_indices = rng.choice(n_tokens, size=n_corrupt, replace=False)
                # Sostituzione casuale con uno dei 4 stati vettoriali (0, 1, 2, 3)
                df_noisy.iloc[corrupt_indices, df_noisy.columns.get_loc('State')] = rng.integers(0, 4, size=n_corrupt)
                
                scores[i] = compute_c_raw_segmented(df_noisy, transition_matrix)

            c_mean = float(np.mean(scores))
            c_std = float(np.std(scores, ddof=1))
            retention = float((c_mean / c_obs_baseline) * 100.0) if c_obs_baseline > 0 else 0.0

        results.append({
            "noise_level": noise,
            "noise_pct": f"{int(noise*100)}%",
            "c_raw_mean": c_mean,
            "std_dev": c_std,
            "retention_pct": retention
        })

        print(f"   - Rumore {int(noise*100):2d}%: C_raw = {c_mean:.6f} | Std = {c_std:.6f} | Ritenzione = {retention:.2f}%")

    results_df = pd.DataFrame(results)
    print("\n[+] Stress Test completato con successo.\n")
    return results_df


if __name__ == "__main__":
    print("Modulo robustness_stress_test.py pronto all'uso e bonificato (v3.2 Canonico).")