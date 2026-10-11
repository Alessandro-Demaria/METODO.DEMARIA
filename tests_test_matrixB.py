#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Modulo: tests_test_matrixB.py
Descrizione: Test di riconciliazione e calcolo analitico dell'Entropia di Shannon H(X) (Punto 2.2 - Scheda SORU).
             Calcola direttamente dal dataset trasformato l'entropia del sistema,
             eliminando asserzioni tautologiche e garantendo la rispondenza con il Trattato.

Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
Licenza Codebase: MIT License
"""

import os
import pytest
import numpy as np
import pandas as pd

from utils_preflight3 import PreflightIntegrityAudit
from core_parser1 import EVAParser
from core_matrix2 import BinaryAdmissibilityMatrix


# Valori teorici ed empirici canonici riconciliati
EXPECTED_H_VOYNICH_TOKENS = 1.6947   # Entropia di primo ordine sui token EVA del corpus (Trattato v3.3)
EXPECTED_H_4STATE_ATTRACTOR = 1.683534 # Entropia dell'attrattore stazionario a 4 stati (Alpha, Beta, Delta, Gamma)


def calculate_shannon_entropy(series: pd.Series) -> float:
    """
    Calcola l'entropia di Shannon di primo ordine H(X) in bit per una data serie simbolica.
    Formula: H(X) = - sum(p_i * log2(p_i))
    """
    probabilities = series.value_counts(normalize=True)
    probabilities = probabilities[probabilities > 0]
    return float(-np.sum(probabilities * np.log2(probabilities)))


def test_shannon_entropy_real_computation():
    """
    Test di calcolo reale dell'Entropia di Shannon (Punto 2.2).
    Verifica che il test estragga le frequenze direttamente dal DataFrame in memoria,
    calcoli l'equazione di Shannon e ne convalidi la corrispondenza numerica senza tautologie.
    """
    dataset_path = "voynich_eva_tokens_extended.csv"

    if os.path.exists(dataset_path):
        preflight = PreflightIntegrityAudit(dataset_path=dataset_path)
        preflight_res = preflight.run_preflight_checks()
        assert preflight_res.get("status") in ["SUCCESS", "PASSED"], "FASE PREFLIGHT FALLITA"
        df_raw = pd.read_csv(dataset_path)
    else:
        pytest.skip("Dataset fisico non trovato. Test riservato all'esecuzione sul corpus master.")

    # 1. Parsing EVA e Generazione degli Stati
    parser = EVAParser()
    df_parsed = parser.parse_dataframe(df_raw)
    assert "state" in df_parsed.columns, "Colonna 'state' mancante dopo il parsing"
    assert "token" in df_parsed.columns, "Colonna 'token' mancante nel dataframe"

    # 2. Calcolo Reale dell'Entropia di Shannon sugli Stati Topologici (4 Stati Minimi)
    h_states_calculated = calculate_shannon_entropy(df_parsed["state"])
    
    # 3. Calcolo Reale dell'Entropia sui Token EVA Originali
    h_tokens_calculated = calculate_shannon_entropy(df_parsed["token"])

    # 4. Asserzioni di Riconciliazione (Vietato EXPECTED == EXPECTED)
    assert isinstance(h_states_calculated, float), "L'entropia calcolata deve essere un float"
    assert isinstance(h_tokens_calculated, float), "L'entropia calcolata deve essere un float"

    # Verifica di vicinanza dell'entropia degli stati con la distribuzione stazionaria
    assert np.isclose(h_states_calculated, EXPECTED_H_4STATE_ATTRACTOR, atol=1e-3), \
        f"DISCREPANZA ENTROPIA STATI: Calcolato {h_states_calculated:.6f} vs Atteso {EXPECTED_H_4STATE_ATTRACTOR:.6f}"

    # Verifica di vicinanza dell'entropia dei token con il valore congelato nel Trattato
    assert np.isclose(h_tokens_calculated, EXPECTED_H_VOYNICH_TOKENS, atol=0.05), \
        f"DISCREPANZA ENTROPIA TOKEN: Calcolato {h_tokens_calculated:.6f} vs Atteso {EXPECTED_H_VOYNICH_TOKENS:.6f}"

    print(f"\n[+] RICONCILIAZIONE ENTROPIA SUPERATA:")
    print(f"    - H(X) Attrattore 4 Stati (Calcolato): {h_states_calculated:.6f} bit (Riferimento: {EXPECTED_H_4STATE_ATTRACTOR:.6f})")
    print(f"    - H(X) Token EVA Corpus (Calcolato):   {h_tokens_calculated:.6f} bit (Riferimento: {EXPECTED_H_VOYNICH_TOKENS:.6f})")


if __name__ == "__main__":
    pytest.main([__file__])