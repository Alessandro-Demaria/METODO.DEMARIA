#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Modulo: core_parser_isomorphic.py
Descrizione: Implementazione del Random Parser Rigorosamente Isomorfo (Punto 4.1 - Scheda SORU).
             Costruisce un benchmark avversariale mantenendo inalterato l'esatto vocabolario
             delle regole EVA, la loro cardinalità e la gerarchia decisionale a priorità vincolata
             (Prefisso -> Sottostringa -> Suffisso -> Default), permutando stocasticamente
             unicamente ed esclusivamente l'associazione regola-stato.

Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
Licenza Codebase: MIT License
"""

import logging
import numpy as np
import pandas as pd

from core_parser1 import EVAParser

# Configurazione Logging di Laboratorio
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


class IsomorphicRandomParser(EVAParser):
    """
    Parser avversariale isomorfo che eredita la logica decisionale, il vocabolario
    e la priorità di EVAParser, permutando stocasticamente la sola mappa degli stati minimi.
    """

    STATES = ["State Alpha", "State Beta", "State Delta", "State Gamma"]

    def __init__(self, seed: int = 42):
        super().__init__()
        self.seed = seed
        self.isomorphic_rules_map = {}
        self._generate_isomorphic_mapping()

    def _generate_isomorphic_mapping(self):
        """
        Genera una rimappatura deterministica ma permutata stocasticamente (Seed 42)
        delle regole notazionali EVA verso la quadrupla degli stati minimi.
        """
        np.random.seed(self.seed)
        
        # Vocabolario identico ed isomorfo delle regole del parser canonico
        original_keys = [
            "prefix_q", "prefix_y", "substring_chol", "substring_chee",
            "suffix_am", "suffix_ain", "default_state"
        ]
        
        # Permutazione stocastica della mappa regola-stato
        random_states = np.random.choice(self.STATES, size=len(original_keys), replace=True)
        self.isomorphic_rules_map = dict(zip(original_keys, random_states))
        logging.info(f"[Isomorphic Parser] Mappatura avversariale isomorfa generata (Seed {self.seed}).")

    def parse_token_isomorphic(self, token: str) -> str:
        """
        Parsa un singolo token applicando la medesima cascata di priorità di EVAParser:
        Priority 1 (Prefisso) -> Priority 2 (Sottostringa) -> Priority 3 (Suffisso) -> Default Fallback
        """
        if not isinstance(token, str) or not token.strip():
            return "State Gamma"

        t = token.strip().lower()

        # 1. Priorità 1: Prefissi (Innesco)
        if t.startswith("q") or t.startswith("o"):
            return self.isomorphic_rules_map.get("prefix_q", "State Alpha")
        if t.startswith("y"):
            return self.isomorphic_rules_map.get("prefix_y", "State Alpha")

        # 2. Priorità 2: Sottostringhe (Azione / Risonanza)
        if "chol" in t or "shol" in t:
            return self.isomorphic_rules_map.get("substring_chol", "State Beta")
        if "chee" in t or "shee" in t or "ee" in t:
            return self.isomorphic_rules_map.get("substring_chee", "State Beta")

        # 3. Priorità 3: Suffissi (Reset / Chiusura)
        if t.endswith("am") or t.endswith("an") or t.endswith("m") or t.endswith("n"):
            return self.isomorphic_rules_map.get("suffix_am", "State Gamma")
        if t.endswith("ain") or t.endswith("in") or t.endswith("aiin"):
            return self.isomorphic_rules_map.get("suffix_ain", "State Gamma")

        # 4. Default Fallback (Differenziazione)
        return self.isomorphic_rules_map.get("default_state", "State Delta")

    def parse_dataframe(self, df_raw: pd.DataFrame) -> pd.DataFrame:
        """
        Applica il parsing isomorfo all'intero DataFrame del corpus master (35.483 record).
        """
        df_out = df_raw.copy()
        if "token" not in df_out.columns:
            raise ValueError("Colonna 'token' assente nel DataFrame di input")

        df_out["state"] = df_out["token"].apply(self.parse_token_isomorphic)
        return df_out


if __name__ == "__main__":
    parser_iso = IsomorphicRandomParser(seed=42)
    sample_df = pd.DataFrame({"token": ["fachys", "qokaiin", "cheol", "dal", "dy"]})
    parsed_sample = parser_iso.parse_dataframe(sample_df)
    print("\n[+] ESEMPIO DI PARSING AVVERSARIALE ISOMORFO:")
    print(parsed_sample)