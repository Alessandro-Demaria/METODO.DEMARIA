import os

class VoynichParser:
    def __init__(self, filepath="voynich_eva.txt"):
        self.filepath = filepath

    def parse(self):
        """
        Legge il file del manoscritto e restituisce una lista di dizionari con keys:
        'folio', 'line', 'tokens'
        """
        if not os.path.exists(self.filepath):
            # Fallback se il file ha estensione doppia o diversa
            if os.path.exists("voynich_eva.txt.txt"):
                self.filepath = "voynich_eva.txt.txt"
            else:
                raise FileNotFoundError(f"File non trovato: {self.filepath}")

        data = []
        with open(self.filepath, 'r', encoding='utf-8') as f:
            for line_idx, line in enumerate(f, start=1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                # Estrazione folio se presente (es. <f1r.P.1>)
                folio = "f1r"
                if line.startswith('<') and '>' in line:
                    parts = line.split('>', 1)
                    meta = parts[0].lstrip('<')
                    line_content = parts[1]
                    folio = meta.split('.')[0]
                else:
                    line_content = line

                # Pulizia e tokenizzazione
                tokens = [t.strip() for t in line_content.replace('.', ' ').split() if t.strip()]
                if tokens:
                    data.append({
                        'folio': folio,
                        'line': line_idx,
                        'tokens': tokens
                    })

        return data