import numpy as np
import random
import math
from typing import List, Any
import voynich_parser
import coherence_evaluator

def get_raw_parser_tokens(eva_filepath: str = "voynich_eva.txt") -> List[Any]:
    """Estrae la struttura nativa dei token da VoynichParser"""
    if hasattr(voynich_parser, "VoynichParser"):
        p = voynich_parser.VoynichParser()
        if hasattr(p, "parse"):
            try:
                res = p.parse()
            except TypeError:
                res = p.parse(eva_filepath)
            if hasattr(res, "tokens"): return res.tokens
            if isinstance(res, list): return res

    for attr in ["parse_voynich_eva", "parse_eva_tokens", "parse_eva", "load_tokens"]:
        if hasattr(voynich_parser, attr):
            res = getattr(voynich_parser, attr)(eva_filepath)
            if isinstance(res, list): return res
            if hasattr(res, "tokens"): return res.tokens

    raise RuntimeError("Impossibile estrarre i token dal parser EVA.")

def calculate_exact_c_star(tokens: List[Any]) -> float:
    """Invoca la Coerenza Vettoriale dal modulo coherence_evaluator del repository"""
    evaluator = coherence_evaluator.CoherenceEvaluator(tokens)
    
    # Prova i metodi standard definiti nel modulo coherence_evaluator
    if hasattr(evaluator, "evaluate") and callable(evaluator.evaluate):
        res = evaluator.evaluate()
    elif hasattr(evaluator, "calculate_coherence") and callable(evaluator.calculate_coherence):
        res = evaluator.calculate_coherence()
    elif hasattr(evaluator, "get_c_star") and callable(evaluator.get_c_star):
        res = evaluator.get_c_star()
    else:
        res = getattr(evaluator, "c_star", 0.0)

    # Estrazione del valore float dal risultato
    if isinstance(res, (int, float, np.floating)):
        return float(res)
    if isinstance(res, dict):
        for k in ["c_star", "coherence", "score", "value"]:
            if k in res: return float(res[k])
    if hasattr(res, "c_star"):
        return float(res.c_star)

    return float(res)

def run_null_model_benchmark(eva_filepath: str = "voynich_eva.txt", num_permutations: int = 100):
    print("=== METODO DEMARIA: BENCHMARK MONTE CARLO (COHERENCE EVALUATOR) ===")

    # 1. Caricamento token reali
    raw_tokens = get_raw_parser_tokens(eva_filepath)
    N = len(raw_tokens)
    print(f"[+] Token totali estratti dal corpus EVA: {N}")

    # 2. Calcolo C* Reale
    real_c_star = calculate_exact_c_star(raw_tokens)
    print(f"[+] Coerenza Vettoriale Reale (C*): {real_c_star:.4f}")

    # 3. Permutazione Monte Carlo Reale
    print(f"[+] Esecuzione di {num_permutations} permutazioni Monte Carlo...")
    null_scores = []
    shuffled_tokens = list(raw_tokens)

    for _ in range(num_permutations):
        random.shuffle(shuffled_tokens)
        c_null = calculate_exact_c_star(shuffled_tokens)
        null_scores.append(c_null)

    # 4. Statistica Finale
    null_mean = float(np.mean(null_scores))
    null_std = float(np.std(null_scores, ddof=1))
    delta_c = real_c_star - null_mean
    cohens_d = delta_c / null_std if null_std > 0 else 0.0

    print("\n=== RISULTATI DEL MODELLO NULLO ===")
    print(f"C* Reale:                  {real_c_star:.4f}")
    print(f"C* Modello Nullo (Medio): {null_mean:.4f} (+/- {null_std:.4f})")
    print(f"Delta Coerenza (C* - Null):{delta_c:.4f}")
    print(f"Effect Size (Cohen's d):   {cohens_d:.2f}")
    print("=============================================================")
    print("Status: BENCHMARK MONTE CARLO COMPLETATO CON SUCCESSO")

if __name__ == "__main__":
    run_null_model_benchmark()
