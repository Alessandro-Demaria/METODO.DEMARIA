"""
===============================================================================
METODO DEMARIA™ — SCRIPT DI SIGILLO E ARCHIVIAZIONE ZIP MASTER (v3.2)
===============================================================================
Modulo: seal_archive.py
Autore: Avv. Alessandro Demaria | Licenza: CC BY 4.0
===============================================================================
"""

import os
import zipfile
import hashlib
from datetime import datetime

# Nome dell'Archivio Sigillato Finale
ARCHIVE_NAME = "METODO_DEMARIA_VOYNICH_AUDIT_MASTER_v3.2_SIGILLATO.zip"

# Elenco completo di tutti i file costituenti il Pacchetto Master v3.2
FILES_TO_INCLUDE = [
    # Dataset e Specifica Algebrica
    "voynich_eva_tokens_extended.csv",
    "method_specification.json",
    
    # Moduli di Laboratorio Python
    "voynich_parser.py",
    "null_model_test.py",
    "double_randomization_test.py",
    "robustness_stress_test.py",
    "batch_runner.py",
    "generate_charts.py",
    "seal_archive.py",
    
    # Report e Audit CSV
    "audit_master_summary_results.csv",
    "robustness_test_results.csv",
    
    # Attestato e Documentazione
    "METODO DEMARIA MANIFEST_AUDIT.txt",
    
    # Grafici ad Alta Risoluzione (300 DPI)
    "chart_1_null_models_zscores.png",
    "chart_2_robustness_stress_test.png",
    "chart_3_double_randomization.png"
]

def calculate_sha256(filepath):
    """Calcola l'impronta crittografica SHA-256 di un file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def create_sealed_zip():
    print("=" * 78)
    print("METODO DEMARIA™ — CREAZIONE E SIGILLO CRITTOGRAFICO PACCHETTO MASTER v3.2")
    print("=" * 78 + "\n")

    # 1. Verifica presenza di tutti i file richiesti
    missing_files = [f for f in FILES_TO_INCLUDE if not os.path.exists(f)]
    if missing_files:
        print(f"[-] ERRORE CRITICO: Mancano i seguenti file richiesti:")
        for mf in missing_files:
            print(f"    - {mf}")
        print("\nImpossibile procedere con il sigillo.")
        return

    # 2. Creazione dell'Archivio ZIP Compresso
    print(f"[*] Compressione dei {len(FILES_TO_INCLUDE)} file dell'Audit Master v3.2...")
    with zipfile.ZipFile(ARCHIVE_NAME, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in FILES_TO_INCLUDE:
            zipf.write(file, arcname=os.path.basename(file))
            print(f"    -> Aggiunto: {file}")

    print(f"\n[+] Archivio ZIP creato con successo: '{ARCHIVE_NAME}'")

    # 3. Calcolo dell'Impronta Crittografica SHA-256 dell'Archivio ZIP
    zip_sha256 = calculate_sha256(ARCHIVE_NAME)
    file_size_bytes = os.path.getsize(ARCHIVE_NAME)
    file_size_mb = file_size_bytes / (1024 * 1024)

    # 4. Output Formale di Congelamento per Uso Legale / Notarile / Zenodo
    print("\n" + "=" * 78)
    print("IMPRONTA CRITTOGRAFICA MASTER PER DEPOSITO LEGALE / NOTARILE / MARCA TEMPORALE")
    print("=" * 78)
    print(f"[*] Nome Pacchetto Sigillato : {ARCHIVE_NAME}")
    print(f"[*] Data e Ora Archiviazione: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"[*] Dimensione Archivio     : {file_size_mb:.2f} MB ({file_size_bytes:,} bytes)")
    print(f"[*] SHA-256 PACCHETTO ZIP   : {zip_sha256}")
    print("=" * 78 + "\n")

if __name__ == "__main__":
    create_sealed_zip()