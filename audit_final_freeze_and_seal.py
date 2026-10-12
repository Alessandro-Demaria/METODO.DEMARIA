#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Edizione Scientifica Pura)

Modulo: audit_final_freeze_and_seal.py
Verifica l'integrità crittografica SHA-256 dei file di master corpus.
Fallisce esplicitamente se i file non sono presenti o non coincidono.
"""

import os
import hashlib


EXPECTED_HASH = "dec87e784290ad5b404bd5ed0110349a2f379c7fb386adb0bca2d7a4b1890999"


def verify_integrity(dataset_path="voynich_eva_tokens_extended.csv"):
    if not os.path.exists(dataset_path):
        print(f"[-] ERRORE CRITICO: File {dataset_path} non presente su disco.")
        return False

    sha256 = hashlib.sha256()
    with open(dataset_path, "rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            sha256.update(block)

    computed_hash = sha256.hexdigest()
    if computed_hash == EXPECTED_HASH:
        print(f"[+] VERIFIED_MATCH: SHA-256 coerente ({computed_hash[:16]}...)")
        return True
    else:
        print(f"[-] HASH_MISMATCH: Calcolato {computed_hash} != Atteso {EXPECTED_HASH}")
        return False


if __name__ == "__main__":
    success = verify_integrity()
    if not success:
        exit(1)
