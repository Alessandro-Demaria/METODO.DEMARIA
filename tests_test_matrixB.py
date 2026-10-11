#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Suite Test 2: tests_test_matrixB.py
Test unitari per la validazione della Matrice Canonica 4x4 e dell'Invariante di Armonia (core_matrix2.py).

Autore: Avv. Alessandro Demaria
Licenza Codebase: MIT License
Tutela Privativa e Marchio: Art. 98 D.Lgs. 30/2005 (CPI) / L. 633/1941
"""

import pytest
import pandas as pd
from core_matrix2 import TransitionMatrixManager


def test_transition_validity():
    """Verifica l'ammissibilità topologica delle transizioni della Matrice Canonica 4x4."""
    matrix_mgr = TransitionMatrixManager()
    # Transizioni Ammesse (1)
    assert matrix_mgr.is_transition_valid("Alpha", "Beta") is True
    assert matrix_mgr.is_transition_valid("Beta", "Gamma") is True
    assert matrix_mgr.is_transition_valid("Gamma", "Alpha") is True
    
    # Transizioni Vietate (0)
    assert matrix_mgr.is_transition_valid("Alpha", "Gamma") is False
    assert matrix_mgr.is_transition_valid("Gamma", "Beta") is False


def test_raw_coherence_computation():
    """Verifica il calcolo della Coerenza Sintattica Grezza su sequenza deterministica nota."""
    matrix_mgr = TransitionMatrixManager()
    # Sequenza con 3 transizioni intrarigo ammesse su 3 (Craw = 1.0)
    df_valid = pd.DataFrame({
        "line_id": ["f1r_l1", "f1r_l1", "f1r_l1", "f1r_l1"],
        "assigned_state": ["Alpha", "Beta", "Gamma", "Alpha"]
    })
    c_raw, valid_t, total_t = matrix_mgr.compute_raw_coherence(df_valid)
    assert total_t == 3
    assert valid_t == 3
    assert c_raw == 1.0


def test_harmony_invariant_and_entropy():
    """Verifica l'operazionalizzazione dell'Invariante di Armonia e dell'Entropia di Shannon."""
    matrix_mgr = TransitionMatrixManager()
    df_data = pd.DataFrame({
        "line_id": ["f1r_l1"] * 4,
        "assigned_state": ["Alpha", "Beta", "Delta", "Gamma"]
    })
    harmony_res = matrix_mgr.compute_harmony_invariant(df_data)
    
    assert "harmony_invariant_phi" in harmony_res
    assert "shannon_entropy_bits" in harmony_res
    # Con 4 stati ad equiprobabilità (p=0.25), l'entropia di Shannon teorica deve essere esattamente 2.0 bit
    assert round(harmony_res["shannon_entropy_bits"], 2) == 2.00


if __name__ == "__main__":
    pytest.main(["-v", "tests_test_matrixB.py"])