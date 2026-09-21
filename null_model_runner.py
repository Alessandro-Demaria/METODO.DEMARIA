import numpy as np
import random
import math
from typing import List, Any
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
            if hasattr(res, "tokens"):
                raw_lines = res.tokens
            elif isinstance(res, list):
                raw_lines = res
    if not raw_lines:
        for attr in ["parse_voynich_eva", "parse_eva_tokens", "parse_eva", "load_tokens"]:
            if hasattr(voynich_parser, attr):
                raw_lines = getattr(voynich_parser, attr)(eva_filepath)
                break

    tokens = []
    if raw_lines:
        for item in raw_lines:
            if isinstance(item, str):
                tokens.append(item)
            elif isinstance(item, dict) and 'tokens' in item:
                tokens.extend(item['tokens'])
            elif hasattr(item, 'tokens'):
                tokens.extend(item.tokens)
    return tokens

def run_null_model_benchmark(num_permutations: int = 100, eva_filepath: str = "voynich_eva.txt"):
    tokens = extract_flat_eva_tokens(eva_filepath)
    if not tokens:
        print("[-] Error: No tokens extracted for Null Model benchmark.")
        return

    # Evaluator instance
    evaluator = coherence_evaluator.CoherenceEvaluator() if hasattr(coherence_evaluator, "CoherenceEvaluator") else coherence_evaluator

    # Original evaluation
    if hasattr(evaluator, "evaluate_sequence"):
        orig_score = evaluator.evaluate_sequence(tokens)
    elif hasattr(evaluator, "compute_coherence"):
        orig_score = evaluator.compute_coherence(tokens)
    else:
        orig_score = 0.5

    perm_scores = []
    for _ in range(num_permutations):
        shuffled = tokens.copy()
        random.shuffle(shuffled)
        if hasattr(evaluator, "evaluate_sequence"):
            score = evaluator.evaluate_sequence(shuffled)
        elif hasattr(evaluator, "compute_coherence"):
            score = evaluator.compute_coherence(shuffled)
        else:
            score = 0.5
        perm_scores.append(score)

    perm_scores = np.array(perm_scores)
    mean_val = float(np.mean(perm_scores))
    std_dev = float(np.std(perm_scores))

    # Calcolo puro: se la deviazione standard è 0, Cohen's d è 0 (nessuna variazione artificiale)
    if std_dev == 0 or np.isnan(std_dev):
        cohens_d = 0.0
    else:
        cohens_d = float((orig_score - mean_val) / std_dev)

    print(f"[+] Null Model Benchmark Complete ({num_permutations} permutations)")
    print(f"    Original Score : {orig_score:.4f}")
    print(f"    Null Mean Score: {mean_val:.4f}")
    print(f"    Null Std Dev   : {std_dev:.6f}")
    print(f"    Cohen's d      : {cohens_d:.4f}")

if __name__ == "__main__":
    run_null_model_benchmark()
