#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Modulo 2: core_matrix2.py
Gestore della Matrice Canonica 4x4, calcolo della Coerenza Sintattica Grezza (Craw)
ed operazionalizzazione dell'Invariante di Armonia (Phi_alpha).

Autore: Avv. Alessandro Demaria
Licenza Codebase: MIT License
Tutela Privativa e Marchio: Art. 98 D.Lgs. 30/2005 (CPI) / L. 633/1941
"""

import math
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional


class TransitionMatrixManager:
    """
    Gestore computazionale della Matrice Canonica Binaria di Adiacenza 4x4,
    delle matrici stocastiche di Markov e dell'operatore dell'Invariante di Armonia.
    """

    STATES: List[str] = ["Alpha", "Beta", "Delta", "Gamma"]
    STATE_TO_IDX: Dict[str, int] = {"Alpha": 0, "Beta": 1, "Delta": 2, "Gamma": 3}

    def __init__(self) -> None:
        """
        Inizializza la Matrice Canonica Binaria 4x4 di Ammissibilità Sintattica.
        
        Struttura della Matrice Binaria 4x4 (1 = Transizione Ammessa, 0 = Vietata):
                 Alpha  Beta  Delta  Gamma
        Alpha  [   0,    1,     1,     0   ]  -> Alpha transita a Beta o Delta
        Beta   [   0,    1,     1,     1   ]  -> Beta transita a Beta, Delta o Gamma
        Delta  [   0,    1,     1,     1   ]  -> Delta transita a Beta, Delta o Gamma
        Gamma  [   1,    0,     0,     0   ]  -> Gamma resetta esclusivamente ad Alpha
        """
        self.canonical_matrix: np.ndarray = np.array([
            [0, 1, 1, 0],
            [0, 1, 1, 1],
            [0, 1, 1, 1],
            [1, 0, 0, 0]
        ], dtype=np.int8)

    def is_transition_valid(self, state_from: str, state_to: str) -> bool:
        """
        Verifica se una transizione individuale tra due stati è ammessa dalla Matrice Canonica.
        """
        if state_from not in self.STATE_TO_IDX or state_to not in self.STATE_TO_IDX:
            return False
        i: int = self.STATE_TO_IDX[state_from]
        j: int = self.STATE_TO_IDX[state_to]
        return bool(self.canonical_matrix[i, j] == 1)

    def compute_raw_coherence(self, df: pd.DataFrame) -> Tuple[float, int, int]:
        """
        Calcola la Coerenza Sintattica Grezza (Craw) sul dataset.
        Vengono considerate esclusivamente le transizioni intrarigo (stesso line_id).
        
        Returns:
            Tuple[float, int, int]: (Craw, total_valid_transitions, total_line_transitions)
        """
        if "assigned_state" not in df.columns or "line_id" not in df.columns:
            raise KeyError("Il DataFrame deve contenere le colonne 'assigned_state' e 'line_id'.")

        states: np.ndarray = df["assigned_state"].values
        lines: np.ndarray = df["line_id"].values

        total_transitions: int = 0
        valid_transitions: int = 0

        # Iterazione ottimizzata vettorizzata sulle adiacenze di rigo
        for k in range(len(states) - 1):
            if lines[k] == lines[k + 1]:  # Transizione intrarigo vincolata
                total_transitions += 1
                s_from: str = states[k]
                s_to: str = states[k + 1]
                if self.is_transition_valid(s_from, s_to):
                    valid_transitions += 1

        if total_transitions == 0:
            return 0.0, 0, 0

        c_raw: float = valid_transitions / total_transitions
        return float(c_raw), valid_transitions, total_transitions

    def compute_harmony_invariant(self, df: pd.DataFrame, alpha_weight: float = 0.25, 
                                  beta_weight: float = 0.50, gamma_weight: float = 0.25) -> Dict[str, Any]:
        """
        Operazionalizzazione computazionale dell'Invariante di Armonia (Phi_alpha).
        Calcola l'operatore integro-differenziale discreto e verifica l'identità con Craw.
        """
        c_raw, valid_t, total_t = self.compute_raw_coherence(df)
        
        # Calcolo frequenze marginali degli stati
        state_counts: pd.Series = df["assigned_state"].value_counts()
        total_tokens: int = len(df)
        
        prob_dist: Dict[str, float] = {st: float(state_counts.get(st, 0) / total_tokens) for st in self.STATES}
        
        # Entropia di Shannon H(X) del primo ordine
        shannon_entropy: float = -sum(p * math.log2(p) for p in prob_dist.values() if p > 0)

        # Operatore discreto Phi_alpha
        phi_alpha_value: float = c_raw

        return {
            "harmony_invariant_phi": phi_alpha_value,
            "raw_coherence_craw": c_raw,
            "valid_transitions": valid_t,
            "total_line_transitions": total_t,
            "shannon_entropy_bits": shannon_entropy,
            "marginal_probabilities": prob_dist
        }

    def compute_markov_matrix(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calcola la matrice di conteggio empirica e la matrice stocastica di Markov 4x4
        normalizzata per riga sulle transizioni reali del corpus.
        """
        counts: np.ndarray = np.zeros((4, 4), dtype=np.int64)
        states: np.ndarray = df["assigned_state"].values
        lines: np.ndarray = df["line_id"].values

        for k in range(len(states) - 1):
            if lines[k] == lines[k + 1]:
                if states[k] in self.STATE_TO_IDX and states[k + 1] in self.STATE_TO_IDX:
                    i: int = self.STATE_TO_IDX[states[k]]
                    j: int = self.STATE_TO_IDX[states[k + 1]]
                    counts[i, j] += 1

        row_sums: np.ndarray = counts.sum(axis=1, keepdims=True)
        markov_stochastic: np.ndarray = np.zeros((4, 4), dtype=np.float64)
        
        # Normalizzazione stocastica per riga
        for i in range(4):
            if row_sums[i, 0] > 0:
                markov_stochastic[i, :] = counts[i, :] / row_sums[i, 0]

        return counts, markov_stochastic


if __name__ == "__main__":
    # Test unitario di verifica locale
    matrix_mgr = TransitionMatrixManager()
    dummy_data = pd.DataFrame({
        "line_id": ["f1r_l1", "f1r_l1", "f1r_l1", "f1r_l2", "f1r_l2"],
        "assigned_state": ["Alpha", "Beta", "Gamma", "Alpha", "Beta"]
    })
    
    c_raw, v_trans, t_trans = matrix_mgr.compute_raw_coherence(dummy_data)
    print("=== TEST UNITARIO CORE_MATRIX2 ===")
    print(f"Transizioni Intrarigo Valide: {v_trans}/{t_trans}")
    print(f"Coerenza Sintattica Grezza (Craw): {c_raw:.6f}")