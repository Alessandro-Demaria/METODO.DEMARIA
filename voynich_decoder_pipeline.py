#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
METODO DEMARIA® — COMPUTATIONAL VOYNICH ANALYSIS FRAMEWORK (Release v3.0 Refresh)
Modulo: voynich_decoder_pipeline.py (Pipeline di Decodifica Strutturale)
Autore: Avv. Alessandro Demaria
Repository: GitHub - METODO.DEMARIA
Zenodo DOI: 10.5281/zenodo.22999135
===============================================================================
Descrizione:
  PIPELINE DI DECODIFICA STRUTTURALE (METODO DEMARIA™ Release v3.0 Refresh).
  Scompone i token del Voynich, rimuove la ridondanza dell'automa e isola
  il nucleo morfologico residuo (structural_core) senza assumere un'interpretazione
  semantica diretta, garantendo il rigore epistemologico del Tier A/B/C.
===============================================================================
"""

import numpy as np
import csv
import os

class VoynichDecoderPipeline:
    """
    PIPELINE DI DECODIFICA STRUTTURALE (Release v3.0 Refresh - Fase 4)
    Scompone i token del Voynich, rimuove la ridondanza dell'automa e isola il nucleo strutturale.
    """
    def __init__(self):
        self.C_BASE = 0.7542
        # Mappatura dei prefissi e suffissi strutturali dell'automa (EVA Transliteration)
        self.STRUCTURAL_PREFIXES = ['qo', 'ch', 'sh', 'ok', 'ot', 'ol']
        self.STRUCTURAL_SUFFIXES = ['edy', 'ain', 'eedy', 'ey', 'ol', 'or', 'ar']
        
    def invert_clock_phase(self, token_index, total_tokens):
        """
        Calcola e annulla l'offset di fase dell'automa per il token specificato.
        """
        delta = 4.50 / (102 * 200)
        return token_index * delta

    def extract_structural_core(self, token):
        """
        Inverte la griglia combinatoria: rimuove i componenti di ridondanza sintattica
        e isola il nucleo strutturale residuo (il dato grezzo).
        """
        cleaned_token = token.lower().strip()
        prefix_found = ""
        suffix_found = ""
        
        # 1. Isolamento Prefisso dell'Automa
        for pfx in sorted(self.STRUCTURAL_PREFIXES, key=len, reverse=True):
            if cleaned_token.startswith(pfx):
                prefix_found = pfx
                cleaned_token = cleaned_token[len(pfx):]
                break
                
        # 2. Isolamento Suffisso di Chiusura Sintattica
        for sfx in sorted(self.STRUCTURAL_SUFFIXES, key=len, reverse=True):
            if cleaned_token.endswith(sfx) and len(cleaned_token) > len(sfx):
                suffix_found = sfx
                cleaned_token = cleaned_token[:-len(sfx)]
                break
                
        core_root = cleaned_token if cleaned_token else token
        return prefix_found, core_root, suffix_found

    def decode_token(self, token, token_idx, total_tokens, module_type="BOTANICA"):
        """
        Esegue la scomposizione strutturale completa del token.
        """
        phase_offset = self.invert_clock_phase(token_idx, total_tokens)
        pfx, root, sfx = self.extract_structural_core(token)
        
        # Flag per identificare se il token conteneva ridondanza generata dall'automa
        is_synthetic_padding = True if (pfx and sfx) else False
        
        return {
            'original_token': token,
            'phase_offset': phase_offset,
            'prefix_grid': pfx if pfx else '[NONE]',
            'structural_core': root,
            'suffix_grid': sfx if sfx else '[NONE]',
            'is_padding': is_synthetic_padding
        }

def run_decryption_demo():
    decoder = VoynichDecoderPipeline()
    
    # Campione di token reali estratti dai fogli chiave
    sample_tokens = [
        ("f1r", "qokedy", "BOTANICA"),
        ("f1r", "chodedy", "BOTANICA"),
        ("f57v", "oror", "BOTANICA"),       # Router Reset
        ("f76r", "qokal", "BALNEOLOGIA"),
        ("f86v4", "skeyain", "COSMOLOGIA"),
        ("f102v1", "qokain", "FARMACIA")
    ]
    
    print("=" * 85)
    print("      PIPELINE AUTOMATIZZATA DI DECODIFICA STRUTTURALE (Release v3.0 Refresh)      ")
    print("=" * 85)
    print(f"{'FOLIO':<8} | {'TOKEN REALE':<12} | {'PREFISSO':<10} | {'STRUCTURAL CORE':<16} | {'SUFFISSO':<10} | {'STATO'}")
    print("-" * 85)
    
    for i, (folio, token, module) in enumerate(sample_tokens):
        result = decoder.decode_token(token, i * 100, 20000, module)
        status = "PADDING AUTOMATIC" if result['is_padding'] else "DATO NATIVO"
        if folio == "f57v":
            status = "RESET ROUTER"
            
        print(f"{folio:<8} | {result['original_token']:<12} | {result['prefix_grid']:<10} | "
              f"{result['structural_core']:<16} | {result['suffix_grid']:<10} | {status}")

    print("=" * 85)
    print("Scomposizione strutturale completata: il nucleo morfologico è isolato dalla griglia.")

if __name__ == "__main__":
    run_decryption_demo()