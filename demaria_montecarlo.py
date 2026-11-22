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

class DemariaMonteCarloEngine:
    def __init__(self, p):
        self.parser = p

    def _blocks(self, g):
        ch = np.where(g[1:] != g[:-1])[0] + 1
        st = np.concatenate(([0], ch))
        en = np.concatenate((ch, [g.size]))
        bl = {}
        for s, l in zip(st, en - st):
            if l > 1:
                bl.setdefault(int(l), []).append(int(s))
        return [(l, np.array([np.arange(s, s + l) for s in sl], dtype=np.int32)) for l, sl in bl.items()]

    def compute_cohen_d_bernoulli(self, c_obs, mu0):
        denom = float(np.sqrt(max(1e-12, c_obs * (1.0 - c_obs))))
        return float((c_obs - mu0) / denom)

    def run_hierarchical_null_model(self, seq, gids, iterations=10000, seed=42, mat=None):
        rng = np.random.default_rng(seed)
        s = np.asarray(seq, dtype=np.uint8)
        g = np.asarray(gids)
        M = self.parser.M4 if mat is None else mat
        lut = np.asarray(M, dtype=np.uint8).ravel()
        k = M.shape[1]
        sm = (g[:-1] == g[1:]) & (s[:-1] >= 1) & (s[1:] >= 1)
        idx = np.where(sm)[0]
        tot = float(idx.size)
        if tot <= 0.0:
            return 0.0, 0.0, 0.0, 1.0
        c_obs = float(np.sum(lut[(s[idx].astype(np.int32) - 1) * k + (s[idx + 1].astype(np.int32) - 1)]) / tot)
        bl = self._blocks(g)
        nulls = np.empty(iterations, dtype=np.float64)
        bs = 500
        n = s.size
        for st in range(0, iterations, bs):
            b = min(bs, iterations - st)
            buf = np.broadcast_to(s, (b, n)).copy()
            for _, mi in bl:
                sub = buf[:, mi]
                rng.permuted(sub, axis=2, out=sub)
                buf[:, mi] = sub
            nulls[st:st + b] = np.sum(lut[(buf[:, idx].astype(np.int32) - 1) * k + (buf[:, idx + 1].astype(np.int32) - 1)], axis=1) / tot
        mu = float(np.mean(nulls))
        sd = float(np.std(nulls, ddof=1))
        z = float((c_obs - mu) / sd) if sd > 1e-12 else 0.0
        pval = float((np.sum(nulls >= c_obs) + 1) / (iterations + 1))
        return mu, sd, z, pval

    def run_positional_rel35_null_model(self, base_seq, gids, iterations=10000, seed=42):
        rng = np.random.default_rng(seed)
        s = np.asarray(base_seq, dtype=np.uint8)
        g = np.asarray(gids)
        n = s.size
        lut = self.parser.LUT6
        st6_obs = self.parser.transduce_positional_rel35(s, g)
        sm = (g[:-1] == g[1:]) & (st6_obs[:-1] >= 1) & (st6_obs[1:] >= 1)
        idx = np.where(sm)[0]
        tot = float(idx.size)
        if tot <= 0.0:
            return 0.0, 0.0, 0.0, 1.0
        c_obs = float(np.sum(lut[(st6_obs[idx].astype(np.int32) - 1) * 6 + (st6_obs[idx + 1].astype(np.int32) - 1)]) / tot)
        ist = np.empty(n, dtype=bool)
        ien = np.empty(n, dtype=bool)
        ist[0] = True
        ien[-1] = True
        ist[1:] = g[1:] != g[:-1]
        ien[:-1] = ist[1:]
        bl = self._blocks(g)
        nulls = np.empty(iterations, dtype=np.float64)
        bs = 500
        for st in range(0, iterations, bs):
            b = min(bs, iterations - st)
            buf = np.broadcast_to(s, (b, n)).copy()
            for _, mi in bl:
                sub = buf[:, mi]
                rng.permuted(sub, axis=2, out=sub)
                buf[:, mi] = sub
            st6 = np.zeros_like(buf)
            st6[:, ist] = np.where(buf[:, ist] == 1, 1, 0)
            st6[:, ~ist] = np.where(buf[:, ~ist] == 1, 2, 0)
            st6[buf == 2] = 3
            st6[buf == 3] = 4
            st6[(buf == 4) & (~ien[None, :])] = 5
            st6[(buf == 4) & (ien[None, :])] = 6
            nulls[st:st + b] = np.sum(lut[(st6[:, idx].astype(np.int32) - 1) * 6 + (st6[:, idx + 1].astype(np.int32) - 1)], axis=1) / tot
        mu = float(np.mean(nulls))
        sd = float(np.std(nulls, ddof=1))
        z = float((c_obs - mu) / sd) if sd > 1e-12 else 0.0
        pval = float((np.sum(nulls >= c_obs) + 1) / (iterations + 1))
        return mu, sd, z, pval
