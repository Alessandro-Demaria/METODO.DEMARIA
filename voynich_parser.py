import os
import re

class VoynichParser:
    def __init__(self, filepath):
        self.filepath = filepath

    def parse(self):
        """
        Legge il file EVA traslitterato e restituisce una struttura dati vettoriale:
        list di dict: [{'folio': 'f1r', 'line': 1, 'tokens': ['fachys', 'ykal', ...]}, ...]
        """
        parsed_data = []
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"File non trovato: {self.filepath}")

        with open(self.filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                # Match tipico del formato EVA (es. <f1r.1,+P0> fachys.ykal.ar.faiin.soor)
                match = re.match(r'<f(\d+[rv])\.(\d+)[^>]*>\s*(.*)', line)
                if match:
                    folio = f"f{match.group(1)}"
                    line_num = int(match.group(2))
                    text = match.group(3)
                    # Pulizia e separazione dei token
                    tokens = [t.strip() for t in re.split(r'[.\s]+', text) if t.strip()]
                    parsed_data.append({
                        'folio': folio,
                        'line': line_num,
                        'tokens': tokens
                    })
        return parsed_data

if __name__ == "__main__":
    parser = VoynichParser("voynich_eva")
    print("voynich_parser.py pronto.")