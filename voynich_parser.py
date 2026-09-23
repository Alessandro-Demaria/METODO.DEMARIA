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
        # Pattern di pulizia metadati ed incertezze editoriali EVA/IVTFF
        self.meta_pattern = re.compile(r'<[^>]+>')
        self.comment_pattern = re.compile(r'\{[^}]+\}')
        self.uncertainty_pattern = re.compile(r'
