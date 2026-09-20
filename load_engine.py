import numpy as np

class LoadEngine:
    def __init__(self, master_clock_freq=0.0416):
        self.omega_0 = master_clock_freq
        self.T_0 = 1.0 / self.omega_0  # ~24 secondi

    def compute_line_load(self, tokens):
        """
        Calcola il profilo di carico Z(t) per un singolo rigo-loop.
        Mappa la sintassi topologica: Inizio (Innesco) -> Sviluppo (Regime) -> Chiusura (Reset).
        """
        if not tokens:
            return {'Z_mean': 0.0, 'Z_max': 0.0, 'dwell_time': 0.0}

        # Fattori di carico associati ai prefissi e grafemi gancio (Gallows)
        load_factors = []
        for i, token in enumerate(tokens):
            # Posizione nel rigo: Inizio, Sviluppo, Chiusura
            pos_ratio = i / max(1, len(tokens) - 1)
            
            base_weight = len(token) * 1.2
            if token.startswith(('qo', 'qok', 'ok')):
                base_weight *= 1.8  # Operatori di riscaldamento/carica
            elif token.endswith(('in', 'or', 'edy')):
                base_weight *= 0.5  # Operatori di scarico/reset

            # Profilo dinamico Z(t) = Pressione / Carico idraulico-meccanico
            z_t = base_weight * (1.0 + 0.5 * np.sin(2 * np.pi * self.omega_0 * i + pos_ratio))
            load_factors.append(z_t)

        z_array = np.array(load_factors)
        z_mean = float(np.mean(z_array))
        z_max = float(np.max(z_array))
        
        # Dwell time Thold calcolato in funzione del carico di picco
        thold = float(self.T_0 * (z_max / (z_mean + 1e-5)) * 0.1)

        return {
            'Z_mean': round(z_mean, 2),
            'Z_max': round(z_max, 2),
            'dwell_time': round(thold, 2)
        }

if __name__ == "__main__":
    engine = LoadEngine()
    print("load_engine.py pronto.")