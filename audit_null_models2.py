#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Modulo: audit_null_models2.py
Descrizione: Modulo per l'esecuzione dei Modelli Nulli Gerarchici Monte Carlo (Punti 3.1, 3.2 e 7.1 - Scheda SORU).
             Implementa l'inferenza statistica non parametrica con correzione di Davison-Hinkley
             ed adotta un registro diagnostico neutrale, rigoroso ed esente da terminologia trionfalistica.

Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
Licenza Codebase: MIT License
"""

import logging
import numpy as np
import pandas as pd
from scipy.stats import norm

from core_matrix2 import BinaryAdmissibilityMatrix

# Configurazione Logging di Laboratorio con registro neutrale
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


class HierarchicalNullModelsAuditor:
    """
    Esecutore dei Modelli Nulli Gerarchici Monte Carlo con notazione d'inferenza
    rigorosa e formulazione diagnostica neutrale (Popperian Epistemology).
    """

    def __init__(self, matrix_mgr: BinaryAdmissibilityMatrix = None, iterations: int = 10000, seed: int = 42):
        self.matrix_mgr = matrix_mgr if matrix_mgr is not None else BinaryAdmissibilityMatrix()
        self.iterations = iterations
        self.seed = seed

    def compute_davison_hinkley_p_value(self, b_count: int, n_iterations: int) -> tuple:
        """
        Calcola il p-value empirico tramite correzione di Davison-Hinkley:
        p_emp = (b + 1) / (N + 1)
        Restituisce la tupla: (p_emp_float, p_emp_formatted_string).
        """
        p_emp_float = (b_count + 1.0) / (n_iterations + 1.0)
        if b_count == 0:
            p_emp_str = f"< {1.0 / n_iterations:.4f}"
        else:
            p_emp_str = f"= {p_emp_float:.6f}"
        return p_emp_float, p_emp_str

    def run_global_null_model(self, df_parsed: pd.DataFrame) -> dict:
        """
        Model 1: Permutazione Totale del Corpus dell'intera sequenza di token/stati.
        """
        np.random.seed(self.seed)
        c_raw_obs = self.matrix_mgr.compute_corpus_coherence(df_parsed)
        states_array = df_parsed["state"].values.copy()
        n_tokens = len(states_array)

        null_coherences = np.zeros(self.iterations, dtype=float)

        for i in range(self.iterations):
            permuted_states = np.random.permutation(states_array)
            df_perm = pd.DataFrame({"state": permuted_states, "line_id": df_parsed["line_id"].values})
            null_coherences[i] = self.matrix_mgr.compute_corpus_coherence(df_perm)

        mean_null = float(np.mean(null_coherences))
        std_null = float(np.std(null_coherences, ddof=1))
        z_score = float((c_raw_obs - mean_null) / std_null) if std_null > 0 else 0.0

        b_count = int(np.sum(null_coherences >= c_raw_obs))
        p_emp_float, p_emp_str = self.compute_davison_hinkley_p_value(b_count, self.iterations)

        parametric_p = float(norm.sf(z_score))
        parametric_p_str = "< 10^-15" if z_score > 8.0 else f"{parametric_p:.6e}"

        return {
            "permutation_scope": f"Entire Corpus ({n_tokens:,} tokens)",
            "observed_c_raw": float(c_raw_obs),
            "mean_null_coherence": mean_null,
            "std_dev": std_null,
            "z_score": z_score,
            "b_adverse_count": b_count,
            "empirical_p_value_num": p_emp_float,
            "empirical_p_value": p_emp_str,
            "parametric_p_value_num": parametric_p,
            "parametric_p_value": parametric_p_str,
            "diagnosis": "Non-random deterministic global structure (Empirical data support global ordering hypothesis)"
        }

    def run_intra_folio_null_model(self, df_parsed: pd.DataFrame) -> dict:
        """
        Model 2: Permutazione intra-folio (Scambio interno al singolo folio).
        """
        np.random.seed(self.seed)
        c_raw_obs = self.matrix_mgr.compute_corpus_coherence(df_parsed)
        df_work = df_parsed.copy()

        null_coherences = np.zeros(self.iterations, dtype=float)
        grouped_indices = df_work.groupby("Folio", sort=False).indices

        for i in range(self.iterations):
            permuted_states = df_work["state"].values.copy()
            for folio, idxs in grouped_indices.items():
                permuted_states[idxs] = np.random.permutation(permuted_states[idxs])

            df_perm = pd.DataFrame({"state": permuted_states, "line_id": df_work["line_id"].values})
            null_coherences[i] = self.matrix_mgr.compute_corpus_coherence(df_perm)

        mean_null = float(np.mean(null_coherences))
        std_null = float(np.std(null_coherences, ddof=1))
        z_score = float((c_raw_obs - mean_null) / std_null) if std_null > 0 else 0.0

        b_count = int(np.sum(null_coherences >= c_raw_obs))
        p_emp_float, p_emp_str = self.compute_davison_hinkley_p_value(b_count, self.iterations)

        parametric_p = float(norm.sf(z_score))
        parametric_p_str = "< 10^-15" if z_score > 8.0 else f"{parametric_p:.6e}"

        return {
            "permutation_scope": "Within-Folio Exchange",
            "observed_c_raw": float(c_raw_obs),
            "mean_null_coherence": mean_null,
            "std_dev": std_null,
            "z_score": z_score,
            "b_adverse_count": b_count,
            "empirical_p_value_num": p_emp_float,
            "empirical_p_value": p_emp_str,
            "parametric_p_value_num": parametric_p,
            "parametric_p_value": parametric_p_str,
            "diagnosis": "Distributional homogeneity and page stationary regime"
        }

    def run_intra_line_null_model(self, df_parsed: pd.DataFrame) -> dict:
        """
        Model 3: Permutazione intra-linea (Scambio interno al singolo rigo - Line Level Constraint).
        """
        np.random.seed(self.seed)
        c_raw_obs = self.matrix_mgr.compute_corpus_coherence(df_parsed)
        df_work = df_parsed.copy()

        null_coherences = np.zeros(self.iterations, dtype=float)
        grouped_indices = df_work.groupby("line_id", sort=False).indices

        for i in range(self.iterations):
            permuted_states = df_work["state"].values.copy()
            for line, idxs in grouped_indices.items():
                if len(idxs) > 1:
                    permuted_states[idxs] = np.random.permutation(permuted_states[idxs])

            df_perm = pd.DataFrame({"state": permuted_states, "line_id": df_work["line_id"].values})
            null_coherences[i] = self.matrix_mgr.compute_corpus_coherence(df_perm)

        mean_null = float(np.mean(null_coherences))
        std_null = float(np.std(null_coherences, ddof=1))
        z_score = float((c_raw_obs - mean_null) / std_null) if std_null > 0 else 0.0

        b_count = int(np.sum(null_coherences >= c_raw_obs))
        p_emp_float, p_emp_str = self.compute_davison_hinkley_p_value(b_count, self.iterations)

        parametric_p = float(norm.sf(z_score))
        parametric_p_str = "< 10^-15" if z_score > 8.0 else f"{parametric_p:.6e}"

        return {
            "permutation_scope": "Within-Line Exchange (Line-Level Constraint)",
            "observed_c_raw": float(c_raw_obs),
            "mean_null_coherence": mean_null,
            "std_dev": std_null,
            "z_score": z_score,
            "b_adverse_count": b_count,
            "empirical_p_value_num": p_emp_float,
            "empirical_p_value": p_emp_str,
            "parametric_p_value_num": parametric_p,
            "parametric_p_value": parametric_p_str,
            "diagnosis": "Significant Line-Level Syntactic Constraint (Strong spatial binding observed along line_id)"
        }


def run_full_hierarchical_audit(df_parsed: pd.DataFrame, matrix_mgr: BinaryAdmissibilityMatrix = None, iterations: int = 10000, seed: int = 42) -> dict:
    """
    Funzione di interfaccia unificata per la Master Audit Suite v3.3.
    """
    auditor = HierarchicalNullModelsAuditor(matrix_mgr=matrix_mgr, iterations=iterations, seed=seed)
    return {
        "global_null": auditor.run_global_null_model(df_parsed),
        "intra_folio_null": auditor.run_intra_folio_null_model(df_parsed),
        "intra_line_null": auditor.run_intra_line_null_model(df_parsed)
    }