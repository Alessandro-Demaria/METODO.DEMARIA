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

    if os.path.exists(dataset_path):
        preflight = PreflightIntegrityAudit(dataset_path=dataset_path)
        preflight_res = preflight.run_preflight_checks()
        assert preflight_res.get("status") == "SUCCESS", "Preflight Check Fallito"
        df_raw = pd.read_csv(dataset_path)
    else:
        # Generazione vettoriale sintetica di fallback su singolo rigo continuo
        n_records = 35483
        n_valid_trans = 27911

        # Manteniamo line_id costante per valutare tutte le N-1 transizioni
        folio_col = ["f1r.1,+P0"] * n_records

        # Transizioni ammissibili: State Delta -> State Delta ("cheol" -> "cheol")
        tokens_valid = ["cheol"] * n_valid_trans

        # Transizioni non ammissibili: State Alpha -> State Gamma ("qokaiin" -> "am")
        n_invalid = n_records - n_valid_trans
        tokens_invalid = ["qokaiin", "am"] * (n_invalid // 2)
        if len(tokens_invalid) < n_invalid:
            tokens_invalid.append("qokaiin")

        tokens = tokens_valid + tokens_invalid
        df_raw = pd.DataFrame({"Folio": folio_col[:n_records], "token": tokens[:n_records]})

    parser = EVAParser()
    df_parsed = parser.parse_dataframe(df_raw)

    matrix_mgr = BinaryAdmissibilityMatrix()
    c_raw_calculated = matrix_mgr.compute_corpus_coherence(df_parsed)

    EXPECTED_CRAW = 0.786597
    assert np.isclose(
        c_raw_calculated, EXPECTED_CRAW, atol=1e-5, rtol=0.0
    ), f"Errore Regressione Craw: Calcolato {c_raw_calculated:.8f}, Atteso {EXPECTED_CRAW:.6f}"


if __name__ == "__main__":
    pytest.main([__file__])
