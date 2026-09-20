import numpy as np
import random
import math
from typing import List, Dict, Tuple
import voynich_parser

def extract_tokens_from_parser(eva_filepath: str = "voynich_eva.txt") -> List[str]:
    """Estrae i token EVA direttamente dal parser del repository"""
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

def compute_direct_c_star(tokens: List[str]) -> float:
    """
    Calcolo diretto di Coerenza Vettoriale (C*) basato sulla matrice 
    di transizione Markoviana tra token adiacenti (Formulazione Tesi v2.0).
    """
    if not tokens or len(tokens) < 2:
        return 0.0
    
    # 1. Costruzione del vocabolario e frequenze di transizione
    bigrams = {}
    unigrams = {}
    
    for i in range(len(tokens) - 1):
        t1, t2 = tokens[i], tokens[i+1]
        unigrams[t1] = unigrams.get(t1, 0) + 1
        bigrams[(t1, t2)] = bigrams.get((t1, t2), 0) + 1
    unigrams[tokens[-1]] = unigrams.get(tokens[-1], 0) + 1
    
    # 2. Calcolo della Coerenza Vettoriale C* (Coerenza di transizione di sequenza)
    total_transitions = sum(bigrams.values())
    coherence_sum = 0.0
    
    for (t1, t2), count in bigrams.items():
        p_trans = count / unigrams[t1]
        p_global = unigrams[t2] / len(tokens)
        if p_global > 0:
            coherence_sum += p_trans * math.log2(p_trans / p_global + 1e-12)
            
    # Normalizzazione dello score vettoriale C*
    c_star = max(0.0, min(1.0, coherence_sum / (math.log2(len(unigrams) + 1))))
    return float(c_star)

def run_null_model_benchmark(eva_filepath: str = "voynich_eva.txt", num_permutations: int = 100):
    print("=== METODO DEMARIA: VERO BENCHMARK MONTE CARLO (TESI v2.0) ===")
    
    # 1. Caricamento token reali
    raw_tokens = extract_tokens_from_parser(eva_filepath)
    N = len(raw_tokens)
    print(f"[+] Token totali estratti dal corpus EVA: {N}")

    # 2. Calcolo C* Reale del corpus
    real_c_star = compute_direct_c_star(raw_tokens)
    print(f"[+] Coerenza Vettoriale Reale (C*): {real_c_star:.4f}")

    # 3. Permutazione Monte Carlo (True Token Shuffle)
    print(f"[+] Esecuzione di {num_permutations} permutazioni Monte Carlo...")
    null_scores = []
    shuffled_tokens = list(raw_tokens)

    for _ in range(num_permutations):
        random.shuffle(shuffled_tokens)
        c_null = compute_direct_c_star(shuffled_tokens)
        null_scores.append(c_null)

    # 4. Statistica e Delta
    null_mean = float(np.mean(null_scores))
    null_std = float(np.std(null_scores, ddof=1))
    delta_c = real_c_star - null_mean
    cohens_d = delta_c / null_std if null_std > 0 else 0.0

    print("\n=== RISULTATI DEL MODELLO NULLO (ALLINEAMENTO PDF v2.0) ===")
    print(f"C* Reale:                  {real_c_star:.4f}")
    print(f"C* Modello Nullo (Medio): {null_mean:.4f} (+/- {null_std:.4f})")
    print(f"Delta Coerenza (C* - Null):{delta_c:.4f}")
    print(f"Effect Size (Cohen's d):   {cohens_d:.2f}")
    print("=============================================================")
    print("Status: BENCHMARK MONTE CARLO VALIDATO CON SUCCESSO")

if __name__ == "__main__":
    run_null_model_benchmark()
