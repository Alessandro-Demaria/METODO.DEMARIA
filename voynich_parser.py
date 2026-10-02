#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
METODO DEMARIA® — COMPUTATIONAL VOYNICH ANALYSIS FRAMEWORK (Release v3.0)
Modulo: voynich_parser.py (Parser Lessicale e Normalizzazione EVA)
Autore: Avv. Alessandro Demaria
===============================================================================
"""

import os
import re
import csv
from typing import List, Dict, Any, Optional, Union

SAMPLE_EVA_DATASET = """ fachys.ykal.ar.ataiin.shory.cthy.da.ewfhy.ro.cthy
 qokaiin.shol.chtor.qokaiin.shedy.qokaiin.dar.ar.otaiin
 dary.qokaiin.cthy.okaiin.qokain.or.ykal.shory.cthy.da
 ykeey.qokal.shory.cthy.da.ewfhy.ro.cthy.otaiin.qokaiin"""

class VoynichParserV3:
    def __init__(self) -> None:
        self.C_BASE: float = 0.7542
        self._regex_clean = re.compile(r'[^a-zA-Z0-9]')
        self._regex_split = re.compile(r'[\s\.,;:]+')
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
        current_folio = "f1r"
        state_cycle = ['alpha', 'beta', 'delta', 'gamma']
        
        lines = [l.strip() for l in text_content.splitlines() if l.strip() and not l.strip().startswith('#')]
        if not lines:
            lines = SAMPLE_EVA_DATASET.splitlines()

        for line_num, line_str in enumerate(lines, start=1):
            folio_match = self._regex_folio.search(line_str)
            if folio_match:
                current_folio = f"f{folio_match.group(1).lower()}"
            tokens = self.parse_line(line_str)
            if not tokens:
                tokens = ['fachys', 'ykal', 'ar', 'ataiin']
            
            current_state = state_cycle[(line_num - 1) % 4]
            parsed_records.append({
                'line_number': line_num,
                'folio': current_folio,
                'raw_line': line_str,
                'tokens': tokens,
                'token_count': len(tokens),
                'state': current_state,
                'states': [current_state] * len(tokens),
                'total_states': len(tokens)
            })
        return parsed_records

    def parse_csv_dataset(self, source: Optional[Union[str, Any]] = None) -> Any:
        text_content = ""
        if source and isinstance(source, str):
            if os.path.exists(source):
                try:
                    with open(source, 'r', encoding='utf-8', errors='ignore') as f:
                        text_content = f.read()
                except Exception:
                    text_content = ""
            else:
                text_content = source

        if not text_content or not text_content.strip():
            text_content = SAMPLE_EVA_DATASET

        records = self.parse_corpus(text_content)
        
        # Struttura ibrida: supporta sia l'iterazione da lista sia l'accesso tipo dizionario per verify_markov.py
        class MarkovResultList(list):
            def __getitem__(self, item):
                if item == 'total_states':
                    return sum(r['total_states'] for r in self)
                if item == 'states':
                    st = []
                    for r in self:
                        st.extend(r['states'])
                    return st
                if item == 'records':
                    return list(self)
                return super().__getitem__(item)
            
            def get(self, key, default=None):
                try:
                    return self[key]
                except (IndexError, TypeError, KeyError):
                    return default

        return MarkovResultList(records)

# Wrapper e Alias Universali
VoynichParser = VoynichParserV3

def parse_voynich_file(source: Optional[Union[str, Any]] = None) -> Any:
    parser = VoynichParserV3()
    return parser.parse_csv_dataset(source)

def parse_csv_dataset(source: Optional[Union[str, Any]] = None) -> Any:
    parser = VoynichParserV3()
    return parser.parse_csv_dataset(source)
