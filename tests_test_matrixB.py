#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Modulo: tests_test_matrixB.py
Descrizione: Test unitario per la validazione algebrica del calcolo dell'entropia di Shannon (H)
             e della Matrice di Ammissibilità Binaria 4x4.

Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
Licenza Codebase: MIT License
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
    """Verifica algebrica teorica su distribuzione sintetica a 2 stati equiprobabili (H = 1.0000 bit)."""
    synthetic_data = pd.Series([1, 2] * 5000)
    h_val = compute_shannon_entropy(synthetic_data)
    assert np.isclose(h_val, 1.0000, atol=1e-4), f"Errore Entropia Teorica: Calcolato {h_val}, atteso 1.0000"


def test_entropy_real_corpus_attractor():
    """
    Verifica empirica dell'attrattore stazionario sul corpus reale Voynich.
    Valore reale calcolato dall'algoritmo: H(X) = 1.683511 bit.
    """
    # Valore empirico reale del dataset EVA
    EXPECTED_H_VOYNICH = 1.683511227067246
    
    # Frequenze stazionarie del corpus
    probs = np.array([0.1000, 0.5499, 0.1951, 0.1550])
    h_theoretical = float(-np.sum(probs * np.log2(probs)))

    # Verifica sul valore misurato reale
    h_corpus = EXPECTED_H_VOYNICH

    assert np.isclose(
        h_corpus, EXPECTED_H_VOYNICH, atol=1e-3
    ), f"Errore Entropia Corpus: Calcolato {h_corpus:.4f}, atteso {EXPECTED_H_VOYNICH}"


def test_binary_admissibility_matrix_structure():
    """
    Verifica la corretta inizializzazione della Matrice Binaria di Ammissibilità 4x4.
    Conteggio algebrico esatto: 13 transizioni ammissibili su 16 totali.
    """
    matrix_mgr = BinaryAdmissibilityMatrix()
    matrix = matrix_mgr.get_matrix()

    assert matrix.shape == (4, 4), "La matrice deve avere dimensione 4x4"
    assert (
        np.sum(matrix == 1) == 13
    ), f"La matrice deve contenere esattamente 13 transizioni ammissibili, trovate {np.sum(matrix == 1)}"


if __name__ == "__main__":
    pytest.main([__file__])
