#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Suite Test 3: tests_test_pipelineC.py
Test d'integrazione end-to-end per la verifica dell'hash crittografico e dell'integrità dei dati.

Autore: Avv. Alessandro Demaria
Licenza Codebase: MIT License
Tutela Privativa e Marchio: Art. 98 D.Lgs. 30/2005 (CPI) / L. 633/1941
"""

import pytest
import os
import pandas as pd
from utils_preflight3 import PreFlightChecker
from core_parser1 import EVAParser
from core_matrix2 import TransitionMatrixManager


def test_preflight_check():
    """Verifica l'integrità crittografica SHA-256 del dataset master (se presente sul disco)."""
    dataset_path = "voynich_eva_tokens_extended.csv"
    if os.path.exists(dataset_path):
        res = PreFlightChecker.run_preflight_check(dataset_path, enforce_hard_stop=False)
        assert res["status"] == "PASSED"
        assert res["calculated_hash"] == PreFlightChecker.MASTER_DATASET_HASH
        assert res["token_count"] == PreFlightChecker.EXPECTED_TOKEN_COUNT


def test_full_pipeline_coherence_integration():
    """Verifica che il parser applicato al dataset master produca la Coerenza Grezza di targa."""
    dataset_path = "voynich_eva_tokens_extended.csv"
    if os.path.exists(dataset_path):
        df_raw = pd.read_csv(dataset_path)
        parser = EVAParser()
        df_parsed = parser.parse_dataframe(df_raw)
        
        matrix_mgr = TransitionMatrixManager()
        c_raw, _, _ = matrix_mgr.compute_raw_coherence(df_parsed)
        
        # Verifica che C_raw coincida con la Coerenza Grezza di targa della Release v3.3 (0.786597)
        assert round(c_raw, 6) == 0.786597


if __name__ == "__main__":
    pytest.main(["-v", "tests_test_pipelineC.py"])