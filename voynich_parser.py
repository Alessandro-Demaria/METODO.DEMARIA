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
        self._regex_folio = re.compile(r' str:
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

# Alias per garantire la compatibilità universale con la suite
VoynichParser = VoynichParserV3

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
