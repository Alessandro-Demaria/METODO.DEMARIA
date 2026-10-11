#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Modulo: core_epistemology_reporting.py
Descrizione: Modulo di Formulazione Epistemologica Popperiana e Reporting Neutrale (Punto 7.2 - Scheda SORU).
             Formalizza la presentazione dell'inferenza statistica adottando la grammatica della falsificabilità,
             del non-rigetto dell'ipotesi alternativa H1 e del rigetto dell'ipotesi nulla H0.

Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
Licenza Codebase: MIT License
"""

import logging
import json
import numpy as np
import pandas as pd

# Configurazione Logging di Laboratorio
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


class PopperianEpistemologyReporter:
    """
    Gestore per la conversione dei risultati numerici di laboratorio in enunciati
    epistemologicamente neutri, rigidi ed orientati alla falsificabilità popperiana (Popper, 1959).
    """

    def __init__(self, alpha_threshold: float = 0.001):
        self.alpha_threshold = alpha_threshold

    def format_null_model_statement(self, model_name: str, z_score: float, empirical_p: str, b_count: int) -> dict:
        """
        Genera un report neutrale per i modelli nulli gerarchici basato sulla logica del rigetto di H0.
        """
        h0_rejected = b_count == 0 or (isinstance(empirical_p, float) and empirical_p < self.alpha_threshold)
        
        if h0_rejected:
            status_statement = "Hypothesis H0 (Random Artifact) Rejected"
            epistemological_conclusion = (
                f"The empirical observed data display significant divergence from the null distribution "
                f"(Z-score = +{z_score:.4f}, empirical p-value {empirical_p}). "
                f"The data support the deterministic structural hypothesis (H1)."
            )
        else:
            status_statement = "Hypothesis H0 (Random Artifact) Not Rejected"
            epistemological_conclusion = "The empirical data do not display sufficient divergence from random baseline."

        return {
            "model_tested": model_name,
            "z_score_observed": float(z_score),
            "empirical_p_value": str(empirical_p),
            "null_hypothesis_status": status_statement,
            "popperian_diagnosis": epistemological_conclusion
        }

    def format_cross_corpus_statement(self, c_voynich: float, c_control_max: float, z_selectivity: float) -> dict:
        """
        Genera un report neutrale di falsificabilità popperiana per il benchmark cross-corpus.
        """
        gap = c_voynich - c_control_max
        is_selective = gap > 0 and z_selectivity > 3.0

        if is_selective:
            diagnosis = (
                f"The model demonstrates selective sensitivity to the Voynich MS 408 corpus "
                f"(coherence gap = +{gap:.6f}, selectivity Z-score = +{z_selectivity:.4f} sigma relative to historical controls). "
                f"The hypothesis of non-specific or generic coherence extraction is empirically falsified."
            )
        else:
            diagnosis = "The model fails to demonstrate selective discrimination across historical corpora."

        return {
            "voynich_c_raw": float(c_voynich),
            "runner_up_control_c_star": float(c_control_max),
            "selectivity_z_score": float(z_selectivity),
            "selectivity_status": "Empirically Verified Selective Discrimination" if is_selective else "Non-Selective",
            "popperian_diagnosis": diagnosis
        }


if __name__ == "__main__":
    reporter = PopperianEpistemologyReporter()
    sample_null_report = reporter.format_null_model_statement("Intra-Line Null Model", 14.5202, "< 0.0001", 0)
    print("\n[+] ESEMPIO DI REPORTING EPISTEMOLOGICO POPPERIANO:")
    print(json.dumps(sample_null_report, indent=4))