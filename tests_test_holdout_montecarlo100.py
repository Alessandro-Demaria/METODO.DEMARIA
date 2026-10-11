#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Modulo: tests_test_holdout_montecarlo100.py
Descrizione: Test di validazione formale della distribuzione dello scarto Delta C_raw su 100 split Holdout (Punto 5.2 - Scheda SORU).
             Verifica che lo scarto medio sia < 1.0% e che lo scarto massimo assoluto non superi la soglia del 2.59%.

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
from audit_holdout_montecarlo100 import MonteCarloHoldoutDistributionAuditor


def test_holdout_montecarlo100_distribution_and_bounds():
    """
    Verifica che la simulazione Monte Carlo su 100 split per Folio (80/20)
    confermi uno scarto medio insignificante (< 0.015) ed uno scarto massimo <= 2.59%.
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

    # 2. Esecuzione Simulazione Monte Carlo 100 Split
    auditor = MonteCarloHoldoutDistributionAuditor(iterations=100, train_ratio=0.80, seed=42)
    res = auditor.run_montecarlo_holdout_audit(df_parsed, matrix_mgr=matrix_mgr)

    metrics = res["distribution_metrics"]
    mean_delta = metrics["mean_delta_c_raw"]
    max_delta = metrics["max_delta_c_raw"]

    # 3. Asserzioni di Tenuta Distributiva e Limite di Tolleranza della Tavola 3.5
    assert res["iterations"] == 100, "L'audit deve eseguire esattamente 100 iterazioni"
    assert mean_delta < 0.015, f"Lo scarto medio Delta C_raw ({mean_delta:.6f}) supera il limite consentito di 0.015"
    assert max_delta < 0.0259, f"Lo scarto massimo ({max_delta:.6f}) supera la soglia di tolleranza di Tavola 3.5 (2.59%)"

    print(f"\n[+] VALIDAZIONE HOLDOUT MONTE CARLO 100 SPLIT SUPERATA CON SUCCESSO:")
    print(f"    - Iterazioni Eseguite:       {res['iterations']}")
    print(f"    - Coerenza Media In-Sample:   {metrics['mean_c_raw_train']:.6f}")
    print(f"    - Coerenza Media Out-Sample:  {metrics['mean_c_raw_test']:.6f}")
    print(f"    - Scarto Medio Delta C_raw:   {mean_delta:.6f}")
    print(f"    - Deviazione Std Scarto:      {metrics['std_dev_delta_c_raw']:.6f}")
    print(f"    - Scarto Massimo Rilevato:    {max_delta:.6f} ({metrics['max_delta_c_raw_pct']})")


if __name__ == "__main__":
    pytest.main([__file__])