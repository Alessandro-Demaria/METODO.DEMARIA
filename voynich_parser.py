import re
import os

class VoynichParser:
    def __init__(self, file_path):
        self.file_path = file_path

    def parse(self):
        """
        Legge il file EVA traslitterato (formato IVTFF) e restituisce una struttura dati vettoriale:
        list di dict: [{'folio': 'f1r', 'line': 1, 'tokens': ['fachys', 'ykal', ...]}, ...]
        """
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File non trovato: {self.file_path}")

        parsed_data = []

        with open(self.file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                # Estrazione del tag di riga/folio (es. <f1r.1,+P0>)
                match = re.match(r'^<([^>]+)>\s*(.*)$', line)
                if match:
                    header = match.group(1)
                    content = match.group(2)

                    # Estrae il folio (es. f1r)
                    folio_match = re.search(r'f\d+[rv](\.\d+)?', header)
                    folio = folio_match.group(0) if folio_match else header

                    # Rimuove i commenti o annotazioni tra parentesi graffe o angolari
                    content_clean = re.sub(r'\{[^}]*\}', '', content)
                    content_clean = re.sub(r'<[^>]*>', '', content_clean)

                    # Estrae tutti i token separati da punti o spazi
                    raw_tokens = re.split(r'[\.\s]+', content_clean)
                    tokens = [t for t in raw_tokens if t and not t.startswith('!') and not t.startswith('$')]

                    if tokens:
                        parsed_data.append({
                            'header': header,
                            'folio': folio,
                            'tokens': tokens
                        })

        return parsed_data
