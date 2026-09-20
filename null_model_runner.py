import numpy as np
import random
import math
from typing import List, Any, Dict
import voynich_parser
import coherence_evaluator

def extract_clean_token_strings(eva_filepath: str = "voynich_eva.txt") -> List[str]:
    """Estrae esattamente il campo di testo EVA dai token del VoynichParser"""
    raw_tokens = []
    if hasattr(voynich_parser, "VoynichParser"):
        p = voynich_parser.VoynichParser()
        if hasattr(p, "parse"):
            try:
                res = p.parse()
            except TypeError:
                res = p.parse(eva_filepath)
            if hasattr(res, "tokens"): raw_tokens = res.tokens
            elif isinstance(res, list): raw_tokens = res

    if not raw_tokens:
        for attr in ["parse_voynich_eva", "parse_eva_tokens", "parse_eva", "load_tokens"]:
            if hasattr(voynich_parser, attr):
                res = getattr(voynich_parser, attr)(eva_filepath)
                if isinstance(res, list): raw_tokens = res; break
                if hasattr(res, "tokens"): raw_tokens = res.tokens; break

    if not raw_tokens:
        raise RuntimeError("Impossibile estrarre i token dal parser EVA.")

    # Diagnostica della struttura del primo token
    first_token = raw_tokens[0]
    print(f"[DEBUG] Tipo primo token: {type(first_token)}")
    if isinstance(first_token, dict):
        print(f"[DEBUG] Chiavi primo token: {list(first_token.keys())}")
        print(f"[DEBUG] Contenuto primo token: {first_token}")

    clean_strings = []
    for t in raw_tokens:
        if isinstance(t, str):
            clean_strings.append(t)
        elif isinstance(t, dict):
            # Cerca prioritariamente i campi specifici del formato EVA/Voynich
            token_str = None
            for key in ["eva", "text", "word", "token", "raw", "val", "transcription", "content"]:
                if key in t and isinstance(t[key], str) and t[key].strip():
                    token_str = t[key]
                    break
            if not token_str:
                # Se non trova le chiavi note, cerca qualsiasi stringa che non sia un metadato di folio/linea
                for k, v in t.items():
                    if isinstance(v, str) and not k.startswith("f") and not k in ["folio", "line", "section"]:
                        token_str = v
                        break
            clean_strings.append(token_str if token_str else str(t))
        elif hasattr(t, "eva"):
            clean_strings.append(str(t.eva))
        elif hasattr(t, "text"):
            clean_strings.append(str(t.text))
        else:
            clean_strings.append(str(t))

    return clean_strings

def run_null_model_benchmark(eva_filepath: str = "voynich_eva.txt", num_permutations: int = 100):
    print("=== METODO DEMARIA: VERO BENCHMARK MONTE CARLO (PRECISIONE ASSOLUTA) ===")

    # 1. Caricamento e pulizia stringhe token
    string_tokens = extract_clean_token_strings(eva_filepath)
    N = len(string_tokens)
    print(f"[+] Token totali estratti e convertiti in stringhe pure: {N}")
    print(f"[+] Esempio primi 5 token estratti: {string_tokens[:5]}")

    # Istanza dell'evaluator e dizionario vuoto per load_data
    evaluator = coherence_evaluator.CoherenceEvaluator()
    data_dict = {}

    # 2. Calcolo C* Reale del corpus originale
    real_c_star = float(evaluator.evaluate(data_dict, string_tokens))
    print(f"[+] Coerenza Vettoriale Reale (C*): {real_c_star:.4f}")

    # 3. Permutazione Monte Carlo Reale (True Token Shuffle)
    print(f"[+] Esecuzione di {num_permutations} permutazioni Monte Carlo...")
    null_scores = []
    working_tokens = list(string_tokens)

    for _ in range(num_permutations):
        random.shuffle(working_tokens)
        c_null = float(evaluator.evaluate(data_dict, working_tokens))
        null_scores.append(c_null)

    # 4. Analisi Statistica e Delta
    null_mean = float(np.mean(null_scores))
    null_std = float(np.std(null_scores, ddof=1))
    delta_c = real_c_star - null_mean
    cohens_d = delta_c / null_std if null_std > 0 else 0.0

    print("\n=== RISULTATI DEL MODELLO NULLO REALE ===")
    print(f"C* Reale:                  {real_c_star:.4f}")
    print(f"C* Modello Nullo (Medio): {null_mean:.4f} (+/- {null_std:.4f})")
    print(f"Delta Coerenza (C* - Null):{delta_c:.4f}")
    print(f"Effect Size (Cohen's d):   {cohens_d:.2f}")
    print("=============================================================")
    print("Status: BENCHMARK MONTE CARLO COMPLETATO CON SUCCESSO")

if __name__ == "__main__":
    run_null_model_benchmark()
