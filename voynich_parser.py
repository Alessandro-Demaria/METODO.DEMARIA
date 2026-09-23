#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
METODO DEMARIA — COMPUTATIONAL VOYNICH ANALYSIS FRAMEWORK (v2.02)
Modulo: voynich_parser.py
Autore: Alessandro Demaria
Repository: GitHub - METODO.DEMARIA
Zenodo DOI: 10.5281/zenodo.22856418
===============================================================================
Descrizione:
  Parser ad alta precisione e vettore di tokenizzazione deterministica.
  Converte i grafemi EVA negli operatori topologici (alpha, beta, delta, gamma).
===============================================================================
"""

import re
from typing import List, Dict, Any


class VoynichParser:
    """
    Parser deterministico 1:1 dai grafemi EVA agli operatori topologici.
    """

    # Tabella di Mapping Deterministica Univoca EVA -> Operatore Topologico
    EVA_MAPPING_TABLE: Dict[str, str] = {
        'f': 'alpha', 'p': 'alpha', 't': 'alpha', 'k': 'alpha',
        'o': 'beta',  'a': 'beta',  'e': 'beta',  'i': 'beta',  'c': 'beta', 'h': 'beta',
        'r': 'delta', 's': 'delta', 'l': 'delta', 'd': 'delta', 'x': 'delta',
        'm': 'gamma', 'g': 'gamma', 'y': 'gamma', 'q': 'gamma', 'n': 'gamma'
    }

    DEFAULT_OPERATOR: str = 'beta'

    def __init__(self):
        # Clean regex patterns (compatibili con editor web)
        self.meta_pattern = re.compile(r'<[^>]+>')
        self.comment_pattern = re.compile(r'\{[^}]+\}')
        self.special_chars = re.compile(r'[%!$*#\-+]')

    def clean_text(self, raw_text: str) -> str:
        """
        Rimuove metadati, annotazioni e caratteri speciali dal testo grezzo.
        """
        text = self.meta_pattern.sub('', raw_text)
        text = self.comment_pattern.sub('', text)
        text = self.special_chars.sub('', text)
        return text.strip()

    def tokenize(self, raw_text: str) -> List[str]:
        """
        Pulisce e tokenizza il testo separando su spazi e punti.
        """
        cleaned = self.clean_text(raw_text)
        normalized = cleaned.replace('.', ' ')
        return [t.strip() for t in normalized.split() if t.strip()]

    def char_to_operator(self, char: str) -> str:
        """
        Mappatura deterministica del singolo grafema EVA.
        """
        return self.EVA_MAPPING_TABLE.get(char.lower(), self.DEFAULT_OPERATOR)

    def parse_token(self, token: str) -> List[str]:
        """
        Traduce un token nella sequenza di operatori topologici.
        """
        return [self.char_to_operator(ch) for ch in token]

    def parse_corpus(self, raw_text: str) -> List[Dict[str, Any]]:
        """
        Scomposizione vettoriale dell'intero corpus/rigo.
        """
        tokens = self.tokenize(raw_text)
        parsed_results = []
        for idx, token in enumerate(tokens):
            vector_seq = self.parse_token(token)
            parsed_results.append({
                'index': idx,
                'token_eva': token,
                'vector_sequence': vector_seq,
                'primary_state': vector_seq[0] if vector_seq else self.DEFAULT_OPERATOR,
                'length': len(token)
            })
        return parsed_results

    def get_state_distribution(self, raw_text: str) -> Dict[str, float]:
        """
        Calcola la distribuzione statistica degli operatori nel testo.
        """
        parsed_data = self.parse_corpus(raw_text)
        counts = {'alpha': 0, 'beta': 0, 'delta': 0, 'gamma': 0}
        total_ops = 0

        for entry in parsed_data:
            for op in entry['vector_sequence']:
                if op in counts:
                    counts[op] += 1
                    total_ops += 1

        if total_ops == 0:
            return {k: 0.0 for k in counts}

        return {k: round(v / total_ops, 4) for k, v in counts.items()}


if __name__ == '__main__':
    parser = VoynichParser()
    sample = " fachys.ykal! ar faiin soor"
    tokens = parser.tokenize(sample)
    parsed = parser.parse_corpus(sample)
    dist = parser.get_state_distribution(sample)
    
    print(f"Token estratti: {len(tokens)}")
    print(f"Distribuzione Beta: {dist['beta'] * 100:.2f}%")
    assert len(tokens) > 0, "Errore Tokenizzazione"
    assert dist['beta'] > 0, "Errore Attrattore Beta"
    print("VERIFICA LOCALE SUPERATA CON SUCCESSO.")
