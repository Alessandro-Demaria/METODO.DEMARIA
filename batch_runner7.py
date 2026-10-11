#!/usr/bin/env python3
"""
LABORATORIO SCIENTIFICO METODO DEMARIA™ - RELEASE v3.3 (AUDIT-MASTER UNIFICATO)

Modulo: batch_runner7.py
Descrizione: Master Orchestrator unico e definitivo per l'esecuzione in batch
             della Master Audit Suite v3.3 del METODO DEMARIA™.
Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
"""

import sys
import os
import json
import pandas as pd

from utils_preflight3 import PreflightIntegrityAudit
from core_parser1 import EVAParser
from core_matrix2 import BinaryAdmissibilityMatrix
from audit_nullmodels4 import HierarchicalNullModelsAudit
from audit_doublerand5 import DoubleRandomizationAudit
from audit_robustness6 import RobustnessStressTestAudit
from audit_holdout8 import HoldoutValidationAudit
from audit_ablation9 import RuleAblationAudit


class MasterBatchRunner:
    """
    Master Orchestrator della Release v3.3.
    Gestisce l'esecuzione sequenziale di tutte le fasi dell'audit
    garantendo la coerenza dei dati e l'esportazione dei report.
    """

    def __init__(self, dataset_path="voynich_eva_tokens_extended.csv", seed=42):
        self.dataset_path = dataset_path
        self.seed = seed
        self.audit_results = {}

    def run_master_pipeline(self):
        print("===================================================================")
        print(" LABORATORIO SCIENTIFICO METODO DEMARIA™ - RELEASE v3.3")
        print(" MASTER AUDIT SUITE - ESECUZIONE ORCHESTRATA UNIFICATA")
        print("===================================================================\n")

        # FASE 1: Preflight Integrity Audit
        print("[FASE 1/9] Esecuzione Preflight Integrity Check...")
        preflight = PreflightIntegrityAudit()
        preflight_status = preflight.run_preflight_checks()
        if not preflight_status.get("status") == "SUCCESS":
            print("[-] CRITICO: Preflight Check Fallito. Interruzione pipeline.")
            sys.exit(1)
        print("[+] FASE 1 Completata: Integrità preflight VERIFICATA.\n")

        # FASE 2: Caricamento e Normalizzazione Canonica Dati (P0.2 / P0.3)
        print("[FASE 2/9] Caricamento Dataset e Normalizzazione Coordinate...")
        if not os.path.exists(self.dataset_path):
            print(f"[-] CRITICO: File dataset '{self.dataset_path}' non trovato.")
            sys.exit(1)

        df_raw = pd.read_csv(self.dataset_path)

        # Scomposizione e normalizzazione canonica degli identificativi
        df_raw["folio_id"] = df_raw["Folio"].astype(str).apply(lambda x: x.split(".")[0])
        df_raw["line_number"] = df_raw["Folio"].astype(str).apply(
            lambda x: x.split(".")[1].split(",")[0] if "." in x else "1"
        )
        df_raw["line_id"] = df_raw["folio_id"] + "." + df_raw["line_number"]
        df_raw["folio"] = df_raw["folio_id"]
        print(f"[+] FASE 2 Completata: Processati {len(df_raw)} record su {df_raw['folio_id'].nunique()} folii unici.\n")

        # FASE 3: Parsing Vettoriale dei Token EVA
        print("[FASE 3/9] Esecuzione Parsing Vettoriale (EVA -> Quadrupla Stati)...")
        parser = EVAParser()
        df_parsed = parser.parse_dataframe(df_raw)
        print("[+] FASE 3 Completata: Parsing vettoriale eseguito con successo.\n")

        # FASE 4: Matrice di Ammissibilità e Baseline Craw
        print("[FASE 4/9] Calcolo Matrice 4x4 e Baseline Coerenza Sintattica Reale (Craw)...")
        matrix_mgr = BinaryAdmissibilityMatrix()
        c_raw = matrix_mgr.compute_corpus_coherence(df_parsed)
        self.audit_results["c_raw"] = c_raw
        print(f"[+] FASE 4 Completata: Baseline Craw = {c_raw:.6f} ({c_raw*100:.2f}%)\n")

        # FASE 5: Modelli Nulli Gerarchici Monte Carlo (N=10.000)
        print("[FASE 5/9] Esecuzione Modelli Nulli Gerarchici Monte Carlo (N=10.000)...")
        null_audit = HierarchicalNullModelsAudit(iterations=10000, seed=self.seed)
        null_results = null_audit.run_full_hierarchical_audit(df_parsed, matrix_mgr)
        self.audit_results["null_models"] = null_results
        print("[+] FASE 5 Completata: Modelli Nulli Gerarchici eseguiti.\n")

        # FASE 6: Test Avversariale Isomorfo di Doppia Randomizzazione
        print("[FASE 6/9] Esecuzione Isomorphic Double Randomization Test (N=10.000)...")
        double_rand = DoubleRandomizationAudit(iterations=10000, seed=self.seed)
        double_rand_results = double_rand.run_double_randomization_test(df_parsed, matrix_mgr)
        self.audit_results["double_randomization"] = double_rand_results
        print("[+] FASE 6 Completata: Double Randomization Test eseguito.\n")

        # FASE 7: Robustness & Noise Sensitivity Stress Test
        print("[FASE 7/9] Esecuzione Robustness & Stress Test (Iniezione Rumore 0%-30%)...")
        robustness = RobustnessStressTestAudit(iterations_per_level=100, seed=self.seed)
        robustness_results = robustness.run_robustness_test(df_parsed, matrix_mgr, parser)
        self.audit_results["robustness"] = robustness_results
        print("[+] FASE 7 Completata: Stress Test di Robustezza eseguito.\n")

        # FASE 8: Spatial Stability Holdout Validation (50%/50%)
        print("[FASE 8/9] Esecuzione Folio-Split Spatial Stability Holdout Validation...")
        holdout = HoldoutValidationAudit(test_size=0.5, seed=self.seed)
        holdout_results = holdout.run_holdout_validation(df_parsed, matrix_mgr)
        self.audit_results["holdout"] = holdout_results
        print("[+] FASE 8 Completata: Validazione Holdout eseguita.\n")

        # FASE 9: Rule Ablation & Random Parser Benchmarking
        print("[FASE 9/9] Esecuzione Rule Ablation & Random Parser Benchmark...")
        ablation = RuleAblationAudit(seed=self.seed)
        ablation_results = ablation.run_ablation_suite(df_parsed, matrix_mgr, parser)
        self.audit_results["ablation"] = ablation_results
        print("[+] FASE 9 Completata: Ablation Audit eseguito.\n")

        print("===================================================================")
        print(" MASTER AUDIT SUITE v3.3 COMPLETATA CON SUCCESSO")
        print(" Tutti i moduli sono riallineati, eseguiti e verificati.")
        print("===================================================================")
        return self.audit_results


if __name__ == "__main__":
    runner = MasterBatchRunner(seed=42)
    results = runner.run_master_pipeline()