# -*- coding: utf-8 -*-
# ==============================================================================
# METODO DEMARIA RELEASE 3.5 (EDIZIONE SCIENTIFICA PURA O NON CIRCOLARE)
# Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
# Affiliazione: Laboratorio Scientifico Metodo Demaria
# Marchio Registrato: METODO DEMARIA (Marchio UIBM N. 302026000161716)
# Concept DOI Madre: 10.5281/zenodo.22789343
# DOI Specifico Release 3.5: 10.5281/zenodo.24444677
# Tutela Legale: Art. 98 CPI (D.Lgs. 30/2005), Legge 22 aprile 1941 n. 633, WIPO
# Dataset Master Autenticato: voynich_eva_tokens_extended.csv (35.483 Token EVA)
# SHA-256 Dataset: dec87e784290ad5b404bd5ed0110349a2f379c7fb386adb0bca2d7a4b1890999
# ==============================================================================
import numpy as np

class DemariaValidationSuite:
    def __init__(self, p):
        self.parser = p

    def holdout_split_validation(self, seq, lids, fids, ratio=0.80):
        uf = np.unique(fids)
        cut = int(uf.size * ratio)
        tr = np.isin(fids, uf[:cut])
        c_tr = self.parser.calculate_line_coherence(seq[tr], lids[tr])[0]
        c_te = self.parser.calculate_line_coherence(seq[~tr], lids[~tr])[0]
        gap_pct = abs(c_tr - c_te) / max(c_tr, 1e-12) * 100.0
        return c_tr, c_te, gap_pct

    def noise_stress_test(self, seq, lids, frac=0.10, seed=42):
        rng = np.random.default_rng(seed)
        s = np.asarray(seq, dtype=np.uint8).copy()
        m = rng.random(s.size) < frac
        s[m] = rng.integers(1, 5, size=int(np.sum(m)), dtype=np.uint8)
        c0 = self.parser.calculate_line_coherence(seq, lids)[0]
        cn = self.parser.calculate_line_coherence(s, lids)[0]
        return cn, (cn / max(c0, 1e-12)) * 100.0

    def isomorphic_double_randomization(self, seq, lids, iterations=2000, seed=42):
        rng = np.random.default_rng(seed)
        s = np.asarray(seq, dtype=np.uint8)
        g = np.asarray(lids)
        c_obs = self.parser.calculate_line_coherence(s, g)[0]
        m = (g[:-1] == g[1:]) & (s[:-1] >= 1) & (s[1:] >= 1)
        idx = np.where(m)[0]
        tot = float(idx.size)
        if tot <= 0.0:
            return 0.0, 0.0, 0.0, 1.0
        s1 = s[idx].astype(np.int32) - 1
        s2 = s[idx + 1].astype(np.int32) - 1
        nulls = np.empty(iterations, dtype=np.float64)
        for i in range(iterations):
            perm_states = rng.permutation(4)
            p_s1 = perm_states[s1]
            p_s2 = perm_states[s2]
            perm_lut = rng.permutation(self.parser.LUT4)
            nulls[i] = float(np.sum(perm_lut[p_s1 * 4 + p_s2])) / tot
        mu = float(np.mean(nulls))
        sd = float(np.std(nulls, ddof=1))
        z = float((c_obs - mu) / sd) if sd > 1e-12 else 0.0
        pval = float((np.sum(nulls >= c_obs) + 1) / (iterations + 1))
        return mu, sd, z, pval