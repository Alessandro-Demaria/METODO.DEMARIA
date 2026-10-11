#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Modulo: tests_test_epistemological_neutrality.py
Descrizione: Test di validazione formale della neutralità epistemologica della codebase (Punto 7.1 - Scheda SORU).
             Verifica l'assenza assoluta di termini celebrativi o categoriali ("smoking gun", "inconfutabile", "prova regina")
             nei dizionari di output e nei report della suite.

Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
Licenza Codebase: MIT License
"""

import pytest
import pandas as pd

from audit_null_models2 import HierarchicalNullModelsAuditor


def test_epistemological_language_neutrality_in_null_models():
    """
    Verifica che il modulo dei Modelli Nulli produca diagnosi accademicamente neutrali
    e del tutto prive di termini non scientifici o celebrativi.
    """
    # Costruzione di un dataset sintetico minimale per la verifica del testo dei dizionari
    sample_df = pd.DataFrame({
        "state": ["State Alpha", "State Beta", "State Delta", "State Gamma"] * 10,
        "Folio": ["f1r"] * 20 + ["f1v"] * 20,
        "line_id": [1, 1, 2, 2] * 10
    })

    auditor = HierarchicalNullModelsAuditor(iterations=10, seed=42)
    res = auditor.run_intra_line_null_model(sample_df)

    diagnosis_str = str(res["diagnosis"]).lower()
    scope_str = str(res["permutation_scope"]).lower()

    # Blocco tassativo dei termini trionfalistici
    forbidden_terms = ["smoking gun", "prova regina", "inconfutabile", "dimostra assolutamente", "perfezione assoluta"]

    for term in forbidden_terms:
        assert term not in diagnosis_str, f"Termine trionfalistico non ammesso rilevato in diagnosis: '{term}'"
        assert term not in scope_str, f"Termine trionfalistico non ammesso rilevato in scope: '{term}'"

    print("\n[+] VALIDAZIONE NEUTRALITÀ EPISTEMOLOGICA LINGUAGGIO SUPERATA CON SUCCESSO:")
    print(f"    - Diagnosi Modello Nullo di Rigo: '{res['diagnosis']}'")
    print("    - Nessun termine trionfalistico rilevato nell'output di laboratorio.")


if __name__ == "__main__":
    pytest.main([__file__])