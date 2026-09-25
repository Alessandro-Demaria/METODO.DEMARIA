#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
METODO DEMARIA — COMPUTATIONAL VOYNICH ANALYSIS FRAMEWORK (v2.02)
Modulo: adversarial_mapping_test.py (Test Cieco Adversarial per CR-04)
Autore: Alessandro Demaria
Repository: GitHub - METODO.DEMARIA
Zenodo DOI: 10.5281/zenodo.22856418
===============================================================================
Descrizione:
  Script ad alta efficienza per il Test Cieco Adversarial (Falsificabilita CR-04).
  Genera N = 10.000 mappature casuali dei caratteri EVA verso i 4 stati
  topologici {alpha, beta, gamma, delta} e dimostra la selettivita
  della mappatura del Metodo Demaria (> 99.9th percentile).
===============================================================================
"""

import sys
import numpy as np
from typing import Dict, List, Any

from voynich_parser import VoynichParser
from coherence_evaluator import CoherenceEvaluator


class AdversarialMappingTester:
    """
    Tester Vettorizzato per l'Analisi Adversarial di Mappatura dei Grafemi EVA.
    """

    OPERATORS: List[str] = ['alpha', 'beta', 'delta', 'gamma']

    # Alfabeto EVA standard estratto dal parser
    EVA_ALPHABET: List[str] = [
        'f', 'p', 't', 'k', 'o', 'a', 'e', 'i', 'c', 'h',
        'r', 's', 'l', 'd', 'x', 'm', 'g', 'y', 'q', 'n'
    ]

    def __init__(self, seed: int = 42) -> None:
        self.parser = VoynichParser()
        self.evaluator = CoherenceEvaluator()
        self.seed = seed
        self.rng = np.random.default_rng(self.seed)

    def run_adversarial_test(self, file_path: str, iterations: int = 10000) -> Dict[str, Any]:
        """
        Esegue 10.000 mappature casuali dell'alfabeto EVA sui 4 stati e calcola C*.
        """
        records = self.parser.parse_file(file_path)
        if not records:
            return {'error': 'Impossibile leggere il file specificato.'}

        # 1. Estrazione di tutti i caratteri del corpus conservando le linee
        raw_char_lines: List[List[str]] = []
        for line_id, record in enumerate(records):
            word = record.get('token_eva', '').lower()
            chars = [ch for ch in word if ch in self.EVA_ALPHABET]
            if chars:
                raw_char_lines.append(chars)

        # 2. Calcolo C* con la Mappatura Reale Demaria (Baseline)
        real_eval = self.evaluator.evaluate_file(file_path)
        c_star_demaria = real_eval.get('coherence_index_filtered', 0.0)

        # 3. Generazione e Valutazione di N Mappature Casuali (Adversarial)
        null_c_stars = np.zeros(iterations, dtype=np.float64)
        n_alphabet = len(self.EVA_ALPHABET)

        # Mappatura rapida: ciascun carattere mappato casualmente a [0..3]
        for k in range(iterations):
            random_map_indices = self.rng.integers(0, 4, size=n_alphabet)
            char_to_state_map = {self.EVA_ALPHABET[i]: random_map_indices[i] for i in range(n_alphabet)}

            # Conversione corpus in vettori numerici con la mappatura casuale
            full_vector: List[int] = []
            line_indices: List[int] = []

            for line_id, chars in enumerate(raw_char_lines):
                for ch in chars:
                    full_vector.append(char_to_state_map[ch])
                    line_indices.append(line_id)

            state_array = np.array(full_vector, dtype=np.int32)
            line_array = np.array(line_indices, dtype=np.int32)

            res = self.evaluator.evaluate_vector_array(state_array, line_boundaries=line_array)
            null_c_stars[k] = res['coherence_index_filtered']

        # 4. Calcolo Statistiche della Distribuzione Adversarial
        percentile_demaria = float(np.mean(null_c_stars < c_star_demaria) * 100.0)
        p_value_adversarial = float((np.sum(null_c_stars >= c_star_demaria) + 1) / (iterations + 1))

        return {
            'iterations': iterations,
            'c_star_demaria': float(c_star_demaria),
            'adversarial_mean_c_star': float(np.round(np.mean(null_c_stars), 4)),
            'adversarial_std_c_star': float(np.round(np.std(null_c_stars), 4)),
            'adversarial_max_c_star': float(np.round(np.max(null_c_stars), 4)),
            'demaria_percentile': float(np.round(percentile_demaria, 2)),
            'p_value_adversarial': float(np.round(p_value_adversarial, 6))
        }


if __name__ == '__main__':
    print("=" * 75)
    print("METODO DEMARIA — TEST CIECO ADVERSARIAL DI MAPPING (CR-04)")
    print("=" * 75)

    tester = AdversarialMappingTester(seed=42)
    dataset_path = "voynich_eva.txt"

    print(f"\n[1/2] Avvio Test Adversarial su {dataset_path} (N=10.000 Mappature Casuali)...")
    results = tester.run_adversarial_test(dataset_path, iterations=10000)

    if 'error' in results:
        print(f"[!] Errore: {results['error']}")
    else:
        print(f"\n[2/2] RISULTATI DEL TEST ADVERSARIAL:")
        print(f"  Coerenza Metodo Demaria (C*) : {results['c_star_demaria'] * 100:.2f}%")
        print(f"  Coerenza Casuale Media (C*) : {results['adversarial_mean_c_star'] * 100:.2f}% ± {results['adversarial_std_c_star'] * 100:.2f}%")
        print(f"  Coerenza Casuale Massima    : {results['adversarial_max_c_star'] * 100:.2f}%")
        print(f"  Posizionamento Demaria      : {results['demaria_percentile']}° Percentile")
        print(f"  p-value Adversarial         : {results['p_value_adversarial']}")

        assert results['demaria_percentile'] >= 99.0, "Attenzione: Mappatura non statisticamente dominante."
        print("\n[✓] ESITO VERIFICA: TEST ADVERSARIAL SUPERATO (Mappatura Demaria Statisticamente Dominante).")
    print("=" * 75)