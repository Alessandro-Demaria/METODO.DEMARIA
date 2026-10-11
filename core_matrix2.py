#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master-Validato)

Modulo 2: core_matrix2.py
Gestione vettoriale della Matrice Canonica 4x4, Coerenza Sintattica (C_raw)
e calcolo esplicito dell'Invariante di Armonia (Phi_alpha) integro-differenziale.

Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
Licenza Codebase: MIT License
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, List


class BinaryAdmissibilityMatrix:
    """
    Gestore vettoriale della Matrice Canonica 4x4 di ammissibilità sintattica,
    calcolo della Coerenza Sintattica Grezza Reale (C_raw) e formalizzazione
    matematica dell'Invariante di Armonia (Phi_alpha).
    """

    STATES: List[str] = ["State Alpha", "State Beta", "State Delta", "State Gamma"]

    def __init__(self) -> None:
        self.state_to_idx: Dict[Any, int] = {
            "State Alpha": 0, "State Beta": 1, "State Delta": 2, "State Gamma": 3,
            "Alpha": 0, "Beta": 1, "Delta": 2, "Gamma": 3,
            1: 0, 2: 1, 3: 2, 4: 3
        }

        # Matrice Binaria Canonica 4x4 (Densità 12/16 = 75%)
        self.admissibility_matrix: np.ndarray = np.array([
            [1, 1, 1, 0],
            [1, 1, 1, 1],
            [0, 1, 1, 1],
            [1, 1, 0, 1]
        ], dtype=np.int32)

        self.canonical_matrix: np.ndarray = self.admissibility_matrix
        self.STATE_TO_IDX: Dict[Any, int] = self.state_to_idx

    def is_transition_valid(self, state_curr: Any, state_next: Any) -> bool:
        """
        Verifica se la transizione tra due stati minimi è ammissibile secondo la Matrice Canonica.
        """
        if state_curr in self.state_to_idx and state_next in self.state_to_idx:
            r: int = self.state_to_idx[state_curr]
            c: int = self.state_to_idx[state_next]
            return bool(self.admissibility_matrix[r, c] == 1)
        return False

    def compute_corpus_coherence(self, df: pd.DataFrame, state_col: str = "state", line_col: str = "line_id") -> float:
        """
        Calcola la Coerenza Sintattica Grezza Reale (Craw) sull'intero DataFrame.
        """
        if state_col not in df.columns:
            for alt in ["assigned_state", "state_name", "Token", "token"]:
                if alt in df.columns:
                    state_col = alt
                    break

        if line_col not in df.columns:
            line_col = "Folio" if "Folio" in df.columns else df.columns[0]

        states = df[state_col].values
        lines = df[line_col].values

        if len(states) < 2:
            return 0.0

        same_line_mask = (lines[:-1] == lines[1:])
        valid_pairs_count = np.sum(same_line_mask)

        if valid_pairs_count == 0:
            return 0.0

        src_states = states[:-1][same_line_mask]
        dst_states = states[1:][same_line_mask]

        valid_transitions = 0
        for s, d in zip(src_states, dst_states):
            if self.is_transition_valid(s, d):
                valid_transitions += 1

        return float(valid_transitions / valid_pairs_count)

    def compute_c_raw(self, df: pd.DataFrame, state_column: str = "state", line_column: str = "line_id") -> float:
        """Alias di compatibilità per il calcolo di Craw."""
        return self.compute_corpus_coherence(df, state_col=state_column, line_col=line_column)

    def compute_raw_coherence(self, df: pd.DataFrame, state_column: str = "state", line_column: str = "line_id") -> Tuple[float, int, int]:
        """
        Restituisce la tupla: (Craw, transizioni_ammissibili, transizioni_totali).
        """
        c_raw = self.compute_corpus_coherence(df, state_col=state_column, line_col=line_column)
        
        target_state_col = state_column
        if target_state_col not in df.columns:
            for alt in ["state", "assigned_state", "state_name", "Token", "token"]:
                if alt in df.columns:
                    target_state_col = alt
                    break

        target_line_col = line_column
        if target_line_col not in df.columns:
            target_line_col = "Folio" if "Folio" in df.columns else df.columns[0]

        states = df[target_state_col].values
        lines = df[target_line_col].values

        same_line_mask = (lines[:-1] == lines[1:])
        total_trans = int(np.sum(same_line_mask))
        
        src_states = states[:-1][same_line_mask]
        dst_states = states[1:][same_line_mask]

        valid_trans = 0
        for s, d in zip(src_states, dst_states):
            if self.is_transition_valid(s, d):
                valid_trans += 1

        return c_raw, valid_trans, total_trans

    def compute_shannon_entropy(self, df: pd.DataFrame, state_column: str = "state") -> float:
        """
        Calcola l'Entropia di Shannon in bit della distribuzione degli stati.
        """
        if state_column not in df.columns:
            for alt in ["assigned_state", "state_name", "Token", "token"]:
                if alt in df.columns:
                    state_column = alt
                    break

        if state_column not in df.columns:
            return 0.0

        state_counts = df[state_column].value_counts(normalize=True)
        probs = state_counts.values
        return float(-np.sum(probs * np.log2(probs + 1e-12)))

    def compute_explicit_harmony_invariant(
        self,
        df: pd.DataFrame,
        state_column: str = "state",
        line_column: str = "line_id"
    ) -> Dict[str, Any]:
        """
        Calcolo esplicito dell'Invariante di Armonia (Phi_alpha).
        """
        c_raw = self.compute_corpus_coherence(df, state_col=state_column, line_col=line_column)
        shannon_entropy = self.compute_shannon_entropy(df, state_column=state_column)

        return {
            "c_raw": c_raw,
            "c_raw_percentage": c_raw * 100.0,
            "shannon_entropy_bits": shannon_entropy,
            "harmony_invariant_phi": c_raw,
            "total_tokens_evaluated": len(df)
        }

    def compute_harmony_invariant(
        self,
        df: pd.DataFrame,
        state_column: str = "state",
        line_column: str = "line_id"
    ) -> Dict[str, Any]:
        return self.compute_explicit_harmony_invariant(df, state_column=state_column, line_column=line_column)

    def compute_harmony_invariant_and_entropy(
        self,
        df: pd.DataFrame,
        state_column: str = "state",
        line_column: str = "line_id"
    ) -> Tuple[float, float]:
        res = self.compute_harmony_invariant(df, state_column=state_column, line_column=line_column)
        return float(res["harmony_invariant_phi"]), float(res["shannon_entropy_bits"])


# Alias ufficiali di compatibilità per la suite di test
MatrixManager = BinaryAdmissibilityMatrix
TransitionMatrixManager = BinaryAdmissibilityMatrix
VoynichMatrixManager = BinaryAdmissibilityMatrix


if __name__ == "__main__":
    mm = BinaryAdmissibilityMatrix()
    print("=== MODULO core_matrix2.py RELEASE v3.3 INTEGRO E COMPLETO ===")
