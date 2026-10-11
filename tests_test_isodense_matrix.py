#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Modulo: tests_test_isodense_matrix.py
Descrizione: Test di validazione formale del campionamento su Matrici Casualmente Isodense (Punto 4.2 - Scheda SORU).
             Verifica la correzione della densità in 13/16 celle e la superiorità della Matrice Canonica.

Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
Licenza Codebase: MIT License
"""

import os
import pytest
import numpy as np
import pandas as pd

from utils_preflight3 import PreflightIntegrityAudit
from core_parser1 import EVAParser
from audit_isodense_matrix import IsodenseMatrixAuditor


def test_isodense_matrix_density_and_coherence_superiority():
    """
    Verifica che il generator di matrici isodense produca esattamente 13 celle a 1
    e che la Matrice Canonica ottenga una coerenza significativamente superiore alle casuali.
    """
    dataset_path = "voynich_eva_tokens_extended.csv"

    if not os.path.exists(dataset_path):
        pytest.skip("Dataset fisico non trovato. Test riservato all'esecuzione sul corpus master.")

    # 1. Preflight Audit
    preflight = PreflightIntegrityAudit(dataset_path=dataset_path)
    preflight_res = preflight.run_preflight_checks()
    assert preflight_res.get("status") in ["SUCCESS", "PASSED"], "FASE PREFLIGHT FALLITA"

    df_raw = pd.read_csv(dataset_path)
    parser = EVAParser()
    df_parsed = parser.parse_dataframe(df_raw)

    auditor = IsodenseMatrixAuditor(iterations=100, seed=42)

    # 2. Verifica Strutturale Densità 13/16
    single_matrix = auditor.generate_random_isodense_matrix()
    assert single_matrix.shape == (4, 4), "La matrice deve avere dimensioni 4x4"
    assert np.sum(single_matrix) == 13, f"Densità errata: trovati {np.sum(single_matrix)} elementi attivi (attesi 13)"

    # 3. Esecuzione Audit e Verifica Superiorità Matrice Canonica
    res = auditor.run_isodense_audit(df_parsed)

    assert res["active_cells_per_matrix"] == 13
    assert res["total_matrix_cells"] == 16
    assert res["c_raw_canonical_observed"] > res["mean_isodense_coherence"], \
        f"La Matrice Canonica ({res['c_raw_canonical_observed']:.6f}) non supera le matrici casuali ({res['mean_isodense_coherence']:.6f})"

    print(f"\n[+] VALIDAZIONE MATRICI ISODENSE (13/16) SUPERATA CON SUCCESSO:")
    print(f"    - Densità Matrice:         {res['density_ratio']}")
    print(f"    - Craw Canonica Reale:    {res['c_raw_canonical_observed']:.6f}")
    print(f"    - Media Matrici Isodense:  {res['mean_isodense_coherence']:.6f}")
    print(f"    - Z-Score Distanza:        +{res['z_score']:.4f}")


if __name__ == "__main__":
    pytest.main([__file__])