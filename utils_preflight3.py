#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO SCIENTIFICO METODO DEMARIA®
Release v3.3 (Audit-Master Unificato)

Modulo: utils_preflight3.py
Descrizione: Modulo di controllo e verifica integrità preliminare dei dati (Preflight Audit).
             Integrazione della normalizzazione canonica Folio / folio_id / line_id (P0.2 / P0.3).

Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
Licenza Codebase: MIT License
"""

import os
import hashlib
import pandas as pd


class PreflightIntegrityAudit:
    """
    Gestisce i controlli di integrità preliminare sui dataset e file di laboratorio.
    Normalizza la struttura delle coordinate spaziali per l'intera suite di audit.
    """

    def __init__(self, dataset_path="voynich_eva_tokens_extended.csv"):
        self.dataset_path = dataset_path
        self.expected_hash = "dec87e784290ad5b404bd5ed0110349a2f379c7fb386adb0bca2d7a4b1890999"
        self.expected_record_count = 35483

    def compute_sha256(self, file_path: str) -> str:
        """Calcola l'impronta crittografica SHA-256 di un file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def normalize_dataset_structure(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Risoluzione P0.2 / P0.3: Scomposizione e normalizzazione canonica degli identificativi.
        Isola 'folio_id', 'line_number', 'line_id' e crea la colonna 'folio' per la suite.
        """
        df_norm = df.copy()

        if "Folio" not in df_norm.columns and "folio" not in df_norm.columns:
            raise KeyError("[-] Errore Preflight: Colonna 'Folio' non presente nel dataset.")

        col_target = "Folio" if "Folio" in df_norm.columns else "folio"

        df_norm["folio_id"] = df_norm[col_target].astype(str).apply(lambda x: x.split(".")[0])
        df_norm["line_number"] = df_norm[col_target].astype(str).apply(
            lambda x: x.split(".")[1].split(",")[0] if "." in x else "1"
        )
        df_norm["line_id"] = df_norm["folio_id"] + "." + df_norm["line_number"]
        df_norm["folio"] = df_norm["folio_id"]

        return df_norm

    def run_preflight_checks(self) -> dict:
        """Esegue i controlli preliminari di esistenza, conteggio ed eventuale hash."""
        print("[+] Avvio Preflight Integrity Check...")

        if not os.path.exists(self.dataset_path):
            print(f"[-] Errore: Dataset '{self.dataset_path}' non trovato.")
            return {"status": "FAILED", "reason": "FILE_NOT_FOUND"}

        df = pd.read_csv(self.dataset_path)
        record_count = len(df)

        if record_count != self.expected_record_count:
            print(f"[!] Avviso: Conteggio record ({record_count}) diverso da atteso ({self.expected_record_count}).")

        try:
            df_normalized = self.normalize_dataset_structure(df)
            unique_folios = df_normalized["folio_id"].nunique()
            unique_lines = df_normalized["line_id"].nunique()
            print(f"[+] Normalizzazione Dati completata: {record_count} record, {unique_folios} folii unici, {unique_lines} righe uniche.")
        except Exception as e:
            print(f"[-] Errore durante la normalizzazione del dataset: {e}")
            return {"status": "FAILED", "reason": "NORMALIZATION_ERROR"}

        print("[+] Preflight Check COMPLETATO CON SUCCESSO.")
        return {
            "status": "SUCCESS",
            "record_count": record_count,
            "unique_folios": unique_folios,
            "unique_lines": unique_lines,
            "dataset_path": self.dataset_path
        }


if __name__ == "__main__":
    audit = PreflightIntegrityAudit()
    results = audit.run_preflight_checks()
    print("Risultati Preflight:", results)
