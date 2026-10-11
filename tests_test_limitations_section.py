#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Modulo: tests_test_limitations_section.py
Descrizione: Test di validazione formale della sezione Limitations and Future Work (Punto 8.2 - Scheda SORU).
             Verifica l'esplicitazione delle limitazioni di trascrizione, astrazione hardware e prospettive v3.4+.

Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
Licenza Codebase: MIT License
"""

import pytest
from core_limitations_and_future_work import LimitationsAndFutureWorkManager


def test_limitations_and_future_work_section_structure():
    """
    Verifica che il gestore generi correttamente le 3 limitazioni fondamentali
    ed i 3 punti di sviluppo futuro conformi ai requisiti di Open Science.
    """
    mgr = LimitationsAndFutureWorkManager(version="v3.3")
    data = mgr.get_formal_limitations_and_future_work()

    # 1. Verifica presenza delle sezioni principali
    assert data["release_version"] == "v3.3"
    assert "limitations_list" in data
    assert "future_work_roadmap" in data

    limits = data["limitations_list"]
    fw = data["future_work_roadmap"]

    # 2. Verifica conteggio e contenuti limitazioni
    assert len(limits) == 3, f"Numero di limitazioni non conforme: trovati {len(limits)} (attesi 3)"
    limit_ids = [l["limit_id"] for l in limits]
    assert "LIM_01_TRANSCRIPTION_CONVENTION" in limit_ids
    assert "LIM_02_HARDWARE_ABSTRACT_SIMULATION" in limit_ids
    assert "LIM_03_NON_SEMANTIC_DECODING" in limit_ids

    # 3. Verifica prospettive di sviluppo futuro
    assert len(fw) == 3, f"Numero di prospettive future non conforme: trovati {len(fw)} (attesi 3)"
    fw_ids = [f["work_id"] for f in fw]
    assert "FW_01_CONTINUOUS_TIME_AUTOMATA" in fw_ids
    assert "FW_02_MULTI_SCALE_MACRO_TOPOLOGY" in fw_ids
    assert "FW_03_DIGITAL_TWIN_HARDWARE_EMULATION" in fw_ids

    print("\n[+] VALIDAZIONE SEZIONE LIMITATIONS AND FUTURE WORK SUPERATA CON SUCCESSO:")
    print(f"    - Release Version:            {data['release_version']}")
    print(f"    - Limitazioni Formalizzate:   {len(limits)}")
    print(f"    - Traiettorie Future Work:     {len(fw)}")


if __name__ == "__main__":
    pytest.main([__file__])