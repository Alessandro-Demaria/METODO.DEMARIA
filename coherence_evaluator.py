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
        has_reset = any(t.endswith(('am', 'or', 'm', 'dy', 'old', 'ol', 'or', 'al')) for t in tokens)
        
        topology_score = 0.0
        if has_header and has_reset:
            topology_score = 1.0
        elif has_header or has_reset:
            topology_score = 0.5

        # 3. Calcolo dell'Indice Composito C* (Coerenza Cibernetica della Rete)
        c_star = 0.6 * stability_ratio + 0.4 * topology_score
        return round(float(c_star), 4)

    def get_status(self, c_star):
        """
        Restituisce l'etichetta accademica neutrale per la soglia di coerenza di picco.
        """
        if c_star >= self.min_threshold:
            return "PEAK_COHERENCE"
        return "BELOW_PEAK_THRESHOLD"
