#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Modulo: tests_test_pipeline_integration.py
Descrizione: Test d'integrazione end-to-end della Master Audit Suite v3.3 (Punto 1.3 - Scheda SORU).
             Verifica la sequenzialità della pipeline ad alte prestazioni sui parametri nominali
             di convergenza (N=10.000 Monte Carlo) ed applica asserzioni congiunte vincolanti.

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
from audit_null_models2 import run_full_hierarchical_audit
from audit_double_null5 import DoubleRandomizationAuditor
from audit_holdout6 import HoldoutCrossValidationAudit
from audit_robustness4 import RobustnessStressTestAudit


def test_full_pipeline_end_to_end_integration_nominal():
    """
    Test d'integrazione bloccante a rigore accademico: esegue sequenzialmente tutti i 7 moduli
    della pipeline v3.3 con parametri nominali ufficiali e verifica congiuntamente gli output.
    """
    dataset_path = "voynich_eva_tokens_extended.csv"
    
    # --- FASE 1: PREFLIGHT CHECK & INTEGRITÀ DATASET ---
    assert os.path.exists(dataset_path), f"FASE 1 FALLITA: Dataset fisico assente al percorso {dataset_path}"
    
    preflight = PreflightIntegrityAudit(dataset_path=dataset_path)
    preflight_res = preflight.run_preflight_checks()
    assert isinstance(preflight_res, dict), "FASE 1 FALLITA: Preflight deve restituire un dizionario"
    assert preflight_res.get("status") in ["SUCCESS", "PASSED"], f"FASE 1 FALLITA: Status Preflight invalido: {preflight_res.get('status')}"
    
    df_raw = pd.read_csv(dataset_path)
    assert not df_raw.empty, "FASE 1 FALLITA: Il DataFrame di input risulta vuoto"
    assert len(df_raw) == 35483, f"FASE 1 FALLITA: Conteggio record non nominale: {len(df_raw)} (attesi 35.483)"
    assert "token" in df_raw.columns, "FASE 1 FALLITA: Colonna 'token' mancante nel dataset"

    # --- FASE 2: PARSING EVA DETERMINISTICO ---
    parser = EVAParser()
    df_parsed = parser.parse_dataframe(df_raw)
    assert df_parsed is not None and not df_parsed.empty, "FASE 2 FALLITA: EVAParser ha restituito un DataFrame vuoto"
    assert "state" in df_parsed.columns, "FASE 2 FALLITA: Mappatura degli stati mancante nel DataFrame elaborato"

    # --- FASE 3: MATRICE BINARIA & COERENZA GREZZA (Craw) ---
    matrix_mgr = BinaryAdmissibilityMatrix()
    c_raw_calculated = matrix_mgr.compute_corpus_coherence(df_parsed)
    assert isinstance(c_raw_calculated, (float, np.floating)), "FASE 3 FALLITA: Craw deve essere un valore numerico floating point"
    assert 0.0 <= c_raw_calculated <= 1.0, f"FASE 3 FALLITA: Craw fuori dall'intervallo [0, 1]: {c_raw_calculated}"
    assert np.isclose(c_raw_calculated, 0.786597, atol=1e-4), f"FASE 3 FALLITA: Craw diverge dal valore congelato: {c_raw_calculated:.6f}"

    # --- FASE 4: MODELLI NULLI GERARCHICI MONTE CARLO ---
    null_models_res = run_full_hierarchical_audit(df_parsed, matrix_mgr=matrix_mgr)
    assert isinstance(null_models_res, dict), "FASE 4 FALLITA: Modelli nulli gerarchici devono restituire un dizionario"
    assert "global_null" in null_models_res and "intra_folio_null" in null_models_res and "intra_line_null" in null_models_res, \
        "FASE 4 FALLITA: Manca uno o più livelli dei modelli nulli gerarchici nell'output"

    # --- FASE 5: ISOMORPHIC DOUBLE RANDOMIZATION TEST (PARAMETRI NOMINALI: N=10.000) ---
    double_auditor = DoubleRandomizationAuditor(matrix_mgr=matrix_mgr, iterations=10000, seed=42)
    double_res = double_auditor.run_audit(df_parsed)
    assert isinstance(double_res, dict), "FASE 5 FALLITA: DoubleRandomizationAuditor deve restituire un dizionario"
    assert "p_value" in double_res and "z_score" in double_res and "empirical_p_value" in double_res, \
        "FASE 5 FALLITA: Incompletezza delle metriche nello Double Randomization Test"

    # --- FASE 6: HOLDOUT CROSS-VALIDATION (PARAMETRI NOMINALI: N=100) ---
    holdout_auditor = HoldoutCrossValidationAudit(iterations=100, seed=42)
    holdout_res = holdout_auditor.run_holdout_audit(df_parsed, matrix_mgr=matrix_mgr)
    assert isinstance(holdout_res, dict), "FASE 6 FALLITA: HoldoutCrossValidationAudit deve restituire un dizionario"
    assert "mean_c_raw_train" in holdout_res and "mean_c_raw_test" in holdout_res and "delta_c_raw" in holdout_res, \
        "FASE 6 FALLITA: Incompletezza delle metriche nello Holdout Cross-Validation"

    # --- FASE 7: ROBUSTNESS & NOISE STRESS TEST ---
    robustness_auditor = RobustnessStressTestAudit(seed=42)
    robustness_res = robustness_auditor.run_robustness_test(df_parsed, matrix_mgr=matrix_mgr, parser=parser)
    assert isinstance(robustness_res, (dict, pd.DataFrame, list)), "FASE 7 FALLITA: Output RobustnessStressTestAudit non conforme"


if __name__ == "__main__":
    pytest.main([__file__])