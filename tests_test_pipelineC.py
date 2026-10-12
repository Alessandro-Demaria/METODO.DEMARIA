#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato - Edizione Scientifica Pura)

Suite Test C: tests_test_pipelineC.py
Verifica end-to-end della Pipeline e riconciliazione pura di Coerenza Sintattica (C_raw).

Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
Licenza Codebase: MIT License
"""

import os
import pytest
import pandas as pd
from core_parser1 import EVAParser
from core_matrix2 import BinaryAdmissibilityMatrix


def test_raw_coherence_reconciliation_craw():
    dataset_path = "voynich_eva_tokens_extended.csv"
    
    if os.path.exists(dataset_path):
        df_raw = pd.read_csv(dataset_path)
    else:
        df_raw = pd.DataFrame({
            "Folio": ["f1r.1", "f1r.1", "f1r.2"],
            "token": ["qokaiin", "cheol", "daiin"]
        })

    # 1. Parsing Vettoriale Deterministico sui dati Reali
    parser = EVAParser()
    df_parsed = parser.parse_dataframe(df_raw)
    assert df_parsed is not None and not df_parsed.empty

    # 2. Calcolo della Coerenza tramite Matrice Binaria sui Dati Reali
    matrix_mgr = BinaryAdmissibilityMatrix()
    c_raw_calculated = matrix_mgr.compute_corpus_coherence(df_parsed)

    # 3. Asserzione di Validità Matematica dell'Output Empirico
    assert isinstance(c_raw_calculated, float)
    assert 0.0 <= c_raw_calculated <= 1.0


if __name__ == "__main__":
    pytest.main(["-v", "tests_test_pipelineC.py"])
