#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Modulo 3: utils_preflight3.py
Checker d'integrità crittografica SHA-256, validazione di immutabilità del dataset master
e gestione del blocco d'arresto vincolante (Hard Stop).

Autore: Avv. Alessandro Demaria
Licenza Codebase: MIT License
Tutela Privativa e Marchio: Art. 98 D.Lgs. 30/2005 (CPI) / L. 633/1941
"""

import hashlib
import os
import pandas as pd
from typing import Dict, Any, Tuple


class PreFlightChecker:
    """
    Modulo di controllo e validazione pre-esecuzione. Garantisce l'integrità
    crittografica SHA-256 e l'immutabilità del dataset master di laboratorio.
    """

    # Impronta SHA-256 congelata di targa del Dataset Master (35.483 EVA tokens)
    MASTER_DATASET_HASH: str = "dec87e784290ad5b404bd5ed0110349a2f379c7fb386adb0bca2d7a4b1890999"
    EXPECTED_TOKEN_COUNT: int = 35483

    @classmethod
    def calculate_file_sha256(cls, file_path: str) -> str:
        """
        Calcola l'impronta crittografica SHA-256 di un file su disco.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File non trovato nel percorso di laboratorio: {file_path}")

        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(65536), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest().lower()

    @classmethod
    def run_preflight_check(cls, dataset_path: str, enforce_hard_stop: bool = True) -> Dict[str, Any]:
        """
        Esegue la verifica d'integrità crittografica e strutturale del dataset.
        
        Args:
            dataset_path (str): Percorso del file CSV del dataset.
            enforce_hard_stop (bool): Se True, solleva un'eccezione ed interrompe
                                      l'esecuzione in caso di mismatch crittografico.
                                      
        Returns:
            Dict[str, Any]: Esito dettagliato del controllo pre-flight.
        """
        if not os.path.exists(dataset_path):
            error_msg = f"CRITICAL PRE-FLIGHT FAILURE: File dataset non trovato in '{dataset_path}'"
            if enforce_hard_stop:
                raise FileNotFoundError(error_msg)
            return {"status": "FAILED", "reason": error_msg}

        # 1. Calcolo Hash SHA-256
        calculated_hash: str = cls.calculate_file_sha256(dataset_path)
        hash_match: bool = (calculated_hash == cls.MASTER_DATASET_HASH)

        # 2. Caricamento e conteggio righe/token
        try:
            df: pd.DataFrame = pd.read_csv(dataset_path)
            token_count: int = len(df)
        except Exception as e:
            error_msg = f"CRITICAL PRE-FLIGHT FAILURE: Errore nella lettura del CSV - {str(e)}"
            if enforce_hard_stop:
                raise RuntimeError(error_msg)
            return {"status": "FAILED", "reason": error_msg}

        token_match: bool = (token_count == cls.EXPECTED_TOKEN_COUNT)

        # 3. Valutazione della conformità complessiva
        is_passed: bool = hash_match and token_match

        if not is_passed:
            details = (
                f"\n=== FAILURE DETAILS ==="
                f"\nCalculated Hash : {calculated_hash}"
                f"\nExpected Hash   : {cls.MASTER_DATASET_HASH}"
                f"\nHash Match      : {hash_match}"
                f"\nToken Count     : {token_count} (Expected: {cls.EXPECTED_TOKEN_COUNT})"
                f"\nToken Match     : {token_match}"
            )
            error_msg = f"CRITICAL PRE-FLIGHT FAILURE: Violazione di integrità del Dataset Master!{details}"
            
            if enforce_hard_stop:
                raise ValueError(error_msg)
            
            return {
                "status": "FAILED",
                "reason": error_msg,
                "calculated_hash": calculated_hash,
                "token_count": token_count
            }

        return {
            "status": "PASSED",
            "calculated_hash": calculated_hash,
            "token_count": token_count,
            "hash_match": True,
            "token_match": True
        }


if __name__ == "__main__":
    # Test unitario rapido di verifica locale
    print("=== TEST UNITARIO UTILS_PREFLIGHT3 ===")
    test_path = "voynich_eva_tokens_extended.csv"
    if os.path.exists(test_path):
        result = PreFlightChecker.run_preflight_check(test_path, enforce_hard_stop=False)
        print(f"Stato Pre-Flight: {result['status']}")
        print(f"Hash Calcolato: {result.get('calculated_hash')}")
        print(f"Token Totali  : {result.get('token_count')}")
    else:
        print(f"File '{test_path}' non presente nella directory locale di test. Modulo pronto per l'integrazione.")