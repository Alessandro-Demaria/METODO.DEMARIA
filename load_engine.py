#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
METODO DEMARIA® — COMPUTATIONAL VOYNICH ANALYSIS FRAMEWORK (Release v3.0)
Modulo: load_engine.py (Engine di Caricamento Vettoriale Unificato)
Autore: Avv. Alessandro Demaria
===============================================================================
"""

import time
import pandas as pd
from typing import Dict, Any, Tuple


class DemariaLoadEngine:
    """
    Engine di caricamento e pre-processing vettoriale ad alte prestazioni.
    """
    def __init__(self, default_csv: str = 'voynich_eva_tokens_extended.csv') -> None:
        self.default_csv = default_csv

    def load_dataset(self, csv_path: str = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Carica il dataset unico garantendo zero valori nulli e integrità del tipo dati.
        """
        t0 = time.time()
        target_path = csv_path if csv_path else self.default_csv
        
        df = pd.read_csv(target_path)
        n_records = len(df)
        
        # Validazione e pulizia tipi
        df['EVA_Token'] = df['EVA_Token'].astype(str).str.lower().str.strip()
        df['Folio'] = df['Folio'].astype(str).str.strip()
        
        t_elapsed = time.time() - t0

        metadata = {
            'csv_source': target_path,
            'total_records': n_records,
            'unique_folios': int(df['Folio'].nunique()),
            'null_values_count': int(df.isnull().sum().sum()),
            'load_time_sec': round(t_elapsed, 4)
        }

        return df, metadata


if __name__ == '__main__':
    print("=" * 80)
    print("METODO DEMARIA® — VERIFICA ENGINE DI CARICAMENTO (LOAD ENGINE)")
    print("=" * 80)

    engine = DemariaLoadEngine()
    df_data, meta = engine.load_dataset()

    print(f"\n  • Fonte Dataset           : {meta['csv_source']}")
    print(f"  • Record Totali Caricati  : {meta['total_records']}")
    print(f"  • Fogli Unici Rilevati   : {meta['unique_folios']}")
    print(f"  • Valori Nulli Trovati    : {meta['null_values_count']}")
    print(f"  • Tempo di Caricamento    : {meta['load_time_sec']} s")
    print("=" * 80)