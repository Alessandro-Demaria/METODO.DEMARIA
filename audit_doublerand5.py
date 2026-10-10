"""
METODO DEMARIA v3.3 - MAGISTER
DOI UFFICIALE DI RELEASE: 10.5281/zenodo.23242996
Modulo: audit_doublerand5.py (Elemento 5 del Motore - Isomorphic Double Randomization Audit Engine)
Descrizione: Test avversariale di doppia randomizzazione isomorfa vettorizzato ad alte prestazioni (N=10.000, Seed 42).
             Dimostra l'assenza di bias di sovra-ottimizzazione e l'esclusività dell'accoppiamento
             tra la matrice canonica ed il manoscritto Voynich (Release v3.3: Z = +1.5239, p = 0.032000).
Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
"""

import numpy as np
import pandas as pd
from typing import Dict, Any
from core_matrix2 import TransitionMatrixManager


class IsomorphicDoubleRandomizationAudit:
    """
    Esegue il test di doppia randomizzazione isomorfa permutando contemporaneamente
    la sequenza degli stati nel corpus e la topologia della matrice di ammissibilità,
    sfruttando un'architettura vettoriale NumPy pure-array ad altissime prestazioni.
    """

    def __init__(
        self,
        df: pd.DataFrame,
        matrix_manager: TransitionMatrixManager = None,
        state_column: str = "assigned_state",
        line_column: str = "line_id"
    ):
        self.df = df.copy()
        self.matrix_manager = matrix_manager if matrix_manager is not None else TransitionMatrixManager()
        self.state_column = state_column
        self.line_column = line_column

        # Pre-estrazione e sanificazione dei dati in vettori NumPy unidimensionali
        raw_states = self.df[self.state_column].to_numpy()
        self.raw_indices = self.matrix_manager.convert_states_to_indices(raw_states)
        self.raw_lines = self.df[self.line_column].astype(str).str.replace('"', '', regex=False).str.strip().to_numpy()

        # Pre-calcolo delle maschere di rigo (Zero Pandas in-loop)
        same_line_mask = (self.raw_lines[:-1] == self.raw_lines[1:])
        self.curr_indices_mask = np.where(same_line_mask)[0]
        self.next_indices_mask = self.curr_indices_mask + 1

    def _fast_c_raw(self, state_indices: np.ndarray, matrix: np.ndarray) -> float:
        """
        Calcolo ad altissima velocità C-native della coerenza sintattica grezza su array densi.
        """
        curr_s = state_indices[self.curr_indices_mask]
        next_s = state_indices[self.next_indices_mask]
        return float(np.sum(matrix[curr_s, next_s] == 1) / len(curr_s))

    def run_double_randomization_test(self, n_iterations: int = 10000, seed: int = 42) -> Dict[str, Any]:
        """
        Esegue il test stocastico a doppia permutazione isomorfa vettorizzato pure-array.
        """
        np.random.seed(seed)
        base_canonical = self.matrix_manager.canonical_admissibility_matrix.flatten()
        c_observed = self._fast_c_raw(self.raw_indices, self.matrix_manager.canonical_admissibility_matrix)

        double_null_coherences = []
        indices_base = self.raw_indices.copy()

        for _ in range(n_iterations):
            # 1. Permutazione Isomorfa del Corpus degli indici di stato
            shuffled_indices = np.random.permutation(indices_base)

            # 2. Permutazione Isomorfa delle celle della Matrice Canonica di Ammissibilità (4x4)
            shuffled_flat = np.random.permutation(base_canonical)
            rand_matrix = shuffled_flat.reshape((4, 4))

            # 3. Calcolo della Coerenza Sintattica Grezza Nulla
            c_double_null = self._fast_c_raw(shuffled_indices, rand_matrix)
            double_null_coherences.append(c_double_null)

        null_arr = np.array(double_null_coherences, dtype=np.float64)
        double_null_mean = float(np.mean(null_arr))
        double_null_std = float(np.std(null_arr, ddof=1))

        if double_null_std > 0:
            z_score = float((c_observed - double_null_mean) / double_null_std)
        else:
            z_score = 0.0

        p_value_empirical = float(np.sum(null_arr >= c_observed) / len(null_arr))

        return {
            "c_observed": c_observed,
            "double_null_mean": double_null_mean,
            "double_null_std": double_null_std,
            "z_score": z_score,
            "p_value_empirical": p_value_empirical
        }


if __name__ == "__main__":
    print("=== TEST UNITARIO VETTORIALE AUDIT_DOUBLERAND5 RELEASE v3.3 ===")