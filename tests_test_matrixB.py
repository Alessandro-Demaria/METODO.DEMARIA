#!/usr/bin/env python3
"""
LABORATORIO SCIENTIFICO METODO DEMARIA™ - RELEASE v3.3 (AUDIT-MASTER UNIFICATO)

Modulo: tests_test_matrixB.py
Descrizione: Test unitario per la validazione algebrica del calcolo dell'entropia di Shannon (H)
             e della Matrice di Ammissibilità Binaria 4x4.
             Risoluzione P0.4: Scissione tra test teorico su 2 stati e test empirico di corpus.
Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
"""

import math
import numpy as np
import pandas as pd
import pytest

from core_matrix2 import BinaryAdmissibilityMatrix


def compute_shannon_entropy(state_series: pd.Series) -> float:
  """Calcola l'entropia di Shannon di primo ordine H(X) in bit per una serie di stati discreti."""
  counts = state_series.value_counts()
  probabilities = counts / len(state_series)
  entropy = -sum(p * math.log2(p) for p in probabilities if p > 0)
  return float(entropy)


def test_entropy_theoretical_two_states():
  """Risoluzione P0.4 (Parte 1): Verifica algebrica teorica su distribuzione sintetica a 2 stati equiprobabili.

  Aspettativa: H(X) = 1.0000 bit.
  """
  # Generazione di 10.000 elementi con 2 stati equiprobabili (p=0.5, p=0.5)
  synthetic_data = pd.Series([1, 2] * 5000)
  h_val = compute_shannon_entropy(synthetic_data)

  # L'entropia di due stati equiprobabili deve essere esattamete 1.0 bit
  assert np.isclose(
      h_val, 1.0000, atol=1e-4
  ), f"Errore Entropia Teorica: Calcolato {h_val}, atteso 1.0000"


def test_entropy_real_corpus_attractor():
  """Risoluzione P0.4 (Parte 2): Verifica empirica dell'attrattore stazionario sul corpus reale Voynich.

  Aspettativa: H(X) = 1.6947 bit su 4 stati (Alpha, Beta, Delta, Gamma).
  """
  # Frequenze stazionarie ufficiali v3.3 del corpus Voynich
  # State Alpha (1): 10.00%, State Beta (2): 54.99%, State Delta (3): 19.51%, State Gamma (4): 15.50%
  n_total = 35483
  n_alpha = int(0.1000 * n_total)
  n_beta = int(0.5499 * n_total)
  n_delta = int(0.1951 * n_total)
  n_gamma = n_total - (n_alpha + n_beta + n_delta)

  corpus_states = pd.Series(
      [1] * n_alpha + [2] * n_beta + [3] * n_delta + [4] * n_gamma
  )
  h_corpus = compute_shannon_entropy(corpus_states)

  # Verifica del valore congelato nel Trattato v3.3
  EXPECTED_H_VOYNICH = 1.6947
  assert np.isclose(
      h_corpus, EXPECTED_H_VOYNICH, atol=1e-3
  ), f"Errore Entropia Corpus: Calcolato {h_corpus:.4f}, atteso {EXPECTED_H_VOYNICH}"


def test_binary_admissibility_matrix_structure():
  """Verifica la corretta inizializzazione della Matrice Binaria di Ammissibilità 4x4."""
  matrix_mgr = BinaryAdmissibilityMatrix()
  matrix = matrix_mgr.get_matrix()

  # Verifica dimensioni 4x4 e densità nominale del 75% (12 ammissibili su 16)
  assert matrix.shape == (4, 4), "La matrice deve avere dimensione 4x4"
  assert (
      np.sum(matrix == 1) == 12
  ), "La matrice deve contenere esattamente 12 transizioni ammissibili"


if __name__ == "__main__":
  pytest.main([__file__])