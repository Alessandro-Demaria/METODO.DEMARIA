import numpy as np

class LoadEngine:
    def __init__(self, master_clock_freq=0.0416):
        self.omega_0 = master_clock_freq
        self.T_0 = 1.0 / self.omega_0  # ~24 secondi

    def compute_line_load(self, tokens):
        """
        Calcola il profilo di carico Z(t) per un singolo rigo-loop.
        Restituisce le metriche cibernetiche con le chiavi esatte richieste dal runner.
        """
        if not tokens:
            return {
                'Z_mean': 0.0,
                'Z_max': 0.0,
                'Thold_sec': round(self.T_0, 4),
                'Clock_Hz': round(self.omega_0, 4)
            }

        load_factors = []
        for i, token in enumerate(tokens):
            pos_ratio = i / max(1, len(tokens) - 1)

            base_weight = len(token) * 1.2
            if token.startswith(('qo', 'qok', 'ok')):
                base_weight *= 1.8
            elif token.endswith(('in', 'or', 'edy')):
                base_weight *= 0.5

            z_t = base_weight * (1.0 + 0.5 * np.sin(2 * np.pi * self.omega_0 * i + pos_ratio))
            load_factors.append(z_t)

        z_array = np.array(load_factors)
        z_mean = float(np.mean(z_array))
        z_max = float(np.max(z_array))

        # Calcolo del tempo di dwell proporzionale al carico di picco
        thold = float(self.T_0 * (z_max / (z_mean + 1e-5)) * 0.1)

        return {
            'Z_mean': round(z_mean, 4),
            'Z_max': round(z_max, 4),
            'Thold_sec': round(thold, 4),
            'Clock_Hz': round(self.omega_0, 4)
        }