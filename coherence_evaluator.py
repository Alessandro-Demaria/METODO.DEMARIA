import numpy as np

class CoherenceEvaluator:
    def __init__(self, min_threshold=0.94):
        self.min_threshold = min_threshold

    def evaluate(self, load_data, tokens):
        if not tokens:
            return 0.0

        # 1. Componente Vettoriale di Carico (Ratio Stabilità Dinamica)
        z_mean = load_data.get('Z_mean', 0.0)
        z_max = load_data.get('Z_max', 1e-5)
        
        if z_max == 0:
            stability_ratio = 0.0
        else:
            stability_ratio = min(1.0, z_mean / z_max)

        # 2. Verifica della Tripartizione Topologica (Header / Innesco e Reset / Chiusura)
        has_header = any(t.startswith(('fachys', 'qok', 'otol', 'saiin', 'pacho', 'ykal', 'ar', 'qof', 'okaiin', 'shol', 'shedy', 'daiin')) for t in tokens)
        has_reset = any(t.endswith(('soor', 'iiin', 'edy', 'l', 'r', 's', 'm', 'n')) for t in tokens)

        # 3. Calcolo Vettoriale Puro C* (Ponderazione Topologica + Stabilità Carico)
        topology_weight = 0.5 * float(has_header) + 0.5 * float(has_reset)
        
        # Punteggio di Coerenza C* basato puramente sui dati
        coherence = 0.6 * stability_ratio + 0.4 * topology_weight

        return round(float(coherence), 4)

if __name__ == "__main__":
    evaluator = CoherenceEvaluator()