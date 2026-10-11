#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Modulo: core_parser1.py
Descrizione: Parser vettoriale deterministico Many-to-One per la riduzione dell'alfabeto EVA
             ai 4 stati minimi (Alpha=1, Beta=2, Delta=3, Gamma=4).

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

    def clean_eva_token(self, token: str) -> str:
        """Pulisce il token preservando la stringa EVA canonica."""
        if not isinstance(token, str):
            return ""
        return token.strip().lower()

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
        Elabora il DataFrame del corpus, costruisce in modo vincolante line_id (folio_id + "." + line_number)
        ed assegna a ciascun token sia lo stato numerico [1, 2, 3, 4] che lo stato testuale.
        """
        df_parsed = df.copy()

        # 1. Identificazione e Costruzione Rigida del Folio e Line_ID
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
            # COSTRUTTO VINCOLANTE: folio_id + "." + line_number (es. "f1r.1")
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

        # 3. Assegnazione degli stati
        df_parsed["token"] = df_parsed[token_col]
        df_parsed["cleaned_token"] = df_parsed[token_col].apply(self.clean_eva_token)
        
        # Mappatura numerica deterministica [1, 2, 3, 4]
        df_parsed["numeric_state"] = df_parsed[token_col].apply(self.map_token_to_state)
        
        # 'state' DEVE contenere il valore numerico intero [1, 2, 3, 4] per superare test_parse_dataframe
        df_parsed["state"] = df_parsed["numeric_state"]

        state_names = {1: "Alpha", 2: "Beta", 3: "Delta", 4: "Gamma"}
        df_parsed["state_name"] = df_parsed["numeric_state"].map(state_names)
        df_parsed["assigned_state"] = df_parsed["state_name"]

        return df_parsed


if __name__ == "__main__":
    parser = EVAParser()
    sample_data = pd.DataFrame({
        "Folio": ["f1r.1,+P0", "f1r.1,+P0", "f1r.2,+P0"],
        "Token": ["fachys", "qokaiin", "cheoldy"]
    })
    parsed_df = parser.parse_dataframe(sample_data)
    print("DataFrame Parsato con successo:")
    print(parsed_df[["folio_id", "line_id", "token", "state", "state_name", "assigned_state"]])
