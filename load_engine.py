import numpy as np

class LoadEngine:
    def __init__(self, master_clock_freq=0.0416):
        self.omega_0 = master_clock_freq
        self.T_0 = 1.0 / self.omega_0  # ~24 secondi

    def compute_line_load(self, tokens):
        """
        Calcola il profilo di carico Z(t) per una sequenza di token.
        Mappa la sintassi topologica: Inizio (Innesco) -> Sviluppo (Regime) -> Chiusura (Reset).
        """
        if not tokens:
            return {'Z_mean': 0.0, 'Z_max': 0.0, 'dwell_time': 0.0}

        load_factors = []
        num_tokens = len(tokens)

        for i, token in enumerate(tokens):
            # Posizione relativa nella riga (da 0 a 1)
            pos_ratio = i / max(1, num_tokens - 1)
            
            # Peso base dato dalla lunghezza del token
            token_length = len(token)
            
            # Modulazione sinusoidale basata sulla frequenza di clock
            phase_factor = np.sin(np.pi * pos_ratio)
            
            z_val = token_length * (1.0 + 0.5 * phase_factor)
            load_factors.append(z_val)

        z_mean = float(np.mean(load_factors)) if load_factors else 0.0
        z_max = float(np.max(load_factors)) if load_factors else 0.0
        dwell_time = float(num_tokens * self.T_0)

        return {
            'Z_mean': z_mean,
            'Z_max': z_max,
            'dwell_time': dwell_time
        }
