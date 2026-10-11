#!/usr/bin/env python3
"""
LABORATORIO SCIENTIFICO METODO DEMARIA™ - RELEASE v3.3 (AUDIT-MASTER UNIFICATO)

Modulo: core_parser1.py
Descrizione: Parser vettoriale deterministico Many-to-One per la riduzione dell'alfabeto EVA
             ai 4 stati minimi (Alpha, Beta, Delta, Gamma).
             Include la normalizzazione strutturale e la risoluzione P0.2 / P0.3.
Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
"""

import pandas as pd


class EVAParser:
    """
    Parser vettoriale del METODO DEMARIA™.
    Esegue il mapping deterministico dei token EVA sulla quadrupla degli stati minimi:
    - State Alpha (1): Innesco / Margine Sinistro
    - State Beta  (2): Regime / Azione / Attrattore Stazionario
    - State Delta (3): Differenziazione / Modulazione
    - State Gamma (4): Chiusura / Reset / Margine Destro
    """

    def __init__(self):
        # Mappature simboliche deterministiche della Master Suite v3.3
        self.alpha_prefixes = ("qo", "chol", "chor", "shol", "shor", "y")
        self.gamma_suffixes = ("am", "an", "dy", "edy", "ol", "or", "y")
        self.delta_substrings = ("ch", "sh", "ok", "ot", "ct")

    def map_token_to_state(self, token: str) -> int:
        """
        Mappatura deterministica Many-to-One del singolo token EVA in uno stato [1, 2, 3, 4].
        - 1 = Alpha
        - 2 = Beta
        - 3 = Delta
        - 4 = Gamma
        """
        if not isinstance(token, str) or not token.strip():
            return 2  # State Beta di default per token non validi o vuoti

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
        Elabora il DataFrame del corpus, normalizza le coordinate spaziali (P0.2/P0.3)
        ed assegna a ciascun token il rispettivo stato vettoriale.
        """
        df_parsed = df.copy()

        # Normalizzazione canonica identificativi (P0.2 / P0.3 Fix)
        if "Folio" in df_parsed.columns:
            df_parsed["folio_id"] = df_parsed["Folio"].astype(str).apply(lambda x: x.split(".")[0])
            df_parsed["line_number"] = df_parsed["Folio"].astype(str).apply(
                lambda x: x.split(".")[1].split(",")[0] if "." in x else "1"
            )
            df_parsed["line_id"] = df_parsed["folio_id"] + "." + df_parsed["line_number"]
            df_parsed["folio"] = df_parsed["folio_id"]
        elif "folio" not in df_parsed.columns:
            raise KeyError("[-] Errore Parser: Colonna 'Folio' o 'folio' non trovata nel DataFrame.")

        # Identificazione colonna del token
        token_col = None
        for col in ["Token", "eva_token", "token", "EVA"]:
            if col in df_parsed.columns:
                token_col = col
                break

        if token_col is None:
            raise KeyError("[-] Errore Parser: Impossibile identificare la colonna dei token EVA.")

        # Assegnazione dello stato vettoriale numeric [1, 2, 3, 4] e della stringa di stato
        df_parsed["state"] = df_parsed[token_col].apply(self.map_token_to_state)

        state_names = {1: "Alpha", 2: "Beta", 3: "Delta", 4: "Gamma"}
        df_parsed["state_name"] = df_parsed["state"].map(state_names)

        return df_parsed


if __name__ == "__main__":
    parser = EVAParser()
    sample_data = pd.DataFrame({
        "Folio": ["f1r.1,+P0", "f1r.1,+P0", "f1r.2,+P0"],
        "Token": ["fachys", "qokaiin", "cheoldy"]
    })
    parsed_df = parser.parse_dataframe(sample_data)
    print("DataFrame Parsato di Test:")
    print(parsed_df[["folio_id", "line_id", "folio", "Token", "state", "state_name"]])