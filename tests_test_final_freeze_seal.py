#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Modulo: tests_test_final_freeze_seal.py
Descrizione: Test di validazione formale del congelamento finale e verifica sigillo SHA-256 (Punto 8.3 - Scheda SORU).
             Verifica l'esatta concordanza dell'impronta crittografica del dataset master e lo stato di sigillo del pacchetto v3.3.

Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
Licenza Codebase: MIT License
"""

import pytest
from audit_final_freeze_and_seal import MasterReleaseFreezeAndSealAuditor, OFFICIAL_MASTER_DATASET_SHA256, OFFICIAL_MASTER_ZIP_SHA256


def test_final_freeze_and_cryptographic_seal_integrity():
    """
    Verifica che l'audit di congelamento emetta il certificato di sigillo v3.3
    e convalidi le impronte crittografiche SHA-256 ufficiali di registro.
    """
    auditor = MasterReleaseFreezeAndSealAuditor()
    cert = auditor.generate_final_seal_certificate()

    # 1. Verifica Dati di Registro
    assert cert["release_title"] == "METODO DEMARIA® Release v3.3 (Audit-Master Unificato)"
    assert cert["author_scientific_director"] == "Avv. Alessandro Demaria"
    assert cert["concept_doi"] == "10.5281/zenodo.22789343"
    assert cert["release_doi"] == "10.5281/zenodo.23242996"

    # 2. Verifica Hash Master Dataset e Hash Master Zip
    dataset_audit = cert["master_dataset_audit"]
    assert dataset_audit["official_expected_sha256"] == OFFICIAL_MASTER_DATASET_SHA256
    assert cert["official_zip_package_sha256"] == OFFICIAL_MASTER_ZIP_SHA256

    # 3. Verifica Stato Sigillo
    assert cert["seal_status"] == "RELEASE_V3_3_SEALED_AND_FROZEN"

    print("\n[+] VALIDAZIONE CONGELAMENTO FINALE E SIGILLO SHA-256 SUPERATA CON SUCCESSO:")
    print(f"    - Release Title:              {cert['release_title']}")
    print(f"    - Dataset Master SHA-256:     {dataset_audit['official_expected_sha256']}")
    print(f"    - Pacchetto Master SHA-256:   {cert['official_zip_package_sha256']}")
    print(f"    - Stato Sigillo:              {cert['seal_status']}")


if __name__ == "__main__":
    pytest.main([__file__])