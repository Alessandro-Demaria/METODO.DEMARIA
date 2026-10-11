#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Modulo: tests_test_golden_results.py
Descrizione: Test di validazione formale del file 'golden_results_v3.3.json' (Punto 2.4 - Scheda SORU).
             Verifica l'esistenza, l'integrità dello schema e la rispondenza delle metriche congelate.

Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
Licenza Codebase: MIT License
"""

import os
import json
import pytest
import numpy as np

from generate_golden_results import build_golden_results_v33


def test_golden_results_file_integrity():
    """
    Test di verifica strutturale e numerica su golden_results_v3.3.json.
    """
    json_path = "golden_results_v3.3.json"

    # Genera il file se non presente
    if not os.path.exists(json_path):
        build_golden_results_v33(output_json_path=json_path)

    assert os.path.exists(json_path), "File golden_results_v3.3.json non trovato"

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. Verifica Sezioni Obbligatorie
    required_keys = [
        "metadata", "baseline_metrics", "attractor_distribution_4state",
        "hierarchical_null_models_n10k", "isomorphic_double_randomization",
        "noise_sensitivity_stress_test_table3", "holdout_cross_validation"
    ]
    for key in required_keys:
        assert key in data, f"Chiave obbligatoria mancante nel file Golden Results: {key}"

    # 2. Verifica Invarianti Numeriche Primarie
    assert np.isclose(data["baseline_metrics"]["c_raw_observed"], 0.786597, atol=1e-5)
    assert np.isclose(data["baseline_metrics"]["shannon_entropy_eva_tokens_bit"], 1.6947, atol=1e-4)
    assert data["metadata"]["dataset_sha256"] == "dec87e784290ad5b404bd5ed0110349a2f379c7fb386adb0bca2d7a4b1890999"

    # 3. Verifica Benchmark Stress Test 10%
    table3 = data["noise_sensitivity_stress_test_table3"]
    row_10 = [row for row in table3 if np.isclose(row["noise_level"], 0.10)][0]
    assert np.isclose(row_10["mean_c_raw_prime"], 0.765752, atol=1e-5)
    assert np.isclose(row_10["coherence_retention_pct"], 97.35, atol=1e-2)

    print("\n[+] VALIDAZIONE GOLDEN RESULTS v3.3 SUPERATA CON SUCCESSO")


if __name__ == "__main__":
    pytest.main([__file__])