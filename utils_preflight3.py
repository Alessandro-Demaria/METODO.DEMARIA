"""
METODO DEMARIA v3.3 - MAGISTER
DOI UFFICIALE DI RELEASE: 10.5281/zenodo.23242996
Modulo: utils_preflight3.py (Elemento 3 del Motore - Pre-Flight Checker & Cryptographic Audit)
Descrizione: Verificatore d'integrità crittografica SHA-256 e sanificazione pre-computazionale
             del dataset master 'voynich_eva_tokens_extended.csv'.
             Garantisce il rispetto vincolante delle invarianti di laboratorio (Release v3.3):
             Hash SHA-256: dec87e784290ad5b404bd5ed0110349a2f379c7fb386adb0bca2d7a4b1890999
             Volumetria: 35.483 EVA tokens validati su 227 folii.
Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
"""

import os
import hashlib
import pandas as pd
from typing import Dict, Any


class PreFlightChecker:
    """
    Verificatore di sicurezza e integrità crittografica SHA-256 per la suite METODO DEMARIA v3.3.
    Assicura l'immutabilità dei dati d'ingresso prima dell'elaborazione stocastica Monte Carlo.
    """

    EXPECTED_SHA256 = "dec87e784290ad5b404bd5ed0110349a2f379c7fb386adb0bca2d7a4b1890999"
    EXPECTED_TOKENS = 35483

    def __init__(self, dataset_path: str = "voynich_eva_tokens_extended.csv"):
        self.dataset_path = dataset_path

    def compute_sha256(self) -> str:
        """
        Calcola l'impronta crittografica SHA-256 del file di dataset in ingresso
        tramite streaming a blocchi di memoria da 64 KB per ottimizzare l'I/O.
        """
        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError(f"Dataset master non trovato al percorso: {self.dataset_path}")

        sha256_hash = hashlib.sha256()
        with open(self.dataset_path, "rb") as f:
            for byte_block in iter(lambda: f.read(65536), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest().lower()

    def run_preflight_check(self, enforce_hard_stop: bool = True) -> Dict[str, Any]:
        """
        Esegue la verifica completa di integrità crittografica e volumetrica.
        Restituisce lo stato 'PASSED' se l'hash corrisponde esattamente alla baseline di Release v3.3.
        """
        computed_hash = self.compute_sha256()

        df = pd.read_csv(self.dataset_path)
        total_tokens = len(df)

        hash_matched = (computed_hash == self.EXPECTED_SHA256.lower())
        tokens_matched = (total_tokens == self.EXPECTED_TOKENS)

        if hash_matched and tokens_matched:
            status = "PASSED"
        else:
            status = "FAILED"

        if status == "FAILED" and enforce_hard_stop:
            raise ValueError(
                f"CRITICAL PRE-FLIGHT ERROR: L'impronta SHA-256 rilevata ({computed_hash}) "
                f"o il numero di token ({total_tokens}) non corrispondono ai valori congelati "
                f"di Release v3.3 ({self.EXPECTED_SHA256} | {self.EXPECTED_TOKENS} tokens). "
                "Esecuzione interrotta per salvaguardare la riproducibilità scientifica."
            )

        return {
            "status": status,
            "computed_sha256": computed_hash,
            "expected_sha256": self.EXPECTED_SHA256,
            "total_tokens_processed": total_tokens,
            "expected_tokens": self.EXPECTED_TOKENS,
            "hash_matched": hash_matched,
            "tokens_matched": tokens_matched
        }


if __name__ == "__main__":
    checker = PreFlightChecker()
    res = checker.run_preflight_check(enforce_hard_stop=False)
    print("=== TEST UNITARIO UTILS_PREFLIGHT3 RELEASE v3.3 ===")
    print(f"Status: {res['status']}")
    print(f"SHA256 Rilevato : {res['computed_sha256']}")
    print(f"Token Processati: {res['total_tokens_processed']}")