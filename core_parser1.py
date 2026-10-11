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
        # Mappatura deterministica dei prefissi d'innesco (Header / State Alpha)
        self.alpha_prefixes = (
            "qo", "cho", "che", "ch", "sh", "ok", "ot", "ol", "op",
            "po", "to", "so", "do", "y", "q"
        )
        
        # Mappatura deterministica dei suffissi di chiusura/reset (Reset / State Gamma)
        self.gamma_suffixes = (
            "am", "an", "ain", "in", "al", "or", "ar", "dy", "eedy",
            "ey", "old", "m", "n", "g", "z"
        )

        # Mappatura dei modulatori interni di variazione (Modulatori / State Delta)
        self.delta_substrings = ("ck", "ct", "ee", "ii", "iii", "aiin")

    def clean_token(self, token: str) -> str:
        """Rimuove marcatori di incertezza e caratteri non appartenenti all'alfabeto EVA."""
        if not isinstance(token, str):
            return ""
        # Rimozione dei caratteri speciali paleografici e marcatori IVTFF
        cleaned = re.sub(r"[!\?\*\.\,\-\=\_]", "", token).strip().lower()
        return cleaned

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

        # Rule 1: Alpha Check (Innesco)
        for pfx in self.alpha_prefixes:
            if tok.startswith(pfx):
                return self.STATE_ALPHA

        # Rule 2: Gamma Check (Chiusura/Reset)
        for sfx in self.gamma_suffixes:
            if tok.endswith(sfx):
                return self.STATE_GAMMA

        # Rule 3: Delta Check (Modulazione interna)
        for sub in self.delta_substrings:
            if sub in tok:
                return self.STATE_DELTA

        # Rule 4: Beta (Stato stazionario di regime)
        return self.STATE_BETA

    def parse_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Elabora il DataFrame del dataset master e genera le colonne
        di parsing vettoriale, distinguendo tra identificatore rigo e folio fisico.
        """
        df_out = df.copy()

        # Identificazione colonna token
        token_col = "token" if "token" in df_out.columns else "eva_token"
        if token_col not in df_out.columns:
            # Fallback sulla prima colonna di tipo testo
            token_col = df_out.select_dtypes(include=["object"]).columns[0]

        # Applicazione della classificazione vettoriale
        df_out["cleaned_token"] = df_out[token_col].apply(self.clean_token)
        df_out["assigned_state"] = df_out[token_col].apply(self.classify_token)

        # Gestione formale e separata dell'identificatore di rigo (line_id)
        if "line_id" not in df_out.columns:
            if "folio" in df_out.columns:
                df_out["line_id"] = df_out["folio"].astype(str)
            else:
                df_out["line_id"] = "line_1"

        return df_out


if __name__ == "__main__":
    parser = EVAParser()
    sample = ["qokaiin", "cheol", "dy", "otckey", "daiin"]
    print("Test Classificazione Parser v3.3:")
    for t in sample:
        print(f"Token: {t:10s} -> State: {parser.classify_token(t)}")
