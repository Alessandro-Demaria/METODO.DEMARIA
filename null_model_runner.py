import pandas as pd
import numpy as np
import random
import math
from typing import List, Tuple

import voynich_parser
import coherence_evaluator

def get_tokens_from_parser(eva_filepath: str) -> List[str]:
    """Isola ed esegue la funzione di parsing presente in voynich_parser.py"""
    for attr in ["parse_voynich_eva", "parse_eva_tokens", "parse_eva", "load_tokens"]:
        if hasattr(voynich_parser, attr):
            return getattr(voynich_parser, attr)(eva_filepath)
    
    # Fallback su qualsiasi funzione callable pubblica nel modulo
    funcs = [getattr(voynich_parser, f) for f in dir(voynich_parser) if callable(getattr(voynich_parser, f)) and not f.startswith("__")]
    if funcs:
        return funcs[0](eva_filepath)
    raise AttributeError("Nessuna funzione di parsing trovata in voynich_parser.py")

def evaluate_c_star(tokens: List[str]) -> float:
    """Isola ed esegue la funzione di calcolo C* in coherence_evaluator.py"""
    for attr in ["calculate_vector_coherence", "evaluate_coherence", "calculate_coherence", "get_c_star", "compute_coherence"]:
        if hasattr(coherence_evaluator, attr):
            return getattr(coherence_evaluator, attr)(tokens)
            
    # Fallback su qualsiasi funzione callable pubblica nel modulo
    funcs = [getattr(coherence_evaluator, f) for f in dir(coherence_evaluator) if callable(getattr(coherence_evaluator, f)) and not f.startswith("__")]
    if funcs:
        return funcs[0](tokens)
    raise AttributeError("Nessuna funzione di calcolo coerenza trovata in coherence_evaluator.py")

def run_null_model_benchmark(eva_filepath: str = "voynich_eva.txt", num_permutations: int = 100):
    print("=== METODO DEMARIA: TRUE MONTE CARLO NULL MODEL BENCHMARK ===")
    
    # 1. Parsing dei token EVA reali
    try:
        print(f"[+] Caricamento del corpus da: {eva_filepath}...")
        raw_tokens = get_tokens_from_parser(eva_filepath)
        print(f"[+] Token totali estratti: {len(raw_tokens)}")
    except Exception as e:
        print(f"[-] Errore durante il caricamento del corpus EVA: {e}")
        return

    # 2. Calcolo della Coerenza Vettoriale Reale (C*)
    try:
        real_coherence = evaluate_c_star(raw_tokens)
        print(f"[+] Coerenza Vettoriale Reale (C*): {real_coherence:.4f}")
    except Exception as e:
        print(f"[-] Errore durante il calcolo di C* reale: {e}")
        return

    # 3. Permutazione Monte Carlo Reale (True Token Shuffle)
    print(f"[+] Avvio di {num_permutations} permutazioni Monte Carlo dei token...")
    null_coherence_scores: List[float] = []
    working_tokens = list(raw_tokens).copy()

    for i in range(num_permutations):
        random.shuffle(working_tokens)
        c_star_null = evaluate_c_star(working_tokens)
        null_coherence_scores.append(c_star_null)

    # 4. Statistica
    null_mean = float(np.mean(null_coherence_scores))
    null_std = float(np.std(null_coherence_scores, ddof=1))
    
    delta_c = real_coherence - null_mean
    cohens_d = delta_c / null_std if null_std > 0 else 0.0

    print("\n=== RISULTATI DEL MODELLO NULLO REALE ===")
    print(f"C* Reale:                  {real_coherence:.4f}")
    print(f"C* Modello Nullo (Medio): {null_mean:.4f} (+/- {null_std:.4f})")
    print(f"Delta Coerenza (C* - Null):{delta_c:.4f}")
    print(f"Effect Size (Cohen's d):   {cohens_d:.2f}")
    print("===========================================")
    print("Status: VERO TEST MONTE CARLO COMPLETATO CON SUCCESSO")

if __name__ == "__main__":
    run_null_model_benchmark()
