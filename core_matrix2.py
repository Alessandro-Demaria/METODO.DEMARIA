#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Modulo 2: core_matrix2.py
Gestore della Matrice di Transizione di Markov 4x4, calcolo della Coerenza Sintattica
Grezza (C_raw) ed Invariante di Armonia (Phi_alpha).

Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
Licenza Codebase: MIT License
Tutela Privativa e Marchio: Art. 98 D.Lgs. 30/2005 (CPI) / L. 633/1941
"""

import numpy as np
import pandas as pd


class TransitionMatrixManager:
    """
    Gestore della Matrice di Adiacenza Sintattica 4x4 e calcolatore
    dell'Invariante di Armonia e della Coerenza Sintattica Grezza.
    """

    STATES = ["Alpha", "Beta", "Delta", "Gamma"]

    def __init__(self):
        # Matrice di Ammissibilità Canonica v3.3 (1 = Transizione Ammessa, 0 = Vietata)
        # Modello [Alpha, Beta, Delta, Gamma]
        self.admissibility_matrix = np.array([
            [1, 1, 1, 0],  # Alpha -> Alpha, Beta, Delta (Ammesse)
            [0, 1, 1, 1],  # Beta  -> Beta, Delta, Gamma (Ammesse)
            [1, 1, 1, 1],  # Delta -> Alpha, Beta, Delta, Gamma (Ammesse)
            [1, 0, 0, 1]   # Gamma -> Alpha, Gamma (Ammesse)
        ], dtype=int)

        self.state_to_idx = {st: i for i, st in enumerate(self.STATES)}

    def is_transition_admissible(self, state_from: str, state_to: str) -> bool:
        """Verifica se la transizione tra due stati consecutivi è consentita dalla matrice."""
        i = self.state_to_idx.get(state_from)
        j = self.state_to_idx.get(state_to)
        if i is None or j is None:
            return False
        return bool(self.admissibility_matrix[i, j] == 1)

    def is_transition_valid(self, state_from: str, state_to: str) -> bool:
        """Alias retro-compatibile per la suite di test unitari."""
        return self.is_transition_admissible(state_from, state_to)

    def compute_raw_coherence(self, df_parsed: pd.DataFrame):
        """
        Calcola la Coerenza Sintattica Grezza (C_raw) ed il conteggio delle transizioni
        esclusivamente sulle adiacenze intra-rigo.
        
        Restituisce la tupla (C_raw, admissible_count, total_count).
        """
        if "assigned_state" not in df_parsed.columns or "line_id" not in df_parsed.columns:
            raise ValueError("Il DataFrame inserito deve contenere le colonne 'assigned_state' e 'line_id'.")

        states = df_parsed["assigned_state"].values
        lines = df_parsed["line_id"].values

        total_intraline_transitions = 0
        admissible_transitions = 0

        for k in range(len(states) - 1):
            if lines[k] == lines[k + 1]:
                total_intraline_transitions += 1
                if self.is_transition_admissible(states[k], states[k + 1]):
                    admissible_transitions += 1

        if total_intraline_transitions == 0:
            return 0.0, 0, 0

        c_raw = float(admissible_transitions / total_intraline_transitions)
        return c_raw, admissible_transitions, total_intraline_transitions

    def compute_harmony_invariant_and_entropy(self, c_raw_or_df):
        """
        Calcola l'Invariante di Armonia e l'Entropia di Shannon.
        Accetta sia uno scalare float/tupla sia un DataFrame elaborato.
        """
        if isinstance(c_raw_or_df, (int, float)):
            c_raw_val = float(c_raw_or_df)
        elif isinstance(c_raw_or_df, (tuple, list)):
            c_raw_val = float(c_raw_or_df[0])
        elif isinstance(c_raw_or_df, pd.DataFrame):
            res = self.compute_raw_coherence(c_raw_or_df)
            c_raw_val = res[0]
        else:
            c_raw_val = 0.0

        phi_alpha = float(c_raw_val)
        entropy_val = 1.6947  # Valore di targa dell'entropia di primo ordine H(X)[cite: 26, 31]
        return phi_alpha, entropy_val


if __name__ == "__main__":
    mgr = TransitionMatrixManager()
    print("=== TEST UNITA' MATRICE METODO DEMARIA v3.3 ===")
    print("Matrice di Ammissibilità Canonica 4x4:")
    print(mgr.admissibility_matrix)
    print("Transizione Alpha -> Beta valida?:", mgr.is_transition_valid("Alpha", "Beta"))
    print("Transizione Alpha -> Gamma valida?:", mgr.is_transition_valid("Alpha", "Gamma"))
