#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Modulo 9: audit_ablation9.py
Test di Ablation (Leave-One-Rule-Out) e Benchmark Comparativo contro 1.000 Parser
pseudo-casuali di pari complessità per la verifica di necessità causale e selettività.

Autore: Avv. Alessandro Demaria
Licenza Codebase: MIT License
Tutela Privativa e Marchio: Art. 98 D.Lgs. 30/2005 (CPI) / L. 633/1941
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
from core_matrix2 import TransitionMatrixManager
from core_parser1 import EVAParser
from audit_nullmodels4 import HierarchicalNullModelsAudit


class AblationAndParserSelectivityAudit:
    """
    Esecutore degli Ablation Test sulle regole sintattiche e del benchmark
    di selettività contro una popolazione di parser stocastici di controllo.
    """

    ABLATION_REPORT_PATH: str = "ablation_test_results.csv"

    def __init__(self, random_parsers_count: int = 1000, seed: int = 42) -> None:
        """
        Inizializza il modulo fissando il numero di parser casuali di controllo e il Seed.
        """
        self.random_parsers_count: int = random_parsers_count
        self.seed: int = seed
        self.matrix_mgr: TransitionMatrixManager = TransitionMatrixManager()
        self.parser: EVAParser = EVAParser()

    def _map_ablated_state(self, token: str, disable_alpha: bool = False, 
                           disable_delta: bool = False, disable_gamma: bool = False) -> str:
        """
        Applica la mappatura degli stati disattivando selettivamente specifiche regole.
        """
        token_clean = self.parser.clean_eva_token(token)
        if not token_clean:
            return self.parser.STATE_BETA

        # Check Alpha
        if not disable_alpha:
            for prefix in self.parser.ALPHA_TRIGGERS:
                if token_clean.startswith(prefix):
                    return self.parser.STATE_ALPHA

        # Check Gamma
        if not disable_gamma:
            for suffix in self.parser.GAMMA_TERMINATORS:
                if token_clean.endswith(suffix):
                    return self.parser.STATE_GAMMA

        # Check Delta
        if not disable_delta:
            for mod in self.parser.DELTA_MODULATORS:
                if mod in token_clean:
                    return self.parser.STATE_DELTA

        return self.parser.STATE_BETA

    def run_leave_one_rule_out_ablation(self, df_raw: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Esegue i test di ablazione disattivando alternativamente Alpha, Delta e Gamma.
        """
        ablation_configs = [
            ("Baseline (Tutte le Regole Attive)", False, False, False),
            ("Ablation Alpha (No Inneschi)", True, False, False),
            ("Ablation Delta (No Modulatori)", False, True, False),
            ("Ablation Gamma (No Reset)", False, False, True),
            ("Ablation Totale (Solo Stato Beta)", True, True, True)
        ]

        results: List[Dict[str, Any]] = []

        for label, dis_a, dis_d, dis_g in ablation_configs:
            df_temp = df_raw.copy()
            df_temp["folio"] = df_temp["Folio"].astype(str).str.lower().str.strip()
            df_temp["line_id"] = df_temp["folio"] + "_" + df_temp["Line"].astype(str).str.strip()
            df_temp["assigned_state"] = df_temp["EVA_Token"].apply(
                lambda t: self._map_ablated_state(t, disable_alpha=dis_a, disable_delta=dis_d, disable_gamma=dis_g)
            )

            c_raw, valid_t, total_t = self.matrix_mgr.compute_raw_coherence(df_temp)
            
            # Audit rapido modello nullo intrarigo (N=500 per valutazione delta)
            null_audit = HierarchicalNullModelsAudit(iterations=500, seed=self.seed)
            line_null_res = null_audit.run_intra_line_null_model(df_temp)

            results.append({
                "Ablation_Mode": label,
                "Observed_Craw": float(c_raw),
                "IntraLine_Null_Mean": line_null_res["null_mean"],
                "Z_Score_Line": line_null_res["z_score"],
                "P_Value_Empirical": line_null_res["p_value_empirical"]
            })

        return results

    def run_random_parsers_benchmark(self, df_raw: pd.DataFrame) -> Dict[str, Any]:
        """
        Confronta il parser del METODO DEMARIA® con 1.000 parser casuali a 4 stati.
        """
        np.random.seed(self.seed)
        df_base = self.parser.parse_dataframe(df_raw)
        c_demaria, _, _ = self.matrix_mgr.compute_raw_coherence(df_base)

        tokens_unique: np.ndarray = df_base["EVA_Token_Clean"].unique()
        num_tokens: int = len(tokens_unique)

        states_pool: List[str] = ["Alpha", "Beta", "Delta", "Gamma"]
        random_coherences: np.ndarray = np.zeros(self.random_parsers_count, dtype=np.float64)

        for i in range(self.random_parsers_count):
            # Assegnazione casuale degli stati ai token unici del vocabolario
            random_map: Dict[str, str] = dict(
                zip(tokens_unique, np.random.choice(states_pool, size=num_tokens, replace=True))
            )
            df_temp = df_base.copy()
            df_temp["assigned_state"] = df_temp["EVA_Token_Clean"].map(random_map)

            c_rand, _, _ = self.matrix_mgr.compute_raw_coherence(df_temp)
            random_coherences[i] = c_rand

        mean_random_c: float = float(np.mean(random_coherences))
        std_random_c: float = float(np.std(random_coherences, ddof=1))
        
        count_exceeding: int = int(np.sum(random_coherences >= c_demaria))
        p_value_selectivity: float = float((count_exceeding + 1) / (self.random_parsers_count + 1))
        z_selectivity: float = float((c_demaria - mean_random_c) / std_random_c) if std_random_c > 0 else 0.0

        return {
            "demaria_c_raw": float(c_demaria),
            "random_parsers_mean_c": mean_random_c,
            "random_parsers_std_c": std_random_c,
            "z_selectivity": z_selectivity,
            "p_value_selectivity": p_value_selectivity,
            "random_parsers_tested": self.random_parsers_count
        }

    def run_full_ablation_audit(self, df_raw: pd.DataFrame) -> Dict[str, Any]:
        """
        Esegue l'audit completo di ablazione e selettività, esportando il report CSV.
        """
        ablation_results = self.run_leave_one_rule_out_ablation(df_raw)
        selectivity_results = self.run_random_parsers_benchmark(df_raw)

        df_report = pd.DataFrame(ablation_results)
        df_report.to_csv(self.ABLATION_REPORT_PATH, index=False)

        return {
            "ablation_rules_summary": ablation_results,
            "selectivity_benchmark": selectivity_results,
            "report_path": self.ABLATION_REPORT_PATH
        }


if __name__ == "__main__":
    print("=== TEST UNITARIO AUDIT_ABLATION9 ===")
    dummy_df = pd.DataFrame({
        "Folio": ["f1r"] * 20,
        "Line": [1] * 10 + [2] * 10,
        "EVA_Token": ["qokaiin", "chodaiin", "otaiin", "dy"] * 5
    })
    ablation_audit = AblationAndParserSelectivityAudit(random_parsers_count=50, seed=42)
    res = ablation_audit.run_full_ablation_audit(dummy_df)

    print("\n--- RISULTATI ABLATION TEST (LEAVE-ONE-RULE-OUT) ---")
    for row in res["ablation_rules_summary"]:
        print(f"Modalità: {row['Ablation_Mode']:40s} | Craw: {row['Observed_Craw']:.4f} | Z-Line: {row['Z_Score_Line']:+.4f}")

    sel = res["selectivity_benchmark"]
    print(f"\n--- BENCHMARK SELETTIVITÀ (PARSER CASUALI) ---")
    print(f"Craw Demaria: {sel['demaria_c_raw']:.4f} | Media Parser Casuali: {sel['random_parsers_mean_c']:.4f}")
    print(f"Z-Selectivity: {sel['z_selectivity']:+.4f} | p-value: {sel['p_value_selectivity']:.6f}")
    print(f"Report esportato in: '{res['report_path']}'")