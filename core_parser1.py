#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master-Validato)

Modulo 1: core_parser1.py
Parser deterministico per la classificazione vettoriale dei token EVA
nella quadrupla degli stati topologici minimi (Alpha, Beta, Delta, Gamma).

Sessione di Lavoro: BARVI
Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
Licenza Codebase: MIT License
Tutela Privativa e Marchio: Art. 98 D.Lgs. 30/2005 (CPI) / L. 633/1941
"""

import re
import pandas as pd
from typing import List, Tuple, Dict, Any, Optional


class EVAParser:
    """
    Parser deterministico a regole prioritarie per la riduzione dell'alfabeto EVA
    alla quadrupla degli stati topologici minimi (Alpha, Beta, Delta, Gamma).
    """

    STATE_ALPHA: str = "Alpha"
    STATE_BETA: str = "Beta"
    STATE_DELTA: str = "Delta"
    STATE_GAMMA: str = "Gamma"

    def __init__(self) -> None:
        """
        Inizializza le sequenze grafematiche deterministiche di ancoraggio,
        transizione e chiusura secondo le specifiche convalidate della Release v3.3.
        """
        # Prefissi d'innesco deterministici (State Alpha / Header di Rigo)
        self.alpha_prefixes: Tuple[str, ...] = (
            "qo", "cho", "che", "ch", "sh", "ok", "ot", "ol", "op",
            "po", "to", "so", "do", "y", "q"
        )
        # Suffissi di chiusura deterministici (State Gamma / Reset e Drenaggio)
        self.gamma_suffixes: Tuple[str, ...] = (
            "am", "an", "ain", "in", "al", "or", "ar", "dy", "eedy",
            "ey", "old", "m", "n", "g", "z"
        )
        # Modulatori interni di variazione (State Delta / Differenziazione)
        self.delta_substrings: Tuple[str, ...] = (
            "ck", "ct", "ee", "ii", "iii", "aiin"
        )

    def clean_token(self, token: Any) -> str:
        """
        Rimuove marcatori di incertezza, punteggiatura e caratteri non appartenenti
        all'alfabeto EVA standard.
        """
        if not isinstance(token, str):
            return ""
        # Rimozione marcatori di incertezza transcrizionale ed interpolazione
        cleaned: str = re.sub(r"[!\?\*\.\,\-\=\_]", "", token)
        return cleaned.strip().lower()

    def clean_eva_token(self, token: Any) -> str:
        """
        Alias retro-compatibile per la suite di test unitari (tests_test_parserA.py).
        """
        return self.clean_token(token)

    def classify_token(self, token: Any) -> str:
        """
        Assegna lo stato sintattico vettoriale secondo la gerarchia di precedenza rigida v3.3:
        1. Alpha (Prefisso d'innesco)
        2. Gamma (Suffisso di chiusura)
        3. Delta (Modulatore interno)
        4. Beta  (Stato stazionario residuale / Azione)
        """
        tok: str = self.clean_token(token)
        if not tok:
            return self.STATE_BETA

        # Priorità 1: Prefissi d'Innesco (State Alpha)
        for pfx in self.alpha_prefixes:
            if tok.startswith(pfx):
                return self.STATE_ALPHA

        # Priorità 2: Suffissi di Chiusura (State Gamma)
        for sfx in self.gamma_suffixes:
            if tok.endswith(sfx):
                return self.STATE_GAMMA

        # Priorità 3: Modulatori Interni (State Delta)
        for sub in self.delta_substrings:
            if sub in tok:
                return self.STATE_DELTA

        # Fallback: Stato Stazionario (State Beta)
        return self.STATE_BETA

    def map_token_to_state(self, token: Any) -> str:
        """
        Alias retro-compatibile per la suite di test unitari (tests_test_parserA.py).
        """
        return self.classify_token(token)

    def parse_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Elabora il DataFrame del dataset master e genera le colonne di parsing vettoriale,
        estrapolando rigorosamente l'identificatore di rigo (line_id) e la coordinata di folio.
        """
        df_out: pd.DataFrame = df.copy()

        # Identificazione deterministica della colonna contenente i token EVA
        token_col: Optional[str] = None
        for col in ["token", "eva_token", "EVA_Token", "EVA_token"]:
            if col in df_out.columns:
                token_col = col
                break
        
        if token_col is None:
            # Selezione della prima colonna di tipo testo se nessuna corrispondenza esplicita è trovata
            object_cols = df_out.select_dtypes(include=["object"]).columns
            if len(object_cols) > 0:
                token_col = object_cols[0]
            else:
                token_col = df_out.columns[0]

        # Applicazione della pulizia e della classificazione deterministica
        df_out["cleaned_token"] = df_out[token_col].apply(self.clean_token)
        df_out["assigned_state"] = df_out[token_col].apply(self.classify_token)

        # Gestione ed estrazione rigorosa di line_id e Folio
        if "line_id" not in df_out.columns:
            if "Folio" in df_out.columns and "Line" in df_out.columns:
                df_out["line_id"] = df_out["Folio"].astype(str) + "." + df_out["Line"].astype(str)
            elif "Folio" in df_out.columns:
                df_out["line_id"] = df_out["Folio"].astype(str)
            elif "folio" in df_out.columns:
                df_out["line_id"] = df_out["folio"].astype(str)
            else:
                df_out["line_id"] = "line_1"

        if "Folio" not in df_out.columns and "folio" in df_out.columns:
            df_out["Folio"] = df_out["folio"]
        elif "Folio" not in df_out.columns:
            df_out["Folio"] = df_out["line_id"].apply(lambda x: str(x).split(".")[0] if "." in str(x) else str(x))

        return df_out


if __name__ == "__main__":
    parser_instance = EVAParser()
    print("=== MODULO core_parser1.py (Release v3.3 Audit-Master-Validato) CARICATO ED ESEGUITO ===")
    print(f"Stati Definiti: {[parser_instance.STATE_ALPHA, parser_instance.STATE_BETA, parser_instance.STATE_DELTA, parser_instance.STATE_GAMMA]}")