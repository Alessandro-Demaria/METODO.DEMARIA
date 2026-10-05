#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
METODO DEMARIA® — COMPUTATIONAL VOYNICH ANALYSIS FRAMEWORK (Release v3.0)
Modulo: intra_folio_coherence.py (Valutatore di Coerenza Intra-Folio Pura)
Autore: Avv. Alessandro Demaria | Licenza: CC BY 4.0
Zenodo DOI: 10.5281/zenodo.23119964
===============================================================================
Descrizione:
  Calcola la coerenza sintattico-topologica C* isolata entro i confini fisici
  di ciascun folio (Zero Inter-Folio Leakage).
  Applica l'aliasing automatico v3.0 e l'ordinamento codicologico sequenziale.
===============================================================================
"""

import os
import sys
import numpy as np
import pandas as pd
from typing import Dict, Any


class IntraFolioCoherenceEvaluator:
    """
    Calcolatore vettoriale della coerenza C* intra-folio per la Release v3.0.
    """

    TRANSITION_MATRIX: np.ndarray = np.array([
        [1, 1, 0, 0],  # alpha -> alpha, beta
        [0, 1, 1, 0],  # beta  -> beta, delta
        [0, 0, 1, 1],  # delta -> delta, gamma
        [1, 0, 0, 1]   # gamma -> gamma, alpha
    ], dtype=np.int8)

    DEMARIA_MAP: Dict[str, int] = {
        'o': 0, 'a': 0, 'e': 0, 'c': 0, 'h': 0,  # alpha (0)
        'k': 1, 't': 1, 'p': 1, 'f': 1, 's': 1,  # beta  (1)
        'r': 2, 'l': 2, 'q': 2, 'y': 2, 'd': 2,  # delta (2)
        'x': 3, 'g': 3, 'm': 3, 'n': 3, 'i': 3   # gamma (3)
    }

    def __init__(self) -> None:
        self.version = "v3.0"

    def _token_to_state(self, token_str: str) -> int:
        mapped_values = [self.DEMARIA_MAP[char] for char in str(token_str) if char in self.DEMARIA_MAP]
        if len(mapped_values) > 0:
            counts = np.bincount(mapped_values, minlength=4)
            return int(np.argmax(counts))
        return 0

    def compute_folio_coherence(self, csv_path: str = "voynich_eva_tokens_extended.csv",
                               output_summary_path: str = "intra_folio_coherence_results.csv") -> pd.DataFrame:
        if not os.path.exists(csv_path):
            print(f"ERRORE CRITICO: File dataset '{csv_path}' non trovato.")
            sys.exit(1)

        df = pd.read_csv(csv_path)

        # Aliasing automatico delle colonne (v3.0)
        if 'Token' not in df.columns and 'EVA_Token' in df.columns:
            df['Token'] = df['EVA_Token']
        if 'Folio_Base' not in df.columns and 'Folio' in df.columns:
            df['Folio_Base'] = df['Folio'].apply(lambda x: str(x).split('.')[0] if '.' in str(x) else str(x))

        if 'Token' not in df.columns or 'Folio_Base' not in df.columns:
            print("ERRORE CRITICO: Colonne 'Token'/'EVA_Token' e 'Folio_Base'/'Folio' necessarie.")
            sys.exit(1)

        # FIXING CRITICO v3.0: Ordinamento sequenziale codicologico esplicito
        sort_cols = [col for col in ['Folio_Base', 'line_id', 'Record_ID'] if col in df.columns]
        if sort_cols:
            df = df.sort_values(by=sort_cols).reset_index(drop=True)

        tokens = df['Token'].astype(str).to_numpy()
        folios = df['Folio_Base'].astype(str).to_numpy()

        states = np.array([self._token_to_state(t) for t in tokens], dtype=int)

        unique_folios = np.unique(folios)
        results_list = []

        total_valid_global = 0.0
        total_trans_global = 0

        for fol in unique_folios:
            fol_mask = (folios == fol)
            fol_states = states[fol_mask]
            
            if len(fol_states) > 1:
                s_curr = fol_states[:-1]
                s_next = fol_states[1:]
                valid_trans = float(np.sum(self.TRANSITION_MATRIX[s_curr, s_next]))
                tot_trans = len(s_curr)
                c_star = valid_trans / tot_trans if tot_trans > 0 else 0.0
                
                total_valid_global += valid_trans
                total_trans_global += tot_trans
            else:
                c_star = 0.0
                tot_trans = 0

            results_list.append({
                'Folio_Base': fol,
                'Token_Count': int(np.sum(fol_mask)),
                'Transitions_Count': tot_trans,
                'C_Star_Intra_Folio': round(c_star, 6)
            })

        summary_df = pd.DataFrame(results_list)
        summary_df.to_csv(output_summary_path, index=False)

        global_c_star = total_valid_global / total_trans_global if total_trans_global > 0 else 0.0

        print("=========================================================")
        print("   METODO DEMARIA® v3.0 — COERENZA INTRA-FOLIO PURA      ")
        print("=========================================================")
        print(f"Dataset Analizzato:        {csv_path}")
        print(f"Folii Distinti Processati: {len(unique_folios):,}")
        print(f"Token Totali Analizzati:   {len(tokens):,}")
        print(f"C* Intra-Folio Globale:    {global_c_star:.6f}")
        print(f"Report Esportato su:       {output_summary_path}")
        print("=========================================================")

        return summary_df


if __name__ == '__main__':
    evaluator = IntraFolioCoherenceEvaluator()
    if os.path.exists("voynich_eva_tokens_extended.csv"):
        evaluator.compute_folio_coherence()
    else:
        print("\n  [INFO] Dataset 'voynich_eva_tokens_extended.csv' non rilevato in locale.")
        print("  [✓] Modulo 'intra_folio_coherence.py' (Release v3.0) caricato e pronto.")