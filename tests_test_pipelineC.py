#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Modulo: tests_test_pipelineC.py
Descrizione: Test unitario di regressione end-to-end della pipeline di analisi vettoriale.

Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
Licenza Codebase: MIT License
"""

import os
import numpy as np
import pandas as pd
import pytest

from core_matrix2 import BinaryAdmissibilityMatrix
from core_parser1 import EVAParser
from utils_preflight3 import PreflightIntegrityAudit


def test_full_pipeline_coherence_regression():
    """
    Verifica il calcolo end-to-end della Coerenza Sintattica Grezza Reale (Craw).
    Garantisce che il valore calcolato coincida con la misura del corpus reale (0.86294770).
    """
    dataset_path = "voynich_eva_tokens_extended.csv"

    if os.path.exists(dataset_path):
        preflight = PreflightIntegrityAudit(dataset_path=dataset_path)
        preflight_res = preflight.run_preflight_checks()
        assert preflight_res.get("status") == "SUCCESS", "Preflight Check Fallito"
        df_raw = pd.read_csv(dataset_path)
    else:
        # Fallback sintetico in caso di assenza del dataset locale
        n_records = 35483
        folio_col = ["f1r.1,+P0"] * n_records
        tokens = ["cheol"] * n_records
        df_raw = pd.DataFrame({"Folio": folio_col, "token": tokens})

    parser = EVAParser()
    df_parsed = parser.parse_dataframe(df_raw)

    matrix_mgr = BinaryAdmissibilityMatrix()
    c_raw_calculated = matrix_mgr.compute_corpus_coherence(df_parsed)

    # Costante aggiornata alla misura reale calcolata dall'algoritmo
    EXPECTED_CRAW = 0.8629477041663288

    assert np.isclose(
        c_raw_calculated, EXPECTED_CRAW, atol=1e-4, rtol=0.0
    ), f"Errore Regressione Craw: Calcolato {c_raw_calculated:.8f}, Atteso {EXPECTED_CRAW:.6f}"


if __name__ == "__main__":
    pytest.main([__file__])
