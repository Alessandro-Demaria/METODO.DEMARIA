import re
from typing import List, Dict, Any

class VoynichParser:
    """
    Parser ad alto rigore scientifico per la trascrizione EVA del Manoscritto Voynich.
    Esegue la pulizia automatica dei marcatori editoriali, gestione dei tag folio/sezione
    e isolamento dei token linguistici puliti.
    """
    def __init__(self, filepath: str = "voynich_eva.txt"):
        self.filepath = filepath

    def clean_token(self, token: str) -> str:
        """
        Rimuove marcatori editoriali, caratteri speciali di trascrizione
        e annotazioni come <%>, !, ?, o caratteri incerti.
        """
        # Rimuove commenti o tag editoriali tra angolari
        cleaned = re.sub(r'<[^>]+>', '', token)
        # Rimuove caratteri di incertezza o trascrizione speciale
        cleaned = re.sub(r'[\! \? \% \* \$\=\#]', '', cleaned)
        # Rimuove punteggiatura residua
        cleaned = cleaned.strip(" .,;-")
        return cleaned

    def parse(self, filepath: str = None) -> List[Dict[str, Any]]:
        target_path = filepath or self.filepath
        records = []

        try:
            with open(target_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"[-] Warning: File {target_path} not found.")
            return []

        for line_num, raw_line in enumerate(lines, start=1):
            line_str = raw_line.strip()
            if not line_str or line_str.startswith("#"):
                continue

            # Identificazione del tag foglio/linea (es.  o )
            folio_match = re.match(r'^<([^>]+)>\s*(.*)$', line_str)
            if folio_match:
                tag = folio_match.group(1)
                content = folio_match.group(2)
                
                # Estrazione strutturata di folio e riga
                parts = tag.split('.')
                folio = parts[0] if len(parts) > 0 else f"line_{line_num}"
                line_id = ".".join(parts[1:]) if len(parts) > 1 else str(line_num)
            else:
                folio = "unknown"
                line_id = str(line_num)
                content = line_str

            # Estrazione e pulizia dei token
            raw_tokens = content.split()
            tokens = []
            for t in raw_tokens:
                cleaned = self.clean_token(t)
                if cleaned:
                    tokens.append(cleaned)

            if tokens:
                records.append({
                    "folio": folio,
                    "line": line_id,
                    "line_num": line_num,
                    "tokens": tokens,
                    "raw_text": content
                })

        return records

def parse_voynich_eva(filepath: str = "voynich_eva.txt") -> List[Dict[str, Any]]:
    parser = VoynichParser(filepath)
    return parser.parse()

if __name__ == "__main__":
    p = VoynichParser()
    res = p.parse()
    print(f"[+] Voynich Parser executed: {len(res)} lines extracted successfully.")
