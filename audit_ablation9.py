#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master-Validato)

Modulo 9: audit_ablation9.py
Test di ablazione selettiva delle regole del parser EVA e benchmark stocastico
su parser casuali (N=1.000) per la verifica della specificità e l'assenza di overfitting.

Sessione di Lavoro: BARVI
Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
Licenza Codebase: MIT License
Tutela Privativa e Marchio: Art. 98 D.Lgs. 30/2005 (CPI) / L. 633/1941
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple
from core_parser1 import EVAParser
from core_matrix2 import MatrixManager


class AblationAuditor:
    """
    Esecutore dei test di ablazione selettiva delle regole del parser EVA
    e del benchmark di confronto con parser casuali (N=1.000).
    """

    ABLATION_REPORT_PATH: str = "ablation_test_results.csv"

    def __init__(self, matrix_mgr: MatrixManager) -> None:
        """
        Inizializza l'auditor collegando l'istanza del gestore della matrice.
        """
        self.matrix_mgr: MatrixManager = matrix_mgr
        self.parser_base: EVAParser = EVAParser()

    def _parse_with_ablated_rules(
        self,
        df: pd.DataFrame,
        ablated_rule: str,
        token_column: str = "EVA_Token"
    ) -> pd.DataFrame:
        """
        Applica il parsing dinamico sul DataFrame disattivando selettivamente una specifica regola.
        """
        df_out: pd.DataFrame = df.copy()
        
        actual_col: str = token_column
        if actual_col not in df_out.columns:
            for col in ["token", "eva_token", "EVA_Token", "EVA_token"]:
                if col in df_out.columns:
                    actual_col = col
                    break

        tokens: np.ndarray = df_out[actual_col].values
        assigned_states: List[str] = []

        alpha_pfx = self.parser_base.alpha_prefixes if ablated_rule != "alpha_prefixes" else ()
        gamma_sfx = self.parser_base.gamma_suffixes if ablated_rule != "gamma_suffixes" else ()
        delta_sub = self.parser_base.delta_substrings if ablated_rule != "delta_substrings" else ()

        for tok_raw in tokens:
            tok: str = self.parser_base.clean_token(tok_raw)
            if not tok:
                assigned_states.append(EVAParser.STATE_BETA)
                continue

            # Rule 1: Alpha Prefixes
            is_alpha: bool = False
            for pfx in alpha_pfx:
                if tok.startswith(pfx):
                    assigned_states.append(EVAParser.STATE_ALPHA)
                    is_alpha = True
                    break
            if is_alpha:
                continue

            # Rule 2: Gamma Suffixes
            is_gamma: bool = False
            for sfx in gamma_sfx:
                if tok.endswith(sfx):
                    assigned_states.append(EVAParser.STATE_GAMMA)
                    is_gamma = True
                    break
            if is_gamma:
                continue

            # Rule 3: Delta Substrings
            is_delta: bool = False
            for sub in delta_sub:
                if sub in tok:
                    assigned_states.append(EVAParser.STATE_DELTA)
                    is_delta = True
                    break
            if is_delta:
                continue

            # Fallback Rule: Beta
            assigned_states.append(EVAParser.STATE_BETA)

        df_out["assigned_state"] = assigned_states
        
        if "line_id" not in df_out.columns:
            if "Folio" in df_out.columns and "Line" in df_out.columns:
                df_out["line_id"] = df_out["Folio"].astype(str) + "." + df_out["Line"].astype(str)
            elif "Folio" in df_out.columns:
                df_out["line_id"] = df_out["Folio"].astype(str)
            else:
                df_out["line_id"] = "line_1"

        return df_out

    def run_ablation_sweep(
        self,
        df: pd.DataFrame,
        token_column: str = "EVA_Token",
        line_column: str = "line_id"
    ) -> List[Dict[str, Any]]:
        """
        Esegue lo sweep completo di ablazione delle regole del parser.
        """
        results: List[Dict[str, Any]] = []
        c_raw_baseline: float = self.matrix_mgr.compute_c_raw(df, state_column="assigned_state", line_column=line_column)

        results.append({
            "test_type": "baseline",
            "ablated_rule": "none",
            "c_raw": c_raw_baseline,
            "delta_c_raw": 0.0,
            "impact_pct": 0.0
        })

        rules_to_ablate: List[Tuple[str, str]] = [
            ("alpha_prefixes", "Ablazione Prefissi d'Innesco (Alpha)"),
            ("gamma_suffixes", "Ablazione Suffissi di Chiusura (Gamma)"),
            ("delta_substrings", "Ablazione Modulatori Interni (Delta)"),
        ]

        for rule_id, rule_desc in rules_to_ablate:
            df_ablated: pd.DataFrame = self._parse_with_ablated_rules(df, ablated_rule=rule_id, token_column=token_column)
            c_ablated: float = self.matrix_mgr.compute_c_raw(df_ablated, state_column="assigned_state", line_column=line_column)
            delta_c: float = c_ablated - c_raw_baseline
            pct_impact: float = (delta_c / c_raw_baseline) * 100.0 if c_raw_baseline > 0 else 0.0

            results.append({
                "test_type": "ablation",
                "ablated_rule": rule_id,
                "description": rule_desc,
                "c_raw": float(c_ablated),
                "delta_c_raw": float(delta_c),
                "impact_pct": float(pct_impact)
            })

        return results

    def run_random_parsers_benchmark(
        self,
        df: pd.DataFrame,
        num_parsers: int = 1000,
        seed: int = 42,
        line_column: str = "line_id"
    ) -> Dict[str, Any]:
        """
        Esegue il benchmark su N=1.000 parser casuali preservando le frequenze marginali.
        """
        np.random.seed(seed)
        c_raw_baseline: float = self.matrix_mgr.compute_c_raw(df, state_column="assigned_state", line_column=line_column)
        states_orig: np.ndarray = df["assigned_state"].values.copy()
        lines_orig: np.ndarray = df[line_column].values if line_column in df.columns else np.zeros(len(df))

        null_coherences: np.ndarray = np.zeros(num_parsers, dtype=np.float64)

        for i in range(num_parsers):
            random_states: np.ndarray = np.random.permutation(states_orig)
            total_trans: int = 0
            admiss_trans: int = 0

            for k in range(len(random_states) - 1):
                if lines_orig[k] == lines_orig[k + 1]:
                    st_curr: str = random_states[k]
                    st_next: str = random_states[k + 1]

                    if st_curr in self.matrix_mgr.state_to_idx and st_next in self.matrix_mgr.state_to_idx:
                        r: int = self.matrix_mgr.state_to_idx[st_curr]
                        c: int = self.matrix_mgr.state_to_idx[st_next]
                        total_trans += 1
                        if self.matrix_mgr.admissibility_matrix[r, c] == 1:
                            admiss_trans += 1

            null_coherences[i] = (admiss_trans / total_trans) if total_trans > 0 else 0.0

        mean_random: float = float(np.mean(null_coherences))
        std_random: float = float(np.std(null_coherences, ddof=1))
        z_score: float = float((c_raw_baseline - mean_random) / std_random) if std_random > 0 else 0.0
        
        count_exceeding: int = int(np.sum(null_coherences >= c_raw_baseline))
        p_value_empirical: float = float((count_exceeding + 1) / (num_parsers + 1))

        return {
            "num_parsers": num_parsers,
            "c_raw_baseline": c_raw_baseline,
            "mean_random_parsers": mean_random,
            "std_random_parsers": std_random,
            "z_score": z_score,
            "p_value_empirical": p_value_empirical
        }

    def run_full_ablation_audit(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Esegue l'audit completo di ablazione e salva il report CSV ufficiale.
        """
        ablation_results: List[Dict[str, Any]] = self.run_ablation_sweep(df)
        random_benchmark: Dict[str, Any] = self.run_random_parsers_benchmark(df, num_parsers=1000, seed=42)

        report_df: pd.DataFrame = pd.DataFrame(ablation_results)
        report_df.to_csv(self.ABLATION_REPORT_PATH, index=False)

        return {
            "ablation_sweep": ablation_results,
            "random_parsers_benchmark": random_benchmark,
            "report_path": self.ABLATION_REPORT_PATH
        }


if __name__ == "__main__":
    mm = MatrixManager()
    auditor = AblationAuditor(mm)
    print("=== MODULO audit_ablation9.py (Release v3.3 Audit-Master-Validato) COMPLETATO E PRONTO ===")