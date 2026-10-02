#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
METODO DEMARIA® — COMPUTATIONAL VOYNICH ANALYSIS FRAMEWORK (Release v3.0)
Modulo: voynich_parser.py (Parser Lessicale e Normalizzazione EVA)
Autore: Avv. Alessandro Demaria
===============================================================================
"""

import re
import csv
from typing import List, Dict, Any, Tuple

class VoynichParserV3:
    """
    PARSER LESSICALE VOYNICH (Release v3.0)
    Esegue il parsing, la tokenizzazione e la pulizia del testo EVA grezzo.
    """
    def __init__(self):
        self.C_BASE = 0.7542
        self._regex_clean = re.compile(r'[^a-zA-Z0-9]')
        self._regex_split = re.compile(r'[\s\.]+')
        # Escape unicode \x3c (<) e \x3e (>) per stabilita di rendering
        self._regex_folio = re.compile(r'\x3cf(\d+[rv])', re.IGNORECASE)

    def clean_token(self, token: str) -> str:
        if not token:
            return ""
        return self._regex_clean.sub('', str(token).lower().strip())

    def parse_line(self, line: str) -> List[str]:
        if not line or line.startswith('#'):
            return []
        raw_tokens = self._regex_split.split(line.strip())
        return [c for t in raw_tokens if (c := self.clean_token(t))]

    def parse_corpus(self, text_content: str) -> List[Dict[str, Any]]:
        parsed_records = []
        current_folio = "UNKNOWN"
        for line_num, line in enumerate(text_content.splitlines(), start=1):
            line_str = line.strip()
            if not line_str:
                continue
            folio_match = self._regex_folio.search(line_str)
            if folio_match:
                current_folio = f"f{folio_match.group(1).lower()}"
            tokens = self.parse_line(line_str)
            if tokens:
                parsed_records.append({
                    'line_number': line_num,
                    'folio': current_folio,
                    'raw_line': line_str,
                    'tokens': tokens,
                    'token_count': len(tokens)
                })
        return parsed_records

    def parse_csv_dataset(self, csv_path: str) -> List[Dict[str, Any]]:
        """Legge e parsed un dataset EVA in formato CSV o testo puro."""
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return self.parse_corpus(content)
        except Exception as e:
            print(f"[ERROR] Impossibile leggere {csv_path}: {e}")
            return []

# Alias di compatibilità universale
VoynichParser = VoynichParserV3

def parse_voynich_file(file_path: str) -> List[Dict[str, Any]]:
    """Funzione di compatibilita usata dagli script di verifica (es. verify_markov.py)"""
    parser = VoynichParserV3()
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return parser.parse_corpus(content)

def parse_csv_dataset(csv_path: str) -> List[Dict[str, Any]]:
    """Funzione standalone di compatibilita per dataset CSV."""
    parser = VoynichParserV3()
    return parser.parse_csv_dataset(csv_path)

if __name__ == "__main__":
    print("=" * 80)
    print(" METODO DEMARIA® — VOYNICH PARSER V3.0 (PERFORMANCE 100% OK)")
    print("=" * 80)
    sample_text = " fachys.ykal.ar.ataiin.shory.cthy.da.ewfhy.ro.cthy"
    parser = VoynichParserV3()
    records = parser.parse_corpus(sample_text)
    if records:
        print(f"Folio Identificato : {records[0]['folio']}")
        print(f"Token Estratti    : {records[0]['tokens']}")
        print(f"Numero di Token   : {records[0]['token_count']}")
    print("=" * 80)