#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
METODO DEMARIA® — COMPUTATIONAL VOYNICH ANALYSIS FRAMEWORK (Release v3.0)
Modulo: voynich_decoder_pipeline.py (Pipeline di Decodifica Inversa e Stripping)
Autore: Avv. Alessandro Demaria | Licenza: CC BY 4.0
===============================================================================
Descrizione:
  Pipeline di decodifica inversa per la scomposizione automatizzata dei token EVA.
  Esegue lo stripping dei prefissi (es. qo-, ch-) e suffissi (es. -edy, -ol) sintattici
  di modulazione di regime, isolando la radice semantica nativa ed estraendo
  l'Instruction Set di comando eseguito dall'automa.
===============================================================================
"""

import os
import sys
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple


class VoynichDecoderPipeline:
    """
    Pipeline di Decodifica Inversa e Stripping Morfologico (Release v3.0).
    """
    def __init__(self) -> None:
        # Prefissi e Suffissi Sintattici di Modulazione (Nomenclatura EVA)
        self.prefixes: List[str] = ['qok', 'qot', 'qo', 'ch', 'sh', 'ok', 'ot']
        self.suffixes: List[str] = ['eedy', 'edy', 'aiin', 'ain', 'am', 'ol', 'or', 'ey', 'dy']
        
        # Mappatura Vettoriale della Radice su Comandi Hardware dell'Automa
        self.command_mapping: Dict[str, str] = {
            'k': 'CMD_CALIBRATION_FLOW',     # Taratura flussi e dosaggio
            't': 'CMD_VALVE_SWITCH',         # Commutazione valvole / otturatore
            'p': 'CMD_PRESSURE_PULSE',       # Spinta e accumulo pressione Z(t)
            'f': 'CMD_FLUID_INJECTION',      # Iniezione fluido / carico
            's': 'CMD_THERMAL_STABILIZATION',# Stabilizzazione gradiente termico Q
            'a': 'CMD_INIT_CYCLE',           # Innesco ciclo di rigo (State alpha)
            'o': 'CMD_BASE_RESONANCE',       # Mantenimento regime stazionario (State beta)
            'r': 'CMD_RECIRCULATION_LOOP',   # Ricircolo nei condotti ciechi
            'l': 'CMD_SURGE_BALANCE',        # Bilanciamento serbatoio di stasi
            'y': 'CMD_SYSTEM_DRAIN_RESET'    # Drenaggio, scarico e reset (State gamma)
        }

    def strip_token_modulations(self, token_eva: str) -> Tuple[str, str, str]:
        """
        Isola prefisso, radice nativa e suffisso dal token EVA.
        """
        token = str(token_eva).strip().lower()
        extracted_prefix = ""
        extracted_suffix = ""
        
        # 1. Stripping Prefisso
        for p in self.prefixes:
            if token.startswith(p):
                extracted_prefix = p
                token = token[len(p):]
                break
                
        # 2. Stripping Suffisso
        for s in self.suffixes:
            if token.endswith(s):
                extracted_suffix = s
                token = token[:len(token) - len(s)]
                break
                
        native_root = token if len(token) > 0 else "k"
        return extracted_prefix, native_root, extracted_suffix

    def process_csv_dataset(self, csv_path: str = "voynich_eva_tokens_extended.csv",
                            output_path: str = "decoded_instruction_set_results.csv") -> pd.DataFrame:
        """
        Esegue la scomposizione batch sull'intero corpus e restituisce il dataframe decodificato.
        """
        if not os.path.exists(csv_path):
            print(f"ERRORE CRITICO: File dataset '{csv_path}' non trovato.")
            sys.exit(1)
            
        df = pd.read_csv(csv_path)
        
        # Normalizzazione ed ordinamento codicologico esplicito v3.0
        if 'Token' not in df.columns and 'EVA_Token' in df.columns:
            df['Token'] = df['EVA_Token']
        if 'Folio_Base' not in df.columns and 'Folio' in df.columns:
            df['Folio_Base'] = df['Folio'].apply(lambda x: str(x).split('.')[0] if '.' in str(x) else str(x))

        sort_cols = [col for col in ['Folio_Base', 'line_id', 'Record_ID'] if col in df.columns]
        if sort_cols:
            df = df.sort_values(by=sort_cols).reset_index(drop=True)

        prefixes_list, roots_list, suffixes_list, commands_list, is_padding_list = [], [], [], [], []

        for token in df['Token'].astype(str):
            pref, root, suff = self.strip_token_modulations(token)
            primary_char = root[0] if len(root) > 0 else 'k'
            cmd = self.command_mapping.get(primary_char, 'CMD_GENERIC_EXECUTION')
            is_padding = bool(pref == "" and suff == "" and len(root) <= 1)
            
            prefixes_list.append(pref)
            roots_list.append(root)
            suffixes_list.append(suff)
            commands_list.append(cmd)
            is_padding_list.append(is_padding)

        df['Prefix_EVA'] = prefixes_list
        df['Native_Root'] = roots_list
        df['Suffix_EVA'] = suffixes_list
        df['Hardware_Command'] = commands_list
        df['Is_Padding'] = is_padding_list

        df.to_csv(output_path, index=False)
        return df


if __name__ == '__main__':
    print("=========================================================")
    print("   METODO DEMARIA® v3.0 — INVERSE DECODING PIPELINE      ")
    print("=========================================================")
    
    pipeline = VoynichDecoderPipeline()
    decoded_df = pipeline.process_csv_dataset("voynich_eva_tokens_extended.csv")
    
    total_tokens = len(decoded_df)
    padding_count = int(decoded_df['Is_Padding'].sum())
    native_count = total_tokens - padding_count
    
    print(f"Dataset Analizzato:        voynich_eva_tokens_extended.csv")
    print(f"Token Totali Processati:   {total_tokens:,}")
    print(f"Radici Native Isolate:     {native_count:,} ({native_count/total_tokens*100:.2f}%)")
    print(f"Token di Padding / Sync:   {padding_count:,} ({padding_count/total_tokens*100:.2f}%)")
    print(f"Comandi Hardware Estratti: {decoded_df['Hardware_Command'].nunique()} tipi unici")
    print(f"Report Esportato su:       decoded_instruction_set_results.csv")
    print("=========================================================")