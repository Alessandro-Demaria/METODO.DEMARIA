import numpy as np

class DemariaMonteCarloEngine:
    def __init__(self, parser):
        self.parser = parser

    def run_null_model(self, state_sequence, iterations=10000, seed=42):
        rng = np.random.default_rng(seed)
        seq = np.array(state_sequence, dtype=np.int32)
        n_trans = len(seq) - 1
        if n_trans < 1:
            return 0.0, 0.0, 0.0, 1.0
        c_null_values = np.zeros(iterations, dtype=np.float64)
        for i in range(iterations):
            perm = rng.permutation(seq)
            c_val, _, _ = self.parser.calculate_coherence(perm)
            c_null_values[i] = c_val
        mean_null = float(np.mean(c_null_values))
        std_null = float(np.std(c_null_values))
        c_obs, _, _ = self.parser.calculate_coherence(state_sequence)
        z_score = (c_obs - mean_null) / std_null if std_null > 0 else 0.0
        p_val = float(np.sum(c_null_values >= c_obs) + 1) / (iterations + 1)
        return mean_null, std_null, z_score, p_val
