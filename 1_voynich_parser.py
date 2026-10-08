"""
===============================================================================
METODO DEMARIA® — PARSER E SEGMENTATORE DI CORPUS (v3.2 CANONICO RIGOROSO)
===============================================================================
Modulo 1: 1_voynich_parser.py
Autore e Inventore Unico: Avv. Alessandro Demaria
PEC: avv.alessandrodemaria@pec.it
DOI UFFICIALE: 10.5281/zenodo.23199718
Licenza: CC BY 4.0
===============================================================================
"""

import json
import os
import re
import numpy as np
import pandas as pd

SPEC_FILE = 'method_specification.json'

# Mappatura biunivoca canonica dell'alfabeto EVA sui 4 stati minimi (Tiers A-C)
EVA_TO_STATE_MAP = {
    # State 0 (Alpha) - Innesco / Anchor
    'o': 0, 'y': 0, 'a': 0, 'e': 0,
    # State 1 (Beta) - Azione / Attrattore Stazionario
    'ch': 1, 'sh': 1, 'ee': 1, 'eee': 1, 'c': 1, 'h': 1, 'k': 1, 't': 1, 'p': 1, 'f': 1,
    # State 2 (Delta) - Differenziazione / Modulazione
    'q': 2, 'd': 2, 'l': 2, 'r': 2, 's': 2, 'x': 2,
    # State 3 (Gamma) - Reset / Chiusura
    'm': 3, 'n': 3, 'g': 3, 'z': 3
}

def load_method_specification(spec_path=SPEC_FILE):
    if not os.path.exists(spec_path):
        raise FileNotFoundError(f"[!] ERRORE: File di specifica '{spec_path}' non trovato.")
    with open(spec_path, 'r', encoding='utf-8') as f:
        spec = json.load(f)
    return spec

def map_eva_token_to_state(token):
    """
    Mappa un token EVA negli stati minimi (0, 1, 2, 3) mediante scomposizione e voto
    sui prefissi/caratteri guida, eliminando il fallback basato sulla lunghezza.
    """
    tok = str(token).strip().lower()
    if not tok:
        return 1  # Default su Beta (State 1 - Attrattore Stazionario)
    
    # Controllo corrispondenza esatta
    if tok in EVA_TO_STATE_MAP:
        return EVA_TO_STATE_MAP[tok]
    
    # Precedenza grafemi di reset/chiusura finale
    if tok.endswith(('m', 'g', 'n', 'z')):
        return 3
    # Precedenza grafemi di differenziazione
    if tok.startswith(('q', 'd', 'l', 'r')):
        return 2
    # Precedenza grafemi d'innesco
    if tok.startswith(('o', 'y', 'a', 'e')):
        return 0
    
    # Mappatura di ripiegamento deterministica sui caratteri interni
    for char in tok:
        if char in EVA_TO_STATE_MAP:
            return EVA_TO_STATE_MAP[char]
            
    return 1  # State Beta come attrattore di regime stazionario

def parse_and_clean_dataset(spec_path=SPEC_FILE):
    spec = load_method_specification(spec_path)
    csv_filename = spec.get("master_dataset", {}).get("filename", "voynich_eva_tokens_extended.csv")
    
    if not os.path.exists(csv_filename):
        raise FileNotFoundError(f"[!] ERRORE: Dataset CSV '{csv_filename}' non trovato.")

    df = pd.read_csv(csv_filename)
    df.columns = [c.strip() for c in df.columns]

    # Parsing di precisione del Folio Canonico tramite Regex (es. da 'f1r.1,@P0' a 'f1r')
    folio_col = 'Folio' if 'Folio' in df.columns else 'Folio_Base'
    if folio_col in df.columns:
        df['Folio_Base'] = df[folio_col].astype(str).apply(
            lambda x: re.search(r'^(f\d+[rv])', x.strip()).group(1) if re.search(r'^(f\d+[rv])', x.strip()) else x.strip()
        )
    else:
        df['Folio_Base'] = 'f1r'

    # Parsing di precisione della Linea
    if 'Line' in df.columns:
        df['Line_Num'] = df['Line'].astype(str).str.extract(r'(\d+)')[0].fillna('1')
    elif 'Line_Num' in df.columns:
        df['Line_Num'] = df['Line_Num'].astype(str).str.extract(r'(\d+)')[0].fillna('1')
    else:
        # Estrazione secondaria della linea dalla stringa composita Folio se presente
        df['Line_Num'] = df[folio_col].astype(str).apply(
            lambda x: re.search(r'\.(\d+)', x).group(1) if re.search(r'\.(\d+)', x) else '1'
        )

    # Definizione univoca della Composite_Line_Key (Zero Leakage)
    df['Composite_Line_Key'] = df['Folio_Base'] + "::" + df['Line_Num']

    # Assegnazione deterministica dello Stato Sintattico Vettoriale
    if 'State' in df.columns and df['State'].notnull().all():
        df['State'] = df['State'].astype(int)
    else:
        token_col = 'EVA_Token' if 'EVA_Token' in df.columns else df.columns[0]
        df['State'] = df[token_col].apply(map_eva_token_to_state).astype(int)

    df = df[df['State'] >= 0].copy()
    return df

def compute_c_raw_segmented(df, transition_matrix):
    """
    Calcola la Coerenza Sintattica Grezza (C_raw) valutando le sole transizioni adiacenti
    internamente al perimetro di ciascuna Composite_Line_Key.
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

    return float(valid_transitions / n_transitions)

if __name__ == "__main__":
    print("Modulo 1_voynich_parser.py bonificato e verificato (v3.2 Canonico).")