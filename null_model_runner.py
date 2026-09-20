import pandas as pd
import numpy as np
import random
import math
from typing import List, Tuple

import voynich_parser
from coherence_evaluator import CoherenceEvaluator

def extract_tokens_from_result(res) -> List[str]:
    if isinstance(res, list):
        return res
    if hasattr(res, "tokens"):
        return res.tokens
    if hasattr(res, "get_tokens") and callable(res.get_tokens):
        return res.get_tokens()
    raise ValueError(f"Impossibile estrarre token dall'oggetto di tipo: {type(res)}")

def get_tokens_from_parser(eva_filepath: str) -> List[str]:
    for attr in ["parse_voynich_eva", "parse_eva_tokens", "parse_eva", "load_tokens"]:
        if hasattr(voynich_parser, attr):
            res = getattr(voynich_parser, attr)(eva_filepath)
            return extract_tokens_from_result(res)
    
    if hasattr(voynich_parser, "VoynichParser"):
        parser_obj = voynich_parser.VoynichParser()
        if hasattr(parser_obj, "parse"):
            try:
                res = parser_obj.parse()
            except TypeError:
                res = parser_obj.parse(eva_filepath)
            return extract_tokens_from_result(res)
        return extract_tokens_from_result(parser_obj)

    funcs = [getattr(voynich_parser, f) for f in dir(voynich_parser) if callable(getattr(voynich_parser, f)) and not f.startswith("__")]
    if funcs:
        try:
            res = funcs[0](eva_filepath)
        except TypeError:
            res = funcs[0]()
        return extract_tokens_from_result(res)
        
    raise AttributeError("Nessuna funzione o classe di parsing valida trovata in voynich_parser.py")

def evaluate_c_star(tokens: List[str]) -> float:
    evaluator = CoherenceEvaluator()
    res = evaluator.evaluate(tokens)
    
    if isinstance(res, (int, float, np.floating)):
        return float(res)
    if hasattr(res, "c_star"):
        return float(res.c_star)
    if hasattr(res, "score"):
        return float(res.score)
    if isinstance(res, dict) and "c_star" in res:
        return float(res["c_star"])
    
    return float(res)

def run_null_model_benchmark(eva_filepath: str = "voynich_eva.txt", num_permutations: int = 100):
    print("=== METODO DEMARIA: TRUE MONTE CARLO NULL MODEL BENCHMARK ===")
    
    try:
        print(f"[+] Caricamento del corpus da: {eva_filepath}...")
        raw_tokens = get_tokens_from_parser(eva_filepath)
        print(f"[+] Token totali estratti con successo: {len(raw_tokens)}")
    except Exception as e:
        print(f"[-] Errore durante il caricamento del corpus EVA: {e}")
        return

    try:
        real_coherence = evaluate_c_star(raw_tokens)
        print(f"[+] Coerenza Vettoriale Reale (C*): {real_coherence:.4f}")
    except Exception as e:
        print(f"[-] Errore durante il calcolo di C* reale: {e}")
        return

    print(f"[+] Avvio di {num_permutations} permutazioni Monte Carlo dei token...")
    null_coherence_scores: List[float] = []
    working_tokens = list(raw_tokens).copy()

    for i in range(num_permutations):
        random.shuffle(working_tokens)
        c_star_null = evaluate_c_star(working_tokens)
        null_coherence_scores.append(c_star_null)

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
