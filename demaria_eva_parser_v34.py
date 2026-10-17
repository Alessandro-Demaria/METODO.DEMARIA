"""
================================================================================
LABORATORIO SCIENTIFICO METODO DEMARIA ® - RELEASE v3.4 (RELEASE FROZEN)
AUTORE, RESPONSABILE SCIENTIFICO E INVENTORE UNICO: AVV. ALESSANDRO DEMARIA
CONCEPT DOI MADRE: 10.5281/zenodo.22789343 | RELEASE DOI: 10.5281/zenodo.23437366
MARCHIO REGISTRATO UIBM N. 302026000161716 | SEGRETO INDUSTRIALE ART. 98 CPI

MODULO: demaria_eva_parser_v34.py
DESCRIZIONE: Parser deterministico dell'alfabeto EVA e trasduzione molti-a-uno
             sulla quadrupla degli stati topologici minimi S = {1, 2, 3, 4}
             con normalizzazione automatica delle coordinate di rigo e folio.
================================================================================
"""

import os
import sys
import hashlib
import pandas as pd
import numpy as np

# Impronta Crittografica SHA-256 congelata di laboratorio per il Master Dataset
EXPECTED_SHA256 = "dec87e784290ad5b404bd5ed0110349a2f379c7fb386adb0bca2d7a4b1890999"

def verify_dataset_integrity(filepath: str) -> bool:
    """
    Verifica l'integrita crittografica SHA-256 del dataset master prima di ogni elaborazione.
    """
    if not os.path.exists(filepath):
        print(f"ERROR: Dataset non trovato nel percorso: {filepath}")
        return False
    
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    
    calculated_hash = sha256_hash.hexdigest()
    if calculated_hash.lower() != EXPECTED_SHA256.lower():
        print(f"CRITICAL: Hash SHA-256 non corrispondente!")
        print(f"Calcolato: {calculated_hash}")
        print(f"Atteso:    {EXPECTED_SHA256}")
        return False
    
    print(f"Dataset Locale: VERIFICATO | SHA-256: {calculated_hash[:16]}...")
    return True

def load_and_normalize_voynich_corpus(filepath: str) -> pd.DataFrame:
    """
    Carica il dataset esteso e normalizza le colonne chiave per prevenire KeyError
    garantendo la piena retrocompatibilita con tutti i moduli di audit (Release v3.4).
    """
    if not verify_dataset_integrity(filepath):
        raise ValueError("Integrita del Master Dataset compromessa o file mancante.")
    
    df = pd.read_csv(filepath)
    
    # Normalizzazione deterministica delle colonne chiave
    if 'folio_num' in df.columns and 'folio_id' not in df.columns:
        df['folio_id'] = df['folio_num']
    elif 'folio' in df.columns and 'folio_id' not in df.columns:
        df['folio_id'] = df['folio']
    elif 'folio_id' not in df.columns:
        df['folio_id'] = df.iloc[:, 0]

    if 'line_num' in df.columns and 'line_id' not in df.columns:
        df['line_id'] = df['line_num']
    elif 'line' in df.columns and 'line_id' not in df.columns:
        df['line_id'] = df['line']

    return df

def eva_to_state_transduction(token: str) -> int:
    """
    Funzione di trasduzione delta_T: Mappatura molti-a-uno dall'alfabeto EVA
    alla quadrupla degli stati topologici minimi S = {1, 2, 3, 4}.
    
    State 1 (Alpha): Header / Innesco (qo-, chol-, chor-, shol-, shor-, y-)
    State 2 (Beta):  Regime Stazionario / Attrattore (Operazioni di corpo rigo default)
    State 3 (Delta): Modulazione Sintattica Infix (ch, sh, ok, ot, ct)
    State 4 (Gamma): Reset / Scarico Terminale (-am, -an, -dy, -edy, -ol, -or, -y)
    """
    if not isinstance(token, str) or not token:
        return 2  # State Beta (Default Attractor)
    
    t = token.lower().strip()
    
    # Regole di Innesco (State Alpha = 1)
    if t.startswith(('qo', 'chol', 'chor', 'shol', 'shor')) or (t.startswith('y') and len(t) > 1):
        return 1
    
    # Regole di Reset / Scarico (State Gamma = 4)
    if t.endswith(('am', 'an', 'dy', 'edy', 'ol', 'or')) or (t.endswith('y') and not t.startswith('y')):
        return 4
    
    # Regole di Modulazione Infix (State Delta = 3)
    if any(infix in t for infix in ['ch', 'sh', 'ok', 'ot', 'ct']):
        return 3
    
    # Regime Stazionario (State Beta = 2)
    return 2

def process_corpus_tokens(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applica la trasduzione vettoriale all'intero DataFrame e genera la sequenza degli stati S.
    """
    if 'eva' in df.columns:
        token_col = 'eva'
    elif 'token' in df.columns:
        token_col = 'token'
    else:
        token_col = df.columns[1]
        
    df['state'] = df[token_col].astype(str).apply(eva_to_state_transduction)
    return df

if __name__ == "__main__":
    dataset_path = "voynich_eva_tokens_extended.csv"
    try:
        data = load_and_normalize_voynich_corpus(dataset_path)
        data = process_corpus_tokens(data)
        print(f"Trasduzione completata con successo su {len(data)} EVA tokens.")
        print(f"Distribuzione Stati Topologici Minimi:")
        print(data['state'].value_counts(normalize=True).sort_index() * 100)
    except Exception as e:
        print(f"Arresto di sicurezza: {e}")
        sys.exit(1)
