#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Modulo 4: audit_nullmodels4.py
Motore stocastico Monte Carlo per l'audit dei tre modelli nulli gerarchici
(Global, Intra-Folio, Intra-Line) con calcolo corretto del p-value empirico.

Autore: Avv. Alessandro Demaria
Licenza Codebase: MIT License
Tutela Privativa e Marchio: Art. 98 D.Lgs. 30/2005 (CPI) / L. 633/1941
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
from core_matrix2 import TransitionMatrixManager


class HierarchicalNullModelsAudit:
    """
    Esecutore stocastico Monte Carlo dei tre modelli nulli gerarchici per la validazione
    della significatività statistica e della forza vincolante della sintassi di rigo.
    """

    def __init__(self, iterations: int = 10000, seed: int = 42) -> None:
        """
        Inizializza il motore stocastico fissando il numero di simulazioni e il Seed di sistema.
        """
        self.iterations: int = iterations
        self.seed: int = seed
        self.matrix_mgr: TransitionMatrixManager = TransitionMatrixManager()

    def _calculate_coherence_from_arrays(self, states: np.ndarray, lines: np.ndarray) -> float:
        """
        Funzione interna ad alte prestazioni per il calcolo della coerenza grezza
        su array NumPy unidimensionali.
        """
        total_transitions: int = 0
        valid_transitions: int = 0

        # Iterazione vettorizzata/ottimizzata per coordinata di rigo
        for k in range(len(states) - 1):
            if lines[k] == lines[k + 1]:
                total_transitions += 1
                if self.matrix_mgr.is_transition_valid(states[k], states[k + 1]):
                    valid_transitions += 1

        if total_transitions == 0:
            return 0.0

        return valid_transitions / total_transitions

    def run_global_null_model(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Model 1: Global Null Model
        Permuta casualmente l'intero vettore degli stati assegnati sull'intero corpus.
        """
        np.random.seed(self.seed)
        states_orig: np.ndarray = df["assigned_state"].values.copy()
        lines_orig: np.ndarray = df["line_id"].values

        c_real, _, _ = self.matrix_mgr.compute_raw_coherence(df)
        null_coherences: np.ndarray = np.zeros(self.iterations, dtype=np.float64)

        for i in range(self.iterations):
            permuted_states: np.ndarray = np.random.permutation(states_orig)
            null_coherences[i] = self._calculate_coherence_from_arrays(permuted_states, lines_orig)

        mean_null: float = float(np.mean(null_coherences))
        std_null: float = float(np.std(null_coherences, ddof=1))
        z_score: float = float((c_real - mean_null) / std_null) if std_null > 0 else 0.0

        # Calcolo corretto e conservativo del p-value Monte Carlo (Davison-Hinkley)
        count_exceeding: int = int(np.sum(null_coherences >= c_real))
        p_value_empirical: float = float((count_exceeding + 1) / (self.iterations + 1))

        return {
            "model_name": "Model 1 (Global Null Model)",
            "c_observed": c_real,
            "null_mean": mean_null,
            "null_std": std_null,
            "z_score": z_score,
            "p_value_empirical": p_value_empirical,
            "count_exceeding": count_exceeding,
            "iterations": self.iterations
        }

    def run_intra_folio_null_model(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Model 2: Intra-Folio Null Model
        Permuta casualmente gli stati esclusivamente all'interno dei confini di ciascun folio.
        """
        np.random.seed(self.seed)
        c_real, _, _ = self.matrix_mgr.compute_raw_coherence(df)

        folios: np.ndarray = df["folio"].values
        unique_folios: np.ndarray = np.unique(folios)
        folio_indices: Dict[Any, np.ndarray] = {f: np.where(folios == f)[0] for f in unique_folios}

        states_base: np.ndarray = df["assigned_state"].values.copy()
        lines_orig: np.ndarray = df["line_id"].values
        null_coherences: np.ndarray = np.zeros(self.iterations, dtype=np.float64)

        for i in range(self.iterations):
            permuted_states: np.ndarray = states_base.copy()
            for f, idxs in folio_indices.items():
                permuted_states[idxs] = np.random.permutation(permuted_states[idxs])
            null_coherences[i] = self._calculate_coherence_from_arrays(permuted_states, lines_orig)

        mean_null: float = float(np.mean(null_coherences))
        std_null: float = float(np.std(null_coherences, ddof=1))
        z_score: float = float((c_real - mean_null) / std_null) if std_null > 0 else 0.0

        count_exceeding: int = int(np.sum(null_coherences >= c_real))
        p_value_empirical: float = float((count_exceeding + 1) / (self.iterations + 1))

        return {
            "model_name": "Model 2 (Intra-Folio Null Model)",
            "c_observed": c_real,
            "null_mean": mean_null,
            "null_std": std_null,
            "z_score": z_score,
            "p_value_empirical": p_value_empirical,
            "count_exceeding": count_exceeding,
            "iterations": self.iterations
        }

    def run_intra_line_null_model(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Model 3: Intra-Line Null Model (Smoking Gun / Prova Regina)
        Permuta casualmente gli stati esclusivamente all'interno dei confini del singolo rigo (line_id).
        """
        np.random.seed(self.seed)
        c_real, _, _ = self.matrix_mgr.compute_raw_coherence(df)

        lines_orig: np.ndarray = df["line_id"].values
        unique_lines: np.ndarray = np.unique(lines_orig)
        line_indices: Dict[Any, np.ndarray] = {l: np.where(lines_orig == l)[0] for l in unique_lines}

        states_base: np.ndarray = df["assigned_state"].values.copy()
        null_coherences: np.ndarray = np.zeros(self.iterations, dtype=np.float64)

        for i in range(self.iterations):
            permuted_states: np.ndarray = states_base.copy()
            for l, idxs in line_indices.items():
                if len(idxs) > 1:
                    permuted_states[idxs] = np.random.permutation(permuted_states[idxs])
            null_coherences[i] = self._calculate_coherence_from_arrays(permuted_states, lines_orig)

        mean_null: float = float(np.mean(null_coherences))
        std_null: float = float(np.std(null_coherences, ddof=1))
        z_score: float = float((c_real - mean_null) / std_null) if std_null > 0 else 0.0

        count_exceeding: int = int(np.sum(null_coherences >= c_real))
        p_value_empirical: float = float((count_exceeding + 1) / (self.iterations + 1))

        return {
            "model_name": "Model 3 (Intra-Line Null Model)",
            "c_observed": c_real,
            "null_mean": mean_null,
            "null_std": std_null,
            "z_score": z_score,
            "p_value_empirical": p_value_empirical,
            "count_exceeding": count_exceeding,
            "iterations": self.iterations
        }

    def run_full_hierarchical_audit(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """
        Esegue la suite completa dei tre modelli nulli gerarchici.
        """
        res_global = self.run_global_null_model(df)
        res_folio = self.run_intra_folio_null_model(df)
        res_line = self.run_intra_line_null_model(df)

        return {
            "global_null": res_global,
            "intra_folio_null": res_folio,
            "intra_line_null": res_line
        }


if __name__ == "__main__":
    # Test unitario rapido di isolamento locale
    print("=== TEST UNITARIO AUDIT_NULLMODELS4 ===")
    dummy_df = pd.DataFrame({
        "folio": ["f1r", "f1r", "f1r", "f1r", "f1r", "f1r"],
        "line_id": ["f1r_l1", "f1r_l1", "f1r_l1", "f1r_l2", "f1r_l2", "f1r_l2"],
        "assigned_state": ["Alpha", "Beta", "Gamma", "Alpha", "Beta", "Gamma"]
    })
    audit_runner = HierarchicalNullModelsAudit(iterations=100, seed=42)
    results = audit_runner.run_full_hierarchical_audit(dummy_df)
    for k, v in results.items():
        print(f"\n[{v['model_name']}]")
        print(f"Craw Osservata: {v['c_observed']:.4f} | Media Nulla: {v['null_mean']:.4f}")
        print(f"Z-Score: {v['z_score']:.4f} | p-value empirico: {v['p_value_empirical']:.6f}")