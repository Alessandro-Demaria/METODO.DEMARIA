#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Suite Test 1: tests_test_parserA.py
Test unitari per la validazione del parser EVA (core_parser1.py).

Autore: Avv. Alessandro Demaria
Licenza Codebase: MIT License
Tutela Privativa e Marchio: Art. 98 D.Lgs. 30/2005 (CPI) / L. 633/1941
"""

import pytest
import pandas as pd
from core_parser1 import EVAParser


def test_clean_eva_token():
    """Verifica la rimozione dei caratteri speciali e marcatori IVTFF."""
    assert EVAParser.clean_eva_token("qokaiin!") == "qokaiin"
    assert EVAParser.clean_eva_token("[f1r.1]chodaiin*") == "chodaiin"
    assert EVAParser.clean_eva_token("{comment}otaiin?") == "otaiin"


def test_map_token_to_state():
    """Verifica la mappatura deterministica molti-a-uno sulla quadrupla degli stati minimi."""
    parser = EVAParser()
    # State Alpha (Prefissi di Innesco)
    assert parser.map_token_to_state("qokaiin") == EVAParser.STATE_ALPHA
    assert parser.map_token_to_state("chodaiin") == EVAParser.STATE_ALPHA
    
    # State Gamma (Suffissi di Chiusura)
    assert parser.map_token_to_state("am") == EVAParser.STATE_GAMMA
    assert parser.map_token_to_state("dy") == EVAParser.STATE_GAMMA
    
    # State Delta (Modulatori)
    assert parser.map_token_to_state("otaiin") == EVAParser.STATE_DELTA
    assert parser.map_token_to_state("shol") == EVAParser.STATE_DELTA
    
    # State Beta (Regime Stazionario / Default)
    assert parser.map_token_to_state("kaiin") == EVAParser.STATE_BETA


def test_parse_dataframe():
    """Verifica la corretta creazione delle colonne folio, line_id e assigned_state."""
    parser = EVAParser()
    df_raw = pd.DataFrame({
        "Folio": ["f1r", "f1r"],
        "Line": [1, 1],
        "EVA_Token": ["qokaiin", "dy"]
    })
    df_parsed = parser.parse_dataframe(df_raw)
    
    assert "folio" in df_parsed.columns
    assert "line_id" in df_parsed.columns
    assert "assigned_state" in df_parsed.columns
    assert df_parsed["line_id"].iloc[0] == "f1r_1"
    assert df_parsed["assigned_state"].iloc[0] == EVAParser.STATE_ALPHA
    assert df_parsed["assigned_state"].iloc[1] == EVAParser.STATE_GAMMA


if __name__ == "__main__":
    pytest.main(["-v", "tests_test_parserA.py"])