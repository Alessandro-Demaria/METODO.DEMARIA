#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Modulo: tests_test_davison_hinkley.py
Descrizione: Test di validazione formale del calcolo del p-value empirico Monte Carlo (Punto 3.1 - Scheda SORU).
             Verifica l'applicazione esatta della formula di Davison-Hinkley p_emp = (b + 1) / (N + 1).

Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
Licenza Codebase: MIT License
"""

import pytest
import numpy as np
from audit_null_models2 import HierarchicalNullModelsAuditor


def test_davison_hinkley_formula_precision():
    """
    Verifica che il calcolo di Davison-Hinkley restituisca i valori esatti e la notazione corretta per b = 0.
    """
    auditor = HierarchicalNullModelsAuditor(iterations=10000)

    # Caso b = 0 (Zero permutazioni avverse su N = 10.000)
    p_float, p_str = auditor.compute_davison_hinkley_p_value(b_count=0, n_iterations=10000)
    expected_p = 1.0 / 10001.0

    assert np.isclose(p_float, expected_p, atol=1e-9), f"Inesattezza numerica in p_emp: {p_float} vs {expected_p}"
    assert p_str == "< 0.0001", f"Formattazione stringa errata: {p_str}"
    assert p_float > 0.0, "Il p-value empirico non può mai essere matematicamente pari a zero"

    # Caso b = 5 (Cinque permutazioni avverse su N = 10.000)
    p_float_5, p_str_5 = auditor.compute_davison_hinkley_p_value(b_count=5, n_iterations=10000)
    expected_p_5 = 6.0 / 10001.0

    assert np.isclose(p_float_5, expected_p_5, atol=1e-9)
    assert p_str_5 == f"= {expected_p_5:.6f}"

    print("\n[+] VALIDAZIONE FORMULA DAVISON-HINKLEY SUPERATA CON SUCCESSO")


if __name__ == "__main__":
    pytest.main([__file__])