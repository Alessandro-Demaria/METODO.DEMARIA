#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master-Validato)

Modulo 5: audit_doublerand5.py
Test avversariale di doppia randomizzazione isomorfa (Double Null Test) per la verifica 
della selettività ed esclusività dell'accoppiamento tra la Matrice Canonica ed il Corpus.

Sessione di Lavoro: BARVI
Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
Licenza Codebase: MIT License
Tutela Privativa e Marchio: Art. 98 D.Lgs. 30/2005 (CPI) / L. 633/1941
"""

import numpy as np
import pandas as pd
from typing import Dict, Any
from core_matrix2 import MatrixManager


class DoubleRandomizationAuditor:
    """
    Esecutore stocastico del Test di Doppia Randomizzazione Isomorfa (Double Null Test).
    Permuta simultaneamente sia la sequenza degli stati sintattici sia la topologia
    della matrice di ammissibilità 4x4, preservandone la densità di celle (12/16).
    """

    def __init__(self, matrix_mgr: MatrixManager) -> None:
        """
        Inizializza l'auditor collegando l'istanza del gestore della matrice.
        Risoluzione P0.2: Collegamento diretto agli attributi canonici unificati.
        """
        self.matrix_mgr: MatrixManager = matrix_mgr

    def run_double_randomization_test(
        self,
        df: pd.DataFrame,
        iterations: int = 10000,
        seed: int = 42,
        state_column: str = "assigned_state",
        line_column: str = "line_id"
    ) -> Dict[str, Any]:
        """
        Esegue le permutazioni Monte Carlo (N=10.000) sul doppio nullo (Corpus + Matrice).
        
        Args:
            df (pd.DataFrame): DataFrame contenente gli stati assegnati ed il vincolo di rigo.
            iterations (int): Numero di simulazioni Monte Carlo. Default = 10.000.
            seed (int): Seed pseudo-casuale per la riproducibilità. Default = 42.
            state_column (str): Nome della colonna contenente gli stati topologici.
            line_column (str): Nome della colonna dell'identificatore di rigo.

        Returns:
            Dict[str, Any]: Report quantitativo con media nulla, z-score e p-value empirico.
        """
        np.random.seed(seed)

        if state_column not in df.columns:
            raise ValueError(f"Colonna degli stati '{state_column}' non presente nel DataFrame.")

        states: np.ndarray = df[state_column].values
        lines: np.ndarray = df[line_column].values if line_column in df.columns else np.zeros(len(df))

        # Accesso diretto agli attributi della Matrice Canonica (Risoluzione P0.2)
        base_matrix: np.ndarray = self.matrix_mgr.admissibility_matrix
        state_map: Dict[str, int] = self.matrix_mgr.state_to_idx
        n_states: int = len(self.matrix_mgr.STATES)

        # Calcolo Coerenza Sintattica Osservata Reale (C_raw)
        c_raw_obs: float = self.matrix_mgr.compute_c_raw(df, state_column=state_column, line_column=line_column)

        double_null_scores: np.ndarray = np.zeros(iterations, dtype=np.float64)
        flattened_matrix: np.ndarray = base_matrix.flatten()

        for it in range(iterations):
            # 1. Randomizzazione della sequenza degli stati
            permuted_states: np.ndarray = np.random.permutation(states)

            # 2. Randomizzazione isomorfa della matrice (conservazione della densità di 12/16)
            permuted_matrix: np.ndarray = np.random.permutation(flattened_matrix).reshape((n_states, n_states))

            total_trans: int = 0
            admiss_trans: int = 0

            # Valutazione della coerenza sul sistema doppio nullo
            for i in range(len(permuted_states) - 1):
                if lines[i] == lines[i + 1]:
                    st_curr: str = permuted_states[i]
                    st_next: str = permuted_states[i + 1]

                    if st_curr in state_map and st_next in state_map:
                        r: int = state_map[st_curr]
                        c: int = state_map[st_next]
                        total_trans += 1
                        if permuted_matrix[r, c] == 1:
                            admiss_trans += 1

            double_null_scores[it] = (admiss_trans / total_trans) if total_trans > 0 else 0.0

        mean_null: float = float(np.mean(double_null_scores))
        std_null: float = float(np.std(double_null_scores, ddof=1))

        z_score: float = float((c_raw_obs - mean_null) / std_null) if std_null > 0 else 0.0
        
        # Calcolo del p-value empirico Monte Carlo (Davison-Hinkley)
        count_exceeding: int = int(np.sum(double_null_scores >= c_raw_obs))
        p_value_empirical: float = float((count_exceeding + 1) / (iterations + 1))

        return {
            "release": "v3.3 (Audit-Master-Validato)",
            "c_raw_observed": c_raw_obs,
            "double_null_mean": mean_null,
            "double_null_std": std_null,
            "z_score": z_score,
            "p_value_empirical": p_value_empirical,
            "count_exceeding": count_exceeding,
            "iterations": iterations
        }


if __name__ == "__main__":
    mm = MatrixManager()
    auditor = DoubleRandomizationAuditor(mm)
    print("=== MODULO audit_doublerand5.py (Release v3.3 Audit-Master-Validato) PRONTO PER APPROVAZIONE ===")