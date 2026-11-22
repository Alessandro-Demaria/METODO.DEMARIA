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
from demaria_montecarlo import DemariaMonteCarloEngine

class DemariaCrossCorpusBenchmark:
    def __init__(self, p):
        self.parser = p
        self.mc = DemariaMonteCarloEngine(p)

    def _decide(self, z4, z6, sel_val):
        return "VALIDATO" if (z4 > 4.5 and z6 > 4.5 and sel_val > 0.30) else "RIGETTATO"

    def _eval_seq(self, seq_null, lids, iterations=2000, seed=42):
        st6 = self.parser.transduce_positional_rel35(seq_null, lids)
        c4 = self.parser.calculate_line_coherence(seq_null, lids)[0]
        c6 = self.parser.calculate_rel35_coherence(st6, lids)[0]
        z4 = self.mc.run_hierarchical_null_model(seq_null, lids, iterations=iterations, seed=seed, mat=self.parser.M4)[2]
        z6 = self.mc.run_positional_rel35_null_model(seq_null, lids, iterations=iterations, seed=seed)[2]
        sel = self.parser.calculate_intrinsic_boundary_selectivity(seq_null, lids)[0]
        return (round(c4, 6), round(z4, 4), round(c6, 6), round(z6, 4), round(sel, 4), self._decide(z4, z6, sel))

    def evaluate(self, seq_obs, lids, c4_v, z4_v, c6_v, z6_v, sel_v, iterations=2000, seed=42):
        rng = np.random.default_rng(seed)
        s = np.asarray(seq_obs, dtype=np.uint8)
        n = s.size
        sv = float(sel_v) if sel_v is not None else 0.0
        res = {
            "1. Manoscritto Voynich (Beinecke MS 408 Reale)": (
                round(float(c4_v), 6), round(float(z4_v), 4),
                round(float(c6_v), 6), round(float(z6_v), 4),
                round(sv, 4), self._decide(float(z4_v), float(z6_v), sv)
            )
        }

        # Controllo Nullo A: Flusso i.i.d. con la stessa distribuzione marginale p
        _, cnts = np.unique(s[s >= 1], return_counts=True)
        p_marg = cnts.astype(np.float64) / float(np.sum(cnts))
        seq_null_a = rng.choice(np.array([1, 2, 3, 4], dtype=np.uint8), size=n, p=p_marg)
        res["2. Controllo Nullo A (Flusso i.i.d. Stessa Marginale p)"] = self._eval_seq(seq_null_a, lids, iterations=iterations, seed=seed + 1)

        # Controllo Nullo B: Catena di Markov Stazionaria del 1 Ordine
        tmat = np.zeros((4, 4), dtype=np.float64)
        idx = np.where((lids[:-1] == lids[1:]) & (s[:-1] >= 1) & (s[1:] >= 1))[0]
        np.add.at(tmat, (s[idx] - 1, s[idx + 1] - 1), 1.0)
        row_sums = tmat.sum(axis=1, keepdims=True)
        trans_p = np.where(row_sums > 0, tmat / np.maximum(row_sums, 1e-12), 0.25)
        seq_null_b = np.empty(n, dtype=np.uint8)
        cur = int(rng.choice([1, 2, 3, 4], p=p_marg))
        for i in range(n):
            if i == 0 or lids[i] != lids[i - 1]:
                cur = int(rng.choice([1, 2, 3, 4], p=p_marg))
            else:
                cur = int(rng.choice([1, 2, 3, 4], p=trans_p[cur - 1]))
            seq_null_b[i] = cur
        res["3. Controllo Nullo B (Catena di Markov Stazionaria 1 Ordine)"] = self._eval_seq(seq_null_b, lids, iterations=iterations, seed=seed + 2)

        # Controllo Nullo C: Sequenza Uniforme Equidistribuita
        seq_null_c = rng.integers(1, 5, size=n, dtype=np.uint8)
        res["4. Controllo Nullo C (Sequenza Uniforme Equidistribuita)"] = self._eval_seq(seq_null_c, lids, iterations=iterations, seed=seed + 3)

        return res