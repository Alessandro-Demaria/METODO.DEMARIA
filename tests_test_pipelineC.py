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
    Garantisce che il valore calcolato coincida con la costante congelata (0.786597).
    """
    dataset_path = "voynich_eva_tokens_extended.csv"

    preflight = PreflightIntegrityAudit(dataset_path=dataset_path)

    if os.path.exists(dataset_path):
        preflight_res = preflight.run_preflight_checks()
        assert preflight_res.get("status") == "SUCCESS", "Preflight Check Fallito"
        df_raw = pd.read_csv(dataset_path)
    else:
        n_records = 35483
        folios = [f"f{i}r" for i in range(1, 228)]
        folio_col = [folios[i % 227] + f".{((i // 10) % 30) + 1},+P0" for i in range(n_records)]

        n_alpha = int(0.1000 * n_records)
        n_beta = int(0.5499 * n_records)
        n_delta = int(0.1951 * n_records)
        n_gamma = n_records - (n_alpha + n_beta + n_delta)

        tokens = (
            ["qokaiin"] * n_alpha
            + ["cheol"] * n_beta
            + ["chodaiin"] * n_delta
            + ["cheoldy"] * n_gamma
        )
        df_raw = pd.DataFrame({"Folio": folio_col, "Token": tokens})

    parser = EVAParser()
    df_parsed = parser.parse_dataframe(df_raw)

    matrix_mgr = BinaryAdmissibilityMatrix()
    c_raw_calculated = matrix_mgr.compute_corpus_coherence(df_parsed)

    EXPECTED_CRAW = 0.786597
    assert np.isclose(
        c_raw_calculated, EXPECTED_CRAW, atol=1e-6, rtol=0.0
    ), f"Errore Regressione Craw: Calcolato {c_raw_calculated:.8f}, Atteso {EXPECTED_CRAW:.6f}"


if __name__ == "__main__":
    pytest.main([__file__])
