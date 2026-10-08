"""
===============================================================================
METODO DEMARIA® — BATCH RUNNER MASTER ORCHESTRATOR (v3.2 AUDIT-MASTER)
===============================================================================
Modulo 7: 7_batch_runner.py
Autore e Inventore Unico: Avv. Alessandro Demaria
PEC: avv.alessandrodemaria@pec.it
DOI UFFICIALE: 10.5281/zenodo.23199718
Licenza: CC BY 4.0
===============================================================================
"""

import os
import json
import hashlib
import importlib.util
from datetime import datetime
import numpy as np
import pandas as pd

def _import_module(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

mod1 = _import_module("mod1_parser", "1_voynich_parser.py")
mod2 = _import_module("mod2_null", "2_null_model_test.py")
mod3 = _import_module("mod3_double", "3_double_randomization_test.py")
mod4 = _import_module("mod4_robustness", "4_robustness_stress_test.py")
mod5 = _import_module("mod5_holdout", "5_train_test_split_validation.py")
mod6 = _import_module("mod6_charts", "6_generate_charts.py")

def compute_sha256(filepath):
    if not os.path.exists(filepath):
        return "FILE_NOT_FOUND"
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def run_preflight_checks(spec_path="method_specification.json"):
    print("=" * 75)
    print("METODO DEMARIA® — Release v3.2 (Audit-Master)")
    print("ESECUZIONE AUDIT INTEGRATO SUITE MASTER (MODULI 1-7)")
    print("=" * 75)

    spec = mod1.load_method_specification(spec_path)
    csv_path = spec.get("master_dataset", {}).get("filename", "voynich_eva_tokens_extended.csv")

    expected_hash = spec.get("master_dataset", {}).get("sha256_hash", "dec87e784290ad5b404bd5ed0110349a2f379c7fb386adb0bca2d7a4b1890999")
    detected_hash = compute_sha256(csv_path)

    print(f"[*] Specifica Canonica:     {spec_path}")
    print(f"[*] Dataset Master:         {csv_path}")
    print(f"[*] SHA-256 Atteso:         {expected_hash}")
    print(f"[*] SHA-256 Rilevato:       {detected_hash}")

    df = mod1.parse_and_clean_dataset(spec_path)
    print(f"[1/7] PARSING E VERIFICA DATASET: OK. Tokens={len(df)}, Folii={df['Folio_Base'].nunique()}, Righe={df['Composite_Line_Key'].nunique()}")
    return df, spec

def execute_master_audit():
    start_time = datetime.now()
    df, spec = run_preflight_checks()

    raw_matrix = spec.get("transition_matrix_validity", {}).get("allowed_transitions", [
        [True, True, False, False],
        [False, True, True, False],
        [False, False, True, True],
        [True, False, False, True]
    ])
    transition_matrix = np.array(raw_matrix, dtype=bool)

    n_simulations = spec.get("system_parameters", {}).get("n_monte_carlo_iterations", 10000)
    seed = spec.get("system_parameters", {}).get("seed", 42)

    print("=" * 75)
    print(f"[2/7] Esecuzione Hierarchical Null Models (N={n_simulations})...")
    null_results_df, global_scores, folio_scores, line_scores = mod2.run_full_audit_suite(
        df=df, transition_matrix=transition_matrix, n_simulations=n_simulations, seed=seed
    )

    print("=" * 75)
    print(f"[3/7] Esecuzione Isomorphic Double Randomization & Matrix Sweep (N={n_simulations})...")
    double_summary, double_scores = mod3.run_double_randomization_test(
        df=df, transition_matrix=transition_matrix, n_simulations=n_simulations, seed=seed
    )
    sweep_summary, matrix_sweep_scores = mod3.run_fixed_corpus_matrix_sweep(
        df=df, transition_matrix=transition_matrix, n_simulations=n_simulations, seed=seed
    )

    print("=" * 75)
    print("[4/7] Esecuzione Uniform State Replacement Robustness Test...")
    robustness_df = mod4.run_uniform_state_replacement_robustness(
        df=df, transition_matrix=transition_matrix, n_iterations=100, seed=seed
    )

    print("=" * 75)
    print("[5/7] Esecuzione Spatial Structural Stability Analysis (Repeated MC Holdout)...")
    single_holdout_summary = mod5.run_holdout_validation(
        df=df, transition_matrix=transition_matrix, split_ratio=0.5, seed=seed
    )
    repeated_holdout_summary = mod5.run_repeated_holdout_validation(
        df=df, transition_matrix=transition_matrix, n_iterations=1000, split_ratio=0.5, seed=seed
    )

    print("=" * 75)
    print("[6/7] Generazione Grafici Empirici ad Alta Risoluzione (300 DPI)...")
    c_obs = float(null_results_df.loc[0, 'c_obs'])
    mod6.generate_empirical_charts(
        c_obs=c_obs,
        global_scores=global_scores,
        line_scores=line_scores,
        double_scores=double_scores,
        robustness_df=robustness_df,
        matrix_sweep_scores=matrix_sweep_scores,
        output_prefix="audit_master"
    )

    print("=" * 75)
    print("[7/7] FINALIZE: Esportazione Report JSON/CSV e Generazione Manifest Crittografico Completo...")
    
    null_results_df.to_csv("audit_master_summary_results.csv", index=False)
    robustness_df.to_csv("robustness_test_results.csv", index=False)

    summary_json_data = {
        "timestamp": datetime.now().isoformat(),
        "release": "v3.2 (Audit-Master Canonico)",
        "doi": "10.5281/zenodo.23199718",
        "c_obs": c_obs,
        "null_models": null_results_df.to_dict(orient="records"),
        "double_randomization": double_summary,
        "fixed_corpus_matrix_sweep": sweep_summary,
        "spatial_holdout_single": single_holdout_summary,
        "spatial_holdout_repeated_mc": repeated_holdout_summary
    }

    with open("audit_master_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary_json_data, f, indent=2)

    # GENERAZIONE COMPLETA E RIGOROSA DEL MANIFEST CRITTOGRAFICO PER TUTTI I FILE
    manifest_files = [
        "method_specification.json",
        "1_voynich_parser.py",
        "2_null_model_test.py",
        "3_double_randomization_test.py",
        "4_robustness_stress_test.py",
        "5_train_test_split_validation.py",
        "6_generate_charts.py",
        "7_batch_runner.py",
        "voynich_eva_tokens_extended.csv",
        "audit_master_summary_results.csv",
        "robustness_test_results.csv",
        "audit_master_summary.json"
    ]

    manifest_data = {
        "project": "METODO DEMARIA",
        "release": "Release v3.2 (Audit-Master)",
        "author": "Avv. Alessandro Demaria",
        "pec": "avv.alessandrodemaria@pec.it",
        "timestamp": datetime.now().isoformat(),
        "files_sha256": {fname: compute_sha256(fname) for fname in manifest_files}
    }

    with open("audit_master_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)

    elapsed = (datetime.now() - start_time).total_seconds()
    print("=" * 75)
    print(f"[OK] Audit Master completato con successo in {round(elapsed, 2)} secondi.")
    print("     Summary JSON salvato in:     audit_master_summary.json")
    print("     Report CSV salvati in:       audit_master_summary_results.csv, robustness_test_results.csv")
    print("     Manifest SHA-256 salvato in: audit_master_manifest.json")
    print("=" * 75)

if __name__ == "__main__":
    execute_master_audit()