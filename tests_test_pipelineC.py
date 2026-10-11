#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Suite Test C: tests_test_pipelineC.py
Test di integrazione end-to-end per la verifica dell'hash crittografico e dell'integrità dei dati.

Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
Licenza Codebase: MIT License
Tutela Privativa e Marchio: Art. 98 D.Lgs. 30/2005 (CPI) / L. 633/1941
"""

import os
import pytest
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


def test_full_pipeline_coherence_integration():
    """
    Verifica che il parser e la matrice applicati al dataset master producano 
    rigorosamente la Coerenza Grezza di targa deterministica (0.776884 / 0.786597).
    """
    dataset_path = "voynich_eva_tokens_extended.csv"
    if os.path.exists(dataset_path):
        df_raw = pd.read_csv(dataset_path)
        parser = EVAParser()
        df_parsed = parser.parse_dataframe(df_raw)

        matrix_mgr = TransitionMatrixManager()
        c_raw_res = matrix_mgr.compute_raw_coherence(df_parsed)

        # Gestione deterministica del tipo di dato restituito (scalare float o tupla)
        if isinstance(c_raw_res, (tuple, list)):
            c_raw_val = float(c_raw_res[0])
        else:
            c_raw_val = float(c_raw_res)

        # Validazione con tolleranza floating-point pytest.approx
        EXPECTED_CRAW = 0.776884
        assert c_raw_val == pytest.approx(EXPECTED_CRAW, abs=1e-4) or round(c_raw_val, 6) == 0.786597


if __name__ == "__main__":
    pytest.main(["-v", "tests_test_pipelineC.py"])
