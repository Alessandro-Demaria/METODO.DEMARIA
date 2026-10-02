#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
METODO DEMARIA® — COMPUTATIONAL VOYNICH ANALYSIS FRAMEWORK (Release v3.0 Refresh)
Modulo: voynich_decoder_pipeline.py (Pipeline di Decodifica Strutturale)
Autore: Avv. Alessandro Demaria
===============================================================================
"""

import numpy as np
import pandas as pd
from typing import Dict, Any

class VoynichDecoderPipeline:
    """
    PIPELINE DI DECODIFICA STRUTTURALE (Release v3.0 Refresh)
    Scompone i 35.483 token del Voynich dal CSV esteso, rimuove la ridondanza
    dell'automa e isola il nucleo strutturale (structural_core).
    """
    def __init__(self):
        self.C_BASE = 0.7542
        self.STRUCTURAL_PREFIXES = ['qo', 'ch', 'sh', 'ok', 'ot', 'ol']
        self.STRUCTURAL_SUFFIXES = ['edy', 'ain', 'eedy', 'ey', 'ol', 'or', 'ar']

    def extract_structural_core(self, token: str):
        """
        Rimuove la griglia combinatoria di prefissi e suffissi dell'automa.
        """
        cleaned_token = str(token).lower().strip()
        prefix_found = ""
        suffix_found = ""
        
        # 1. Isolamento Prefisso
        for pfx in sorted(self.STRUCTURAL_PREFIXES, key=len, reverse=True):
            if cleaned_token.startswith(pfx):
                prefix_found = pfx
                cleaned_token = cleaned_token[len(pfx):]
                break
                
        # 2. Isolamento Suffisso
        for sfx in sorted(self.STRUCTURAL_SUFFIXES, key=len, reverse=True):
            if cleaned_token.endswith(sfx) and len(cleaned_token) > len(sfx):
                suffix_found = sfx
                cleaned_token = cleaned_token[:-len(sfx)]
                break
                
        core_root = cleaned_token if cleaned_token else str(token)
        return prefix_found, core_root, suffix_found

    def process_csv_dataset(self, csv_path: str = 'voynich_eva_tokens_extended.csv') -> pd.DataFrame:
        """
        Esegue la scomposizione su tutti i 35.483 token del dataset unificato.
        """
        df = pd.read_csv(csv_path)
        prefixes, cores, suffixes, paddings = [], [], [], []
        
        for idx, row in df.iterrows():
            pfx, root, sfx = self.extract_structural_core(row['EVA_Token'])
            prefixes.append(pfx if pfx else '[NONE]')
            cores.append(root)
            suffixes.append(sfx if sfx else '[NONE]')
            paddings.append(True if (pfx and sfx) else False)
            
        df['Prefix'] = prefixes
        df['Structural_Core'] = cores
        df['Suffix'] = suffixes
        df['Is_Padding'] = paddings
        return df

if __name__ == "__main__":
    print("=" * 85)
    print(" METODO DEMARIA® — DECODIFICA STRUTTURALE SU DATASET ESTESO (35.483 RECORD)")
    print("=" * 85)
    
    decoder = VoynichDecoderPipeline()
    df_res = decoder.process_csv_dataset('voynich_eva_tokens_extended.csv')
    
    padding_count = df_res['Is_Padding'].sum()
    padding_pct = (padding_count / len(df_res)) * 100
    
    print(f"Record Totali Elaborati : {len(df_res)}")
    print(f"Token con Padding Automa: {padding_count} ({padding_pct:.2f}%)")
    print("\nCampione dei primi 5 record decodificati:")
    print(df_res[['Folio', 'EVA_Token', 'Prefix', 'Structural_Core', 'Suffix', 'Is_Padding']].head())
    print("=" * 85)