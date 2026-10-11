#!/usr/bin/env python3
"""LABORATORIO SCIENTIFICO METODO DEMARIA™ - RELEASE v3.3 (AUDIT-MASTER UNIFICATO)

Modulo: make_runner.py
Descrizione: Wrapper e runner automatizzato per la rigenerazione completa degli audit.
             Riallineato esattamente alle API ufficiali della Master Audit Suite v3.3.
Autore: Avv. Alessandro Demaria
"""

import sys
import os
import pandas as pd

from utils_preflight3 import PreflightIntegrityAudit
from core_parser1 import EVAParser
from core_matrix2 import BinaryAdmissibilityMatrix
from audit_nullmodels4 import HierarchicalNullModelsAudit
from audit_doublerand5 import DoubleRandomizationAudit
from audit_robustness6 import RobustnessStressTestAudit
from audit_holdout8 import HoldoutValidationAudit
from audit_ablation9 import RuleAblationAudit


def execute_make_runner():
  """Esegue la pipeline di rigenerazione e audit mediante chiamate esplicite alle API v3.3."""
  print(
      "[+] Avvio Esecuzione Automatica Runner v3.3 (Metodo Demaria)..."
  )

  # 1. Verification e Preflight Integrity Check
  preflight = PreflightIntegrityAudit()
  preflight_status = preflight.run_preflight_checks()
  if not preflight_status.get("status") == "SUCCESS":
    print("[-] Preflight Check Fallito. Interruzione esecuzione.")
    sys.exit(1)

  # 2. Caricamento Dataset e Normalizzazione Canonica (P0.2 / P0.3)
  csv_path = "voynich_eva_tokens_extended.csv"
  if not os.path.exists(csv_path):
    print(f"[-] Errore: File dataset '{csv_path}' non trovato.")
    sys.exit(1)

  df_raw = pd.read_csv(csv_path)

  # Normalizzazione identificativi folio e line_id
  df_raw["folio_id"] = df_raw["Folio"].astype(str).apply(lambda x: x.split(".")[0])
  df_raw["line_number"] = df_raw["Folio"].astype(str).apply(lambda x: x.split(".")[1].split(",")[0] if "." in x else "1")
  df_raw["line_id"] = df_raw["folio_id"] + "." + df_raw["line_number"]
  df_raw["folio"] = df_raw["folio_id"]

  # 3. Parsing Vettoriale dei Token EVA
  parser = EVAParser()
  df_parsed = parser.parse_dataframe(df_raw)

  # 4. Matrice di Ammissibilita e Calcolo Coerenza Craw
  matrix_mgr = BinaryAdmissibilityMatrix()
  c_raw = matrix_mgr.compute_corpus_coherence(df_parsed)
  print(f"[+] Coerenza Sintattica Grezza Reale (Craw): {c_raw:.6f}")

  # 5. Modelli Nulli Gerarchici Monte Carlo (P0.1a Fix)
  print("[+] Esecuzione Modelli Nulli Gerarchici (N=10.000, Seed=42)...")
  null_audit = HierarchicalNullModelsAudit(iterations=10000, seed=42)
  null_results = null_audit.run_full_hierarchical_audit(df_parsed, matrix_mgr)

  # 6. Test Avversariale Isomorfo di Doppia Randomizzazione
  print("[+] Esecuzione Double Randomization Test...")
  double_rand = DoubleRandomizationAudit(iterations=10000, seed=42)
  double_rand_results = double_rand.run_double_randomization_test(
      df_parsed, matrix_mgr
  )

  # 7. Stress Test di Robustezza e Sensibilita al Rumore (P0.1b Fix)
  print("[+] Esecuzione Robustness & Stress Test...")
  robustness = RobustnessStressTestAudit(iterations_per_level=100, seed=42)
  robustness_results = robustness.run_robustness_test(
      df_parsed, matrix_mgr, parser
  )

  # 8. Validazione Out-of-Sample Holdout (P0.2 Fix)
  print("[+] Esecuzione Spatial Stability Holdout Validation...")
  holdout = HoldoutValidationAudit(test_size=0.5, seed=42)
  holdout_results = holdout.run_holdout_validation(df_parsed, matrix_mgr)

  print("[+] Esecuzione Runner Completata con Successo.")
  return {
      "c_raw": c_raw,
      "null_results": null_results,
      "double_rand_results": double_rand_results,
      "robustness_results": robustness_results,
      "holdout_results": holdout_results,
  }


if __name__ == "__main__":
  execute_make_runner()