#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Modulo: core_parser1.py
Descrizione: Parser vettoriale deterministico Many-to-One per la riduzione dell'alfabeto EVA
             ai 4 stati minimi (Alpha, Beta, Delta, Gamma).

Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
Licenza Codebase: MIT License
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

    STATE_ALPHA = "Alpha"
    STATE_BETA = "Beta"
    STATE_DELTA = "Delta"
    STATE_GAMMA = "Gamma"

    def __init__(self):
        self.alpha_prefixes = ("qo", "chol", "chor", "shol", "shor", "y")
        self.gamma_suffixes = ("am", "an", "dy", "edy", "ol", "or", "y")
        self.delta_substrings = ("ch", "sh", "ok", "ot", "ct")

    @staticmethod
    def clean_eva_token(token: str) -> str:
        """Pulisce il token EVA rimuovendo caratteri speciali e punteggiatura esogena."""
        if not isinstance(token, str):
            return ""
        cleaned = token.strip().lower()
        for char in ["!", "*", "?", ".", ",", "-"]:
            cleaned = cleaned.replace(char, "")
        return cleaned

    def map_token_to_state(self, token: str) -> str:
        """
        Mappatura deterministica Many-to-One del singolo token EVA restituendo la stringa di stato.
        """
        token_clean = self.clean_eva_token(token)
        if not token_clean:
            return self.STATE_BETA

        for prefix in self.alpha_prefixes:
            if token_clean.startswith(prefix):
                return self.STATE_ALPHA

        for suffix in self.gamma_suffixes:
            if token_clean.endswith(suffix):
                return self.STATE_GAMMA

        for sub in self.delta_substrings:
            if sub in token_clean:
                return self.STATE_DELTA

        return self.STATE_BETA

    def parse_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Elabora il DataFrame del corpus, pulisce i token ed assegna gli stati vettoriali.
        """
        df_parsed = df.copy()

        if "Folio" in df_parsed.columns:
            df_parsed["folio_id"] = df_parsed["Folio"].astype(str).apply(lambda x: x.split(".")[0])
            df_parsed["line_number"] = df_parsed["Folio"].astype(str).apply(
                lambda x: x.split(".")[1].split(",")[0] if "." in x else "1"
            )
            df_parsed["line_id"] = df_parsed["folio_id"] + "." + df_parsed["line_number"]
            df_parsed["folio"] = df_parsed["folio_id"]

        token_col = None
        for col in ["Token", "eva_token", "token", "EVA"]:
            if col in df_parsed.columns:
                token_col = col
                break

        if token_col is None:
            raise KeyError("[-] Errore Parser: Impossibile identificare la colonna dei token EVA.")

        df_parsed["cleaned_token"] = df_parsed[token_col].apply(self.clean_eva_token)
        df_parsed["assigned_state"] = df_parsed["cleaned_token"].apply(self.map_token_to_state)

        # Mappatura numerica equivalente per la suite
        state_to_num = {self.STATE_ALPHA: 1, self.STATE_BETA: 2, self.STATE_DELTA: 3, self.STATE_GAMMA: 4}
        df_parsed["state"] = df_parsed["assigned_state"].map(state_to_num)
        df_parsed["state_name"] = df_parsed["assigned_state"]

        return df_parsed


if __name__ == "__main__":
    parser = EVAParser()
    sample_df = pd.DataFrame({"Folio": ["f1r.1,+P0"], "Token": ["qokaiin!"]})
    out_df = parser.parse_dataframe(sample_df)
    print("Test Parser completato:", out_df[["cleaned_token", "assigned_state", "state"]])
