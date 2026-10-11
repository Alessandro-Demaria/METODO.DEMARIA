#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Modulo 7: batch_runner7.py
Orchestratore Master unificato per l'esecuzione dinamica end-to-end dell'intera suite
di laboratorio, la riproducibilità popperiana sui dati reali e l'esportazione dei report CSV.

Autore: Avv. Alessandro Demaria
Licenza Codebase: MIT License
Tutela Privativa e Marchio: Art. 98 D.Lgs. 30/2005 (CPI) / L. 633/1941
"""

import sys
import os
import time
import pandas as pd
from typing import Dict, Any

# Importazione dinamica dei moduli funzionali della suite
from utils_preflight3 import PreFlightChecker
from core_parser1 import EVAParser
from core_matrix2 import TransitionMatrixManager
from audit_nullmodels4 import HierarchicalNullModelsAudit
from audit_doublerand5 import IsomorphicDoubleRandomizationAudit
from audit_robustness6 import RobustnessStressTestAudit


class MasterBatchRunner:
    """
    Orchestratore Master del METODO DEMARIA®. Esegue in sequenza e in tempo reale
    l'intera pipeline computazionale sul dataset master senza fare uso di costanti hardcoded.
    """

    DATASET_PATH: str = "voynich_eva_tokens_extended.csv"
    SUMMARY_REPORT_PATH: str = "audit_master_summary_results.csv"
    ROBUSTNESS_REPORT_PATH: str = "robustness_test_results.csv"

    def __init__(self, iterations_null: int = 10000, iterations_robustness: int = 100, seed: int = 42) -> None:
        """
        Inizializza l'Orchestratore Master fissando i parametri stocastici di esecuzione.
        """
        self.iterations_null: int = iterations_null
        self.iterations_robustness: int = iterations_robustness
        self.seed: int = seed

    def execute_full_audit(self) -> None:
        """
        Esegue la pipeline di audit end-to-end dinamica sul dataset master.
        """
        start_time: float = time.time()
        print("================================================================================")
        print("         LABORATORIO SCIENTIFICO METODO DEMARIA® - RELEASE v3.3                 ")
        print("                 AUDIT-MASTER UNIFICATO END-TO-END                              ")
        print("================================================================================\n")

        # -----------------------------------------------------------------------------
        # FASE 0: PRE-FLIGHT CHECK (INTEGRITÀ CRITTOGRAFICA SHA-256)
        # -----------------------------------------------------------------------------
        print("[FASE 0/6] Esecuzione Pre-Flight Check Crittografico SHA-256...")
        try:
            preflight_res: Dict[str, Any] = PreFlightChecker.run_preflight_check(
                self.DATASET_PATH, enforce_hard_stop=True
            )
            print(f" -> STATO: {preflight_res['status']}")
            print(f" -> HASH SHA-256: {preflight_res['calculated_hash']}")
            print(f" -> TOKEN TOTALI: {preflight_res['token_count']}\n")
        except Exception as e:
            print(f"\n[CRITICAL ERROR] Interruzione della pipeline: {str(e)}")
            sys.exit(1)

        # -----------------------------------------------------------------------------
        # FASE 1: PARSING E MAPPTATURA DEGLI STATI MINIMI
        # -----------------------------------------------------------------------------
        print("[FASE 1/6] Caricamento Dataset e Mappatura Vettoriale del Corpus (EVA -> 4 Stati)...")
        df_raw: pd.DataFrame = pd.read_csv(self.DATASET_PATH)
        parser: EVAParser = EVAParser()
        df_parsed: pd.DataFrame = parser.parse_dataframe(df_raw)
        print(" -> Mappatura completata con successo.")
        print(f" -> Folii unici elaborati: {df_parsed['folio'].nunique()}")
        print(f" -> Coordinate di rigo (line_id) create: {df_parsed['line_id'].nunique()}\n")

        # -----------------------------------------------------------------------------
        # FASE 2: MATRICE CANONICA 4x4 E COERENZA GREZZA (Craw)
        # -----------------------------------------------------------------------------
        print("[FASE 2/6] Calcolo della Coerenza Sintattica Grezza (Craw) e dell'Invariante...")
        matrix_mgr: TransitionMatrixManager = TransitionMatrixManager()
        c_raw, valid_t, total_t = matrix_mgr.compute_raw_coherence(df_parsed)
        harmony_res: Dict[str, Any] = matrix_mgr.compute_harmony_invariant(df_parsed)
        
        print(f" -> Transizioni Intrarigo Valide: {valid_t} / {total_t}")
        print(f" -> Coerenza Sintattica Grezza (Craw): {c_raw:.6f} ({c_raw * 100:.2f}%)")
        print(f" -> Invariante di Armonia (Phi_alpha): {harmony_res['harmony_invariant_phi']:.6f}")
        print(f" -> Entropia di Shannon H(X): {harmony_res['shannon_entropy_bits']:.4f} bit\n")

        # -----------------------------------------------------------------------------
        # FASE 3: MODELLI NULLI GERARCHICI MONTE CARLO
        # -----------------------------------------------------------------------------
        print(f"[FASE 3/6] Audit Stocastico Modelli Nulli Gerarchici (N={self.iterations_null}, Seed={self.seed})...")
        null_audit: HierarchicalNullModelsAudit = HierarchicalNullModelsAudit(
            iterations=self.iterations_null, seed=self.seed
        )
        null_results: Dict[str, Dict[str, Any]] = null_audit.run_full_hierarchical_audit(df_parsed)

        for key, res in null_results.items():
            print(f"  * {res['model_name']}:")
            print(f"    - Media C_null: {res['null_mean']:.6f} | Dev.Std: {res['null_std']:.6f}")
            print(f"    - Z-Score     : {res['z_score']:+.4f}")
            print(f"    - p-value     : {res['p_value_empirical']:.6f} (Conteggio superamenti: {res['count_exceeding']})")
        print()

        # -----------------------------------------------------------------------------
        # FASE 4: TEST AVVERSARIALE DI DOPPIA RANDOMIZZAZIONE ISOMORFA
        # -----------------------------------------------------------------------------
        print(f"[FASE 4/6] Audit Avversariale Doppia Randomizzazione Isomorfa (N={self.iterations_null}, Seed={self.seed})...")
        double_audit: IsomorphicDoubleRandomizationAudit = IsomorphicDoubleRandomizationAudit(
            iterations=self.iterations_null, seed=self.seed
        )
        double_res: Dict[str, Any] = double_audit.run_double_randomization_test(df_parsed)
        
        print(f" -> Media Doppio Nullo: {double_res['double_null_mean']:.6f} | Dev.Std: {double_res['double_null_std']:.6f}")
        print(f" -> Double-Null Z-Score: {double_res['z_double_score']:+.4f}")
        print(f" -> p-value empirico  : {double_res['p_value_empirical']:.6f}\n")

        # -----------------------------------------------------------------------------
        # FASE 5: STRESS TEST DI SENSIBILITÀ AL RUMORE SINTATTICO
        # -----------------------------------------------------------------------------
        print(f"[FASE 5/6] Stress Test di Sensibilità al Rumore Sintattico (0.0% -> 30.0%)...")
        robustness_audit: RobustnessStressTestAudit = RobustnessStressTestAudit(
            iterations_per_level=self.iterations_robustness, seed=self.seed
        )
        robustness_res: Dict[str, Any] = robustness_audit.run_robustness_test(df_parsed)

        for lvl in robustness_res["levels_summary"]:
            print(f"  * Rumore {lvl['noise_level_pct']:5.1f}% | Craw' Medio: {lvl['c_raw_mean']:.6f} "
                  f"| Ritenzione: {lvl['retention_pct']:6.2f}% | Diagnosi: {lvl['diagnosis']}")
        print()

        # -----------------------------------------------------------------------------
        # FASE 6: ESPORTAZIONE AUTOMATICA DEI REPORT CSV
        # -----------------------------------------------------------------------------
        print("[FASE 6/6] Esportazione dei Report CSV di Audit...")
        
        # 1. Report Sintetico Master
        summary_data = [
            {"Metric_Name": "Dataset_Tokens", "Value": preflight_res['token_count']},
            {"Metric_Name": "Observed_Craw", "Value": c_raw},
            {"Metric_Name": "Harmony_Invariant_Phi", "Value": harmony_res['harmony_invariant_phi']},
            {"Metric_Name": "Shannon_Entropy_Bits", "Value": harmony_res['shannon_entropy_bits']},
            {"Metric_Name": "Model1_Global_Null_Mean", "Value": null_results['global_null']['null_mean']},
            {"Metric_Name": "Model1_Global_Z_Score", "Value": null_results['global_null']['z_score']},
            {"Metric_Name": "Model1_Global_P_Value", "Value": null_results['global_null']['p_value_empirical']},
            {"Metric_Name": "Model2_IntraFolio_Null_Mean", "Value": null_results['intra_folio_null']['null_mean']},
            {"Metric_Name": "Model2_IntraFolio_Z_Score", "Value": null_results['intra_folio_null']['z_score']},
            {"Metric_Name": "Model2_IntraFolio_P_Value", "Value": null_results['intra_folio_null']['p_value_empirical']},
            {"Metric_Name": "Model3_IntraLine_Null_Mean", "Value": null_results['intra_line_null']['null_mean']},
            {"Metric_Name": "Model3_IntraLine_Z_Score", "Value": null_results['intra_line_null']['z_score']},
            {"Metric_Name": "Model3_IntraLine_P_Value", "Value": null_results['intra_line_null']['p_value_empirical']},
            {"Metric_Name": "DoubleRandomization_Null_Mean", "Value": double_res['double_null_mean']},
            {"Metric_Name": "DoubleRandomization_Z_Score", "Value": double_res['z_double_score']},
            {"Metric_Name": "DoubleRandomization_P_Value", "Value": double_res['p_value_empirical']},
        ]
        df_summary = pd.DataFrame(summary_data)
        df_summary.to_csv(self.SUMMARY_REPORT_PATH, index=False)
        print(f" -> Salvato: '{self.SUMMARY_REPORT_PATH}'")

        # 2. Report Stress Test Robustezza
        df_robustness = pd.DataFrame(robustness_res["levels_summary"])
        df_robustness.to_csv(self.ROBUSTNESS_REPORT_PATH, index=False)
        print(f" -> Salvato: '{self.ROBUSTNESS_REPORT_PATH}'\n")

        elapsed: float = time.time() - start_time
        print("================================================================================")
        print(f"AUDIT COMPUTAZIONALE COMPLETATO CON SUCCESSO IN {elapsed:.2f} SECONDI")
        print("RISULTATI DINAMICI 100% RIPRODUCIBILI ED ESPOPORTATI SUL DISCO DI LABORATORIO.")
        print("================================================================================\n")


if __name__ == "__main__":
    # Esecuzione dell'Orchestratore Master
    runner = MasterBatchRunner(iterations_null=10000, iterations_robustness=100, seed=42)
    runner.execute_full_audit()