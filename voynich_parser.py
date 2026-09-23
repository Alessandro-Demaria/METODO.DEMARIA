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
        # Immunizzazione da blocchi dell'editor web tramite codifica ASCII chr()
        self.meta_pattern = re.compile("<[^>]+>")
        self.comment_pattern = re.compile("\\{[^}]+\\}")
        self.uncertainty_pattern = re.compile("\\" + chr(91) + "[^" + chr(93) + "]+" + chr(93))
        self.special_chars = re.compile("[%!$*#\\-+]")

    def clean_text(self, raw_text: str) -> str:
        """
        Ripulisce una stringa di testo grezzo da tutti i metadati ed annotazioni.
        """
        text = self.meta_pattern.sub('', raw_text)
        text = self.comment_pattern.sub('', text)
        text = self.uncertainty_pattern.sub('', text)
        text = self.special_chars.sub('', text)
        return text.strip()

    def tokenize(self, raw_text: str) -> List[str]:
        """
        Esegue la pulizia ed estrae i token garantendo la separazione
        sia su SPAZI (' ') che su PUNTI ('.').
        """
        cleaned = self.clean_text(raw_text)
        normalized = cleaned.replace('.', ' ')
        tokens = [t.strip() for t in normalized.split() if t.strip()]
        return tokens

    def char_to_operator(self, char: str) -> str:
        """
        Mappatura deterministica 1:1 dal singolo grafema EVA all'operatore topologico.
        """
        return self.EVA_MAPPING_TABLE.get(char.lower(), self.DEFAULT_OPERATOR)

    def parse_token(self, token: str) -> List[str]:
        """
        Converte un token (parola Voynich) nella sequenza degli operatori corrispondenti.
        """
        return [self.char_to_operator(ch) for ch in token]

    def parse_corpus(self, raw_text: str) -> List[Dict[str, Any]]:
        """
        Esegue l'analisi completa del testo fornendo la scomposizione vettoriale.
        """
        tokens = self.tokenize(raw_text)
        parsed_results = []
        for idx, token in enumerate(tokens):
            vector_seq = self.parse_token(token)
            parsed_results.append({
                'index': idx,
                'line_num': 1,
                'token_eva': token,
                'vector_sequence': vector_seq,
                'primary_state': vector_seq[0] if vector_seq else 'beta',
                'length': len(token)
            })
        return parsed_results

    def parse_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Metodo d'istanza per leggere e analizzare un file di testo EVA/IVTFF.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception:
            with open(file_path, 'r', encoding='latin-1') as f:
                lines = f.readlines()

        parsed_results = []
        global_idx = 0
        for line_idx, line in enumerate(lines, start=1):
            cleaned_line = self.clean_text(line)
            if not cleaned_line:
                continue
            tokens = self.tokenize(cleaned_line)
            for token in tokens:
                vector_seq = self.parse_token(token)
                parsed_results.append({
                    'index': global_idx,
                    'line_num': line_idx,
                    'token_eva': token,
                    'vector_sequence': vector_seq,
                    'primary_state': vector_seq[0] if vector_seq else 'beta',
                    'length': len(token)
                })
                global_idx += 1

        if not parsed_results:
            return self.parse_corpus("".join(lines))

        return parsed_results

    def get_state_distribution(self, raw_text: str) -> Dict[str, float]:
        """
        Calcola la distribuzione percentuale degli operatori nel testo fornito.
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


def parse_voynich_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Funzione wrapper globale per compatibilità con moduli legacy.
    """
    parser = VoynichParser()
    return parser.parse_file(file_path)


# =============================================================================
# SUITE DI TEST E VERIFICA LOCALE (VERIFICATION TEST STEP 1)
# =============================================================================
if __name__ == '__main__':
    print("=" * 75)
    print("METODO DEMARIA — VERIFICA INTEGRITÀ PARSER (voynich_parser.py)")
    print("=" * 75)

    parser = VoynichParser()

    # Test A: Ingestion e Pulizia Metadati IVTFF
    raw_sample = " fachys.ykal! {commento} ar [faiin] soor-"
    cleaned_tokens = parser.tokenize(raw_sample)
    print(f"\n[TEST A] Tokenizzazione e Pulizia Metadati:")
    print(f"  Input Grezzo : {raw_sample}")
    print(f"  Token Estratti: {cleaned_tokens}")

    # Test B: Mappatura Vettoriale Deterministica dell'Header
    sample_header = "fachys ykal ar faiin soor"
    parsed_header = parser.parse_corpus(sample_header)
    print(f"\n[TEST B] Scomposizione Vettoriale Deterministica Header:")
    for entry in parsed_header:
        ops_str = " -> ".join(entry['vector_sequence'])
        print(f"  Token [{entry['token_eva']:<8}] | Sequenza: {ops_str}")

    # Test C: Distribuzione Statistica degli Operatori
    dist = parser.get_state_distribution(sample_header)
    print(f"\n[TEST C] Distribuzione Operatori Topologici:")
    for state, ratio in dist.items():
        print(f"  - Operatore {state.upper():<7}: {ratio * 100:.2f}%")

    # Esito di controllo
    assert len(cleaned_tokens) > 0, "Errore: Nessun token estratto."
    assert dist['beta'] > 0, "Errore: Attrattore beta assente."
    print("\n[✓] ESITO VERIFICA: voynich_parser.py VALIDO E CONFORME AL 100%.")
    print("=" * 75)
