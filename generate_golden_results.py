#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Edizione Scientifica Pura)

Modulo: generate_golden_results.py
Genera il file dei risultati empirici ufficiali (golden_results.json)
senza valori cablati o calibrazioni sintetiche.
"""

import os
import json
import pandas as pd
from core_parser1 import EVAParser
from core_matrix2 import BinaryAdmissibilityMatrix


def main():
    dataset_path = "voynich_eva_tokens_extended.csv"
    output_path = "golden_results.json"

    if not os.path.exists(dataset_path):
        print(f"[-] Errore: File dataset {dataset_path} non trovato.")
        return

    print("[+] Caricamento ed elaborazione dati empirici...")
    df_raw = pd.read_csv(dataset_path)
    
    parser = EVAParser()
    df_parsed = parser.parse_dataframe(df_raw)

    matrix_mgr = BinaryAdmissibilityMatrix()
    c_raw = matrix_mgr.compute_corpus_coherence(df_parsed)
    h_states = matrix_mgr.compute_shannon_entropy(df_parsed, state_column="assigned_state")

    golden_data = {
        "release": "v3.3_pure",
        "total_records": len(df_parsed),
        "c_raw_observed": c_raw,
        "shannon_entropy_observed": h_states,
        "status": "COMPUTED_FROM_EMPIRICAL_DATA"
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(golden_data, f, indent=4)

    print(f"[+] File {output_path} generato con successo basandosi sui dati reali.")


if __name__ == "__main__":
    main()
