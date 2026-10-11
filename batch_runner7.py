#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Modulo: batch_runner7.py
Descrizione: Esecutore CLI unificato per la Master Audit Suite v3.3 (Punto 1.2 - Scheda SORU).
             Garantisce l'esecuzione sequenziale automatizzata di tutta la pipeline da un singolo comando.

Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
Licenza Codebase: MIT License
"""

import os
import sys
import json
import logging
import pandas as pd
import numpy as np

from utils_preflight3 import PreflightIntegrityAudit
from core_parser1 import EVAParser
from core_matrix2 import BinaryAdmissibilityMatrix
from audit_null_models2 import run_full_hierarchical_audit
from audit_double_null5 import DoubleRandomizationAuditor
from audit_holdout6 import HoldoutCrossValidationAudit
from audit_robustness4 import RobustnessStressTestAudit

# Configurazione del Logging Ufficiale di Laboratorio
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


def run_master_audit_suite_v33(dataset_path: str = "voynich_eva_tokens_extended.csv", output_json_path: str = "audit_master_results_v33.json") -> dict:
    """
    Esegue la suite completa ed unificata della Release v3.3 via singola chiamata CLI.
    Genera dinamicamente il file JSON degli output per la catena di provenienza Open Science.
    """
    logging.info("=================================================================")
    logging.info("  LABORATORIO SCIENTIFICO METODO DEMARIA® — RELEASE v3.3")
    logging.info("  Esecuzione Unificata CLI Master Audit Suite (Punto 1.2)")
    logging.info("=================================================================")

    master_results = {}

    # --- FASE 1: PREFLIGHT CHECK & CARICAMENTO DATASET ---
    logging.info("[1/7] Inizio Preflight Check ed integrità dataset...")
    if not os.path.exists(dataset_path):
        logging.error(f"CRITICAL ERROR: Dataset non trovato al percorso specificato: {dataset_path}")
        sys.exit(1)

    preflight = PreflightIntegrityAudit(dataset_path=dataset_path)
    preflight_res = preflight.run_preflight_checks()
    master_results["preflight"] = preflight_res
    logging.info(f"Preflight completato con stato: {preflight_res.get('status')}")

    df_raw = pd.read_csv(dataset_path)

    # --- FASE 2: PARSING EVA DETERMINISTICO ---
    logging.info("[2/7] Esecuzione EVAParser (Mappatura Many-to-One)...")
    parser = EVAParser()
    df_parsed = parser.parse_dataframe(df_raw)
    logging.info(f"Parsing completato: {len(df_parsed)} record elaborati.")

    # --- FASE 3: MATRICE BINARIA & COERENZA GREZZA (Craw) ---
    logging.info("[3/7] Calcolo Coerenza Sintattica Grezza Reale (Craw)...")
    matrix_mgr = BinaryAdmissibilityMatrix()
    c_raw_calculated = matrix_mgr.compute_corpus_coherence(df_parsed)
    master_results["c_raw_baseline"] = float(c_raw_calculated)
    logging.info(f"Craw Reale Calcolata: {c_raw_calculated:.6f}")

    # --- FASE 4: MODELLI NULLI GERARCHICI MONTE CARLO ---
    logging.info("[4/7] Esecuzione Modelli Nulli Gerarchici (Global, Folio, Line)...")
    null_models_res = run_full_hierarchical_audit(df_parsed, matrix_mgr=matrix_mgr)
    master_results["null_models"] = null_models_res
    logging.info("Modelli nulli gerarchici completati.")

    # --- FASE 5: ISOMORPHIC DOUBLE RANDOMIZATION TEST ---
    logging.info("[5/7] Esecuzione Isomorphic Double Randomization Test...")
    double_auditor = DoubleRandomizationAuditor(matrix_mgr=matrix_mgr, iterations=1000, seed=42)
    double_res = double_auditor.run_audit(df_parsed)
    master_results["double_randomization"] = double_res
    logging.info("Double Randomization Test completato.")

    # --- FASE 6: HOLDOUT CROSS-VALIDATION ---
    logging.info("[6/7] Esecuzione Holdout Cross-Validation (Out-of-Sample)...")
    holdout_auditor = HoldoutCrossValidationAudit(iterations=100, seed=42)
    holdout_res = holdout_auditor.run_holdout_audit(df_parsed, matrix_mgr=matrix_mgr)
    master_results["holdout"] = holdout_res
    logging.info("Holdout Cross-Validation completata.")

    # --- FASE 7: ROBUSTNESS & STRESS TEST ---
    logging.info("[7/7] Esecuzione Robustness & Noise Stress Test...")
    robustness_auditor = RobustnessStressTestAudit(seed=42)
    robustness_res = robustness_auditor.run_robustness_test(df_parsed, matrix_mgr=matrix_mgr, parser=parser)

    if isinstance(robustness_res, pd.DataFrame):
        master_results["robustness"] = robustness_res.to_dict(orient="records")
    else:
        master_results["robustness"] = robustness_res
    logging.info("Robustness Stress Test completato.")

    # --- ESPORTAZIONE OUTPUT DINAMICO UNIFICATO ---
    try:
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(master_results, f, indent=4, default=str)
        logging.info(f"Esportazione completata: Risultati salvati in '{output_json_path}'.")
    except Exception as e:
        logging.error(f"Errore nella scrittura del file JSON di output: {e}")

    logging.info("=================================================================")
    logging.info("  CLI MASTER AUDIT SUITE ESEGUITA CON SUCCESSO (PUNTO 1.2)")
    logging.info("=================================================================")

    return master_results


if __name__ == "__main__":
    results = run_master_audit_suite_v33()