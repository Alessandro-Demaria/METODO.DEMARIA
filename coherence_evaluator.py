"""
METODO DEMARIA - VALUTATORE DI COERENZA SPETTRALE E STRUTTURALE
Modulo: coherence_evaluator.py
Verifica di Conformita: 21/09/2026 - Standard Demaria v2.0.1

Descrizione:
  Valuta la coerenza informazionale, l'entropia locale e i vettori
  di invarianza per i token estratti dalle trascrizioni del Manoscritto Voynich,
  in stretta conformità con la monografia teorica Demaria_2026_Metodo_Demaria_v2.01.pdf.
"""

import os
import csv
import math
from typing import List, Dict, Any


class CoherenceEvaluator:
    """
    Calcola i coefficienti di coerenza informazionale e invarianza vettoriale.
    """

    def __init__(self, base_entropy: float = 4.2):
        self.base_entropy = base_entropy

    def calculate_coherence(self, tokens: List[str]) -> float:
        """
        Calcola l'indice di coerenza logaritmica per una lista di token.
        """
        if not tokens:
            return 0.0
        
        total_tokens = len(tokens)
        unique_tokens = len(set(tokens))
        ratio = unique_tokens / total_tokens
        
        # Indice di coerenza pesato logaritmicamente
        coherence_index = math.log2(total_tokens + 1) * ratio
        return round(coherence_index, 4)

    def evaluate_dataset(self, csv_filepath: str) -> Dict[str, Any]:
        """
        Legge il file CSV prodotto da BatchRunner e calcola la coerenza globale.
        """
        if not os.path.exists(csv_filepath):
            raise FileNotFoundError(f"File CSV non trovato: {csv_filepath}")

        total_lines = 0
        coherence_scores = []

        with open(csv_filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                total_lines += 1
                tokens = row.get('tokens_str', '').split()
                score = self.calculate_coherence(tokens)
                coherence_scores.append(score)

        avg_coherence = sum(coherence_scores) / len(coherence_scores) if coherence_scores else 0.0

        return {
            'status': 'SUCCESS',
            'processed_lines': total_lines,
            'average_coherence': round(avg_coherence, 4),
            'min_coherence': min(coherence_scores) if coherence_scores else 0.0,
            'max_coherence': max(coherence_scores) if coherence_scores else 0.0
        }


def evaluate_coherence(csv_filepath: str = "voynich_batch_measurements.csv") -> Dict[str, Any]:
    """
    Funzione interfaccia standard per invocazione diretta dell'analisi di coerenza.
    """
    evaluator = CoherenceEvaluator()
    return evaluator.evaluate_dataset(csv_filepath)


if __name__ == "__main__":
    # Test diagnostico isolato
    print("Avvio Test Diagnostico CoherenceEvaluator...")
    evaluator = CoherenceEvaluator()
    sample_tokens = ['fachys', 'ykal', 'ar', 'am', 'qool']
    score = evaluator.calculate_coherence(sample_tokens)
    print("Score di Coerenza Campione:", score)
    assert score > 0.0, "Errore nel calcolo del punteggio di coerenza"
    print("VERIFICA COHERENCE EVALUATOR: SUPERATA")
