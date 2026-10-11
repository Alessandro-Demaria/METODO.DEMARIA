#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Modulo 1: core_parser1.py
Parser deterministico per la classificazione vettoriale dei token EVA
in quattro stati sintattici minimi: Alpha, Beta, Delta, Gamma.

Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
Licenza Codebase: MIT License
Tutela Privativa e Marchio: Art. 98 D.Lgs. 30/2005 (CPI) / L. 633/1941
"""

import pandas as pd
import re


class EVAParser:
    """
    Parser deterministico a regole prioritarie per la riduzione dell'alfabeto EVA
    alla quadrupla degli stati topologici minimi (Alpha, Beta, Delta, Gamma).
    """

    STATE_ALPHA = "Alpha"
    STATE_BETA = "Beta"
    STATE_DELTA = "Delta"
    STATE_GAMMA = "Gamma"

    def __init__(self):
        # Prefissi d'innesco deterministici (State Alpha / Header di Rigo)
        self.alpha_prefixes = (
            "qo", "cho", "che", "ch", "sh", "ok", "ot", "ol", "op",
            "po", "to", "so", "do", "y", "q"
        )
        # Suffissi di chiusura deterministici (State Gamma / Reset e Drenaggio)
        self.gamma_suffixes = (
            "am", "an", "ain", "in", "al", "or", "ar", "dy", "eedy",
            "ey", "old", "m", "n", "g", "z"
        )
        # Modulatori interni di variazione (State Delta / Differenziazione)
        self.delta_substrings = ("ck", "ct", "ee", "ii", "iii", "aiin")

    def clean_token(self, token: str) -> str:
        """Rimuove marcatori di incertezza e caratteri non appartenenti all'alfabeto EVA."""
        if not isinstance(token, str):
            return ""
        return re.sub(r"[!\?\*\.\,\-\=\_]", "", token).strip().lower()

    def clean_eva_token(self, token: str) -> str:
        """Alias retro-compatibile per la suite di test unitari."""
        return self.clean_token(token)

    def classify_token(self, token: str) -> str:
        """
        Assegna lo stato sintattico vettoriale secondo la precedenza rigida v3.3:
        1. Alpha (Prefisso d'innesco)
        2. Gamma (Suffisso di chiusura)
        3. Delta (Modulatore interno)
        4. Beta  (Stato stazionario residuale / Azione)
        """
        tok = self.clean_token(token)
        if not tok:
            return self.STATE_BETA

        for pfx in self.alpha_prefixes:
            if tok.startswith(pfx):
                return self.STATE_ALPHA

        for sfx in self.gamma_suffixes:
            if tok.endswith(sfx):
                return self.STATE_GAMMA

        for sub in self.delta_substrings:
            if sub in tok:
                return self.STATE_DELTA

        return self.STATE_BETA

    def map_token_to_state(self, token: str) -> str:
        """Alias retro-compatibile per la suite di test unitari."""
        return self.classify_token(token)

    def parse_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Elabora il DataFrame del dataset master e genera le colonne
        di parsing vettoriale, distinguendo tra identificatore rigo e folio fisico.
        """
        df_out = df.copy()

        # Identificazione automatica della colonna contenente i token EVA
        token_col = None
        for col in ["token", "eva_token", "EVA_Token", "EVA_token"]:
            if col in df_out.columns:
                token_col = col
                break
        if token_col is None:
            token_col = df_out.select_dtypes(include=["object"]).columns[0]

        df_out["cleaned_token"] = df_out[token_col].apply(self.clean_token)
        df_out["assigned_state"] = df_out[token_col].apply(self.classify_token)

        # Tracciamento formale dell'identificatore di rigo (line_id) e del folio fisico (Folio)
        if "line_id" not in df_out.columns:
            if "Line" in df_out.columns and "Folio" in df_out.columns:
                df_out["line_id"] = df_out["Folio"].astype(str) + "." + df_out["Line"].astype(str)
            elif "folio" in df_out.columns:
                df_out["line_id"] = df_out["folio"].astype(str)
            else:
                df_out["line_id"] = "line_1"

        if "Folio" not in df_out.columns and "folio" in df_out.columns:
            df_out["Folio"] = df_out["folio"]

        return df_out


if __name__ == "__main__":
    parser = EVAParser()
    sample_tokens = ["qokaiin", "cheol", "dy", "otckey", "daiin"]
    print("=== TEST UNITA' PARSER METODO DEMARIA v3.3 ===")
    for t in sample_tokens:
        print(f"Token: {t:10s} | Pulito: {parser.clean_token(t):10s} | Stato: {parser.classify_token(t)}")
