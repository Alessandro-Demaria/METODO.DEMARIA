#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Modulo: core_parser1.py
Descrizione: Parser vettoriale deterministico Many-to-One per la riduzione dell'alfabeto EVA
             ai 4 stati minimi (Alpha=1, Beta=2, Delta=3, Gamma=4).
             Allineamento deterministico per Craw = 0.786597 ed H(X) = 1.683534 bit.

Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
Licenza Codebase: MIT License
"""

import pandas as pd


class EVAParser:
    """
    Parser vettoriale del METODO DEMARIA®.
    Esegue il mapping deterministico dei token EVA sulla quadrupla degli stati minimi:
    - State Alpha (1): Innesco / Margine Sinistro
    - State Beta  (2): Regime / Azione / Attrattore Stazionario
    - State Delta (3): Differenziazione / Modulazione
    - State Gamma (4): Chiusura / Reset / Margine Destro
    """

    STATE_ALPHA = "Alpha"
    STATE_BETA = "Beta"
    STATE_DELTA = "Delta"
    STATE_GAMMA = "Gamma"

    def __init__(self):
        # Mappature simboliche deterministiche della Master Suite v3.3
        self.alpha_prefixes = ("qo", "chol", "chor", "shol", "shor", "y")
        self.gamma_suffixes = ("am", "an", "dy", "edy", "ol", "or", "y")
        self.delta_substrings = ("ch", "sh", "ok", "ot", "ct")

    def map_token_to_state(self, token: str) -> int:
        """
        Mappatura deterministica Many-to-One del singolo token EVA in uno stato numerico [1, 2, 3, 4].
        - 1 = Alpha
        - 2 = Beta
        - 3 = Delta
        - 4 = Gamma
        """
        if not isinstance(token, str) or not token.strip():
            return 2  # State Beta

        token_clean = token.strip().lower()

        # Regola 1: Innesco / Header (State Alpha = 1)
        for prefix in self.alpha_prefixes:
            if token_clean.startswith(prefix):
                return 1

        # Regola 2: Chiusura / Terminale (State Gamma = 4)
        for suffix in self.gamma_suffixes:
            if token_clean.endswith(suffix):
                return 4

        # Regola 3: Differenziazione / Modulazione (State Delta = 3)
        for sub in self.delta_substrings:
            if sub in token_clean:
                return 3

        # Regola 4: Regime Stazionario (State Beta = 2)
        return 2

    def parse_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Elabora il DataFrame del corpus, normalizza le coordinate spaziali line_id
        ed assegna a ciascun token il rispettivo stato vettoriale numerico e testuale.
        """
        df_parsed = df.copy()

        # 1. Identificazione Flessibile della colonna Folio
        folio_col_found = None
        for col in df_parsed.columns:
            if str(col).strip().lower() in ["folio", "folio_id"]:
                folio_col_found = col
                break

        if folio_col_found is not None:
            df_parsed["folio_id"] = df_parsed[folio_col_found].astype(str).apply(lambda x: x.split(".")[0])
            df_parsed["line_number"] = df_parsed[folio_col_found].astype(str).apply(
                lambda x: x.split(".")[1].split(",")[0] if "." in x else "1"
            )
            df_parsed["line_id"] = df_parsed["folio_id"] + "." + df_parsed["line_number"]
            df_parsed["folio"] = df_parsed["folio_id"]
            df_parsed["Folio"] = df_parsed[folio_col_found]
        else:
            raise KeyError("[-] Errore Parser: Colonna 'Folio' o 'folio' non trovata nel DataFrame.")

        # 2. Identificazione Flessibile della colonna Token
        token_col = None
        for col in df_parsed.columns:
            if str(col).strip().lower() in ["token", "eva_token", "eva", "cleaned_token"]:
                token_col = col
                break

        if token_col is None:
            raise KeyError("[-] Errore Parser: Impossibile identificare la colonna dei token EVA.")

        # 3. Mappatura degli stati (state=interi 1..4, state_name/assigned_state=stringhe)
        df_parsed["token"] = df_parsed[token_col]
        df_parsed["state"] = df_parsed[token_col].apply(self.map_token_to_state)

        state_names = {1: "Alpha", 2: "Beta", 3: "Delta", 4: "Gamma"}
        df_parsed["state_name"] = df_parsed["state"].map(state_names)
        df_parsed["assigned_state"] = df_parsed["state_name"]

        return df_parsed


if __name__ == "__main__":
    parser = EVAParser()
    sample_data = pd.DataFrame({
        "Folio": ["f1r.1,+P0", "f1r.1,+P0", "f1r.2,+P0"],
        "Token": ["fachys", "qokaiin", "cheoldy"]
    })
    parsed_df = parser.parse_dataframe(sample_data)
    print("DataFrame Parsato:")
    print(parsed_df[["folio_id", "line_id", "token", "state", "state_name", "assigned_state"]])
