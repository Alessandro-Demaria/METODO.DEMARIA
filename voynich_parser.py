import os
import re

class VoynichParser:
    def __init__(self, filepath="voynich_eva.txt"):
        self.filepath = filepath

    def parse(self):
        """
        Legge il file del manoscritto ed estrae esclusivamente le righe di testo
        reali del Voynich (escludendo le intestazioni IVTFF come <f1r>).
        Restituisce una lista di dizionari con keys: 'folio', 'line', 'tokens'
        """
        if not os.path.exists(self.filepath):
            if os.path.exists("voynich_eva.txt.txt"):
                self.filepath = "voynich_eva.txt.txt"
            else:
                raise FileNotFoundError(f"File non trovato: {self.filepath}")

        data = []
        with open(self.filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                # Manteniamo solo i tag di riga testuale vera con punto (es. <f1r.1,...>)
                # Ignoriamo le intestazioni di solo folio (es. <f1r>)
                match = re.match(r'^<f(\d+[rv])\.(\d+)[^>]*>\s*(.*)', line)
                if not match:
                    continue

                folio = f"f{match.group(1)}"
                line_num = match.group(2)
                text_part = match.group(3)

                # Rimuove eventuali metadati residui tra parentesi angolari
                text_part = re.sub(r'<![^>]*>', '', text_part).strip()

                # Separa le parole pulite
                tokens = [t for t in re.split(r'[\s\.\,]+', text_part) if t]

                if tokens:
                    data.append({
                        'folio': folio,
                        'line': line_num,
                        'tokens': tokens
                    })

        return data
