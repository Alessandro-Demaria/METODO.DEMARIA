"""
METODO DEMARIA - VETTORE DI PARSING E TOKENIZZAZIONE
Modulo: voynich_parser.py
Verifica di Conformita: 22/09/2026 - Versione Ultra-Accurata v2.0.2

Descrizione:
  Esegue la pulizia dei metadati editoriali EVA ed estrae i token
  garantendo la corretta separazione sia su SPAZI (' ') che su PUNTI ('.').
  Rimuove commenti, marcatura di pagina, incertezze editoriali e simboli speciali.
"""

import re
from typing import List, Dict, Any


class VoynichParser:
    """
    Parser ad alta precisione per trascrizioni in formato EVA (Extensible Text Format).
    """

    def __init__(self):
        # Utilizzo di codifica esadecimale per evitare blocchi dell'editor web di GitHub
        self.meta_pattern = re.compile(r'<[^>]+>')
        self.comment_pattern = re.compile(r'\{[^}]+\}')
        self.uncertainty_pattern = re.compile(r'\x5b[^\x5d]+\x5d')
        self.special_chars = re.compile(r'[%!$?*@#-]+')

    def clean_text(self, raw_text: str) -> str:
        """
        Ripulisce una stringa di testo grezzo da tutti i metadati ed annotazioni.
        """
        text = self.meta_pattern.sub('', raw_text)
        text = self.comment_pattern.sub('', text)
        text = self.uncertainty_pattern.sub('', text)
        text = self.special_chars.sub('', text)
        return text.strip()

    def tokenize_line(self, raw_line: str) -> List[str]:
        """
        Esegue la tokenizzazione esatta dividendo la riga pulita sia su SPAZI che su PUNTI.
        """
        cleaned = self.clean_text(raw_line)
        if not cleaned:
            return []
        
        normalized_line = cleaned.replace('.', ' ')
        tokens = [token.strip() for token in normalized_line.split() if token.strip()]
        return tokens

    def parse_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Legge il file di trascrizione ed estrae la struttura righe con ID e token.
        """
        records = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, start=1):
                    line_str = line.strip()
                    if not line_str or line_str.startswith('#'):
                        continue
                    
                    line_id = f"L{line_num}"
                    id_match = re.search(r'<([^>]+)>', line_str)
                    if id_match:
                        line_id = id_match.group(1)

                    tokens = self.tokenize_line(line_str)
                    if tokens:
                        records.append({
                            'line_num': line_num,
                            'line_id': line_id,
                            'raw_text': line_str,
                            'tokens': tokens,
                            'token_count': len(tokens)
                        })
        except Exception as e:
            raise IOError(f"Errore durante la lettura del file {file_path}: {str(e)}")
            
        return records


def parse_voynich_file(file_path: str = "voynich_eva.txt") -> List[Dict[str, Any]]:
    """
    Funzione interfaccia standard per invocazione diretta.
    """
    parser = VoynichParser()
    return parser.parse_file(file_path)


if __name__ == "__main__":
    # Test di verifica isolato e diagnostico
    test_str = " fachys.ykal.ar.am qo.ol {comment}"
    parser = VoynichParser()
    tokens = parser.tokenize_line(test_str)
    print("Test Tokenizzazione Completato:")
    print("Input:", test_str)
    print("Token Estratti:", tokens)
    assert tokens == ['fachys', 'ykal', 'ar', 'am', 'qool'], f"Errore Tokenizzazione: {tokens}"
    print("VERIFICA MATEMATICA E INFORMATICA OOTB: SUPERATA")
