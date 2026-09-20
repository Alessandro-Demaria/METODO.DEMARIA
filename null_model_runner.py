import pandas as pd
import numpy as np
import random
import math
from typing import List, Tuple

# Import flessibile per gestire la funzione di parsing corretta
import voynich_parser
from coherence_evaluator import calculate_vector_coherence

def get_tokens_from_parser(eva_filepath: str) -> List[str]:
    """Tenta l'importazione dinamica della funzione di parsing da voynich_parser.py"""
    if hasattr(voynich_parser, "parse_voynich_eva"):
        return voynich_parser.parse_voynich_eva(eva_filepath)
    elif hasattr(voynich_parser, "parse_eva_tokens"):
        return voynich_parser.parse_eva_tokens(eva_filepath)
    elif hasattr(voynich_parser, "parse_eva"):
        return voynich_parser.parse_eva(eva_filepath)
    elif hasattr(voynich_parser, "load_tokens"):
        return voynich_parser.load_tokens(eva_filepath)
    else:
        # Cerca la prima funzione disponibile nel modulo
        functions = [getattr(voynich_parser, func) for func in dir(voynich_parser) if callable(getattr(voynich_parser, func)) and not func.startswith("__")]
        if functions:
            return functions[0](eva_filepath)
        raise AttributeError("Nessuna funzione di parsing valida trovata in voynich_parser.py")

def run_null_model_benchmark(eva_filepath: str = "voynich_eva.txt", num_permutations: int = 100):
    print("=== METODO DEMARIA: TRUE MONTE CARLO NULL MODEL BENCHMARK ===")
    
    # 1. Caricamento e parsing dei token EVA reali dal file
    try:
        print(f"[+] Caricamento del corpus da: {eva_filepath}...")
        raw_tokens = get_tokens_from_parser(eva_filepath)
        print(f"[+] Token totali estratti: {len(raw_tokens)}")
    except Exception as e:
        print(f"[-] Errore durante il caricamento del corpus EVA: {e}")
        return

    # 2. Calcolo della Coerenza Vettoriale Reale (C*)
    try:
        real_coherence = calculate_vector_coherence(raw_tokens)
        print(f"[+] Coerenza Vettoriale Reale (C*): {real_coherence:.4f}")
    except Exception as e:
        print(f"[-] Errore durante il calcolo di C* reale: {e}")
        return

    # 3. Esecuzione della vera permutazione Monte Carlo (True Token Shuffle)
    print(f"[+] Avvio di {num_permutations} permutazioni Monte Carlo dei token...")
    null_coherence_scores: List[float] = []
    working_tokens = list(raw_tokens).copy()

    for i in range(num_permutations):
        # Permutazione fisica dei token (mantiene le frequenze, distrugge la sintassi adiacente)
        random.shuffle(working_tokens)
        
        # Ricalcolo reale di C* passando attraverso la pipeline
        c_star_null = calculate_vector_coherence(working_tokens)
        null_coherence_scores.append(c_star_null)

    # 4. Analisi Statistica e Confronto
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
