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
    # Transizioni ammesse
    assert mgr.is_transition_admissible("Alpha", "Beta") == True
    assert mgr.is_transition_admissible("Beta", "Gamma") == True
    # Transizione vietata
    assert mgr.is_transition_admissible("Alpha", "Gamma") == False


def test_raw_coherence_computation():
    mgr = TransitionMatrixManager()
    df_dummy = pd.DataFrame({
        "line_id": ["L1", "L1", "L1"],
        "assigned_state": ["Alpha", "Beta", "Gamma"]
    })
    # Alpha->Beta (OK) e Beta->Gamma (OK) -> 2/2 = 1.0
    c_raw = mgr.compute_raw_coherence(df_dummy)
    assert c_raw == 1.0


def test_harmony_invariant():
    mgr = TransitionMatrixManager()
    phi_alpha = mgr.compute_harmony_invariant(0.786597)
    assert phi_alpha == 0.786597


if __name__ == "__main__":
    pytest.main(["-v", "tests_test_matrixB.py"])
