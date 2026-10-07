#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
METODO DEMARIA® — HELD-OUT STRUCTURAL STABILITY SUITE (v3.0 - Canonico)
Modulo: train_test_split_validation.py
Autore: Avv. Alessandro Demaria | Licenza: CC BY 4.0
===============================================================================
Descrizione:
  Test di stabilità e generalizzazione strutturale su raggruppamento rigido 50/50
  per Folio_Base.
  Utilizza voynich_parser.py per l'ingestion pulita e la funzione canonica
  compute_c_raw_segmented() per garantire zero inter-folio / inter-line leakage.
  Legge i parametri esclusivamente da method_specification.json.
===============================================================================
"""

import os
import json
import hashlib
import datetime
import numpy as np
import pandas as pd
from voynich_parser import (
    parse_and_clean_dataset,
    compute_c_raw_segmented,
    load_method_specification,
    SPEC_FILE
)

def get_file_sha256(filepath: str) -> str:
    if not os.path.exists(filepath):
        return 'FILE_NOT_FOUND'
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        hasher.update(f.read())
    return hasher.hexdigest()

def run_train_test_validation():
    print("==================================================================")
    print(" METODO DEMARIA® — HELD-OUT STRUCTURAL STABILITY SUITE (v3.0) ")
    print("==================================================================")

    spec = load_method_specification(SPEC_FILE)
    dataset_path = spec['master_dataset']['filename']
    expected_hash = spec['master_dataset']['sha256_hash']
    seed = spec['system_parameters']['seed']

    dataset_hash = get_file_sha256(dataset_path)
    print(f"[*] Single Source of Truth: {SPEC_FILE}")
    print(f"[*] Dataset Input:          {dataset_path}")
    print(f"[*] SHA-256 Atteso:         {expected_hash}")
    print(f"[*] SHA-256 Rilevato:       {dataset_hash}")

    if dataset_hash.lower() != expected_hash.lower():
        print("[!] ATTENZIONE CRITICA: SHA-256 non corrisponde all'hash congelato in specifica!")
    else:
        print("[✓] PROVENIENZA DATASET VERIFICATA (HASH SHA-256 MATCH).")

    if not os.path.exists(dataset_path):
        print(f"[!] ERRORE CRITICO: Dataset '{dataset_path}' non trovato.")
        return

    # Ingestion pulita e segmentata via parser canonico
    df = parse_and_clean_dataset(SPEC_FILE)
    transition_matrix = np.array(spec['transition_matrix_validity']['allowed_transitions'], dtype=float)

    # Raggruppamento per veri folii base unici (203 folii)
    unique_folios = np.array(sorted(df['Folio_Base'].unique()))
    
    rng = np.random.RandomState(seed)
    rng.shuffle(unique_folios)

    # Split 50/50 sui folii unici
    split_idx = len(unique_folios) // 2
    train_folios = set(unique_folios[:split_idx])
    test_folios = set(unique_folios[split_idx:])

    train_df = df[df['Folio_Base'].isin(train_folios)].copy()
    test_df = df[df['Folio_Base'].isin(test_folios)].copy()

    # Calcolo C_raw segmentato senza leakage inter-linea / inter-folio
    c_train = compute_c_raw_segmented(train_df, transition_matrix, group_by=['Folio_Base', 'Line_Num'])
    c_test = compute_c_raw_segmented(test_df, transition_matrix, group_by=['Folio_Base', 'Line_Num'])
    delta_abs = abs(c_train - c_test)

    print("\n[+] RISULTATI HELD-OUT STRUCTURAL STABILITY (50/50 Grouped on Folio_Base):")
    print(f"   - Folii Unici Totali:     {len(unique_folios)}")
    print(f"   - Folii Train Set (50%):  {len(train_folios)}")
    print(f"   - Folii Test Set  (50%):  {len(test_folios)}")
    print(f"   - Train Coherence (C_raw): {c_train:.6f} ({c_train*100:.2f}%)")
    print(f"   - Test Coherence  (C_raw): {c_test:.6f} ({c_test*100:.2f}%)")
    print(f"   - Delta Assoluto (|ΔC|):   {delta_abs:.6f} ({delta_abs*100:.2f}%)")

    output_csv = 'train_test_validation_results.csv'
    res_df = pd.DataFrame([{
        'Timestamp': datetime.datetime.now().isoformat(),
        'Dataset_SHA256': dataset_hash,
        'Seed': seed,
        'N_Folios_Total': len(unique_folios),
        'N_Folios_Train': len(train_folios),
        'N_Folios_Test': len(test_folios),
        'C_Train_Raw': c_train,
        'C_Test_Raw': c_test,
        'Delta_Abs': delta_abs
    }])
    res_df.to_csv(output_csv, index=False)
    print(f"\n[V] Report di Audit salvato in: '{output_csv}'")

if __name__ == '__main__':
    run_train_test_validation()