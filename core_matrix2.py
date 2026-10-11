#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master-Validato)

Modulo 2: core_matrix2.py
Gestione vettoriale della Matrice Canonica 4x4, Coerenza Sintattica (C_raw)
e calcolo esplicito dell'Invariante di Armonia (Phi_alpha) integro-differenziale.

Sessione di Lavoro: BARVI
Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
Licenza Codebase: MIT License
Tutela Privativa e Marchio: Art. 98 D.Lgs. 30/2005 (CPI) / L. 633/1941
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, List


class MatrixManager:
    """
    Gestore vettoriale della Matrice Canonica 4x4 di ammissibilità sintattica,
    calcolo della Coerenza Sintattica Grezza Reale (C_raw) e formalizzazione
    matematica dell'Invariante di Armonia (Phi_alpha).
    """

    STATES: List[str] = ["Alpha", "Beta", "Delta", "Gamma"]

    def __init__(self) -> None:
        self.state_to_idx: Dict[str, int] = {state: i for i, state in enumerate(self.STATES)}
        self.idx_to_state: Dict[int, str] = {i: state for i, state in enumerate(self.STATES)}

        # Matrice Binaria Canonica 4x4 (Densità 12/16 = 75%)
        self.admissibility_matrix: np.ndarray = np.array([
            [1, 1, 1, 0],
            [1, 1, 1, 1],
            [0, 1, 1, 1],
            [1, 1, 0, 1]
        ], dtype=np.int32)

        self.canonical_matrix: np.ndarray = self.admissibility_matrix
        self.STATE_TO_IDX: Dict[str, int] = self.state_to_idx

    def is_transition_valid(self, state_curr: str, state_next: str) -> bool:
        if state_curr in self.state_to_idx and state_next in self.state_to_idx:
            r: int = self.state_to_idx[state_curr]
            c: int = self.state_to_idx[state_next]
            return bool(self.admissibility_matrix[r, c] == 1)
        return False

    def compute_c_raw(
        self,
        df: pd.DataFrame,
        state_column: str = "assigned_state",
        line_column: str = "line_id"
    ) -> float:
        if state_column not in df.columns:
            raise ValueError(f"Colonna degli stati '{state_column}' non presente nel DataFrame.")

        states: np.ndarray = df[state_column].values
        lines: np.ndarray = df[line_column].values if line_column in df.columns else np.zeros(len(df))

        total_trans: int = 0
        admiss_trans: int = 0

        for i in range(len(states) - 1):
            if lines[i] == lines[i + 1]:
                st_curr: str = states[i]
                st_next: str = states[i + 1]

                if st_curr in self.state_to_idx and st_next in self.state_to_idx:
                    r: int = self.state_to_idx[st_curr]
                    c: int = self.state_to_idx[st_next]
                    total_trans += 1
                    if self.admissibility_matrix[r, c] == 1:
                        admiss_trans += 1

        return float(admiss_trans / total_trans) if total_trans > 0 else 0.0

    def compute_raw_coherence(
        self,
        df: pd.DataFrame,
        state_column: str = "assigned_state",
        line_column: str = "line_id"
    ) -> Tuple[float, int, int]:
        c_raw: float = self.compute_c_raw(df, state_column=state_column, line_column=line_column)
        states: np.ndarray = df[state_column].values
        lines: np.ndarray = df[line_column].values if line_column in df.columns else np.zeros(len(df))
        
        total_trans: int = 0
        admiss_trans: int = 0
        for i in range(len(states) - 1):
            if lines[i] == lines[i + 1]:
                total_trans += 1
                if self.is_transition_valid(states[i], states[i + 1]):
                    admiss_trans += 1

        return c_raw, admiss_trans, total_trans

    def compute_shannon_entropy(self, df: pd.DataFrame, state_column: str = "assigned_state") -> float:
        if state_column not in df.columns or len(df) == 0:
            return 0.0

        state_counts: pd.Series = df[state_column].value_counts(normalize=True)
        probs: np.ndarray = state_counts.values
        entropy_bits: float = -float(np.sum(probs * np.log2(probs + 1e-12)))
        return float(entropy_bits)

    def compute_explicit_harmony_invariant(
        self,
        df: pd.DataFrame,
        state_column: str = "assigned_state",
        line_column: str = "line_id",
        alpha: float = 0.4,
        beta: float = 0.4,
        gamma: float = 0.2
    ) -> Dict[str, Any]:
        """
        PUNTO 2.1: Implementazione esplicita dell'Invariante di Armonia (Phi_alpha)
        integro-differenziale calcolato lungo la sequenza degli N operatori.
        """
        c_raw: float = self.compute_c_raw(df, state_column=state_column, line_column=line_column)
        shannon_entropy: float = self.compute_shannon_entropy(df, state_column=state_column)

        # Calcolo dei contributi dinamici se le colonne di carico Z_t e Clock_Phase sono presenti
        if "Z_t" in df.columns and "Clock_Phase" in df.columns:
            z_vals: np.ndarray = df["Z_t"].values.astype(float)
            clock_vals: np.ndarray = df["Clock_Phase"].values.astype(float)

            delta_z: np.ndarray = np.diff(z_vals, prepend=z_vals[0])
            delta_t: np.ndarray = np.diff(clock_vals, prepend=clock_vals[0])
            delta_t[delta_t <= 0] = 1e-4  # Prevenzione divisione per zero

            # Tassonomia del tempo di stasi nello State Beta
            is_beta: np.ndarray = (df[state_column].values == "Beta").astype(float)
            
            # Integrazione vettoriale dell'invariante
            term_kinetic: np.ndarray = alpha * np.abs(delta_z / delta_t)
            term_entropic: float = beta * shannon_entropy
            term_hold: np.ndarray = gamma * is_beta

            phi_integrand: np.ndarray = term_kinetic + term_entropic + term_hold
            phi_computed: float = float(np.mean(phi_integrand) * c_raw)
        else:
            phi_computed = c_raw

        return {
            "c_raw": c_raw,
            "c_raw_percentage": c_raw * 100.0,
            "shannon_entropy_bits": shannon_entropy,
            "harmony_invariant_phi": phi_computed,
            "total_tokens_evaluated": len(df)
        }

    def compute_harmony_invariant(
        self,
        df: pd.DataFrame,
        state_column: str = "assigned_state",
        line_column: str = "line_id"
    ) -> Dict[str, Any]:
        return self.compute_explicit_harmony_invariant(df, state_column=state_column, line_column=line_column)

    def compute_harmony_invariant_and_entropy(
        self,
        df: pd.DataFrame,
        state_column: str = "assigned_state",
        line_column: str = "line_id"
    ) -> Tuple[float, float]:
        res: Dict[str, Any] = self.compute_harmony_invariant(df, state_column=state_column, line_column=line_column)
        return float(res["harmony_invariant_phi"]), float(res["shannon_entropy_bits"])


TransitionMatrixManager = MatrixManager
VoynichMatrixManager = MatrixManager


if __name__ == "__main__":
    mm = MatrixManager()
    print("=== MODULO core_matrix2.py (PUNTO 2.1 - Invariante di Armonia) PRONTO PER APPROVAZIONE ===")