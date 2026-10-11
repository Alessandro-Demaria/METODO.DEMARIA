#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Modulo 6: audit_robustness6.py
Test di sensibilità, stabilità e resilienza al rumore sintattico inoculato (0.0% -> 30.0%).

Autore: Avv. Alessandro Demaria
Licenza Codebase: MIT License
Tutela Privativa e Marchio: Art. 98 D.Lgs. 30/2005 (CPI) / L. 633/1941
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
from core_matrix2 import TransitionMatrixManager


class RobustnessStressTestAudit:
    """
    Esecutore dello Stress Test di Sensibilità al Rumore Sintattico per la verifica
    della tolleranza agli errori di trascrizione e della tenuta del segnale topologico.
    """

    NOISE_LEVELS: List[float] = [0.0, 0.01, 0.05, 0.10, 0.20, 0.30]
    STATES: List[str] = ["Alpha", "Beta", "Delta", "Gamma"]

    def __init__(self, iterations_per_level: int = 100, seed: int = 42) -> None:
        """
        Inizializza il modulo fissando le iterazioni per livello e il Seed deterministico.
        """
        self.iterations_per_level: int = iterations_per_level
        self.seed: int = seed
        self.matrix_mgr: TransitionMatrixManager = TransitionMatrixManager()

    def _calculate_coherence_from_arrays(self, states: np.ndarray, lines: np.ndarray) -> float:
        """
        Calcola la coerenza sintattica grezza su array unidimensionali di stati e righe.
        """
        total_transitions: int = 0
        valid_transitions: int = 0

        for k in range(len(states) - 1):
            if lines[k] == lines[k + 1]:
                total_transitions += 1
                if self.matrix_mgr.is_transition_valid(states[k], states[k + 1]):
                    valid_transitions += 1

        if total_transitions == 0:
            return 0.0

        return valid_transitions / total_transitions

    def run_robustness_test(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Esegue lo stress test di inoculazione del rumore sintattico a gradini.
        
        Args:
            df (pd.DataFrame): DataFrame contenente 'assigned_state' e 'line_id'.
            
        Returns:
            Dict[str, Any]: Report dettagliato per ciascun livello di rumore con medie,
                            deviazioni standard e percentuali di ritenzione del segnale.
        """
        np.random.seed(self.seed)

        states_orig: np.ndarray = df["assigned_state"].values.copy()
        lines_orig: np.ndarray = df["line_id"].values
        total_tokens: int = len(states_orig)

        c_baseline, _, _ = self.matrix_mgr.compute_raw_coherence(df)

        results_by_level: List[Dict[str, Any]] = []

        for noise in self.NOISE_LEVELS:
            if noise == 0.0:
                results_by_level.append({
                    "noise_level_pct": 0.0,
                    "c_raw_mean": float(c_baseline),
                    "c_raw_std": 0.0,
                    "retention_pct": 100.0,
                    "diagnosis": "Baseline di riferimento"
                })
                continue

            coherences: np.ndarray = np.zeros(self.iterations_per_level, dtype=np.float64)
            num_corruptions: int = int(noise * total_tokens)

            for it in range(self.iterations_per_level):
                noisy_states: np.ndarray = states_orig.copy()
                
                # Selezione casuale degli indici da alterare
                corrupt_indices: np.ndarray = np.random.choice(
                    total_tokens, size=num_corruptions, replace=False
                )
                
                # Inoculazione di stati estratti uniformemente
                replacement_states: np.ndarray = np.random.choice(
                    self.STATES, size=num_corruptions, replace=True
                )
                noisy_states[corrupt_indices] = replacement_states

                # Calcolo coerenza sul vettore perturbato
                coherences[it] = self._calculate_coherence_from_arrays(noisy_states, lines_orig)

            mean_c_noisy: float = float(np.mean(coherences))
            std_c_noisy: float = float(np.std(coherences, ddof=1))
            retention: float = float((mean_c_noisy / c_baseline) * 100.0) if c_baseline > 0 else 0.0

            # Diagnostica di tenuta
            if noise <= 0.05:
                diag = "Altissima tenuta"
            elif noise <= 0.10:
                diag = "Tolleranza straordinaria agli errori"
            elif noise <= 0.20:
                diag = "Conservazione del segnale"
            else:
                diag = "Risposta lineare e controllata"

            results_by_level.append({
                "noise_level_pct": float(noise * 100.0),
                "c_raw_mean": mean_c_noisy,
                "c_raw_std": std_c_noisy,
                "retention_pct": retention,
                "diagnosis": diag
            })

        return {
            "test_name": "Robustness & Noise Sensitivity Stress Test",
            "c_baseline": c_baseline,
            "levels_summary": results_by_level
        }


if __name__ == "__main__":
    # Test unitario rapido di isolamento locale
    print("=== TEST UNITARIO AUDIT_ROBUSTNESS6 ===")
    dummy_df = pd.DataFrame({
        "line_id": ["f1r_l1"] * 10 + ["f1r_l2"] * 10,
        "assigned_state": ["Alpha", "Beta", "Beta", "Delta", "Gamma"] * 4
    })
    robustness_audit = RobustnessStressTestAudit(iterations_per_level=20, seed=42)
    res = robustness_audit.run_robustness_test(dummy_df)
    print(f"Coerenza Baseline: {res['c_baseline']:.4f}\n")
    for lvl in res["levels_summary"]:
        print(f"Rumore: {lvl['noise_level_pct']:5.1f}% | Craw' Medio: {lvl['c_raw_mean']:.4f} "
              f"| Ritenzione: {lvl['retention_pct']:6.2f}% | Diagnosi: {lvl['diagnosis']}")