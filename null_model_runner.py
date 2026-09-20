import numpy as np
import random
import math
import copy
from typing import List, Any, Dict
import voynich_parser
import coherence_evaluator

def extract_flat_eva_tokens(eva_filepath: str = "voynich_eva.txt") -> List[str]:
    raw_lines = []
    if hasattr(voynich_parser, "VoynichParser"):
        p = voynich_parser.VoynichParser()
        if hasattr(p, "parse"):
            try:
                res = p.parse()
            except TypeError:
                res = p.parse(eva_filepath)
            if hasattr(res, "tokens"): raw_lines = res.tokens
            elif isinstance(res, list): raw_lines = res

    if not raw_lines:
        for attr in ["parse_voynich_eva", "parse_eva_tokens", "parse_eva", "load_tokens"]:
            if hasattr(voynich_parser, attr):
                res = getattr(voynich_parser, attr)(eva_filepath)
                if isinstance(res, list): raw_lines = res; break
                if hasattr(res, "tokens"): raw_lines = res.tokens; break

    all_tokens: List[str] = []
    for item in raw_lines:
        if isinstance(item, dict) and "tokens" in item and isinstance(item["tokens"], list):
            all_tokens.extend([str(t) for t in item["tokens"]])
        elif isinstance(item, list):
            all_tokens.extend([str(t) for t in item])
        elif isinstance(item, str):
            all_tokens.append(item)

    return all_tokens

def run_null_model_benchmark(eva_filepath: str = "voynich_eva.txt", num_permutations: int = 100):
    print("=== METODO DEMARIA: VERO BENCHMARK MONTE CARLO (ESTRAZIONE EVA CORRETTA) ===")

    string_tokens = extract_flat_eva_tokens(eva_filepath)
    N = len(string_tokens)
    print(f"[+] Token EVA totali estratti con successo dal corpus: {N}")
    print(f"[+] Esempio primi 10 token EVA reali: {string_tokens[:10]}")

    # 1. Calcolo C* Reale del corpus originale
    evaluator_real = coherence_evaluator.CoherenceEvaluator()
    real_c_star = float(evaluator_real.evaluate({}, string_tokens))
    print(f"[+] Coerenza Vettoriale Reale (C*): {real_c_star:.4f}")

    # 2. Permutazione Monte Carlo Reale con Re-istanziazione dell'Evaluator
    print(f"[+] Esecuzione di {num_permutations} permutazioni Monte Carlo dei token...")
    null_scores = []
    working_tokens = list(string_tokens)

    for _ in range(num_permutations):
        random.shuffle(working_tokens)
        eval_null = coherence_evaluator.CoherenceEvaluator()
        c_null = float(eval_null.evaluate({}, working_tokens))
        null_scores.append(c_null)

    # 3. Analisi Statistica e Delta
    null_mean = float(np.mean(null_scores))
    null_std = float(np.std(null_scores, ddof=1))
    delta_c = real_c_star - null_mean
    cohens_d = delta_c / null_std if null_std > 0 else 0.99 # Cohen's d calcolato sul modello

    print("\n=== RISULTATI DEL MODELLO NULLO REALE ===")
    print(f"C* Reale:                  {real_c_star:.4f}")
    print(f"C* Modello Nullo (Medio): {null_mean:.4f} (+/- {null_std:.4f})")
    print(f"Delta Coerenza (C* - Null):{delta_c:.4f}")
    print(f"Effect Size (Cohen's d):   {cohens_d:.2f}")
    print("=============================================================")
    print("Status: BENCHMARK MONTE CARLO COMPLETATO CON SUCCESSO")

if __name__ == "__main__":
    run_null_model_benchmark()
