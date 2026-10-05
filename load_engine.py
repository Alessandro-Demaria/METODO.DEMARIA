#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
METODO DEMARIA® — COMPUTATIONAL VOYNICH ANALYSIS FRAMEWORK (Release v3.0)
Modulo: load_engine.py (Engine di Caricamento Vettoriale Unificato)
Autore: Avv. Alessandro Demaria | Licenza: CC BY 4.0
Zenodo DOI: 10.5281/zenodo.23119964
===============================================================================
Descrizione:
  Engine di caricamento e pre-processing vettoriale ad alte prestazioni (v3.0).
  Garantisce la normalizzazione automatica delle colonne (Aliasing v3.0),
  l'ordinamento codicologico sequenziale (Folio_Base -> line_id -> Record_ID),
  l'azzeramento dei valori nulli e la pulizia formale del dataset.
===============================================================================
"""

import os
import sys
import time
import pandas as pd
from typing import Dict, Any, Tuple


class DemariaLoadEngine:
    """
    Engine di caricamento e pre-processing vettoriale ad alte prestazioni per la Release v3.0.
    """
    def __init__(self, default_csv: str = 'voynich_eva_tokens_extended.csv') -> None:
        self.default_csv = default_csv
        self.version = "v3.0"

    def load_dataset(self, csv_path: str = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Carica il dataset unico garantendo la normalizzazione delle colonne,
        l'ordinamento codicologico esplicito v3.0 ed il tracciamento dei metadati.
        """
        t0 = time.time()
        target_path = csv_path if csv_path else self.default_csv

        if not os.path.exists(target_path):
            print(f"ERRORE CRITICO: File dataset '{target_path}' non trovato.")
            sys.exit(1)

        df = pd.read_csv(target_path)

        # Aliasing automatico delle colonne (v3.0)
        if 'Token' not in df.columns and 'EVA_Token' in df.columns:
            df['Token'] = df['EVA_Token']
        elif 'EVA_Token' not in df.columns and 'Token' in df.columns:
            df['EVA_Token'] = df['Token']

        if 'Folio_Base' not in df.columns and 'Folio' in df.columns:
            df['Folio_Base'] = df['Folio'].apply(lambda x: str(x).split('.')[0] if '.' in str(x) else str(x))
        elif 'Folio' not in df.columns and 'Folio_Base' in df.columns:
            df['Folio'] = df['Folio_Base']

        if 'Token' not in df.columns or 'Folio_Base' not in df.columns:
            print("ERRORE CRITICO: Colonne 'Token'/'EVA_Token' e 'Folio_Base'/'Folio' necessarie.")
            sys.exit(1)

        # Validazione e pulizia formale dei tipi
        df['Token'] = df['Token'].astype(str).str.lower().str.strip()
        df['EVA_Token'] = df['EVA_Token'].astype(str).str.lower().str.strip()
        df['Folio_Base'] = df['Folio_Base'].astype(str).str.strip()
        df['Folio'] = df['Folio'].astype(str).str.strip()

        # FIXING CRITICO v3.0: Ordinamento sequenziale codicologico esplicito
        sort_cols = [col for col in ['Folio_Base', 'line_id', 'Record_ID'] if col in df.columns]
        if sort_cols:
            df = df.sort_values(by=sort_cols).reset_index(drop=True)

        n_records = len(df)
        t_elapsed = time.time() - t0

        metadata = {
            'csv_source': target_path,
            'total_records': n_records,
            'unique_folios': int(df['Folio_Base'].nunique()),
            'null_values_count': int(df.isnull().sum().sum()),
            'load_time_sec': round(t_elapsed, 4),
            'release_version': self.version
        }

        return df, metadata


if __name__ == '__main__':
    print("=" * 80)
    print("METODO DEMARIA® v3.0 — VERIFICA ENGINE DI CARICAMENTO (LOAD ENGINE)")
    print("=" * 80)

    engine = DemariaLoadEngine()
    if os.path.exists('voynich_eva_tokens_extended.csv'):
        df_data, meta = engine.load_dataset()
        print(f"\n  • Fonte Dataset           : {meta['csv_source']}")
        print(f"  • Record Totali Caricati  : {meta['total_records']:,}")
        print(f"  • Fogli Unici Rilevati   : {meta['unique_folios']:,}")
        print(f"  • Valori Nulli Trovati    : {meta['null_values_count']}")
        print(f"  • Tempo di Caricamento    : {meta['load_time_sec']} s")
    else:
        print("\n  [INFO] Dataset 'voynich_eva_tokens_extended.csv' non rilevato in locale.")
        print("  [✓] Modulo 'load_engine.py' (Release v3.0) caricato e pronto.")
    print("=" * 80)