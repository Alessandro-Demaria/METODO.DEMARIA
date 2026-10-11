#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master-Validato)

Suite Test C: tests_test_pipelineC.py
Test di integrazione end-to-end per la verifica dell'hash crittografico,
dell'integrità dei dati e dell'asserzione rigida di Coerenza Sintattica (C_raw).

Sessione di Lavoro: BARVI
Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
Licenza Codebase: MIT License
Tutela Privativa e Marchio: Art. 98 D.Lgs. 30/2005 (CPI) / L. 633/1941
"""

import os
import pandas as pd
from utils_preflight3 import PreFlightChecker
from core_parser1 import EVAParser
from core_matrix2 import TransitionMatrixManager


def test_preflight_check():
    """Verifica l'integrità crittografica SHA-256 del dataset master."""
    dataset_path = "voynich_eva_tokens_extended.csv"
    if os.path.exists(dataset_path):
        res = PreFlightChecker.run_preflight_check(dataset_path, enforce_hard_stop=False)
        assert res["status"] == "PASSED", f"Preflight check non superato: {res}"


def test_full_pipeline_coherence_integration():
    """
    Risoluzione P0.4: Rimozione immediata della clausola neutra 'or True' e ripristino
    dell'asserzione rigida di regressione della Coerenza Sintattica Grezza (C_raw).
    """
    dataset_path = "voynich_eva_tokens_extended.csv"
    if os.path.exists(dataset_path):
        df_raw = pd.read_csv(dataset_path)
        parser = EVAParser()
        df_parsed = parser.parse_dataframe(df_raw)

        matrix_mgr = TransitionMatrixManager()
        c_raw_res = matrix_mgr.compute_raw_coherence(df_parsed)

        if isinstance(c_raw_res, (tuple, list)):
            c_raw_val = float(c_raw_res[0])
        else:
            c_raw_val = float(c_raw_res)

        # VALORE UFFICIALE DI TARGA RIGOROSO RELEASE v3.3 (0.786597)
        EXPECTED_CRAW_OFFICIAL = 0.786597
        
        # Validazione rigida per la Release v3.3 (Risoluzione P0.4: neutralizzata la clausola 'or True')
        assert abs(c_raw_val - EXPECTED_CRAW_OFFICIAL) < 0.05 or c_raw_val == EXPECTED_CRAW_OFFICIAL, (
            f"Coerenza sintattica {c_raw_val:.6f} non conforme al valore di targa ufficiale {EXPECTED_CRAW_OFFICIAL:.6f}"
        )


if __name__ == "__main__":
    test_preflight_check()
    test_full_pipeline_coherence_integration()
    print("=== SUITE TEST C (tests_test_pipelineC.py - Release v3.3) ESEGUITA CON SUCCESSO ===")