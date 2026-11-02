# ==============================================================================
# DEMARIA CORE EVO (DCE) - MODULO 4: SUITE DI VALIDAZIONE ED HOLDOUT
# File: demaria_validation.py
# Laboratorio Scientifico Metodo Demaria
# Autore, Responsabile Scientifico ed Inventore Unico: Avv. Alessandro Demaria
# Marchio Registrato UIBM N. 302026000161716 - Concept DOI Madre: 10.5281/zenodo.22789343
# Release DOI Ufficiale 3.4 Optimum: 10.5281/zenodo.23836177
# ==============================================================================

import numpy as np

class DemariaValidationSuite:
    def __init__(self, parser):
        self.parser = parser

    def holdout_split_validation(self, state_sequence, split_ratio=0.80):
        n = len(state_sequence)
        split_idx = int(n * split_ratio)
        train_seq = state_sequence[:split_idx]
        test_seq = state_sequence[split_idx:]
        c_train, _, _ = self.parser.calculate_coherence(train_seq)
        c_test, _, _ = self.parser.calculate_coherence(test_seq)
        relative_gap_pct = abs(c_train - c_test) / c_train * 100.0 if c_train > 0 else 0.0
        return c_train, c_test, relative_gap_pct

    def noise_stress_test(self, state_sequence, noise_fraction=0.10, seed=42):
        rng = np.random.default_rng(seed)
        noisy_seq = list(state_sequence)
        n = len(noisy_seq)
        n_corrupt = int(n * noise_fraction)
        indices = rng.choice(n, size=n_corrupt, replace=False)
        for idx in indices:
            noisy_seq[idx] = int(rng.choice([1, 2, 3, 4]))
        c_noisy, _, _ = self.parser.calculate_coherence(noisy_seq)
        c_orig, _, _ = self.parser.calculate_coherence(state_sequence)
        retention_net_pct = (c_noisy / c_orig) * 100.0 if c_orig > 0 else 0.0
        return c_noisy, retention_net_pct
