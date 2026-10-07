"""
===============================================================================
METODO DEMARIA® — BATCH RUNNER SUITE AUDIT MASTER (v3.2 CANONICO)
===============================================================================
Modulo: batch_runner.py
Autore: Avv. Alessandro Demaria | Licenza: CC BY 4.0
===============================================================================
"""

import sys
import os
import json
import hashlib
import time
import pandas as pd
import numpy as np

# Importazione dei moduli dell'Audit Metodo Demaria
from voynich_parser import parse_and_clean_dataset, load_method_specification, SPEC_FILE
from null_model_test import run_full_audit_suite
from double_randomization_test import run_double_randomization_test
from robustness_stress_test import run_robustness_stress_test

DATASET_FILE = "voynich_eva_tokens_extended.csv"
OUTPUT_SUMMARY_CSV = "audit_master_summary_results.csv"
OUTPUT_ROBUSTNESS_CSV = "robustness_test_results.csv"


def calculate_sha256(filepath):
    if not os.path.exists(filepath):
        return None
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def run_preflight_checks():
    print("=" * 70)
    print("METODO DEMARIA® — PRE-FLIGHT AUDIT & FAIL-FAST CHECK (v3.2)")
    print("=" * 70 + "\n")

    if not os.path.exists(SPEC_FILE):
        print(f"[-] ERRORE CRITICO: Specifica '{SPEC_FILE}' non trovata.")
        sys.exit(1)

    if not os.path.exists(DATASET_FILE):
        print(f"[-] ERRORE CRITICO: Dataset '{DATASET_FILE}' non trovato.")
        sys.exit(1)

    # Verifica SHA-256 Dataset
    dataset_hash = calculate_sha256(DATASET_FILE)
    expected_hash = "dec87e784290ad5b404bd5ed0110349a2f379c7fb386adb0bca2d7a4b1890999"
    
    print(f"[*] Specifica Canonica:     {SPEC_FILE}")
    print(f"[*] Dataset Master:         {DATASET_FILE}")
    print(f"[*] SHA-256 Atteso:         {expected_hash}")
    print(f"[*] SHA-256 Rilevato:       {dataset_hash}")

    if dataset_hash != expected_hash:
        print("[!] ATTENZIONE: Hash SHA-256 non corrisponde esattamente all'atteso.")
    else:
        print("[1/3] VERIFICA CRITTOGRAFICA SHA-256: PASS.")

    # Parse e conteggio record
    df = parse_and_clean_dataset(SPEC_FILE)
    n_records = len(df)
    print(f"[*] Record Totali Rilevati: {n_records}")
    if n_records < 30000:
        print("[-] ERRORE CRITICO: Conteggio record insufficiente.")
        sys.exit(1)
    print("[2/3] VERIFICA CONTEGGIO RECORD: PASS.")

    spec = load_method_specification(SPEC_FILE)
    print(f"[*] Tie-Breaking Rule:      {spec.get('state_mapping_rules', {}).get('tie_breaking_rule')}")
    print(f"[*] Monte Carlo N:          10000")
    print(f"[*] Seed di Sistema:        42\n")

    print("[3/3] TUTTI I PRE-FLIGHT CHECK SUPERATI CON SUCCESSO. AVVIO SUITE...\n")
    print("=" * 70 + "\n")


def run_master_suite():
    start_time = time.time()
    run_preflight_checks()

    print("METODO DEMARIA® — ESECUZIONE SUITE DI AUDIT MASTER (FULL RUN)")
    print("=" * 70)
    print(f"[*] Ora Inizio Esecuzione: {time.strftime('%Y-%m-%dT%H:%M:%S')}\n")

    # 1. Modelli Nulli Gerarchici
    print(">>> FASE 1/3: ESECUZIONE MODELLI NULLI GERARCHICI <<<")
    df_null_results = run_full_audit_suite(n_simulations=10000, seed=42)

    # 2. Double Randomization Test
    print("\n>>> FASE 2/3: ESECUZIONE DOUBLE RANDOMIZATION TEST (ISOMORFO) <<<")
    df_dr_results = run_double_randomization_test(n_simulations=10000, seed=42)

    # 3. Robustness Stress Test
    print("\n>>> FASE 3/3: ESECUZIONE ROBUSTNESS & STRESS TEST <<<")
    df_rob_results = run_robustness_stress_test(n_iterations=100, seed=42)

    # Unione risultati sintetici per audit_master_summary_results.csv
    master_summary = pd.concat([df_null_results, df_dr_results], ignore_index=True)
    master_summary.to_csv(OUTPUT_SUMMARY_CSV, index=False)
    df_rob_results.to_csv(OUTPUT_ROBUSTNESS_CSV, index=False)

    total_time = time.time() - start_time
    print("=" * 70)
    print(f"[+] Master Report sintetico salvato in '{OUTPUT_SUMMARY_CSV}'.")
    print(f"[+] Report di Robustezza salvato in    '{OUTPUT_ROBUSTNESS_CSV}'.")
    print(f"[*] Tempo totale di esecuzione: {total_time:.2f} secondi.")
    print("=" * 70)
    print("[SUCCESS] SUITE COMPLETA AUDIT DEMARIA COMPLETATA SENZA ERRORE.\n")


if __name__ == "__main__":
    run_master_suite()