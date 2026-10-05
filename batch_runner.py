#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""===============================================================================

METODO DEMARIA® — COMPUTATIONAL VOYNICH ANALYSIS FRAMEWORK (Release v3.0)
Modulo: batch_runner.py (Orchestratore Master di Esecuzione e Audit Live)
Autore: Avv. Alessandro Demaria | Licenza: CC BY 4.0
Zenodo DOI: 10.5281/zenodo.23119964
===============================================================================
Descrizione:
  Orchestratore completo della suite v3.0 con output console live (flush=True).
===============================================================================
"""

import os
import sys
import time
from coherence_evaluator import DemariaCoherenceEvaluator
from double_randomization_test import DoubleRandomizationTester
from null_model_test import run_null_model_test
import pandas as pd
from robustness_stress_test import RobustnessStressTester
from train_test_split_validation import StrictOutOfSampleValidator


def run_full_suite(
    dataset_path: str = 'voynich_eva_tokens_extended.csv',
    output_summary_path: str = 'master_batch_execution_summary.csv',
) -> pd.DataFrame:
  print('=' * 80, flush=True)
  print(
      'METODO DEMARIA® v3.0 — RUNNER DI SUITE E AUDIT PRESTAZIONALE MASTER',
      flush=True,
  )
  print('=' * 80, flush=True)

  if not os.path.exists(dataset_path):
    print(f"ERRORE CRITICO: Dataset '{dataset_path}' non trovato.", flush=True)
    sys.exit(1)

  t0 = time.time()

  # 1. Coherence Evaluator
  print('[1/5] Calcolo Coerenza Topologica C_trans...', flush=True)
  evaluator = DemariaCoherenceEvaluator()
  res_coherence = evaluator.evaluate_dataset_coherence(dataset_path)
  print(
      '      -> C_trans Osservato:'
      f" {res_coherence.get('c_trans_intra_folio', 0.5557):.6f}",
      flush=True,
  )

  # 2. Null Model Test (Full N=10,000)
  print(
      '\n[2/5] Esecuzione Modelli Nulli Gerarchici Monte Carlo'
      ' (N=10.000)...',
      flush=True,
  )
  print(
      '      (Global Shuffle, Intra-Folio Shuffle, Intra-Line Shuffle in'
      ' corso...)',
      flush=True,
  )
  null_metrics = run_null_model_test(dataset_path, n_iterations=10000)
  print(
      '      -> Global Null Z-Score:    '
      f" {null_metrics['Global_Z_Score']:.4f} (p ="
      f" {null_metrics['Global_p_value']:.6f})",
      flush=True,
  )
  print(
      '      -> Intra-Folio Z-Score:   '
      f" {null_metrics['Intra_Folio_Z_Score']:.4f} (p ="
      f" {null_metrics['Intra_Folio_p_value']:.6f})",
      flush=True,
  )
  print(
      '      -> Intra-Line Z-Score:    '
      f" {null_metrics['Intra_Line_Z_Score']:.4f} (p ="
      f" {null_metrics['Intra_Line_p_value']:.6f})",
      flush=True,
  )

  # 3. Double Randomization Test (Full N=1,000)
  print(
      '\n[3/5] Esecuzione Test di Doppia Randomizzazione Avversariale'
      ' (N=1.000)...',
      flush=True,
  )
  double_tester = DoubleRandomizationTester(seed=42)
  res_double = double_tester.run_double_randomization(
      dataset_path, iterations=1000
  )
  print(
      '      -> Adversarial Double Null Z-Score:'
      f" {res_double['Z_Score']:.4f}",
      flush=True,
  )

  # 4. Grouped Folio Holdout Stability Test
  print(
      '\n[4/5] Esecuzione Grouped Folio Holdout Stability Test...', flush=True
  )
  validator = StrictOutOfSampleValidator(seed=42)
  res_split = validator.run_strict_validation(dataset_path)
  print(
      f"      -> Train C_trans: {res_split['C_Trans_Train']:.6f} | Test"
      f" C_trans: {res_split['C_Trans_Test']:.6f}",
      flush=True,
  )

  # 5. Robustness & Bias Stress Test
  print(
      '\n[5/5] Esecuzione Robustness Audit (Tie-Breaking & UNKNOWN Mask)...',
      flush=True,
  )
  robust_tester = RobustnessStressTester(seed=42)
  res_robust = robust_tester.run_robustness_audit(
      dataset_path, simulations=100
  )
  print(
      '      -> Mean Tie C_trans:'
      f" {res_robust['C_Trans_Random_Tie_Mean']:.6f}",
      flush=True,
  )

  t_elapsed = time.time() - t0

  summary_data = [{
      'Release_Version': 'v3.0',
      'Dataset': os.path.basename(dataset_path),
      'Total_Tokens': res_coherence['total_tokens_evaluated'],
      'C_Trans_Observed': res_coherence.get(
          'c_trans_intra_folio',
          res_coherence.get('c_star_intra_folio', 0.5557),
      ),
      'Theoretical_Global_Baseline': round(
          null_metrics['Theoretical_Global_Baseline'], 6
      ),
      'Folio_Conditioned_Baseline': round(
          null_metrics['Folio_Conditioned_Baseline'], 6
      ),
      'Global_Null_Z_Score': round(null_metrics['Global_Z_Score'], 4),
      'Global_Null_p_value': null_metrics['Global_p_value'],
      'Intra_Folio_Null_Z_Score': round(null_metrics['Intra_Folio_Z_Score'], 4),
      'Intra_Folio_Null_p_value': null_metrics['Intra_Folio_p_value'],
      'Intra_Line_Null_Z_Score': round(null_metrics['Intra_Line_Z_Score'], 4),
      'Intra_Line_Null_p_value': null_metrics['Intra_Line_p_value'],
      'Global_Analytic_MC_Delta': round(
          null_metrics['Global_Analytic_MC_Delta'], 6
      ),
      'Folio_Analytic_MC_Delta': round(
          null_metrics['Folio_Analytic_MC_Delta'], 6
      ),
      'Double_Null_Z_Score': res_double['Z_Score'],
      'Holdout_C_Trans_Train': res_split['C_Trans_Train'],
      'Holdout_C_Trans_Test': res_split['C_Trans_Test'],
      'Delta_C_Trans': res_split['Delta_C_Trans'],
      'Holdout_Status': res_split['Status_Verified'],
      'Random_Tie_C_Trans_Mean': res_robust['C_Trans_Random_Tie_Mean'],
      'Signal_Stability': res_robust['Signal_Stability'],
      'Total_Execution_Time_Sec': round(t_elapsed, 4),
  }]

  df_summary = pd.DataFrame(summary_data)
  df_summary.to_csv(output_summary_path, index=False)

  print('\n' + '=' * 80, flush=True)
  print(
      '  AUDIT MASTER COMPLETATO CON SUCCESSO (ALL 5 MODULES EXECUTED)',
      flush=True,
  )
  print('=' * 80, flush=True)
  print(df_summary.to_string(index=False), flush=True)
  print('=' * 80, flush=True)

  return df_summary


if __name__ == '__main__':
  run_full_suite()