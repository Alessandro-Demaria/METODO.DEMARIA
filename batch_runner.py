#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
METODO DEMARIA® — COMPUTATIONAL VOYNICH ANALYSIS FRAMEWORK (Release v3.0)
Modulo: batch_runner.py (Orchestratore di Esecuzione Batch)
Autore: Avv. Alessandro Demaria
===============================================================================
Descrizione:
  Orchestratore principale che esegue in sequenza la pipeline completa:
  Parsing -> Core Algorithm -> Null Model Monte Carlo -> Structural Decoder
  leggendo unicamente il dataset unificato voynich_eva_tokens_extended.csv.
===============================================================================
"""

import time
import pandas as pd
from typing import Dict, Any

from voynich_parser import VoynichParserV3
from voynich_core_algorithm import run_canonical_evaluation
from null_model_runner import DemariaNullModelSuite
from voynich_decoder_pipeline import VoynichDecoderPipeline


class DemariaBatchRunner:
    """
    Orchestrator per l'esecuzione batch e la reportistica integrata.
    """
    def __init__(self, csv_path: str = 'voynich_eva_tokens_extended.csv'):
        self.csv_path = csv_path

    def run_full_pipeline_batch(self, mc_iterations: int = 10000) -> Dict[str, Any]:
        """
        Esegue la pipeline completa in sequenza sui dati reali.
        """
        t_start = time.time()
        
        # 1. Verification & Parsing
        parser = VoynichParserV3()
        records = parser.parse_csv_dataset(self.csv_path)
        n_tokens = len(records)

        # 2. Core Algorithm Evaluation
        df_core = run_canonical_evaluation(self.csv_path)
        mean_c_star = float(df_core['C_star_computed'].mean())

        # 3. Monte Carlo Surrogate Test
        null_suite = DemariaNullModelSuite(seed=42)
        mc_results = null_suite.run_monte_carlo_test(self.csv_path, iterations=mc_iterations)

        # 4. Structural Decoding
        decoder = VoynichDecoderPipeline()
        df_decoded = decoder.process_csv_dataset(self.csv_path)
        padding_count = int(df_decoded['Is_Padding'].sum())

        t_total = time.time() - t_start

        return {
            'status': 'SUCCESS',
            'total_tokens_processed': n_tokens,
            'mean_computed_c_star': round(mean_c_star, 4),
            'monte_carlo_p_value': mc_results['p_value_empirical'],
            'padding_tokens_found': padding_count,
            'native_tokens_found': n_tokens - padding_count,
            'total_execution_time_sec': round(t_total, 4)
        }


if __name__ == '__main__':
    print("=" * 80)
    print("METODO DEMARIA® — ESECUZIONE BATCH PIPELINE INTEGRATA (Release v3.0)")
    print("=" * 80)

    runner = DemariaBatchRunner('voynich_eva_tokens_extended.csv')
    report = runner.run_full_pipeline_batch(mc_iterations=10000)

    print(f"\n[✓] STATO ESECUZIONE        : {report['status']}")
    print(f"  • Token Reali Processati   : {report['total_tokens_processed']}")
    print(f"  • Coerenza Media C*        : {report['mean_computed_c_star']}")
    print(f"  • p-value Monte Carlo      : {report['monte_carlo_p_value']}")
    print(f"  • Token di Padding Automa  : {report['padding_tokens_found']}")
    print(f"  • Nuclei Morfologici Nativi: {report['native_tokens_found']}")
    print(f"  • Tempo Totale Pipeline    : {report['total_execution_time_sec']} s")
    print("=" * 80)