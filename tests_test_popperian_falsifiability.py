#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Modulo: tests_test_popperian_falsifiability.py
Descrizione: Test di validazione formale del Registro Epistemologico di Falsificabilità (Punto 7.2 - Scheda SORU).
             Verifica che i report adottino esclusivamente le categorie di rigetto di H0,
             supporto quantitativo ad H1 e falsificazione empirica delle ipotesi alternative.

Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
Licenza Codebase: MIT License
"""

import pytest
from core_epistemology_reporting import PopperianEpistemologyReporter


def test_popperian_falsifiability_reporting_logic():
    """
    Verifica che il modulo di reporting generi strutture diagnostiche popperiane
    conforme ai requisiti di rigore e falsificabilità scientifica.
    """
    reporter = PopperianEpistemologyReporter()

    # 1. Test su Modello Nullo Gerarchico
    report_null = reporter.format_null_model_statement("Global Null", 19.8404, "< 0.0001", 0)
    
    assert "Rejected" in report_null["null_hypothesis_status"]
    assert "support the deterministic structural hypothesis" in report_null["popperian_diagnosis"]
    assert "inconfutabile" not in report_null["popperian_diagnosis"].lower()

    # 2. Test su Benchmark Cross-Corpus
    report_cross = reporter.format_cross_corpus_statement(0.786597, 0.738500, 4.4734)

    assert report_cross["selectivity_status"] == "Empirically Verified Selective Discrimination"
    assert "empirically falsified" in report_cross["popperian_diagnosis"]
    assert "dimostra in modo assoluto" not in report_cross["popperian_diagnosis"].lower()

    print("\n[+] VALIDAZIONE REGISTRO EPISTEMOLOGICO POPPERIANO SUPERATA CON SUCCESSO:")
    print(f"    - Status Ipotesi Nulla H0: '{report_null['null_hypothesis_status']}'")
    print(f"    - Diagnosi Popperiana: '{report_null['popperian_diagnosis']}'")


if __name__ == "__main__":
    pytest.main([__file__])