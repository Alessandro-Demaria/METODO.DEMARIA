#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Modulo: generate_audit_master_summary.py
Descrizione: Generatore dinamico del Summary Report dell'Audit Master (Punto 1.5 - Scheda SORU).
             Elimina ogni valore hard-coded e costruisce la tabella riassuntiva
             esclusivamente dai dati grezzi elaborati in tempo reale (audit_master_results_v33.json).

Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
Licenza Codebase: MIT License
"""

import os
import sys
import json
import logging
import pandas as pd

# Configurazione Logging di Laboratorio
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


def generate_master_summary_from_json(json_input_path: str = "audit_master_results_v33.json", csv_output_path: str = "audit_master_summary.csv") -> pd.DataFrame:
    """
    Legge il file JSON di output dinamico dell'Audit Master e genera il file CSV
    di sintesi senza ricorrere ad alcun valore pre-compilato o congelato.
    """
    logging.info(f"[Summary Generator] Caricamento risultati grezzi da: {json_input_path}")
    
    if not os.path.exists(json_input_path):
        logging.error(f"CRITICAL ERROR: File JSON di output non trovato: {json_input_path}. Eseguire prima batch_runner7.py.")
        sys.exit(1)

    with open(json_input_path, "r", encoding="utf-8") as f:
        master_data = json.load(f)

    summary_rows = []

    # 1. Baseline Real Raw Coherence (Craw)
    c_raw = master_data.get("c_raw_baseline", 0.0)
    preflight_info = master_data.get("preflight", {})
    dataset_sha256 = preflight_info.get("sha256_hash", "N/A")
    total_records = preflight_info.get("total_records", 0)

    summary_rows.append({
        "Metric_Category": "Baseline Corpus",
        "Test_Name": "Real Raw Syntactic Coherence (Craw)",
        "Observed_Value": c_raw,
        "Z_Score": "N/A",
        "Empirical_P_Value": "N/A",
        "Parametric_P_Value": "N/A",
        "Dataset_SHA256": dataset_sha256,
        "Sample_Size": total_records,
        "Diagnosis": "Observed Real Coherence on Master Dataset"
    })

    # 2. Modelli Nulli Gerarchici Monte Carlo
    null_models = master_data.get("null_models", {})
    for model_key, model_data in null_models.items():
        if isinstance(model_data, dict):
            summary_rows.append({
                "Metric_Category": "Hierarchical Null Models",
                "Test_Name": model_key,
                "Observed_Value": model_data.get("mean_null_coherence", "N/A"),
                "Z_Score": model_data.get("z_score", "N/A"),
                "Empirical_P_Value": model_data.get("empirical_p_value", "N/A"),
                "Parametric_P_Value": model_data.get("parametric_p_value", "N/A"),
                "Dataset_SHA256": dataset_sha256,
                "Sample_Size": total_records,
                "Diagnosis": model_data.get("diagnosis", "Null Model Evaluation")
            })

    # 3. Double Randomization Test
    double_null = master_data.get("double_randomization", {})
    if double_null:
        summary_rows.append({
            "Metric_Category": "Adversarial Test",
            "Test_Name": "Isomorphic Double Randomization",
            "Observed_Value": double_null.get("mean_double_null_coherence", "N/A"),
            "Z_Score": double_null.get("z_score", "N/A"),
            "Empirical_P_Value": double_null.get("empirical_p_value", "N/A"),
            "Parametric_P_Value": double_null.get("parametric_p_value", "N/A"),
            "Dataset_SHA256": dataset_sha256,
            "Sample_Size": total_records,
            "Diagnosis": double_null.get("diagnosis", "Matrix-Corpus Specificity Test")
        })

    # 4. Holdout Cross-Validation
    holdout = master_data.get("holdout", {})
    if holdout:
        summary_rows.append({
            "Metric_Category": "Out-of-Sample Validation",
            "Test_Name": "Holdout Folio-Split Cross-Validation",
            "Observed_Value": holdout.get("mean_c_raw_test", "N/A"),
            "Z_Score": "N/A",
            "Empirical_P_Value": "N/A",
            "Parametric_P_Value": "N/A",
            "Dataset_SHA256": dataset_sha256,
            "Sample_Size": total_records,
            "Diagnosis": f"Delta Craw Train/Test: {holdout.get('delta_c_raw', 'N/A')}"
        })

    df_summary = pd.DataFrame(summary_rows)
    df_summary.to_csv(csv_output_path, index=False, encoding="utf-8")
    logging.info(f"[Summary Generator] File CSV di sintesi dinamica esportato con successo in: '{csv_output_path}'")
    
    return df_summary


if __name__ == "__main__":
    generate_master_summary_from_json()