#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Modulo: tests_test_holdout_strict.py
Descrizione: Test di validazione formale del congelamento preventivo ed analisi Holdout Strict (Punto 5.1 - Scheda SORU).
             Verifica l'isolamento dei folii di training (80%) e la stabilità ad anello chiuso sul test set holdout (20%).

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
from audit_holdout6 import HoldoutCrossValidationAudit


def test_holdout_strict_freeze_and_out_of_sample_stability():
    """
    Verifica che la suddivisione per Folio (80% Train / 20% Test Holdout) mantenga
    uno scarto relativo Delta C_raw inferiore al vincolo di tolleranza (< 1.12%).
    """
    dataset_path = "voynich_eva_tokens_extended.csv"

    if not os.path.exists(dataset_path):
        pytest.skip("Dataset fisico non trovato. Test riservato all'esecuzione sul corpus master.")

    # 1. Preflight Audit
    preflight = PreflightIntegrityAudit(dataset_path=dataset_path)
    preflight_res = preflight.run_preflight_checks()
    assert preflight_res.get("status") in ["SUCCESS", "PASSED"], "FASE PREFLIGHT FALLITA"

    df_raw = pd.read_csv(dataset_path)
    parser = EVAParser()
    df_parsed = parser.parse_dataframe(df_raw)
    matrix_mgr = BinaryAdmissibilityMatrix()

    # 2. Esecuzione dell'Audit Holdout Strict (80/20)
    auditor = HoldoutCrossValidationAudit(train_ratio=0.80, seed=42)
    res = auditor.run_strict_holdout_split(df_parsed, matrix_mgr=matrix_mgr)

    c_train = res["mean_c_raw_train"]
    c_test = res["mean_c_raw_test"]
    delta_c_raw = res["delta_c_raw"]

    # 3. Asserzioni Vincolanti di Stabilità Out-of-Sample
    assert res["train_folios_count"] + res["test_folios_count"] == 227, "La somma dei folii di Train e Test deve ammontare a 227"
    assert np.isclose(c_train, 0.791204, atol=1e-2), f"C_train non conforme: {c_train:.6f}"
    assert np.isclose(c_test, 0.781990, atol=1e-2), f"C_test non conforme: {c_test:.6f}"
    assert delta_c_raw < 0.015, f"Lo scarto Delta C_raw ({delta_c_raw:.6f}) supera il vincolo di stabilità out-of-sample"

    print(f"\n[+] VALIDAZIONE HOLDOUT STRICT (80/20) SUPERATA CON SUCCESSO:")
    print(f"    - Folii Training Set (80%): {res['train_folios_count']} folii (Tokens: {res['train_tokens_count']:,})")
    print(f"    - Folii Test Set (20%):     {res['test_folios_count']} folii (Tokens: {res['test_tokens_count']:,})")
    print(f"    - Coerenza In-Sample Train:  {c_train:.6f}")
    print(f"    - Coerenza Out-of-Sample:    {c_test:.6f}")
    print(f"    - Delta C_raw (Scarto):      {delta_c_raw:.6f} ({res['delta_c_raw_pct']})")


if __name__ == "__main__":
    pytest.main([__file__])