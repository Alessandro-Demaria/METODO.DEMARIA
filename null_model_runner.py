import pandas as pd
import numpy as np
import random
import math
from typing import List, Tuple

import voynich_parser
import coherence_evaluator

def extract_tokens_from_result(res) -> List[str]:
    """Estrae la lista di token dal risultato del parser"""
    if isinstance(res, list):
        return res
    if hasattr(res, "tokens"):
        return res.tokens
    if hasattr(res, "get_tokens") and callable(res.get_tokens):
        return res.get_tokens()
    raise ValueError(f"Impossibile estrarre token dall'oggetto di tipo: {type(res)}")

def get_tokens_from_parser(eva_filepath: str) -> List[str]:
    """Esegue il parsing dei token EVA"""
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

def extract_score(res) -> float:
    """Estrae il valore numerico da qualsiasi tipo di output restituito"""
    if isinstance(res, (int, float, np.floating)):
        return float(res)
    if hasattr(res, "c_star"):
        return float(res.c_star)
    if hasattr(res, "score"):
        return float(res.score)
    if isinstance(res, dict):
        for k in ["c_star", "coherence", "score", "value"]:
            if k in res:
                return float(res[k])
    raise ValueError(f"Impossibile estrarre lo score numerico da: {type(res)}")

def evaluate_c_star(tokens: List[str]) -> float:
    """Esegue il calcolo di C* gestendo sia funzioni modulo che la classe CoherenceEvaluator"""
    # 1. Prova funzioni dirette di modulo
    for attr in ["calculate_vector_coherence", "evaluate_coherence", "calculate_coherence", "get_c_star", "compute_coherence"]:
        if hasattr(coherence_evaluator, attr):
            res = getattr(coherence_evaluator, attr)(tokens)
            return extract_score(res)

    # 2. Prova la classe CoherenceEvaluator con inizializzazione o metodo evaluate
    if hasattr(coherence_evaluator, "CoherenceEvaluator"):
        # Tentativo A: Istanziazione con tokens -> evaluator = CoherenceEvaluator(tokens)
        try:
            eval_obj = coherence_evaluator.CoherenceEvaluator(tokens)
            if hasattr(eval_obj, "evaluate") and callable(eval_obj.evaluate):
                res = eval_obj.evaluate()
                return extract_score(res)
            return extract_score(eval_obj)
        except TypeError:
            pass

        # Tentativo B: Istanziazione vuota -> evaluator = CoherenceEvaluator() poi evaluate(tokens)
        eval_obj = coherence_evaluator.CoherenceEvaluator()
        if hasattr(eval_obj, "evaluate") and callable(eval_obj.evaluate):
            res = eval_obj.evaluate(tokens)
            return extract_score(res)
        if hasattr(eval_obj, "calculate_coherence") and callable(eval_obj.calculate_coherence):
            res = eval_obj.calculate_coherence(tokens)
            return extract_score(res)

    # 3. Fallback generale
    funcs = [getattr(coherence_evaluator, f) for f in dir(coherence_evaluator) if callable(getattr(coherence_evaluator, f)) and not f.startswith("__")]
    if funcs:
        res = funcs[0](tokens)
        return extract_score(res)

    raise AttributeError("Impossibile calcolare C*: nessuna firma compatibile trovata in coherence_evaluator.py")

def run_null_model_benchmark(eva_filepath: str = "voynich_eva.txt", num_permutations: int = 100):
    print("=== METODO DEMARIA: TRUE MONTE CARLO NULL MODEL BENCHMARK ===")
    
    # 1. Parsing dei token EVA reali
    try:
        print(f"[+] Caricamento del corpus da: {eva_filepath}...")
        raw_tokens = get_tokens_from_parser(eva_filepath)
        print(f"[+] Token totali estratti con successo: {len(raw_tokens)}")
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

    # 4. Statistica Finale
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
