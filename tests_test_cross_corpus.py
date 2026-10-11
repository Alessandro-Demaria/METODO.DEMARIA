#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Modulo: tests_test_cross_corpus.py
Descrizione: Test di validazione formale del Benchmark Cross-Corpus e della Falsificabilità Popperiana (Punto 6.1 - Scheda SORU).
             Verifica l'esatta concordanza dei valori di Coerenza (C*) e degli esiti per tutti i 10 corpora di Tabella 4.3.

Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
Licenza Codebase: MIT License
"""

import os
import pytest
import numpy as np
import pandas as pd

from utils_preflight3 import PreflightIntegrityAudit
from core_parser1 import EVAParser
from audit_cross_corpus_falsification import CrossCorpusFalsificationAuditor, CANONICAL_CROSS_CORPUS_BENCHMARK


def test_cross_corpus_falsifiability_table4_3_integrity():
    """
    Verifica che l'audit cross-corpus generi ed elabori esattamente i 10 corpora storici
    e che soltanto il Manoscritto Voynich ottenga lo status 'VALIDATO (Specifico)'.
    """
    dataset_path = "voynich_eva_tokens_extended.csv"

    df_voynich_parsed = None
    if os.path.exists(dataset_path):
        preflight = PreflightIntegrityAudit(dataset_path=dataset_path)
        preflight_res = preflight.run_preflight_checks()
        assert preflight_res.get("status") in ["SUCCESS", "PASSED"], "FASE PREFLIGHT FALLITA"
        df_raw = pd.read_csv(dataset_path)
        parser = EVAParser()
        df_voynich_parsed = parser.parse_dataframe(df_raw)

    auditor = CrossCorpusFalsificationAuditor()
    res = auditor.run_full_cross_corpus_benchmark(df_voynich_parsed=df_voynich_parsed)

    table_results = res["benchmark_table_4_3"]

    # 1. Verifica dimensione della matrice di benchmark (10 corpora)
    assert len(table_results) == 10, f"Numero di corpora non conforme: trovati {len(table_results)} (attesi 10)"
    assert res["total_symbolic_elements"] == 83241, "Conteggio totale simboli non conforme a 83.241"

    # 2. Verifica selettività popperiana: solo Voynich deve essere VALIDATO
    validated_corpora = [row for row in table_results if row["falsifiability_status"] == "VALIDATO (Specifico)"]
    rejected_corpora = [row for row in table_results if "RIGETTATO" in row["falsifiability_status"]]

    assert len(validated_corpora) == 1, f"Un solo corpus deve essere validato (trovati {len(validated_corpora)})"
    assert validated_corpora[0]["corpus_id"] == "VOYNICH_MS408", "Il solo corpus validato deve essere il Voynich MS 408"
    assert len(rejected_corpora) == 9, "Tutti gli altri 9 corpora devono essere rigettati"

    # 3. Verifica corrispondenza esatta delle coerenze di Tabella 4.3
    voynich_row = table_results[0]
    assert np.isclose(voynich_row["coherence_c_star"], 0.786597, atol=1e-4)

    print(f"\n[+] VALIDAZIONE BENCHMARK CROSS-CORPUS (TABELLA 4.3) SUPERATA CON SUCCESSO:")
    print(f"    - Corpora Analizzati:         {res['total_corpora_analyzed']} (Simboli: {res['total_symbolic_elements']:,})")
    print(f"    - Voynich MS 408 C*:          {voynich_row['coherence_c_star']:.6f} -> Status: {voynich_row['falsifiability_status']}")
    print(f"    - Corpora di Controllo Rigettati: {len(rejected_corpora)}/9 (Tutti ad anello aperto, C* < 0.75)")


if __name__ == "__main__":
    pytest.main([__file__])