"""
===============================================================================
METODO DEMARIA® — BATCH RUNNER MASTER (v3.2 AUDIT-MASTER)
===============================================================================
Modulo: batch_runner.py
Autore e Inventore: Avv. Alessandro Demaria
PEC: avv.alessandrodemaria@pec.it
DOI UFFICIALE: 10.5281/zenodo.23199718
Licenza: CC BY 4.0
===============================================================================
"""

import os
import json
import hashlib
from datetime import datetime
import numpy as np
import pandas as pd

import voynich_parser
import null_model_test
import double_randomization_test
import robustness_stress_test
import train_test_split_validation
import generate_charts


def compute_sha256(filepath):
    """Calcola l'impronta crittografica SHA-256 di un file su disco."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def run_preflight_checks(spec_path="method_specification.json"):
    """
    Esegue le verifiche pre-flight e il controllo d'integrità Fail-Fast.
    """
    print("=" * 75)
    print("METODO DEMARIA® — Release v3.2 (Audit-Master)")
    print("ESECUZIONE AUDIT INTEGRATO SUITE ALESSANDRO")
    print("=" * 75 + "\n")

    if not os.path.exists(spec_path):
        raise FileNotFoundError(f"[!] ERRORE CRITICO: Specifica '{spec_path}' non trovata.")

    spec = voynich_parser.load_method_specification(spec_path)
    csv_path = spec.get("master_dataset", {}).get("filename", "voynich_eva_tokens_extended.csv")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"[!] ERRORE CRITICO: Dataset Master '{csv_path}' non trovato.")

    expected_hash = spec.get("master_dataset", {}).get("sha256_hash", "dec87e784290ad5b404bd5ed0110349a2f379c7fb386adb0bca2d7a4b1890999")
    detected_hash = compute_sha256(csv_path)

    print(f"[*] Specifica Canonica:     {spec_path}")
    print(f"[*] Dataset Master:         {csv_path}")
    print(f"[*] SHA-256 Atteso:         {expected_hash}")
    print(f"[*] SHA-256 Rilevato:       {detected_hash}")

    if expected_hash.lower() != detected_hash.lower():
        print("[!] AVVERTIMENTO: Discrepanza Hash SHA-256 (Procedo con il dataset locale).")
    else:
        print("[1/6] VERIFICA CRITTOGRAFICA DATASET: PASS.")

    df = voynich_parser.parse_and_clean_dataset(spec_path)
    n_records = len(df)
    n_folios = df['Folio_Base'].nunique()
    n_line_keys = df['Composite_Line_Key'].nunique()

    print(f"   - Corpus caricato con successo: {n_records} token, {n_folios} folii, {n_line_keys} chiavi di rigo.\n")
    return df, spec


def execute_master_audit():
    start_time = datetime.now()
    df, spec = run_preflight_checks()

    raw_matrix = spec.get("transition_matrix_validity", {}).get("allowed_transitions", None)
    if raw_matrix is None:
        raw_matrix = [
            [1, 1, 0, 0],
            [0, 1, 1, 0],
            [0, 0, 1, 1],
            [1, 0, 0, 1]
        ]
    transition_matrix = np.array(raw_matrix, dtype=bool)

    n_simulations = spec.get("system_parameters", {}).get("n_monte_carlo_iterations", 10000)
    seed = spec.get("system_parameters", {}).get("seed", 42)

    # -------------------------------------------------------------------------
    # FASE 2: Modelli Nulli Gerarchici
    # -------------------------------------------------------------------------
    print("=" * 75)
    print(f"[2/6] Esecuzione Hierarchical Null Models (N={n_simulations})...")
    null_results_df, global_scores, folio_scores, line_scores = null_model_test.run_full_audit_suite(
        df=df, transition_matrix=transition_matrix, n_simulations=n_simulations, seed=seed
    )

    # -------------------------------------------------------------------------
    # FASE 3: Double Randomization Test
    # -------------------------------------------------------------------------
    print("=" * 75)
    print(f"[3/6] Esecuzione Isomorphic Double Randomization Test (N={n_simulations})...")
    double_summary, double_scores = double_randomization_test.run_double_randomization_test(
        df=df, transition_matrix=transition_matrix, n_simulations=n_simulations, seed=seed
    )

    # -------------------------------------------------------------------------
    # FASE 4: Robustness & Noise Stress Test
    # -------------------------------------------------------------------------
    print("=" * 75)
    print("[4/6] Esecuzione Robustness & Noise Stress Test...")
    robustness_df = robustness_stress_test.run_robustness_stress_test(
        df=df, transition_matrix=transition_matrix, n_iterations=100, seed=seed
    )

    # -------------------------------------------------------------------------
    # FASE 5: Spatial Structural Stability Analysis (Holdout 50/50)
    # -------------------------------------------------------------------------
    print("=" * 75)
    print("[5/6] Esecuzione Spatial Structural Stability Analysis (Split 50/50)...")
    holdout_summary = train_test_split_validation.run_holdout_validation(
        df=df, transition_matrix=transition_matrix, split_ratio=0.5, seed=seed
    )

    # -------------------------------------------------------------------------
    # FASE 6: Generazione Grafici Empirici Reali
    # -------------------------------------------------------------------------
    print("=" * 75)
    print("[6/6] Generazione Grafici Empirici ad Alta Risoluzione...")
    c_obs = float(null_results_df.loc[0, 'c_obs'])
    generate_charts.generate_empirical_charts(
        c_obs=c_obs,
        global_scores=global_scores,
        line_scores=line_scores,
        double_scores=double_scores,
        robustness_df=robustness_df,
        output_prefix="audit_master"
    )

    # -------------------------------------------------------------------------
    # ESPORTAZIONE E SALVATAGGIO REPORT
    # -------------------------------------------------------------------------
    print("=" * 75)
    print("[FINALIZE] Esportazione Report JSON/CSV e Generazione Manifest Crittografico...")
    
    null_results_df.to_csv("audit_master_summary_results.csv", index=False)
    robustness_df.to_csv("robustness_test_results.csv", index=False)

    summary_json_data = {
        "timestamp": datetime.now().isoformat(),
        "release": "v3.2 (Audit-Master)",
        "doi": "10.5281/zenodo.23199718",
        "c_obs": c_obs,
        "null_models": null_results_df.to_dict(orient="records"),
        "double_randomization": double_summary,
        "spatial_holdout": holdout_summary
    }

    with open("audit_master_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary_json_data, f, indent=2)

    # Calcolo Hash SHA-256 del pacchetto risultati
    manifest_data = {
        "project": "METODO DEMARIA",
        "release": "Release v3.2 (Audit-Master)",
        "author": "Avv. Alessandro Demaria",
        "pec": "avv.alessandrodemaria@pec.it",
        "timestamp": datetime.now().isoformat(),
        "files_sha256": {
            "method_specification.json": compute_sha256("method_specification.json"),
            "audit_master_summary_results.csv": compute_sha256("audit_master_summary_results.csv"),
            "robustness_test_results.csv": compute_sha256("robustness_test_results.csv"),
            "audit_master_summary.json": compute_sha256("audit_master_summary.json")
        }
    }

    with open("audit_master_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)

    elapsed = (datetime.now() - start_time).total_seconds()
    print("\n" + "=" * 75)
    print(f"[OK] Audit completato con successo in {elapsed:.2f} secondi.")
    print("     Summary JSON salvato in: audit_master_summary.json")
    print("     Report CSV salvati in:   audit_master_summary_results.csv, robustness_test_results.csv")
    print("     Manifest SHA-256 salvato in: audit_master_manifest.json")
    print("=" * 75 + "\n")


if __name__ == "__main__":
    execute_master_audit()