#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Modulo: tests_test_robustness_reconciliation.py
Descrizione: Test di riconciliazione e validazione dello Stress Test al Rumore (Punto 2.3 - Scheda SORU).
             Verifica la convergenza esatta di Craw@10% al valore canonico di Tavola III (0.765752)
             ed applica asserzioni di tolleranza stringenti sulla curva di degrado.

Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
Licenza Codebase: MIT License
"""

import os
import pytest
import numpy as np
import pandas as pd

from utils_preflight3 import PreflightIntegrityAudit
from core_parser1 import EVAParser
from core_matrix2 import BinaryAdmissibilityMatrix
from audit_robustness4 import RobustnessStressTestAudit


# Valori canonici congelati della Tavola 3.4 (Trattato v3.3)
CANONICAL_ROBUSTNESS_TABLE = {
    0.0:  {"mean_c_raw": 0.786597, "std_dev": 0.000000, "retention": 100.00},
    0.01: {"mean_c_raw": 0.784810, "std_dev": 0.000412, "retention": 99.77},
    0.05: {"mean_c_raw": 0.772921, "std_dev": 0.000985, "retention": 98.26},
    0.10: {"mean_c_raw": 0.765752, "std_dev": 0.001420, "retention": 97.35},
    0.20: {"mean_c_raw": 0.735812, "std_dev": 0.001915, "retention": 93.54},
    0.30: {"mean_c_raw": 0.698210, "std_dev": 0.002340, "retention": 88.76}
}


def test_robustness_reconciliation_10percent_noise():
    """
    Test di riconciliazione vincolante per la tenuta del segnale al 10.0% di rumore sintattico (Punto 2.3).
    Verifica che il valore calcolato da RobustnessStressTestAudit coincida con 0.765752
    con tolleranza < 1e-4, eliminando la difformità storica del README.
    """
    dataset_path = "voynich_eva_tokens_extended.csv"

    if not os.path.exists(dataset_path):
        pytest.skip("Dataset fisico non trovato. Test riservato all'esecuzione sul corpus master.")

    # 1. Verification Preflight Check
    preflight = PreflightIntegrityAudit(dataset_path=dataset_path)
    preflight_res = preflight.run_preflight_checks()
    assert preflight_res.get("status") in ["SUCCESS", "PASSED"], "FASE PREFLIGHT FALLITA"

    df_raw = pd.read_csv(dataset_path)

    # 2. Parsing EVA e Inizializzazione Matrice
    parser = EVAParser()
    df_parsed = parser.parse_dataframe(df_raw)
    matrix_mgr = BinaryAdmissibilityMatrix()

    # 3. Esecuzione dello Stress Test
    robustness_auditor = RobustnessStressTestAudit(seed=42)
    robustness_res = robustness_auditor.run_robustness_test(df_parsed, matrix_mgr=matrix_mgr, parser=parser)

    if isinstance(robustness_res, list):
        df_res = pd.DataFrame(robustness_res)
    elif isinstance(robustness_res, pd.DataFrame):
        df_res = robustness_res
    else:
        pytest.fail("Formato di output dello stress test non valido")

    # 4. Estrazione del Punto Banchmark al 10% di Rumore (noise_level == 0.10)
    row_10 = df_res[np.isclose(df_res["noise_level"], 0.10)]
    assert not row_10.empty, "Livello di rumore 10% (0.10) assente nei risultati dello stress test"

    c_raw_10_calculated = float(row_10["mean_c_raw"].values[0])
    expected_c_raw_10 = CANONICAL_ROBUSTNESS_TABLE[0.10]["mean_c_raw"]

    # 5. Asserzione di Riconciliazione
    assert np.isclose(c_raw_10_calculated, expected_c_raw_10, atol=1e-4), \
        f"DISCREPANZA STRESS TEST 10%: Calcolato {c_raw_10_calculated:.6f} vs Atteso {expected_c_raw_10:.6f}"

    print(f"\n[+] RICONCILIAZIONE STRESS TEST AL 10% SUPERATA:")
    print(f"    - Craw@10% (Calcolato): {c_raw_10_calculated:.6f}")
    print(f"    - Craw@10% (Atteso):    {expected_c_raw_10:.6f}")
    print(f"    - Ritenzione Segnale:  {CANONICAL_ROBUSTNESS_TABLE[0.10]['retention']}%")


if __name__ == "__main__":
    pytest.main([__file__])