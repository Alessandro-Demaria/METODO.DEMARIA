#!/usr/bin/env python3
"""LABORATORIO SCIENTIFICO METODO DEMARIA™ - RELEASE v3.3 (AUDIT-MASTER UNIFICATO)

Modulo: run_audit_direct.py
Descrizione: Script di esecuzione diretta dell'Audit di Robustezza e Stress Test.
             Riallineato esattamente alle API ufficiali della Master Audit Suite v3.3.
Autore: Avv. Alessandro Demaria
"""

import os
import sys
import pandas as pd

from audit_robustness6 import RobustnessStressTestAudit
from core_matrix2 import BinaryAdmissibilityMatrix
from core_parser1 import EVAParser
from utils_preflight3 import PreflightIntegrityAudit


def execute_direct_robustness_audit():
  """Esegue direttamente lo Stress Test di Robustezza mediante chiamate alle API v3.3."""
  print("[+] Avvio Audit Diretto di Robustezza v3.3 (Metodo Demaria)...")

  # 1. Preflight Integrity Check
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
  df_raw["folio_id"] = (
      df_raw["Folio"].astype(str).apply(lambda x: x.split(".")[0])
  )
  df_raw["line_number"] = df_raw["Folio"].astype(str).apply(
      lambda x: x.split(".")[1].split(",")[0] if "." in x else "1"
  )
  df_raw["line_id"] = df_raw["folio_id"] + "." + df_raw["line_number"]
  df_raw["folio"] = df_raw["folio_id"]

  # 3. Parsing Vettoriale dei Token EVA
  parser = EVAParser()
  df_parsed = parser.parse_dataframe(df_raw)

  # 4. Matrice di Ammissibilità e Baseline
  matrix_mgr = BinaryAdmissibilityMatrix()
  c_raw = matrix_mgr.compute_corpus_coherence(df_parsed)
  print(f"[+] Baseline Coerenza Grezza Reale (Craw): {c_raw:.6f}")

  # 5. Esecuzione Robustness & Stress Test (Riallineamento API v3.3 - P0.1b)
  print(
      "[+] Esecuzione RobustnessStressTestAudit (100 iterazioni/livello,"
      " Seed=42)..."
  )
  robustness_audit = RobustnessStressTestAudit(
      iterations_per_level=100, seed=42
  )
  robustness_results = robustness_audit.run_robustness_test(
      df_parsed, matrix_mgr, parser
  )

  print("[+] Audit Diretto di Robustezza Completato con Successo.")
  return robustness_results


if __name__ == "__main__":
  execute_direct_robustness_audit()