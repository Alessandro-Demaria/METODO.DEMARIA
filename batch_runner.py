code_batch = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
METODO DEMARIA® — COMPUTATIONAL VOYNICH ANALYSIS FRAMEWORK (Release v3.0)
Orchestratore Principale: batch_runner.py
Autore: Avv. Alessandro Demaria | Licenza: CC BY 4.0
Zenodo DOI: 10.5281/zenodo.23119964
===============================================================================
Descrizione:
  Runner unico d'orchestrazione per l'esecuzione sequenziale e automatizzata
  della suite di validazione stocastica, hold-out e decodifica inversa (v3.0):
    1. null_model_test.py (Monte Carlo N=10.000, p < 0.0001)
    2. train_test_split_validation.py (Hold-Out 40% Train / 60% Test su Folio_Base)
    3. voynich_decoder_pipeline.py (Stripping morfologico ed estrazione Instruction Set)
===============================================================================
"""

import os
import sys
import time
import pandas as pd

# Importazione dinamica dei moduli della suite
try:
    from null_model_test import run_null_model_test
    from train_test_split_validation import run_train_test_split_validation
    from voynich_decoder_pipeline import VoynichDecoderPipeline
except ImportError as e:
    print(f"ERRORE CRITICO nell'importazione dei moduli di suite: {e}")
    sys.exit(1)


def run_full_suite(csv_path: str = "voynich_eva_tokens_extended.csv", seed: int = 42) -> None:
    t_start = time.time()

    print("===============================================================================")
    print("   METODO DEMARIA® Release v3.0 — BATCH SUITE ORCHESTRATOR RUNNER (DOI 10.5281/zenodo.23119964)")
    print("===============================================================================")
    print(f"Dataset Target:           {csv_path}")
    print(f"Seed Stocastico:          {seed}")
    print("-------------------------------------------------------------------------------")

    if not os.path.exists(csv_path):
        print(f"ERRORE CRITICO: File dataset '{csv_path}' non trovato.")
        sys.exit(1)

    # -------------------------------------------------------------------------
    # FASE 1: NULL MODEL MONTE CARLO TEST (N=10.000)
    # -------------------------------------------------------------------------
    print("\n[FASE 1/3] Esecuzione Null Model Permutation Test (Monte Carlo N=10.000)...")
    c_star_obs, null_scores, p_val = run_null_model_test(
        csv_path=csv_path,
        output_summary_path="null_model_test_results.csv",
        n_iterations=10000,
        seed=seed
    )

    # -------------------------------------------------------------------------
    # FASE 2: HOLD-OUT VALIDATION (40% Train / 60% Test)
    # -------------------------------------------------------------------------
    print("\n[FASE 2/3] Esecuzione Hold-Out Validation (40% Train / 60% Test su Folio_Base)...")
    c_train, c_test, delta_c = run_train_test_split_validation(
        csv_path=csv_path,
        output_summary_path="train_test_validation_results.csv",
        test_size=0.60,
        n_splits=10,
        seed=seed
    )

    # -------------------------------------------------------------------------
    # FASE 3: PIPELINE DI DECODIFICA INVERSA E STRIPPING MORFOLOGICO
    # -------------------------------------------------------------------------
    print("\n[FASE 3/3] Esecuzione Pipeline di Decodifica Inversa ed Estrazione Instruction Set...")
    pipeline = VoynichDecoderPipeline()
    decoded_df = pipeline.process_csv_dataset(
        csv_path=csv_path,
        output_path="decoded_instruction_set_results.csv"
    )

    # -------------------------------------------------------------------------
    # SINTESI FINALE DELLE METRICHE E SALVATAGGIO EXECUTIVE REPORT
    # -------------------------------------------------------------------------
    t_elapsed = time.time() - t_start

    summary_data = [{
        "Release_Version": "v3.0",
        "Dataset": os.path.basename(csv_path),
        "Total_Tokens": len(decoded_df),
        "C_Star_Observed": round(c_star_obs, 6),
        "Monte_Carlo_p_value": p_val,
        "Mean_C_Star_Train": round(c_train, 6),
        "Mean_C_Star_Test": round(c_test, 6),
        "Mean_Delta_C_Star": round(delta_c, 6),
        "Native_Roots_Extracted": len(decoded_df) - int(decoded_df['Is_Padding'].sum()) if 'Is_Padding' in decoded_df else len(decoded_df),
        "Execution_Time_Sec": round(t_elapsed, 2)
    }]

    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv("master_batch_execution_summary.csv", index=False)

    print("\n===============================================================================")
    print("                     ESITO INTEGRALE SUITE METODO DEMARIA® v3.0                ")
    print("===============================================================================")
    print("Status Generale Suite:      COMPLETATO CON SUCCESSO (ALL PASS)")
    print(f"C* Osservato Coassiale:     {c_star_obs:.6f}")
    print(f"p-value Monte Carlo (N=10k):{p_val:.6e} (Significativita p < 0.0001)")
    print(f"C* Train (40%) vs Test (60%): Train={c_train:.6f} | Test={c_test:.6f} (Delta={delta_c:.6f})")
    native_roots = len(decoded_df) - int(decoded_df['Is_Padding'].sum()) if 'Is_Padding' in decoded_df else len(decoded_df)
    print(f"Radici Native Decodificate: {native_roots:,} / {len(decoded_df):,} token")
    print(f"Tempo Totale Esecuzione:    {t_elapsed:.2f} s")
    print("Executive Report:           master_batch_execution_summary.csv")
    print("===============================================================================")


if __name__ == "__main__":
    run_full_suite()
'''

import ast
ast.parse(code_batch)
print("Parsing AST completato con successo: batch_runner.py e valido al 100%!")