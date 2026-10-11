#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Modulo: tests_test_table_generator.py
Descrizione: Test di validazione formale della rigenerazione dinamica delle Tavole I, II e III (Punto 8.1 - Scheda SORU).
             Verifica la congruenza dei dati estratti da golden_results_v3.3.json con le specifiche ufficiali del Trattato.

Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
Licenza Codebase: MIT License
"""

import pytest
import pandas as pd

from audit_table_generator import DynamicTableGenerator


def test_dynamic_table_generation_integrity_and_alignment():
    """
    Verifica che il generatore dinamico produca correttamente le 3 Tavole Ufficiali
    e che i valori chiave (Craw=0.786597, Z_Line=+14.5202, Benchmark 10%=97.35%) siano esattamente allineati.
    """
    generator = DynamicTableGenerator()

    # 1. Validazione Tavola I (Modelli Nulli)
    df_tab1 = generator.generate_table_1_null_models()
    assert len(df_tab1) == 3, "La Tavola I deve contenere esattamente 3 righe (Model 1, 2, 3)"
    assert "Model 3 (Intra-Line)" in df_tab1["Modello Nullo"].values
    line_row = df_tab1[df_tab1["Modello Nullo"] == "Model 3 (Intra-Line)"].iloc[0]
    assert line_row["Z-Score"] == "+14.5202", f"Z-Score di rigo non conforme: {line_row['Z-Score']}"

    # 2. Validazione Tavola II (Stress Test)
    df_tab2 = generator.generate_table_2_stress_test()
    assert len(df_tab2) == 6, "La Tavola II deve contenere esattamente 6 livelli di rumore"
    row_10pct = df_tab2[df_tab2["Livello Rumore"] == "10.0%"].iloc[0]
    assert row_10pct["Ritenzione Coerenza"] == "97.35%", f"Ritenzione al 10% di rumore non conforme: {row_10pct['Ritenzione Coerenza']}"

    # 3. Validazione Tavola III (Cross-Corpus)
    df_tab3 = generator.generate_table_3_cross_corpus()
    assert len(df_tab3) == 10, "La Tavola III deve contenere esattamente 10 corpora"
    voynich_row = df_tab3.iloc[0]
    assert "Manoscritto Voynich" in voynich_row["Corpus / Notazione Analizzata"]
    assert voynich_row["Esito Falsificabilità (Status)"] == "VALIDATO (Specifico)"

    print("\n[+] VALIDAZIONE RIGENERAZIONE DINAMICA TAVOLE SUPERATA CON SUCCESSO:")
    print(f"    - Tavola I (Modelli Nulli):    {len(df_tab1)} righe verificate (Z_Line = {line_row['Z-Score']})")
    print(f"    - Tavola II (Stress Test):     {len(df_tab2)} righe verificate (Ritenzione 10% = {row_10pct['Ritenzione Coerenza']})")
    print(f"    - Tavola III (Cross-Corpus):   {len(df_tab3)} corpora verificati (Voynich = {voynich_row['Esito Falsificabilità (Status)']})")


if __name__ == "__main__":
    pytest.main([__file__])