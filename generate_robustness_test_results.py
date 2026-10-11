#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Modulo: generate_robustness_test_results.py
Descrizione: Generatore dinamico del Report di Robustezza e Stress Test al Rumore (Punto 1.5 - Scheda SORU).
             Legge ed esporta la curva di degradazione direttamente dagli output grezzi
             di memoria (audit_master_results_v33.json) senza valori hard-coded.

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


def generate_robustness_report_from_json(json_input_path: str = "audit_master_results_v33.json", csv_output_path: str = "robustness_test_results.csv") -> pd.DataFrame:
    """
    Estrae la curva di tolleranza al rumore e stabilità del sensore matematico
    dal file JSON dell'Audit Master ed esporta la tabella CSV dinamica.
    """
    logging.info(f"[Robustness Generator] Caricamento risultati di stress test da: {json_input_path}")
    
    if not os.path.exists(json_input_path):
        logging.error(f"CRITICAL ERROR: File JSON di output non trovato: {json_input_path}. Eseguire prima batch_runner7.py.")
        sys.exit(1)

    with open(json_input_path, "r", encoding="utf-8") as f:
        master_data = json.load(f)

    robustness_data = master_data.get("robustness", [])
    
    if not robustness_data:
        logging.error("CRITICAL ERROR: Dati di Robustness Stress Test assenti nel file JSON.")
        sys.exit(1)

    if isinstance(robustness_data, list):
        df_robustness = pd.DataFrame(robustness_data)
    else:
        df_robustness = pd.DataFrame([robustness_data])

    df_robustness.to_csv(csv_output_path, index=False, encoding="utf-8")
    logging.info(f"[Robustness Generator] Report di robustezza dinamico esportato con successo in: '{csv_output_path}'")
    
    return df_robustness


if __name__ == "__main__":
    generate_robustness_report_from_json()