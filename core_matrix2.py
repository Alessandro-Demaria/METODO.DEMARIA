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
        # Righe: Stato Corrente (from) | Colonne: Stato Successivo (to)
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

    def compute_raw_coherence(self, df_parsed: pd.DataFrame) -> float:
        """
        Calcola la Coerenza Sintattica Grezza (C_raw) esclusivamente sulle
        transizioni intra-rigo (senza scavalcare i limiti del rigo pergamenaceo).
        
        Restituisce un valore scalare float rigorosamente convalidato.
        """
        if "assigned_state" not in df_parsed.columns or "line_id" not in df_parsed.columns:
            raise ValueError("Il DataFrame inserito non contiene 'assigned_state' o 'line_id'.")

        states = df_parsed["assigned_state"].values
        lines = df_parsed["line_id"].values

        total_intraline_transitions = 0
        admissible_transitions = 0

        # Scorrimento vettoriale sequenziale ristretto alle adiacenze di rigo
        for k in range(len(states) - 1):
            if lines[k] == lines[k + 1]:
                total_intraline_transitions += 1
                if self.is_transition_admissible(states[k], states[k + 1]):
                    admissible_transitions += 1

        if total_intraline_transitions == 0:
            return 0.0

        c_raw = float(admissible_transitions / total_intraline_transitions)
        return c_raw

    def compute_harmony_invariant(self, c_raw: float, entropy_val: float = 1.6947) -> float:
        """
        Formalizzazione operativa dell'Invariante di Armonia Phi_alpha.
        Nello stato stazionario di targa, Phi_alpha coincide esattamente con C_raw.
        """
        # Sotto vincolo stazionario: Phi_alpha = C_raw
        phi_alpha = float(c_raw)
        return phi_alpha


if __name__ == "__main__":
    mgr = TransitionMatrixManager()
    print("Matrice di Ammissibilità Canonica v3.3:")
    print(mgr.admissibility_matrix)
    print("Transizione Alpha -> Beta ammessa?:", mgr.is_transition_admissible("Alpha", "Beta"))
    print("Transizione Alpha -> Gamma ammessa?:", mgr.is_transition_admissible("Alpha", "Gamma"))
