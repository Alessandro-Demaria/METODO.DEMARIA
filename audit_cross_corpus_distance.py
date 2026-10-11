#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Modulo: audit_cross_corpus_distance.py
Descrizione: Quantificazione della Distanza Stocastica e Specificità Selettiva Cross-Corpus (Punto 6.2 - Scheda SORU).
             Calcola momenti statistici, Z-score selettivo, distanza dal secondo classificato (Codice di Dresda)
             e scarto percentuale relativo rispetto alla baseline dei 9 corpora di controllo.

Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
Licenza Codebase: MIT License
"""

import logging
import numpy as np
import pandas as pd

from audit_cross_corpus_falsification import CANONICAL_CROSS_CORPUS_BENCHMARK

# Configurazione Logging di Laboratorio
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


class CrossCorpusDistanceAuditor:
    """
    Gestore per il calcolo analitico delle metriche di distanza stocastica e separazione della risposta
    tra il Manoscritto Voynich ed il gruppo dei 9 corpora storici di controllo (Tabella 4.3).
    """

    def __init__(self, benchmark_data: list = None):
        self.benchmark_data = benchmark_data if benchmark_data is not None else CANONICAL_CROSS_CORPUS_BENCHMARK

    def compute_selectivity_distance_metrics(self) -> dict:
        """
        Calcola la media, deviazione standard dei controlli, Z-score di selettività,
        distanza assoluta dal secondo classificato e scarto relativo percentuale.
        """
        logging.info("[Cross-Corpus Distance] Avvio calcolo metriche di separazione stocastica...")

        voynich_entry = None
        control_coherences = []

        for entry in self.benchmark_data:
            if entry["corpus_id"] == "VOYNICH_MS408":
                voynich_entry = entry
            else:
                control_coherences.append(entry["c_expected"])

        if voynich_entry is None or len(control_coherences) != 9:
            raise ValueError("Registro benchmark cross-corpus non conforme o incompleto")

        c_voynich = voynich_entry["c_expected"]
        control_array = np.array(control_coherences, dtype=float)

        mean_ctrl = float(np.mean(control_array))
        std_ctrl = float(np.std(control_array, ddof=1))
        
        # Z-score di selettività del Voynich rispetto ai controlli
        z_selectivity = float((c_voynich - mean_ctrl) / std_ctrl) if std_ctrl > 0 else 0.0

        # Secondo classificato nei controlli (Codice di Dresda: 0.7385)
        max_ctrl = float(np.max(control_array))
        margin_from_runner_up = float(c_voynich - max_ctrl)

        # Scarto relativo percentuale rispetto alla media dei controlli
        relative_gap_pct = float(((c_voynich - mean_ctrl) / mean_ctrl) * 100.0)

        return {
            "c_voynich_observed": c_voynich,
            "control_group_metrics": {
                "control_corpora_count": len(control_array),
                "mean_coherence_controls": mean_ctrl,
                "std_dev_controls": std_ctrl,
                "max_coherence_controls": max_ctrl,
                "runner_up_corpus": "DRESDEN_CODEX (0.7385)"
            },
            "separation_distance_metrics": {
                "z_selectivity_score": z_selectivity,
                "margin_from_runner_up": margin_from_runner_up,
                "relative_gap_percentage": f"+{relative_gap_pct:.2f}%"
            },
            "diagnosis": f"Voynich MS 408 is separated by {z_selectivity:.2f} standard deviations from historical controls"
        }


if __name__ == "__main__":
    auditor = CrossCorpusDistanceAuditor()
    res = auditor.compute_selectivity_distance_metrics()
    print("\n[+] ESEMPIO DI ANALISI DISTANZA CROSS-CORPUS (PUNTO 6.2):")
    print(res)