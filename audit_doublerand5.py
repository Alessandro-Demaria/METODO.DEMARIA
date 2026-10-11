#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Modulo 5: audit_doublerand5.py
Test avversariale di Doppia Randomizzazione Isomorfa (N=10.000, Seed 42)
per la verifica della specificità dell'accoppiamento Matrice-Corpus.

Autore: Avv. Alessandro Demaria
Licenza Codebase: MIT License
Tutela Privativa e Marchio: Art. 98 D.Lgs. 30/2005 (CPI) / L. 633/1941
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from core_matrix2 import TransitionMatrixManager


class IsomorphicDoubleRandomizationAudit:
    """
    Esecutore stocastico per l'Audit Avversariale di Doppia Randomizzazione Isomorfa.
    Permuta simultaneamente le sequenze sintattiche del corpus e la struttura
    della Matrice Canonica 4x4 conservando la densità topologica degli archi.
    """

    def __init__(self, iterations: int = 10000, seed: int = 42) -> None:
        """
        Inizializza il modulo fissando il numero di simulazioni e il Seed deterministico.
        """
        self.iterations: int = iterations
        self.seed: int = seed
        self.matrix_mgr: TransitionMatrixManager = TransitionMatrixManager()

    def _compute_coherence_with_custom_matrix(self, states: np.ndarray, lines: np.ndarray, 
                                              matrix: np.ndarray) -> float:
        """
        Calcola la coerenza sintattica grezza su array di stati e righe utilizzando
        una matrice binaria 4x4 arbitraria o permutata.
        """
        total_transitions: int = 0
        valid_transitions: int = 0
        state_map: Dict[str, int] = self.matrix_mgr.STATE_TO_IDX

        for k in range(len(states) - 1):
            if lines[k] == lines[k + 1]:
                total_transitions += 1
                s_from = states[k]
                s_to = states[k + 1]
                if s_from in state_map and s_to in state_map:
                    i = state_map[s_from]
                    j = state_map[s_to]
                    if matrix[i, j] == 1:
                        valid_transitions += 1

        if total_transitions == 0:
            return 0.0

        return valid_transitions / total_transitions

    def run_double_randomization_test(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Esegue l'Audit di Doppia Randomizzazione Isomorfa su N iterazioni.
        
        Algoritmo:
        1. Estrae le sequenze reali di stati e line_id.
        2. Calcola la coerenza osservata reale C_raw.
        3. Per ciascuna iterazione:
           a. Permuta globalmente la sequenza degli stati assegnati.
           b. Permuta casualmente gli elementi della Matrice Canonica 4x4
              mantenendo invariato il numero totale di 1 (densità di ammissibilità).
           c. Calcola la coerenza sulla combinazione doppiamente permutata.
        4. Estrae media nulla, deviazione standard, Double-Null Z-Score e p-value.
        """
        np.random.seed(self.seed)

        states_orig: np.ndarray = df["assigned_state"].values.copy()
        lines_orig: np.ndarray = df["line_id"].values
        canonical_matrix: np.ndarray = self.matrix_mgr.canonical_matrix.copy()

        # Coerenza osservata reale
        c_real, _, _ = self.matrix_mgr.compute_raw_coherence(df)

        null_coherences: np.ndarray = np.zeros(self.iterations, dtype=np.float64)
        flat_matrix: np.ndarray = canonical_matrix.flatten()

        for it in range(self.iterations):
            # Permutazione 1: Vettore degli stati
            permuted_states: np.ndarray = np.random.permutation(states_orig)

            # Permutazione 2: Celle della Matrice 4x4 (conservando la densità di 1)
            permuted_flat_matrix: np.ndarray = np.random.permutation(flat_matrix)
            permuted_matrix: np.ndarray = permuted_flat_matrix.reshape((4, 4))

            # Calcolo coerenza su doppio nullo
            null_coherences[it] = self._compute_coherence_with_custom_matrix(
                permuted_states, lines_orig, permuted_matrix
            )

        mean_double_null: float = float(np.mean(null_coherences))
        std_double_null: float = float(np.std(null_coherences, ddof=1))

        # Calcolo Double-Null Z-Score
        z_double_score: float = (
            float((c_real - mean_double_null) / std_double_null)
            if std_double_null > 0 else 0.0
        )

        # Calcolo corretto e conservativo del p-value Monte Carlo (Davison-Hinkley)
        count_exceeding: int = int(np.sum(null_coherences >= c_real))
        p_value_empirical: float = float((count_exceeding + 1) / (self.iterations + 1))

        return {
            "test_name": "Isomorphic Double Randomization Test",
            "c_observed": c_real,
            "double_null_mean": mean_double_null,
            "double_null_std": std_double_null,
            "z_double_score": z_double_score,
            "p_value_empirical": p_value_empirical,
            "count_exceeding": count_exceeding,
            "iterations": self.iterations
        }


if __name__ == "__main__":
    # Test unitario rapido di isolamento locale
    print("=== TEST UNITARIO AUDIT_DOUBLERAND5 ===")
    dummy_df = pd.DataFrame({
        "line_id": ["f1r_l1", "f1r_l1", "f1r_l1", "f1r_l2", "f1r_l2", "f1r_l2"],
        "assigned_state": ["Alpha", "Beta", "Gamma", "Alpha", "Beta", "Gamma"]
    })