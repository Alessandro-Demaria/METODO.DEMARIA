#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Modulo: utils_preflight3.py
Descrizione: Audit di integrità e preflight crittografico (Punto 1.4 - Scheda SORU).
             Effettua il controllo vincolante (hard check) sull'hash SHA-256 del dataset canonico,
             sulla cardinalità esatta (35.483 record) e sulla struttura delle coordinate.

Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
Licenza Codebase: MIT License
"""

import os
import hashlib
import logging
import pandas as pd

# Configurazione Logger di Laboratorio
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


class PreflightIntegrityAudit:
    """
    Gestore dell'Audit di Integrità e Validazione Crittografica Preflight.
    Impone vincoli d'arresto immediato (hard fail) in caso di discrepanza dati/hash.
    """

    # Impronta crittografica ufficiale SHA-256 congelata nel Trattato v3.3
    CANONICAL_SHA256 = "dec87e784290ad5b404bd5ed0110349a2f379c7fb386adb0bca2d7a4b1890999"
    CANONICAL_RECORD_COUNT = 35483

    def __init__(self, dataset_path: str = "voynich_eva_tokens_extended.csv"):
        self.dataset_path = dataset_path

    def compute_sha256(self) -> str:
        """Calcola l'impronta crittografica SHA-256 del file su disco."""
        sha256_hash = hashlib.sha256()
        with open(self.dataset_path, "rb") as f:
            for byte_block in iter(lambda: f.read(65536), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest().lower()

    def run_preflight_checks(self) -> dict:
        """
        Esegue i controlli vincolanti di preflight sul dataset master.
        Restituisce un dizionario contenente l'esito formale e le metriche di validazione.
        """
        logging.info("[Preflight] Avvio verifica di integrità ed hash crittografico SHA-256...")

        # 1. Verifica Esistenza File
        if not os.path.exists(self.dataset_path):
            msg = f"FILE NOT FOUND: Impossibile trovare il dataset al percorso {self.dataset_path}"
            logging.error(f"[Preflight] {msg}")
            return {"status": "FAILED", "error": msg}

        # 2. Controllo Crittografico SHA-256 (Hard Fail)
        calculated_hash = self.compute_sha256()
        if calculated_hash != self.CANONICAL_SHA256:
            msg = (
                f"CRITICAL SHA256 MISMATCH: Hash calcolato ({calculated_hash}) "
                f"difforme dall'hash canonico v3.3 ({self.CANONICAL_SHA256})"
            )
            logging.error(f"[Preflight] {msg}")
            return {
                "status": "FAILED",
                "calculated_sha256": calculated_hash,
                "expected_sha256": self.CANONICAL_SHA256,
                "error": msg
            }

        logging.info(f"[Preflight] Hash SHA-256 VERIFICATO: {calculated_hash}")

        # 3. Caricamento Dati e Verifica Strutturale
        try:
            df = pd.read_csv(self.dataset_path)
        except Exception as e:
            msg = f"PARSE ERROR: Errore durante il caricamento del file CSV: {e}"
            logging.error(f"[Preflight] {msg}")
            return {"status": "FAILED", "error": msg}

        # 4. Verifica Cardinalità Record (Hard Fail)
        actual_records = len(df)
        if actual_records != self.CANONICAL_RECORD_COUNT:
            msg = (
                f"RECORD COUNT MISMATCH: Conteggio record ({actual_records}) "
                f"difforme dal valore canonico ({self.CANONICAL_RECORD_COUNT})"
            )
            logging.error(f"[Preflight] {msg}")
            return {
                "status": "FAILED",
                "actual_records": actual_records,
                "expected_records": self.CANONICAL_RECORD_COUNT,
                "error": msg
            }

        # 5. Controllo Flessibile e Case-Insensitive delle Colonne
        cols_lower = [str(c).strip().lower() for c in df.columns]

        has_record_id = "record_id" in cols_lower
        has_folio = "folio" in cols_lower
        has_token = any(t in cols_lower for t in ["token", "eva_token", "eva"])

        if not (has_record_id and has_folio and has_token):
            missing = []
            if not has_record_id: missing.append("Record_ID")
            if not has_folio: missing.append("Folio")
            if not has_token: missing.append("token")
            msg = f"MISSING COLUMNS: Colonne obbligatorie assenti: {missing}"
            logging.error(f"[Preflight] {msg}")
            return {"status": "FAILED", "error": msg}

        # 6. Identificazione e verifica colonna Token
        token_col = None
        for col in df.columns:
            if str(col).strip().lower() in ["token", "eva_token", "eva"]:
                token_col = col
                break

        if token_col is None or df[token_col].isnull().any():
            msg = "NULL VALUES: Presenti valori nulli o vuoti nella colonna dei token"
            logging.error(f"[Preflight] {msg}")
            return {"status": "FAILED", "error": msg}

        logging.info(f"[Preflight] Dataset di {actual_records} record validato con successo.")

        folio_col = next((col for col in df.columns if str(col).strip().lower() == "folio"), "Folio")
        return {
            "status": "SUCCESS",
            "sha256_hash": calculated_hash,
            "total_records": actual_records,
            "unique_folios": int(df[folio_col].nunique())
        }


if __name__ == "__main__":
    audit = PreflightIntegrityAudit()
    result = audit.run_preflight_checks()
    print("\nResult:", result)
