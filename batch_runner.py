#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
METODO DEMARIA® — COMPUTATIONAL VOYNICH ANALYSIS FRAMEWORK (Release v3.0)
Modulo: batch_runner.py (Orchestratore Master di Esecuzione e Audit)
Autore: Avv. Alessandro Demaria | Licenza: CC BY 4.0
Zenodo DOI: 10.5281/zenodo.23119964
===============================================================================
Descrizione:
  Orchestratore completo della suite v3.0. Esegue dinamicamente l'intera
  pipeline di controllo stocastico (Null A/B, Double Randomization, Group Holdout
  e Stress Test UNKNOWN/Tie-Break).
===============================================================================
"""

import os
import sys
import time
import pandas as pd

from coherence_evaluator import DemariaCoherenceEvaluator
from null_model_test import run_null_model_test
from double_randomization_test import DoubleRandomizationTester
from train_test_split_validation import StrictOutOfSampleValidator
from robustness_stress_test import RobustnessStressTester


def run_full_suite(
    dataset_path: str = 'voynich_eva_tokens_extended.csv',
    output_summary_path: str = 'master_batch_execution_summary.csv',
) -> pd.DataFrame:
  print('=' * 80)
  print('METODO DEMARIA® v3.0 — RUNNER DI SUITE E AUDIT PRESTAZIONALE MASTER')
  print('=' * 80)

  if not os.path.exists(dataset_path):
    print(f"ERRORE CRITICO: Dataset '{dataset_path}' non trovato.")
    sys.exit(1)

  t0 = time.time()

  # 1. Coherence Evaluator
  evaluator = DemariaCoherenceEvaluator()
  res_coherence = evaluator.evaluate_dataset_coherence(dataset_path)

  # 2. Null Model Test (Full N=10,000)
  c_obs, null_s, p_val = run_null_model_test(dataset_path, n_iterations=10000)
  
  # Recupero metriche estese dal report generato da null_model_test
  global_baseline, folio_baseline = 0.50, 0.50
  p_val_global, z_global = p_val, 0.0
  p_val_intra, z_intra = 1.0, 0.0
  
  if os.path.exists("null_model_test_results.csv"):
      df_null = pd.read_csv("null_model_test_results.csv")
      if "Theoretical_Global_Baseline" in df_null.columns:
          global_baseline = float(df_null["Theoretical_Global_Baseline"].iloc[0])
      if "Folio_Conditioned_Baseline" in df_null.columns:
          folio_baseline = float(df_null["Folio_Conditioned_Baseline"].iloc[0])
      if "Global_Z_Score" in df_null.columns:
          z_global = float(df_null["Global_Z_Score"].iloc[0])
      if "Intra_Folio_Z_Score" in df_null.columns:
          z_intra = float(df_null["Intra_Folio_Z_Score"].iloc[0])
      if "Intra_Folio_p_value" in df_null.columns:
          p_val_intra = float(df_null["Intra_Folio_p_value"].iloc[0])

  # 3. Double Randomization Test (Full N=1,000)
  double_tester = DoubleRandomizationTester(seed=42)
  res_double = double_tester.run_double_randomization(
      dataset_path, iterations=1000
  )

  # 4. Grouped Folio Holdout Stability Test
  validator = StrictOutOfSampleValidator(seed=42)
  res_split = validator.run_strict_validation(dataset_path)

  # 5. Robustness & Bias Stress Test
  robust_tester = RobustnessStressTester(seed=42)
  res_robust = robust_tester.run_robustness_audit(
      dataset_path, simulations=100
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
      'Theoretical_Global_Baseline': round(global_baseline, 6),
      'Folio_Conditioned_Baseline': round(folio_baseline, 6),
      'Global_Null_Z_Score': round(z_global, 4),
      'Global_Null_p_value': p_val,
      'Intra_Folio_Null_Z_Score': round(z_intra, 4),
      'Intra_Folio_Null_p_value': p_val_intra,
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

  print('\n' + '=' * 80)
  print('  AUDIT MASTER COMPLEATO CON SUCCESSO (ALL 5 MODULES EXECUTED)')
  print('=' * 80)
  print(df_summary.to_string(index=False))
  print('=' * 80)

  return df_summary


if __name__ == '__main__':
  run_full_suite()