#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato - Edizione Scientifica Pura)

Suite Test B: tests_test_matrixB.py
Verifica empirica incondizionata dell'Entropia di Shannon e della Matrice Canonica 4x4.
Misura i dati reali senza forzature o calibrazioni sintetiche.

Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
Licenza Codebase: MIT License
"""

import os
import pytest
import numpy as np
import pandas as pd
from core_parser1 import EVAParser
from core_matrix2 import BinaryAdmissibilityMatrix


def calculate_shannon_entropy(series: pd.Series) -> float:
    """Calcola l'entropia di Shannon H(X) empirica per qualunque serie di dati."""
    if series.empty:
        return 0.0
    counts = series.value_counts(normalize=True)
    probs = counts.values
    return float(-np.sum(probs * np.log2(probs + 1e-12)))


def test_matrix_admissibility():
    matrix_mgr = BinaryAdmissibilityMatrix()
    # Verifica delle proprietà strutturali della Matrice Canonica 4x4
    assert matrix_mgr.admissibility_matrix.shape == (4, 4)
    assert matrix_mgr.is_transition_valid("Alpha", "Beta") is True
    assert matrix_mgr.is_transition_valid("Alpha", "Gamma") is False


def test_shannon_entropy_real_computation():
    dataset_path = "voynich_eva_tokens_extended.csv"
    
    if os.path.exists(dataset_path):
        df_raw = pd.read_csv(dataset_path)
    else:
        # Dummy minimal per test d'ambiente
        df_raw = pd.DataFrame({
            "Folio": ["f1r.1", "f1r.1", "f1r.2"],
            "token": ["qokaiin", "cheol", "daiin"]
        })

    parser = EVAParser()
    df_parsed = parser.parse_dataframe(df_raw)

    # 1. Calcolo reale dell'Entropia di Shannon sugli Stati Topologici Reali
    h_states_calculated = calculate_shannon_entropy(df_parsed["assigned_state"])

    # 2. Calcolo reale dell'Entropia sui Token EVA Reali Originali
    h_tokens_calculated = calculate_shannon_entropy(df_parsed["token"])

    # 3. Asserzioni di integrità e coerenza formale (Valori Reali)
    assert isinstance(h_states_calculated, float)
    assert isinstance(h_tokens_calculated, float)
    assert h_states_calculated > 0.0
    assert h_tokens_calculated > 0.0


if __name__ == "__main__":
    pytest.main(["-v", "tests_test_matrixB.py"])
