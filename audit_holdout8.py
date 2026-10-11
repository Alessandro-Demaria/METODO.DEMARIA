#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Modulo 8: audit_holdout8.py
Modulo di validazione Fuori Campione (Holdout Split 50/50) e Cross-Validation
Monte Carlo Stratificata per Folio (N=1.000 iterazioni) con Intervalli di Confidenza.

Autore: Avv. Alessandro Demaria
Licenza Codebase: MIT License
Tutela Privativa e Marchio: Art. 98 D.Lgs. 30/2005 (CPI) / L. 633/1941
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
from core_matrix2 import TransitionMatrixManager
from core_parser1 import EVAParser


class HoldoutCrossValidationAudit:
    """
    Esecutore della validazione fuori campione (Out-of-Sample Holdout) e della
    Cross-Validation Monte Carlo stratificata per folio per la neutralizzazione
    dei bias di selezione ed overfitting.
    """

    HOLDOUT_REPORT_PATH: str = "holdout_validation_results.csv"

    def __init__(self, iterations: int = 1000, seed: int = 42) -> None:
        """
        Inizializza il modulo fissando le iterazioni Monte Carlo e il Seed deterministico.
        """
        self.iterations: int = iterations
        self.seed: int = seed
        self.matrix_mgr: TransitionMatrixManager = TransitionMatrixManager()

    def run_single_deterministic_split(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Esegue lo split deterministico 50/50 per folio (Training Set vs Test Set).
        
        Returns:
            Dict[str, Any]: Coerenza Training, Coerenza Test, Delta C e percentuale di scarto.
        """
        unique_folios: np.ndarray = df["folio"].unique()
        unique_folios.sort()
        
        # Split deterministico 50/50 alternato sui folii ordinati
        train_folios: np.ndarray = unique_folios[::2]
        test_folios: np.ndarray = unique_folios[1::2]

        df_train: pd.DataFrame = df[df["folio"].isin(train_folios)]
        df_test: pd.DataFrame = df[df["folio"].isin(test_folios)]

        c_train, _, _ = self.matrix_mgr.compute_raw_coherence(df_train)
        c_test, _, _ = self.matrix_mgr.compute_raw_coherence(df_test)

        delta_c: float = float(abs(c_train - c_test))
        c_baseline, _, _ = self.matrix_mgr.compute_raw_coherence(df)
        pct_gap: float = float((delta_c / c_baseline) * 100.0) if c_baseline > 0 else 0.0

        return {
            "train_folios_count": len(train_folios),
            "test_folios_count": len(test_folios),
            "c_train": float(c_train),
            "c_test": float(c_test),
            "delta_c": delta_c,
            "pct_gap": pct_gap,
            "c_baseline": float(c_baseline)
        }

    def run_repeated_monte_carlo_cv(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Esegue la Cross-Validation Monte Carlo stratificata per folio (N=1.000 iterazioni).
        Calcola la distribuzione del Delta C e gli Intervalli di Confidenza al 95%.
        """
        np.random.seed(self.seed)
        unique_folios: np.ndarray = df["folio"].unique()
        num_folios: int = len(unique_folios)
        train_size: int = num_folios // 2

        delta_c_array: np.ndarray = np.zeros(self.iterations, dtype=np.float64)
        c_train_array: np.ndarray = np.zeros(self.iterations, dtype=np.float64)
        c_test_array: np.ndarray = np.zeros(self.iterations, dtype=np.float64)

        for i in range(self.iterations):
            shuffled_folios: np.ndarray = np.random.permutation(unique_folios)
            train_f: np.ndarray = shuffled_folios[:train_size]
            test_f: np.ndarray = shuffled_folios[train_size:]

            df_tr: pd.DataFrame = df[df["folio"].isin(train_f)]
            df_te: pd.DataFrame = df[df["folio"].isin(test_f)]

            c_tr, _, _ = self.matrix_mgr.compute_raw_coherence(df_tr)
            c_te, _, _ = self.matrix_mgr.compute_raw_coherence(df_te)

            c_train_array[i] = c_tr
            c_test_array[i] = c_te
            delta_c_array[i] = abs(c_tr - c_te)

        mean_delta_c: float = float(np.mean(delta_c_array))
        std_delta_c: float = float(np.std(delta_c_array, ddof=1))
        
        # Calcolo Intervallo di Confidenza 95% (Percentili 2.5% e 97.5%)
        ci_95_lower: float = float(np.percentile(delta_c_array, 2.5))
        ci_95_upper: float = float(np.percentile(delta_c_array, 97.5))

        mean_c_train: float = float(np.mean(c_train_array))
        mean_c_test: float = float(np.mean(c_test_array))

        return {
            "iterations": self.iterations,
            "mean_c_train": mean_c_train,
            "mean_c_test": mean_c_test,
            "mean_delta_c": mean_delta_c,
            "std_delta_c": std_delta_c,
            "ci_95_lower": ci_95_lower,
            "ci_95_upper": ci_95_upper
        }

    def run_full_holdout_audit(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Esegue l'audit completo di holdout e salva il report CSV.
        """
        deterministic_res = self.run_single_deterministic_split(df)
        mc_cv_res = self.run_repeated_monte_carlo_cv(df)

        report_df = pd.DataFrame([
            {"Metric": "Deterministic_Train_Folios", "Value": deterministic_res["train_folios_count"]},
            {"Metric": "Deterministic_Test_Folios", "Value": deterministic_res["test_folios_count"]},
            {"Metric": "Deterministic_C_Train", "Value": deterministic_res["c_train"]},
            {"Metric": "Deterministic_C_Test", "Value": deterministic_res["c_test"]},
            {"Metric": "Deterministic_Delta_C", "Value": deterministic_res["delta_c"]},
            {"Metric": "Deterministic_PCT_Gap", "Value": deterministic_res["pct_gap"]},
            {"Metric": "MC_CV_Iterations", "Value": mc_cv_res["iterations"]},
            {"Metric": "MC_CV_Mean_C_Train", "Value": mc_cv_res["mean_c_train"]},
            {"Metric": "MC_CV_Mean_C_Test", "Value": mc_cv_res["mean_c_test"]},
            {"Metric": "MC_CV_Mean_Delta_C", "Value": mc_cv_res["mean_delta_c"]},
            {"Metric": "MC_CV_Std_Delta_C", "Value": mc_cv_res["std_delta_c"]},
            {"Metric": "MC_CV_CI95_Lower", "Value": mc_cv_res["ci_95_lower"]},
            {"Metric": "MC_CV_CI95_Upper", "Value": mc_cv_res["ci_95_upper"]},
        ])
        
        report_df.to_csv(self.HOLDOUT_REPORT_PATH, index=False)

        return {
            "deterministic_split": deterministic_res,
            "monte_carlo_cv": mc_cv_res,
            "report_path": self.HOLDOUT_REPORT_PATH
        }


if __name__ == "__main__":
    print("=== TEST UNITARIO AUDIT_HOLDOUT8 ===")
    parser = EVAParser()
    dummy_df = pd.DataFrame({
        "Folio": ["f1r"] * 10 + ["f1v"] * 10 + ["f2r"] * 10 + ["f2v"] * 10,
        "Line": [1, 2] * 20,
        "EVA_Token": ["qokaiin", "chodaiin", "otaiin", "dy"] * 10
    })
    parsed_df = parser.parse_dataframe(dummy_df)
    
    holdout_audit = HoldoutCrossValidationAudit(iterations=100, seed=42)
    res = holdout_audit.run_full_holdout_audit(parsed_df)
    
    det = res["deterministic_split"]
    mc = res["monte_carlo_cv"]
    print(f"Deterministic Split 50/50 -> Train C: {det['c_train']:.4f} | Test C: {det['c_test']:.4f} | Delta C: {det['delta_c']:.4f} ({det['pct_gap']:.2f}%)")
    print(f"Monte Carlo CV (N=100)   -> Mean Delta C: {mc['mean_delta_c']:.4f} | CI 95%: [{mc['ci_95_lower']:.4f}, {mc['ci_95_upper']:.4f}]")
    print(f"Report esportato in: '{res['report_path']}'")