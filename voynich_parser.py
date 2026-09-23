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
  Parser ad alta precisione per trascrizioni in formato EVA/IVTFF.
  Esegue la pulizia dei metadati ed applica la mappatura deterministica univoca
  dai grafemi EVA ai 4 operatori topologici dello spazio degli stati:
    - ANCHOR (alpha): Inizializzazione e ancoraggio di stato
    - ACTION (beta): Esecuzione del carico e attrattore di scorrimento
    - DIFFERENTIAL (delta): Retroazione differenziale e correzione di flusso
    - RESET (gamma): Routine di azzeramento e scarico
===============================================================================
"""

import re
from typing import List, Dict, Any


class VoynichParser:
    """
    Parser ad alta precisione e vettore di tokenizzazione per il Metodo Demaria.
    """

    # Tabella di Mapping Deterministica Univoca EVA -> Operatore Topologico
    EVA_MAPPING_TABLE: Dict[str, str] = {
        # Anchor (alpha) - Gallows e vettori d'innesco
        'f': 'alpha', 'p': 'alpha', 't': 'alpha', 'k': 'alpha',
        # Action (beta) - Scorrimento dinamico e attrattore primario
        'o': 'beta',  'a': 'beta',  'e': 'beta',  'i': 'beta',  'c': 'beta', 'h': 'beta',
        # Differential (delta) - Retroazione e correzione intermedia
        'r': 'delta', 's': 'delta', 'l': 'delta', 'd': 'delta', 'x': 'delta',
        # System Reset (gamma) - Routine di scarico e terminatori caudali
        'm': 'gamma', 'g': 'gamma', 'y': 'gamma', 'q': 'gamma', 'n': 'gamma'
    }

    DEFAULT_OPERATOR: str = 'beta'

    def __init__(self):
        # Pattern di pulizia metadati ed incertezze editoriali EVA/IVTFF
        self.meta_pattern = re.compile(r'<[^>]+>')
        self.comment_pattern = re.compile(r'\{[^}]+\}')
        self.uncertainty_pattern = re.compile(r'
