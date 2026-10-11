#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Modulo: tests_test_cross_corpus_distance.py
Descrizione: Test di validazione formale della distanza stocastica e specificità selettiva (Punto 6.2 - Scheda SORU).
             Verifica che lo Z-score di selettività sia > +4.0 sigma ed il margine dal secondo classificato sia > 0.048.

Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
Licenza Codebase: MIT License
"""

import pytest
import numpy as np
from audit_cross_corpus_distance import CrossCorpusDistanceAuditor


def test_cross_corpus_selectivity_and_distance_bounds():
    """
    Verifica che il Manoscritto Voynich mantenga una separazione stocastica significativa
    rispetto a tutti i corpora di controllo (Z_selectivity > +4.0 std dev).
    """
    auditor = CrossCorpusDistanceAuditor()
    res = auditor.compute_selectivity_distance_metrics()

    c_voynich = res["c_voynich_observed"]
    ctrl = res["control_group_metrics"]
    sep = res["separation_distance_metrics"]

    # 1. Verifica Coerenza Baseline Voynich
    assert np.isclose(c_voynich, 0.786597, atol=1e-4), f"Coerenza Voynich errata: {c_voynich}"

    # 2. Verifica Z-Score Selettivo (> +4.0 deviazioni standard)
    z_sel = sep["z_selectivity_score"]
    assert z_sel > 4.0, f"Z-score di selettività insufficiente: {z_sel:.4f} (atteso > +4.0)"

    # 3. Verifica Margine di Sicurezza dal Secondo Classificato (Codice di Dresda)
    margin = sep["margin_from_runner_up"]
    assert margin > 0.048, f"Margine dal secondo classificato troppo ridotto: {margin:.6f} (atteso > 0.048)"

    # 4. Verifica Scarto Relativo
    assert ctrl["control_corpora_count"] == 9, "I corpora di controllo devono essere esattamente 9"

    print(f"\n[+] VALIDAZIONE DISTANZA STOCASTICA CROSS-CORPUS SUPERATA CON SUCCESSO:")
    print(f"    - Coerenza Voynich MS 408:    {c_voynich:.6f}")
    print(f"    - Media 9 Corpora Controllo:  {ctrl['mean_coherence_controls']:.6f}")
    print(f"    - Secondo Classificato:       {ctrl['max_coherence_controls']:.6f} (Dresden Codex)")
    print(f"    - Z-Score Selettività:        +{z_sel:.4f} sigma")
    print(f"    - Margine Netto Separazione:  +{margin:.6f}")
    print(f"    - Scarto Relativo Percentuale: {sep['relative_gap_percentage']}")


if __name__ == "__main__":
    pytest.main([__file__])