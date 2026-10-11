#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Suite Test B: tests_test_matrixB.py
Test unitari per la verifica della matrice di ammissibilità 4x4 e calcolo di C_raw.

Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
Licenza Codebase: MIT License
"""

import pytest
import pandas as pd
from core_matrix2 import TransitionMatrixManager


def test_transition_validity():
    mgr = TransitionMatrixManager()
    assert mgr.is_transition_valid("Alpha", "Beta") == True
    assert mgr.is_transition_valid("Beta", "Gamma") == True
    assert mgr.is_transition_valid("Alpha", "Gamma") == False


def test_raw_coherence_computation():
    mgr = TransitionMatrixManager()
    df_dummy = pd.DataFrame({
        "line_id": ["L1", "L1", "L1"],
        "assigned_state": ["Alpha", "Beta", "Gamma"]
    })
    c_raw, adm, tot = mgr.compute_raw_coherence(df_dummy)
    assert c_raw == 1.0
    assert adm == 2
    assert tot == 2


def test_harmony_invariant_and_entropy():
    mgr = TransitionMatrixManager()
    df_dummy = pd.DataFrame({
        "line_id": ["L1", "L1"],
        "assigned_state": ["Alpha", "Beta"]
    })
    phi_alpha, entropy_val = mgr.compute_harmony_invariant_and_entropy(df_dummy)
    assert phi_alpha == 1.0
    assert round(entropy_val, 4) == 1.6947


if __name__ == "__main__":
    pytest.main(["-v", "tests_test_matrixB.py"])
