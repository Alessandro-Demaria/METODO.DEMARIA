#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
METODO DEMARIA® — PIPELINE INTEGRATA DI DECODIFICA VETTORIALE (v3.0 - Canonico)
Modulo: voynich_decoder_pipeline.py
Autore: Avv. Alessandro Demaria | Licenza: CC BY 4.0
===============================================================================
Descrizione:
  Pipeline di decodifica vettoriale e ricostruzione della traiettoria di stato.
  Utilizza voynich_parser.py per l'ingestion pulita del dataset e legge i
  parametri esclusivamente da method_specification.json.
===============================================================================
"""

import os
import json
import numpy as np
import pandas as pd
from voynich_parser import parse_and_clean_dataset, load_method_specification, SPEC_FILE

class VoynichDecoderPipeline:
    def __init__(self, spec_path: str = SPEC_FILE):
        self.spec = load_method_specification(spec_path)
        self.transition_matrix = np.array(self.spec['transition_matrix_validity']['allowed_transitions'], dtype=float)
        
    def execute_pipeline(self) -> dict:
        df = parse_and_clean_dataset(SPEC_FILE)
        valid_df = df[df['State'] >= 0].copy()
        
        states = valid_df['State'].values
        if len(states) < 2:
            raise ValueError("[!] ERRORE: Numero insufficiente di stati validi per la decodifica.")
            
        s1 = states[:-1]
        s2 = states[1:]
        
        # Calcolo Matrice di Transizione Empirica di Markov (4x4)
        markov_counts = np.zeros((4, 4), dtype=int)
        for a, b in zip(s1, s2):
            markov_counts[a, b] += 1
            
        row_sums = markov_counts.sum(axis=1, keepdims=True)
        markov_probs = np.divide(markov_counts, row_sums, where=row_sums != 0)
        
        # Calcolo C_raw
        valid_transitions = int(np.sum(self.transition_matrix[s1, s2]))
        total_transitions = len(s1)
        c_raw = float(valid_transitions / total_transitions) if total_transitions > 0 else 0.0
        
        # Distribuzione degli Stati
        state_counts = pd.Series(states).value_counts(normalize=True).to_dict()
        state_names = {0: 'alpha', 1: 'beta', 2: 'delta', 3: 'gamma'}
        distribution = {state_names[k]: round(float(v), 4) for k, v in state_counts.items()}
        
        return {
            'total_tokens_processed': len(df),
            'valid_state_tokens': len(valid_df),
            'unique_folios': int(df['Folio_Base'].nunique()),
            'c_raw_observed': round(c_raw, 6),
            'state_distribution': distribution,
            'markov_counts': markov_counts.tolist(),
            'markov_probabilities': np.round(markov_probs, 4).tolist()
        }

def run_decoder_pipeline():
    print("==================================================================")
    print("METODO DEMARIA® — PIPELINE DI DECODIFICA VETTORIALE (v3.0 Canonico)")
    print("==================================================================")
    
    pipeline = VoynichDecoderPipeline()
    results = pipeline.execute_pipeline()
    
    print(f"[*] Token Totali Processati: {results['total_tokens_processed']}")
    print(f"[*] Token con Stato Valido:  {results['valid_state_tokens']}")
    print(f"[*] Folii Unici Coperti:     {results['unique_folios']}")
    print(f"[*] Coerenza C_raw Rilevata: {results['c_raw_observed']:.6f} ({results['c_raw_observed']*100:.2f}%)")
    print(f"\n[*] Distribuzione Empirica degli Stati: {results['state_distribution']}")
    print("\n[*] Matrice delle Transizioni Empiriche (Markov 4x4):")
    print(np.array(results['markov_probabilities']))
    
    output_json = 'decoding_pipeline_results.json'
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"\n[V] Risultati della pipeline salvati in '{output_json}'.")

if __name__ == '__main__':
    run_decoder_pipeline()