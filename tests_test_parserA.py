
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Suite Test A: tests_test_parserA.py
Test unitari per la verifica del parser e della classificazione degli stati.

Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
Licenza Codebase: MIT License
"""

import pytest
import pandas as pd
from core_parser1 import EVAParser


def test_clean_eva_token():
    parser = EVAParser()
    assert parser.clean_eva_token("qokaiin!") == "qokaiin"
    assert parser.clean_eva_token("cheol*") == "cheol"


def test_map_token_to_state():
    parser = EVAParser()
    assert parser.map_token_to_state("qokaiin") == EVAParser.STATE_ALPHA
    assert parser.map_token_to_state("cheol") == EVAParser.STATE_ALPHA
    assert parser.map_token_to_state("am") == EVAParser.STATE_GAMMA
    assert parser.map_token_to_state("ck") == EVAParser.STATE_DELTA


def test_parse_dataframe():
    parser = EVAParser()
    df_dummy = pd.DataFrame({"folio": ["f1r", "f1r"], "token": ["qokaiin", "cheol"]})
    df_out = parser.parse_dataframe(df_dummy)
    
    assert "cleaned_token" in df_out.columns
    assert "assigned_state" in df_out.columns
    assert "line_id" in df_out.columns


if __name__ == "__main__":
    pytest.main(["-v", "tests_test_parserA.py"])
