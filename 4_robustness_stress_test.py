"""
===============================================================================
METODO DEMARIA® — UNIFORM STATE REPLACEMENT ROBUSTNESS TEST (v3.2 CANONICO)
===============================================================================
Modulo 4: 4_robustness_stress_test.py
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


def run_uniform_state_replacement_robustness(df=None, transition_matrix=None, noise_levels=[0.0, 0.01, 0.05, 0.10, 0.20, 0.30], n_iterations=100, seed=42):
    """
    Esegue lo Stress Test di Robustezza a Perturbazione Uniforme degli Stati (Uniform State Replacement Robustness Test).
    Inietta quote crescenti di rumore numerico rimpiazzando casualmente uno stato con un intero uniforme da 0 a 3,
    misurando la ritenzione di coerenza sintattica grezza C_raw.
    Integrazione NOTA SAVERIO (Punto 3.3 / P1.3): Correct labeling formale ed eliminazione di sovra-interpretazioni semantiche.
    """
    if df is None or transition_matrix is None:
        df, transition_matrix = _load_default_inputs()

    df = df[df['State'] >= 0].copy()
    c_obs_baseline = vp1.compute_c_raw_segmented(df, transition_matrix)

    rng = np.random.default_rng(seed)
    results = []

    print("\n>>> ESECUZIONE UNIFORM STATE REPLACEMENT ROBUSTNESS TEST <<<")
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
                # Sostituzione casuale uniforme tra i 4 stati vettoriali minimi (0, 1, 2, 3)
                df_noisy.iloc[corrupt_indices, df_noisy.columns.get_loc('State')] = rng.integers(0, 4, size=n_corrupt)
                
                scores[i] = vp1.compute_c_raw_segmented(df_noisy, transition_matrix)

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

        print(f"   - Livello Perturbazione {int(noise*100):2d}%: C_raw = {c_mean:.6f} | Std = {c_std:.6f} | Ritenzione = {retention:.2f}%")

    results_df = pd.DataFrame(results)
    print("\n[+] Stress test di perturbazione uniforme completato con successo.\n")
    return results_df


run_robustness_stress_test = run_uniform_state_replacement_robustness


if __name__ == "__main__":
    print("Modulo 4_robustness_stress_test.py pronto all'uso e bonificato (v3.2 Canonico).")