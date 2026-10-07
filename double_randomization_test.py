"""
===============================================================================
METODO DEMARIA® — DOUBLE RANDOMIZATION TEST (v3.1 CANONICO - ISOMORFO)
===============================================================================
Modulo: double_randomization_test.py
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


def run_double_randomization_test(df=None, transition_matrix=None, n_simulations=10000, seed=42):
    """
    Esegue il Double Randomization Test controllato:
    1. Permutazione stocastica della sequenza di stati del testo.
    2. Permutazione isomorfa delle etichette della matrice di adiacenza 
       (preserva gradi uscenti/entranti e la densità topologica del grafo).
    """
    if df is None or transition_matrix is None:
        df, transition_matrix = _load_inputs()

    rng = np.random.default_rng(seed)
    
    states = df['State'].to_numpy(dtype=int)
    line_ids = df['Line_Num'].to_numpy(dtype=int)

    # Maschera per transizioni sullo stesso rigo
    same_line_mask = (line_ids[:-1] == line_ids[1:])
    n_transitions = np.sum(same_line_mask)

    if n_transitions == 0:
        raise ValueError("[-] ERRORE CRITICO: Nessuna transizione valida nel dataset.")

    # Calcolo C_raw osservato
    src_obs = states[:-1][same_line_mask]
    dst_obs = states[1:][same_line_mask]
    tm_array = np.array(transition_matrix, dtype=bool)
    c_obs = np.sum(tm_array[src_obs, dst_obs]) / n_transitions

    print("=" * 70)
    print("METODO DEMARIA® — DOUBLE RANDOMIZATION TEST (v3.1 ISOMORFO)")
    print("=" * 70)
    print(f"\n[+] Coerenza Osservata Reale (C_raw):         {c_obs:.6f} ({c_obs*100:.2f}%)")
    print(f"[*] Simulazioni Monte Carlo (N):             {n_simulations}")
    print(f"[*] Seed del Generatore Pseudo-Casuale:     {seed}\n")
    print("-" * 70)

    null_scores = np.zeros(n_simulations, dtype=np.float64)

    for i in range(n_simulations):
        # 1. Permutazione stocastica della sequenza di testo
        perm_states = rng.permutation(states)
        src = perm_states[:-1][same_line_mask]
        dst = perm_states[1:][same_line_mask]

        # 2. Permutazione isomorfa delle etichette dei nodi (0, 1, 2, 3)
        node_perm = rng.permutation(4)
        # Riorganizza le righe e le colonne della matrice in base alla permutazione dei nodi
        perm_tm = tm_array[node_perm][:, node_perm]

        # 3. Calcolo della coerenza nullo
        null_scores[i] = np.sum(perm_tm[src, dst]) / n_transitions

    # Statistiche sintetiche
    dr_mean = float(np.mean(null_scores))
    dr_std = float(np.std(null_scores, ddof=1))
    dr_z = float((c_obs - dr_mean) / dr_std) if dr_std > 0 else 0.0
    dr_p = float(np.sum(null_scores >= c_obs) / n_simulations)

    print(">>> RISULTATI DOUBLE RANDOMIZATION TEST (ISOMORFO) <<<")
    print(f"   - Double Null Mean : {dr_mean:.6f}")
    print(f"   - Double Null Std  : {dr_std:.6f}")
    print(f"   - Z-Score          : {dr_z:+.4f}")
    print(f"   - Empirical p-val  : {dr_p:.6f}\n")

    if dr_z > 3.0:
        print("[+] ESITO: SIGNIFICATIVITÀ CONFERMATA. L'effetto sintattico è robusto")
        print("    sia contro la sequenza sia contro il mapping delle etichette.")
    else:
        print("[!] ESITO: Significatività non raggiunta sotto doppia permutazione.")

    print("=" * 70 + "\n")

    results_df = pd.DataFrame([{
        "model": "Double Randomization Null (Isomorph)",
        "c_obs": c_obs,
        "mean": dr_mean,
        "std": dr_std,
        "z_score": dr_z,
        "p_value": dr_p
    }])

    return results_df


if __name__ == "__main__":
    run_double_randomization_test()