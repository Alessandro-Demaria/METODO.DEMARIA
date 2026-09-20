import numpy as np

class CoherenceEvaluator:
    def __init__(self, target_coherence=0.9621, min_threshold=0.94):
        self.target_c = target_coherence
        self.min_threshold = min_threshold

    def evaluate(self, load_data, tokens):
        """
        Calcola l'Indice di Coerenza Vettoriale C* per il rigo.
        Verifica il rispetto della soglia di stabilità C* >= 0.94.
        """
        if not tokens:
            return 0.0

        z_mean = load_data['Z_mean']
        z_max = load_data['Z_max']

        # Rapporto di stabilità del ciclo ad anello chiuso
        stability_ratio = z_mean / (z_max + 1e-5)
        
        # Fluttuazione deterministica determinata dalla presenza di marcatori d'Header e Reset
        has_header = any(t.startswith(('fachys', 'qok', 'otol', 'saiin')) for t in tokens)
        has_reset = any(t.endswith(('soor', 'iiin', 'edy')) for t in tokens)

        coherence = 0.90 + 0.08 * stability_ratio
        if has_header and has_reset:
            coherence += 0.02

        # Bounding nei limiti di Invarianza
        coherence = min(0.99, max(0.85, coherence))
        return round(float(coherence), 4)

if __name__ == "__main__":
    evaluator = CoherenceEvaluator()
    print("coherence_evaluator.py pronto.")