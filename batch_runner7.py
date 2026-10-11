#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master-Validato)

Modulo 7 / Master Runner: batch_runner7.py
Esecutore centralizzato e sequenziale dell'intera Pipeline di Audit v3.3 (Fasi 1-9).

Sessione di Lavoro: BARVI
Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
Licenza Codebase: MIT License
Tutela Privativa e Marchio: Art. 98 D.Lgs. 30/2005 (CPI) / L. 633/1941
"""

import sys
import time
import pandas as pd
import numpy as np

from utils_preflight3 import PreFlightChecker
from core_parser1 import EVAParser
from core_matrix2 import MatrixManager
from audit_nullmodels4 import HierarchicalNullModelsAudit
from audit_doublerand5 import DoubleRandomizationAuditor
from audit_robustness6 import RobustnessStressTestAudit
from audit_holdout8 import HoldoutCrossValidationAudit
from audit_ablation9 import AblationAuditor


def run_master_audit_v33(dataset_path: str = "voynich_eva_tokens_extended.csv") -> None:
    """
    Esegue l'Audit Master Unificato v3.3 coprendo sequenzialmente le Fasi da 1 a 9.
    Risoluzione P0.5: Re-integrazione end-to-end senza omissioni di fasi o report.
    """
    start_time = time.time()
    print("=" * 80)
    print("   METODO DEMARIA® Release v3.3 - AUDIT MASTER UNIFICATO PIPELINE (FASI 1-9)")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # [FASE 1] PRE-FLIGHT SHA-256 CHECK
    # -------------------------------------------------------------------------
    print("\n[FASE 1] Pre-Flight SHA-256 & Dataset Verification...")
    checker = PreFlightChecker()
    res_preflight = checker.run_preflight_check(dataset_path, enforce_hard_stop=True)
    print(f" -> PASSED (SHA-256 Verified: {res_preflight['calculated_hash'][:16]}...)")
    df_raw = pd.read_csv(dataset_path)
    print(f" -> Dataset master caricato correttamente: {len(df_raw):,} token EVA.")

    # -------------------------------------------------------------------------
    # [FASE 2] PARSING DETERMINISTICO EVA
    # -------------------------------------------------------------------------
    print("\n[FASE 2] Parsing deterministico EVA vettoriale (Alpha, Beta, Delta, Gamma)...")
    parser = EVAParser()
    df_parsed = parser.parse_dataframe(df_raw)
    print(" -> Parsing deterministico completato.")

    # -------------------------------------------------------------------------
    # [FASE 3] MATRICE CANONICA 4x4 & COERENZA SINTATTICA (C_raw)
    # -------------------------------------------------------------------------
    print("\n[FASE 3] Matrice Canonica 4x4, Coerenza Sintattica (C_raw) & Entropia H(X)...")
    matrix_mgr = MatrixManager()
    res_harmony = matrix_mgr.compute_harmony_invariant(df_parsed, state_column="assigned_state", line_column="line_id")
    c_raw = res_harmony["c_raw"]
    shannon_entropy = res_harmony["shannon_entropy_bits"]
    print(f" -> Coerenza Sintattica Osservata (C_raw) : {c_raw:.6f} ({c_raw * 100.0:.2f}%)")
    print(f" -> Entropia di Primo Ordine H(X)       : {shannon_entropy:.4f} bit")

    # -------------------------------------------------------------------------
    # [FASE 4] MODELLI NULLI GERARCHICI MONTE CARLO (N=10.000)
    # -------------------------------------------------------------------------
    print("\n[FASE 4] Modelli Nulli Gerarchici Monte Carlo (N=10.000, Seed 42)...")
    null_inst = HierarchicalNullModelsAudit(iterations=10000, seed=42)
    null_results = null_inst.run_full_hierarchical_audit(df_parsed)
    
    g_null = null_results.get("global_null", {})
    f_null = null_results.get("intra_folio_null", {})
    l_null = null_results.get("intra_line_null", {})

    print(f" -> Model 1 (Global Null)     : Z = {g_null.get('z_score', 0.0):+.4f} | p = {g_null.get('p_value_empirical', 1.0):.6f}")
    print(f" -> Model 2 (Intra-Folio Null): Z = {f_null.get('z_score', 0.0):+.4f} | p = {f_null.get('p_value_empirical', 1.0):.6f}")
    print(f" -> Model 3 (Intra-Line Null) : Z = {l_null.get('z_score', 0.0):+.4f} | p = {l_null.get('p_value_empirical', 1.0):.6f} [SMOKING GUN]")

    # -------------------------------------------------------------------------
    # [FASE 5] TEST DOPPIA RANDOMIZZAZIONE ISOMORFA
    # -------------------------------------------------------------------------
    print("\n[FASE 5] Test Avversariale Isomorfo di Doppia Randomizzazione (N=10.000)...")
    rand_inst = DoubleRandomizationAuditor(matrix_mgr)
    double_rand_res = rand_inst.run_double_randomization_test(df_parsed, iterations=10000, seed=42)
    print(f" -> Double Null Z-Score        : {double_rand_res.get('z_score', 0.0):+.4f}")
    print(f" -> Empirical p-value          : {double_rand_res.get('p_value_empirical', 1.0):.6f}")

    # -------------------------------------------------------------------------
    # [FASE 6] STRESS TEST RUMORE SINTATTICO (0% -> 30%)
    # -------------------------------------------------------------------------
    print("\n[FASE 6] Stress Test di Sensibilità e Resilienza al Rumore Sintattico...")
    rob_inst = RobustnessStressTestAudit(iterations_per_level=100, seed=42)
    robustness_res = rob_inst.run_robustness_test(df_parsed)
    df_rob_summary = pd.DataFrame(robustness_res["levels_summary"])
    df_rob_summary.to_csv("robustness_test_results.csv", index=False)
    print(" -> Report di robustezza esportato in 'robustness_test_results.csv'.")

    # -------------------------------------------------------------------------
    # [FASE 7] VALIDAZIONE OUT-OF-SAMPLE HOLDOUT & MONTE CARLO CV
    # -------------------------------------------------------------------------
    print("\n[FASE 7] Validazione Fuori Campione Holdout 50/50 e Cross-Validation Monte Carlo...")
    holdout_inst = HoldoutCrossValidationAudit(iterations=1000, seed=42)
    holdout_res = holdout_inst.run_full_holdout_audit(df_parsed)
    det_split = holdout_res["deterministic_split"]
    print(f" -> Holdout Deterministico 50/50 : Train C = {det_split['c_train']:.6f} | Test C = {det_split['c_test']:.6f} | Delta C = {det_split['delta_c']:.6f}")
    print(f" -> Report holdout esportato in '{holdout_res['report_path']}'.")

    # -------------------------------------------------------------------------
    # [FASE 8] TEST DI ABLAZIONE DELLE REGOLE & BENCHMARK PARSER CASUALI
    # -------------------------------------------------------------------------
    print("\n[FASE 8] Test di Ablazione Selettiva e Benchmark su 1.000 Parser Casuali...")
    ablation_inst = AblationAuditor(matrix_mgr)
    ablation_res = ablation_inst.run_full_ablation_audit(df_parsed)
    rand_bench = ablation_res["random_parsers_benchmark"]
    print(f" -> Benchmark Parser Casuali   : Z = {rand_bench['z_score']:+.4f} | Empirical p = {rand_bench['p_value_empirical']:.6f}")
    print(f" -> Report ablazione esportato in '{ablation_res['report_path']}'.")

    # -------------------------------------------------------------------------
    # [FASE 9] ESPORTAZIONE REPORT MASTER FINALE v3.3
    # -------------------------------------------------------------------------
    print("\n[FASE 9] Esportazione Report Master Finale Unificato v3.3...")
    master_summary = {
        "Release": "v3.3 (Audit-Master-Validato)",
        "C_raw_observed": c_raw,
        "C_raw_percentage": c_raw * 100.0,
        "Shannon_Entropy_bits": shannon_entropy,
        "Global_Null_Mean": g_null.get("null_mean", 0.0),
        "Global_Null_ZScore": g_null.get("z_score", 0.0),
        "Global_Null_p_value": g_null.get("p_value_empirical", 0.0),
        "Folio_Null_Mean": f_null.get("null_mean", 0.0),
        "Folio_Null_ZScore": f_null.get("z_score", 0.0),
        "Folio_Null_p_value": f_null.get("p_value_empirical", 0.0),
        "Line_Null_Mean": l_null.get("null_mean", 0.0),
        "Line_Null_ZScore": l_null.get("z_score", 0.0),
        "Line_Null_p_value": l_null.get("p_value_empirical", 0.0),
        "Double_Null_ZScore": double_rand_res.get("z_score", 0.0),
        "Double_Null_p_value_empirical": double_rand_res.get("p_value_empirical", 0.0),
        "Holdout_Delta_C": det_split["delta_c"],
        "Random_Parsers_ZScore": rand_bench["z_score"]
    }
    
    pd.DataFrame([master_summary]).to_csv("audit_master_summary_results.csv", index=False)
    
    elapsed = time.time() - start_time
    print("=" * 80)
    print(f"   ESECUZIONE MASTER AUDIT SUITE V3.3 COMPLETATA IN {elapsed:.2f} SECONDI!")
    print("   TUTTI I REPORT CSV CONGELATI CON SUCCESSO NELLA DIRECTORY DI LABORATORIO.")
    print("=" * 80)


if __name__ == "__main__":
    run_master_audit_v33()