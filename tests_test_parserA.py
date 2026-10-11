#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Suite Test A: tests_test_parserA.py
Test unitari per la verifica della logica di parsing ed assegnazione degli stati v3.3.

Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
Licenza Codebase: MIT License
"""

import pytest
import pandas as pd
from core_parser1 import EVAParser


def test_map_token_to_state():
    parser = EVAParser()
    # Mappatura deterministica Many-to-One: 1=Alpha, 2=Beta, 3=Delta, 4=Gamma
    assert parser.map_token_to_state("qokaiin") == 1
    assert parser.map_token_to_state("cheol") == 1
    assert parser.map_token_to_state("am") == 4
    assert parser.map_token_to_state("ck") == 3
    assert parser.map_token_to_state("random_token") == 2


def test_parse_dataframe():
    parser = EVAParser()
    df_dummy = pd.DataFrame({
        "Folio": ["f1r.1,+P0", "f1r.1,+P0"],
        "token": ["qokaiin", "cheol"]
    })
    df_out = parser.parse_dataframe(df_dummy)
    
    assert "state" in df_out.columns
    assert "state_name" in df_out.columns
    assert "line_id" in df_out.columns
    assert df_out["line_id"].iloc[0] == "f1r.1"


if __name__ == "__main__":
    pytest.main(["-v", "tests_test_parserA.py"])
