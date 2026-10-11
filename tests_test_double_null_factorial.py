#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Modulo: tests_test_double_null_factorial.py
Descrizione: Test di validazione formale del Double-Null Fattoriale 2x2 Design (Punto 4.3 - Scheda SORU).
             Verifica l'integrità delle 4 celle ortogonali e l'effetto d'interazione specifico.

Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
Licenza Codebase: MIT License
"""

import os
import pytest
import numpy as np
import pandas as pd

from utils_preflight3 import PreflightIntegrityAudit
from core_parser1 import EVAParser
from audit_double_null_factorial import FactorialDoubleNullAuditor


def test_double_null_factorial_2x2_structure_and_coupling():
    """
    Verifica che il test fattoriale 2x2 generi correttamente le 4 condizioni ortogonali
    e che la baseline reale (C11) superi nettamente tutte le altre 3 celle nulle.
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

    auditor = FactorialDoubleNullAuditor(iterations=100, seed=42)
    res = auditor.run_factorial_2x2_audit(df_parsed)

    table_2x2 = res["factorial_design_table_2x2"]

    # 2. Verifica presenza delle 4 condizioni ortogonali
    assert "cell_11_real_corpus_canonical_matrix" in table_2x2
    assert "cell_21_permuted_corpus_canonical_matrix" in table_2x2
    assert "cell_12_real_corpus_isodense_matrix" in table_2x2
    assert "cell_22_permuted_corpus_isodense_matrix" in table_2x2

    c_11 = table_2x2["cell_11_real_corpus_canonical_matrix"]["mean_coherence"]
    c_21 = table_2x2["cell_21_permuted_corpus_canonical_matrix"]["mean_coherence"]
    c_12 = table_2x2["cell_12_real_corpus_isodense_matrix"]["mean_coherence"]
    c_22 = table_2x2["cell_22_permuted_corpus_isodense_matrix"]["mean_coherence"]

    # 3. Asserzioni di superiorità della baseline reale (C11 > C21, C12, C22)
    assert np.isclose(c_11, 0.786597, atol=1e-4), f"Coerenza baseline C11 non conforme: {c_11}"
    assert c_11 > c_21, f"C11 ({c_11:.6f}) deve superare il Global Null C21 ({c_21:.6f})"
    assert c_11 > c_12, f"C11 ({c_11:.6f}) deve superare il Matrix Null C12 ({c_12:.6f})"
    assert c_11 > c_22, f"C11 ({c_11:.6f}) deve superare il Double Null C22 ({c_22:.6f})"

    # 4. Verifica Effetto d'Interazione Positivo
    i_ab = res["double_null_metrics"]["interaction_effect_i_ab"]
    assert i_ab > 0, f"L'effetto d'interazione I_AB deve essere positivo: {i_ab}"

    print(f"\n[+] VALIDAZIONE DOUBLE-NULL FATTORIALE 2x2 SUPERATA CON SUCCESSO:")
    print(f"    - Cell 11 (Reale/Canonica):   {c_11:.6f}")
    print(f"    - Cell 21 (Permutato/Canonica):{c_21:.6f}")
    print(f"    - Cell 12 (Reale/Isodensa):  {c_12:.6f}")
    print(f"    - Cell 22 (Permutato/Isodensa):{c_22:.6f}")
    print(f"    - Effetto d'Interazione I_AB: +{i_ab:.6f}")


if __name__ == "__main__":
    pytest.main([__file__])