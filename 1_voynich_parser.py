"""
===============================================================================
METODO DEMARIA® — PARSER E SEGMENTATORE DI CORPUS (v3.2 CANONICO)
===============================================================================
Modulo 1: 1_voynich_parser.py
Autore e Inventore: Avv. Alessandro Demaria
PEC: avv.alessandrodemaria@pec.it
DOI UFFICIALE: 10.5281/zenodo.23199718
Licenza: CC BY 4.0
===============================================================================
"""

import json
import os
import numpy as np
import pandas as pd

SPEC_FILE = 'method_specification.json'


def load_method_specification(spec_path=SPEC_FILE):
    if not os.path.exists(spec_path):
        raise FileNotFoundError(f"[!] ERRORE: File di specifica '{spec_path}' non trovato.")
    with open(spec_path, 'r', encoding='utf-8') as f:
        spec = json.load(f)
    return spec


def parse_and_clean_dataset(spec_path=SPEC_FILE):
    spec = load_method_specification(spec_path)
    csv_filename = spec.get("master_dataset", {}).get("filename", "voynich_eva_tokens_extended.csv")
    
    if not os.path.exists(csv_filename):
        raise FileNotFoundError(f"[!] ERRORE: Dataset CSV '{csv_filename}' non trovato.")

    df = pd.read_csv(csv_filename)
    
    # Pulizia colonne e rimozione spazi bianchi
    df.columns = [c.strip() for c in df.columns]
    
    # Normalizzazione Folio e Line Number
    if 'Folio' in df.columns and 'Folio_Base' not in df.columns:
        df['Folio_Base'] = df['Folio'].astype(str).str.strip()
    elif 'Folio_Base' not in df.columns:
        df['Folio_Base'] = 'f1r'

    if 'Line' in df.columns and 'Line_Num' not in df.columns:
        df['Line_Num'] = df['Line'].astype(str).str.strip()
    elif 'Line_Num' not in df.columns:
        df['Line_Num'] = '1'

    # Creazione tassativa della Composite_Line_Key univoca per azzerare ogni data leakage inter-linea
    df['Composite_Line_Key'] = df['Folio_Base'].astype(str) + "::" + df['Line_Num'].astype(str)

    # Mappatura dello Stato sintattico vettoriale (0, 1, 2, 3)
    if 'State' not in df.columns:
        if 'EVA_Token' in df.columns:
            # Mappatura euristica deterministica basata sulla lunghezza token se lo Stato non è esplicito
            df['State'] = df['EVA_Token'].astype(str).apply(lambda x: len(x) % 4)
        else:
            df['State'] = 0

    df['State'] = df['State'].astype(int)
    # Filtra eventuali token non riconosciuti
    df = df[df['State'] >= 0].copy()
    
    return df


def compute_c_raw_segmented(df, transition_matrix):
    """
    Calcola la Coerenza Sintattica Grezza (C_raw) valutando le sole transizioni adiacenti
    interne al perimetro della medesima Composite_Line_Key (Zero Leakage).
    """
    states = df['State'].to_numpy(dtype=int)
    line_keys = df['Composite_Line_Key'].to_numpy()

    same_line_mask = (line_keys[:-1] == line_keys[1:])
    n_transitions = np.sum(same_line_mask)

    if n_transitions == 0:
        return 0.0

    src = states[:-1][same_line_mask]
    dst = states[1:][same_line_mask]

    tm_array = np.array(transition_matrix, dtype=bool)
    valid_transitions = np.sum(tm_array[src, dst])

    c_raw = float(valid_transitions / n_transitions)
    return c_raw


if __name__ == "__main__":
    print("Modulo 1_voynich_parser.py pronto all'uso e bonificato (v3.2 Canonico).")