#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
METODO DEMARIA® — MASTER BATCH RUNNER & ORCHESTRATOR (v3.0 - Canonico)
Modulo: batch_runner.py
Autore: Avv. Alessandro Demaria | Licenza: CC BY 4.0
===============================================================================
Descrizione:
  Orchestratore e runner master unico per l'esecuzione end-to-end sequenziale
  di tutti i 4 moduli di audit e validazione del Metodo Demaria.
  Verifica l'integrità del dataset tramite SHA-256 e importa esclusivamente
  la configurazione da method_specification.json.
===============================================================================
"""

import os
import json
import time
import datetime
import hashlib
import pandas as pd

# Importazione esplicita dei moduli canonizzati
from null_model_test import run_full_audit_suite, load_method_specification, get_file_sha256
from double_randomization_test import run_double_randomization_test
from train_test_split_validation import run_train_test_validation
from robustness_stress_test import run_robustness_stress_test

SPEC_FILE = 'method_specification.json'

def execute_master_suite():
    t_start = time.time()
    print("==================================================================")
    print(" METODO DEMARIA® v3.0 — MASTER BATCH RUNNER & AUDIT ORCHESTRATOR ")
    print("==================================================================")
    print(f"[*] Timestamp Esecuzione: {datetime.datetime.now().isoformat()}")
    
    # 1. Verifica Single Source of Truth
    if not os.path.exists(SPEC_FILE):
        print(f"[!] ERRORE CRITICO: Architettura bloccata. File '{SPEC_FILE}' assente.")
        return
        
    spec = load_method_specification(SPEC_FILE)
    dataset_path = spec['master_dataset']['filename']
    expected_hash = spec['master_dataset']['sha256_hash']
    
    # 2. Controllo Provenienza Hash SHA-256
    measured_hash = get_file_sha256(dataset_path)
    print(f"[*] Dataset Master:       {dataset_path}")
    print(f"[*] Hash SHA-256 Atteso:  {expected_hash}")
    print(f"[*] Hash SHA-256 Rilevato:{measured_hash}")
    
    if measured_hash.lower() != expected_hash.lower():
        print("[!] ATTENZIONE CRITICA: L'hash del dataset differisce da quello congelato!")
    else:
        print("[✓] PROVENIENZA DATASET VERIFICATA AL 100% (HASH SHA-256 MATCH).")
        
    print("\n------------------------------------------------------------------")
    print("FASE 1/4: Esecuzione Modelli Nulli Gerarchici (null_model_test.py)")
    print("------------------------------------------------------------------")
    run_full_audit_suite()
    
    print("\n------------------------------------------------------------------")
    print("FASE 2/4: Esecuzione Test Avversariale Double Null (double_randomization_test.py)")
    print("------------------------------------------------------------------")
    run_double_randomization_test()
    
    print("\n------------------------------------------------------------------")
    print("FASE 3/4: Esecuzione Holdout Cross-Validation (train_test_split_validation.py)")
    print("------------------------------------------------------------------")
    run_train_test_validation()
    
    print("\n------------------------------------------------------------------")
    print("FASE 4/4: Esecuzione Stress Test di Sensibilità (robustness_stress_test.py)")
    print("------------------------------------------------------------------")
    run_robustness_stress_test()
    
    t_elapsed = round(time.time() - t_start, 2)
    print("\n==================================================================")
    print("   ESECUZIONE INTEGRALE MASTER SUITE COMPLETATA CON SUCCESSO!   ")
    print(f"   - Tempo Totale di Calcolo: {t_elapsed} s")
    print("==================================================================")
    
    # Registro di audit unico
    log_data = [{
        'Timestamp': datetime.datetime.now().isoformat(),
        'Specification_File': SPEC_FILE,
        'Dataset_Path': dataset_path,
        'SHA256_Hash': measured_hash,
        'Hash_Verified': bool(measured_hash.lower() == expected_hash.lower()),
        'Execution_Time_Sec': t_elapsed,
        'Status': 'SUCCESS'
    }]
    pd.DataFrame(log_data).to_csv('master_suite_execution_log.csv', index=False)
    print("[V] Log di tracciabilità della suite salvato in 'master_suite_execution_log.csv'.")

if __name__ == '__main__':
    execute_master_suite()