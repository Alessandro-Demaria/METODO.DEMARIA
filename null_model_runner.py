#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
METODO DEMARIA — COMPUTATIONAL VOYNICH ANALYSIS FRAMEWORK (Release v3.0)
Modulo: null_model_runner.py (Monte Carlo & Adversarial Mapping Suite)
Autore: Avv. Alessandro Demaria
===============================================================================
"""

import numpy as np
import pandas as pd
from typing import Dict, Any

class DemariaNullModelSuite:
    """
    Suite Integrata di Modelli Nulli e Test Avversariali Monte Carlo (Release v3.0).
    Alimentata direttamente dal dataset reale voynich_eva_tokens_extended.csv.
    """

    # Matrice mask 4x4 delle transizioni valide (Black-Box IP)
    VALID_TRANSITIONS_MASK: np.ndarray = np.array([
        [0, 1, 0, 0],  # alpha -> beta
        [0, 1, 1, 0],  # beta  -> beta, delta
        [0, 1, 0, 1],  # delta -> beta, gamma
        [1, 1, 0, 0]   # gamma -> alpha, beta
    ], dtype=bool)

    def __init__(self, seed: int = 42) -> None:
        self.seed = seed
        self.rng = np.random.default_rng(self.seed)

    def _map_tokens_to_states(self, tokens: pd.Series) -> np.ndarray:
        """
        Mappatura deterministica sui 4 stati operatoriali [0..3].
        """
        states = []
        for t in tokens:
            t_str = str(t).lower() if pd.notnull(t) else ''
            if any(c in t_str for c in ['f', 'p', 't', 'k']):
                states.append(0)  # alpha
            elif 'ch' in t_str or 'sh' in t_str:
                states.append(1)  # beta
            elif 'ee' in t_str or 'ii' in t_str:
                states.append(2)  # delta
            else:
                states.append(3)  # gamma
        return np.array(states, dtype=np.int32)

    def run_monte_carlo_test(self, csv_path: str = 'voynich_eva_tokens_extended.csv', iterations: int = 10000) -> Dict[str, Any]:
        """
        Esegue il test Monte Carlo a permutazione casuale sui 35.483 token reali.
        """
        df = pd.read_csv(csv_path)
        states = self._map_tokens_to_states(df['EVA_Token'])
        n_tokens = len(states)

        # 1. Coerenza Osservata Reale
        from_st = states[:-1]
        to_st = states[1:]
        c_star_obs = float(np.mean(self.VALID_TRANSITIONS_MASK[from_st, to_st]))

        # 2. Permutazioni Monte Carlo (Surrogate Data)
        null_c_stars = np.zeros(iterations, dtype=np.float64)
        shuffled_states = states.copy()

        for k in range(iterations):
            self.rng.shuffle(shuffled_states)
            valid_mask = self.VALID_TRANSITIONS_MASK[shuffled_states[:-1], shuffled_states[1:]]
            null_c_stars[k] = np.mean(valid_mask)

        # 3. Calcolo p-value empirico
        p_value = float((np.sum(null_c_stars >= c_star_obs) + 1) / (iterations + 1))

        return {
            'total_tokens': n_tokens,
            'iterations': iterations,
            'observed_c_star': float(np.round(c_star_obs, 4)),
            'null_mean_c_star': float(np.round(np.mean(null_c_stars), 4)),
            'null_std_c_star': float(np.round(np.std(null_c_stars), 4)),
            'null_max_c_star': float(np.round(np.max(null_c_stars), 4)),
            'p_value_empirical': float(np.round(p_value, 6))
        }

if __name__ == '__main__':
    print("=" * 75)
    print("METODO DEMARIA — VERIFICA SUITE MONTE CARLO (35.483 TOKEN REALI)")
    print("=" * 75)

    suite = DemariaNullModelSuite(seed=42)
    res = suite.run_monte_carlo_test('voynich_eva_tokens_extended.csv', iterations=10000)

    print(f"\n[TEST MONTE CARLO] Risultati su N = {res['iterations']} permutazioni:")
    print(f"  Token Totali Processati : {res['total_tokens']}")
    print(f"  Coerenza Osservata (C*) : {res['observed_c_star']:.4f}")
    print(f"  Coerenza Nulla Media    : {res['null_mean_c_star']:.4f} ± {res['null_std_c_star']:.4f}")
    print(f"  Coerenza Nulla Massima  : {res['null_max_c_star']:.4f}")
    print(f"  p-value Empirico        : p = {res['p_value_empirical']}")
    print("=" * 75)