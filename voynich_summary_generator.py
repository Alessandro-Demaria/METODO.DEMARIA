#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
METODO DEMARIA® — COMPUTATIONAL VOYNICH ANALYSIS FRAMEWORK (Release v3.0)
Modulo: voynich_summary_generator.py (Generatore Report di Sintesi Master)
Autore: Avv. Alessandro Demaria
===============================================================================
"""

import time
import json
import pandas as pd
import numpy as np
from typing import Dict, Any


class VoynichSummaryGenerator:
    """
    Modulo master per la generazione dei report statistici e sintetici
    dell'intero corpus del Manoscritto Voynich.
    """

    def __init__(self, csv_path: str = 'voynich_eva_tokens_extended.csv') -> None:
        self.csv_path = csv_path

    def generate_master_summary(self, output_json: str = 'voynich_master_summary.json') -> Dict[str, Any]:
        """
        Scansione completa del dataset ed esportazione delle metriche sintetiche generali.
        """
        t0 = time.time()
        df = pd.read_csv(self.csv_path)

        if df.empty:
            raise ValueError(f"[ERROR] Il file dataset '{self.csv_path}' è vuoto.")

        total_tokens = len(df)
        total_folios = df['Folio'].nunique() if 'Folio' in df.columns else 0
        
        c_star_mean = float(df['C_star_t'].mean())
        c_star_std = float(df['C_star_t'].std())
        z_t_mean = float(df['Z_t'].mean())
        z_t_std = float(df['Z_t'].std())

        # Ripartizione per sezioni macro
        section_summary = {}
        if 'Folio' in df.columns:
            df['Folio_Base'] = df['Folio'].astype(str).apply(lambda x: x.split('.')[0] if '.' in x else x)
            section_summary['botanica_tokens'] = int(len(df[df['Folio_Base'].apply(lambda x: x.startswith('f') and x[1:-1].isdigit() and 1 <= int(x[1:-1]) <= 66)]))
            section_summary['balneologica_tokens'] = int(len(df[df['Folio_Base'].apply(lambda x: x.startswith('f') and x[1:-1].isdigit() and 75 <= int(x[1:-1]) <= 84)]))
            section_summary['farmacia_tokens'] = int(len(df[df['Folio_Base'].apply(lambda x: x.startswith('f') and x[1:-1].isdigit() and 87 <= int(x[1:-1]) <= 102)]))

        summary_data = {
            'framework': 'METODO DEMARIA® v3.0',
            'dataset': self.csv_path,
            'total_tokens_processed': total_tokens,
            'unique_folios': total_folios,
            'global_metrics': {
                'c_star_mean': round(c_star_mean, 4),
                'c_star_std': round(c_star_std, 4),
                'z_t_mean': round(z_t_mean, 4),
                'z_t_std': round(z_t_std, 4)
            },
            'section_breakdown': section_summary,
            'execution_time_sec': round(time.time() - t0, 4)
        }

        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=4, ensure_ascii=False)

        return summary_data


if __name__ == '__main__':
    print("=" * 80)
    print("METODO DEMARIA® — GENERAZIONE REPORT DI SINTESI MASTER")
    print("=" * 80)

    generator = VoynichSummaryGenerator('voynich_eva_tokens_extended.csv')
    report = generator.generate_master_summary('voynich_master_summary.json')

    print(f"\n  • Token Totali Processati     : {report['total_tokens_processed']}")
    print(f"  • Folii Unici Individuati     : {report['unique_folios']}")
    print(f"  • Coerenza Globale C*         : {report['global_metrics']['c_star_mean']} ± {report['global_metrics']['c_star_std']}")
    print(f"  • Carico Medio Z(t)          : {report['global_metrics']['z_t_mean']} ± {report['global_metrics']['z_t_std']}")
    print(f"  • Report JSON Esportato       : 'voynich_master_summary.json'")
    print(f"  • Tempo di Esecuzione         : {report['execution_time_sec']} s")
    print("=" * 80)