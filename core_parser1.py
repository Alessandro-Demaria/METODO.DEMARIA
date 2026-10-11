#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Modulo 1: core_parser1.py
Parser deterministico per trascrizioni EVA (IVTFF) e mappatura vettoriale
sulla quadrupla degli stati minimi (Alpha, Beta, Delta, Gamma).

Autore: Avv. Alessandro Demaria
Licenza Codebase: MIT License
Tutela Privativa e Marchio: Art. 98 D.Lgs. 30/2005 (CPI) / L. 633/1941
"""

import re
import pandas as pd
from typing import Dict, List, Tuple, Optional


class EVAParser:
    """
    Parser deterministico dell'alfabeto e della notazione EVA (European Voynich Alphabet)
    in formato IVTFF, deputato alla trasformazione simbolico-vettoriale dei token
    nella quadrupla degli stati minimi topologici (Alpha, Beta, Delta, Gamma).
    """

    # Definizione congelata dei gruppi di caratteri EVA e delle regole di prefisso/suffisso
    ALPHA_TRIGGERS: Tuple[str, ...] = ("qo", "cho", "cho", "cht", "da", "so")
    GAMMA_TERMINATORS: Tuple[str, ...] = ("am", "al", "or", "ar", "dy", "ed", "ey")
    DELTA_MODULATORS: Tuple[str, ...] = ("sh", "ch", "ok", "ot", "ct")

    STATE_ALPHA: str = "Alpha"
    STATE_BETA: str = "Beta"
    STATE_DELTA: str = "Delta"
    STATE_GAMMA: str = "Gamma"

    def __init__(self, target_distribution: Optional[Dict[str, float]] = None) -> None:
        """
        Inizializza il parser congelando la baseline delle distribuzioni teoriche di targa.
        """
        self.target_distribution: Dict[str, float] = target_distribution or {
            self.STATE_ALPHA: 10.00,
            self.STATE_BETA: 54.99,
            self.STATE_DELTA: 19.51,
            self.STATE_GAMMA: 15.50
        }

    @staticmethod
    def clean_eva_token(token_raw: str) -> str:
        """
        Rimuove i marcatori di incertezza, i commenti e i caratteri speciali del formato IVTFF.
        """
        if not isinstance(token_raw, str):
            return ""
        # Rimuove note tra parentesi quadre/graffe e caratteri di dubbia lettura
        cleaned: str = re.sub(r"\[.*?\]|\{.*?\}|\!|\?|\*|\$", "", token_raw.strip())
        return cleaned.lower()

    @classmethod
    def map_token_to_state(cls, token: str) -> str:
        """
        Mappatura deterministica molti-a-uno dal token EVA allo stato topologico minimo.
        
        Regole di precedenza:
        1. Alpha (Innesco/Header): Se il token inizia con prefissi specifici di innesco.
        2. Gamma (Reset/Chiusura): Se il token termina con suffissi di scarico/sincronizzazione.
        3. Delta (Modulatore): Se il token contiene strutture grafemiche intermedie varianti.
        4. Beta (Azione/Resonance): Attrattore stazionario predefinito (Stato di Regime).
        """
        token_clean = cls.clean_eva_token(token)
        if not token_clean:
            return cls.STATE_BETA

        # Check 1: Prefissi d'Innesco (State Alpha)
        for prefix in cls.ALPHA_TRIGGERS:
            if token_clean.startswith(prefix):
                return cls.STATE_ALPHA

        # Check 2: Suffissi di Chiusura (State Gamma)
        for suffix in cls.GAMMA_TERMINATORS:
            if token_clean.endswith(suffix):
                return cls.STATE_GAMMA

        # Check 3: Modulatori di Variazione (State Delta)
        for mod in cls.DELTA_MODULATORS:
            if mod in token_clean:
                return cls.STATE_DELTA

        # Default: Attrattore Stazionario di Regime (State Beta)
        return cls.STATE_BETA

    def parse_dataframe(self, df_raw: pd.DataFrame) -> pd.DataFrame:
        """
        Elabora il DataFrame grezzo, garantendo l'estrazione e la creazione dinamica
        delle colonne 'folio', 'line_id' e 'assigned_state'.
        """
        df: pd.DataFrame = df_raw.copy()

        # Normalizzazione nomi colonne
        df.columns = [c.strip() for c in df.columns]

        # Individuazione colonna token EVA
        token_col: Optional[str] = None
        for col_name in ["EVA_Token", "eva_token", "Token", "token"]:
            if col_name in df.columns:
                token_col = col_name
                break

        if not token_col:
            raise KeyError("Impossibile individuare la colonna contenente i token EVA nel dataset.")

        # Generazione o estrazione dinamica di Folio e Line_ID
        if "Folio" in df.columns:
            df["folio"] = df["Folio"].astype(str).str.lower().str.strip()
        elif "folio" not in df.columns:
            df["folio"] = "f1r"  # Fallback di sicurezza

        if "Line_ID" in df.columns:
            df["line_id"] = df["Line_ID"].astype(str).str.strip()
        elif "line_id" not in df.columns:
            if "Line" in df.columns:
                df["line_id"] = df["folio"] + "_" + df["Line"].astype(str).str.strip()
            elif "Record_ID" in df.columns:
                # Ricostruzione line_id da Record_ID o raggruppamento
                df["line_id"] = df["folio"] + "_l1"
            else:
                df["line_id"] = df["folio"] + "_l0"

        # Mappatura deterministica degli stati
        df["EVA_Token_Clean"] = df[token_col].apply(self.clean_eva_token)
        df["assigned_state"] = df["EVA_Token_Clean"].apply(self.map_token_to_state)

        return df


if __name__ == "__main__":
    # Test unitario rapido di esecuzione isolata
    parser = EVAParser()
    test_tokens = ["qokaiin", "chodaiin", "otaiin", "chodin", "dy", "or", "shol"]
    print("=== TEST UNITARIO CORE_PARSER1 ===")
    for t in test_tokens:
        st = parser.map_token_to_state(t)
        print(f"Token EVA: '{t:10s}' -> Stato Assegnato: {st}")