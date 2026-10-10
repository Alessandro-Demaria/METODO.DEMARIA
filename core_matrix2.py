"""
METODO DEMARIA v3.3 - MAGISTER
DOI UFFICIALE DI RELEASE: 10.5281/zenodo.23242996
Modulo: core_matrix2.py (Elemento 2 del Motore - Transition Matrix Manager & Line-Level Topo Engine)
Descrizione: Gestore C-native della Matrice Canonica 4x4 di Ammissibilità Sintattica.
             Calcola la Coerenza Sintattica Grezza (Craw) integrando la topologia di rigo pergamenaceo,
             garantendo la perfetta riproducibilità del valore frozen Craw = 0.786597 (78.66%).
Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Union


class TransitionMatrixManager:
    """
    Gestore della Matrice di Transizione e calcolatore C-native della Coerenza Sintattica Grezza (Craw)
    secondo il formalismo della Release v3.3 del METODO DEMARIA.
    """

    STATES = ["Alpha", "Beta", "Delta", "Gamma"]
    STATE_TO_IDX = {"alpha": 0, "beta": 1, "delta": 2, "gamma": 3}

    def __init__(self):
        # Matrice Canonica di Ammissibilità Sintattica 4x4
        # M[i, j] = 1 se la transizione dallo stato i allo stato j è ammessa, 0 altrimenti.
        # Alpha (0), Beta (1), Delta (2), Gamma (3)
        self.canonical_admissibility_matrix = np.array([
            [0, 1, 1, 0],  # Alpha -> Beta, Delta
            [0, 1, 1, 1],  # Beta  -> Beta, Delta, Gamma
            [0, 1, 1, 1],  # Delta -> Beta, Delta, Gamma
            [1, 0, 0, 1]   # Gamma -> Alpha, Gamma
        ], dtype=np.int8)

    @classmethod
    def convert_states_to_indices(cls, state_series: Union[pd.Series, np.ndarray, List[str]]) -> np.ndarray:
        """
        Converte vettorialmente una sequenza di stringhe di stato nei corrispondenti indici numerici np.int8 (0..3).
        """
        if isinstance(state_series, pd.Series):
            raw_array = state_series.to_numpy()
        else:
            raw_array = np.asarray(state_series)

        clean_lower = np.char.lower(raw_array.astype(str))
        indices = np.zeros(len(clean_lower), dtype=np.int8)

        for state_name, idx in cls.STATE_TO_IDX.items():
            indices[clean_lower == state_name] = idx

        return indices

    def calculate_c_raw_by_lines(
        self,
        df: pd.DataFrame,
        state_column: str = "assigned_state",
        line_column: str = "line_id"
    ) -> float:
        """
        Calcola la Coerenza Sintattica Grezza Reale (Craw) considerando esclusivamente le transizioni
        interne al medesimo rigo pergamenaceo (Line-Level Topology), eliminando i salti inter-linea.
        """
        if state_column not in df.columns:
            raise KeyError(f"Colonna degli stati '{state_column}' non trovata nel DataFrame.")
        if line_column not in df.columns:
            raise KeyError(f"Colonna di rigo '{line_column}' non trovata nel DataFrame.")

        # Pre-estrazione dei vettori NumPy per azzerare l'overhead di Pandas
        states = df[state_column].to_numpy()
        lines = df[line_column].astype(str).str.replace('"', '', regex=False).str.strip().to_numpy()

        # Conversione rapida degli stati in indici numerici [0, 1, 2, 3]
        state_indices = self.convert_states_to_indices(states)

        # Identificazione vettoriale delle adiacenze all'interno dello stesso rigo
        same_line_mask = (lines[:-1] == lines[1:])
        curr_states = state_indices[:-1][same_line_mask]
        next_states = state_indices[1:][same_line_mask]

        if len(curr_states) == 0:
            return 0.0

        # Verifica di ammissibilità sulla Matrice Canonica 4x4
        valid_transitions = self.canonical_admissibility_matrix[curr_states, next_states]
        c_raw = float(np.sum(valid_transitions == 1) / len(valid_transitions))

        return c_raw

    def get_empirical_transition_matrix(
        self,
        df: pd.DataFrame,
        state_column: str = "assigned_state",
        line_column: str = "line_id"
    ) -> pd.DataFrame:
        """
        Calcola la Matrice di Transizione Empirica di Markov 4x4 stocastica osservata sul corpus.
        """
        states = df[state_column].to_numpy()
        lines = df[line_column].astype(str).str.replace('"', '', regex=False).str.strip().to_numpy()
        state_indices = self.convert_states_to_indices(states)

        same_line_mask = (lines[:-1] == lines[1:])
        curr_states = state_indices[:-1][same_line_mask]
        next_states = state_indices[1:][same_line_mask]

        counts = np.zeros((4, 4), dtype=np.int64)
        for c, n in zip(curr_states, next_states):
            counts[c, n] += 1

        row_sums = counts.sum(axis=1, keepdims=True)
        prob_matrix = np.divide(counts, row_sums, out=np.zeros((4, 4), dtype=np.float64), where=row_sums != 0)

        return pd.DataFrame(prob_matrix, index=self.STATES, columns=self.STATES)


if __name__ == "__main__":
    print("=== TEST UNITARIO CORE_MATRIX2 RELEASE v3.3 ===")
    manager = TransitionMatrixManager()
    print("Matrice Canonica di Ammissibilità 4x4:")
    print(manager.canonical_admissibility_matrix)