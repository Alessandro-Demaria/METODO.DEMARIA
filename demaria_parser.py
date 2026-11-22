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

class DemariaVectorParser:
    def __init__(self):
        self.M4 = np.array([
            [0, 1, 1, 0],
            [0, 1, 1, 1],
            [0, 1, 1, 1],
            [1, 1, 1, 1]
        ], dtype=np.uint8)
        self.M4_T = self.M4.T.copy()
        self.LUT4 = self.M4.ravel()
        self.LUT4_T = self.M4_T.ravel()
        self.M6 = np.array([
            [0, 1, 1, 1, 1, 0],
            [0, 0, 1, 1, 1, 1],
            [0, 0, 1, 1, 1, 1],
            [0, 0, 1, 1, 1, 1],
            [0, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1]
        ], dtype=np.uint8)
        self.LUT6 = self.M6.ravel()

    def transduce_universal_agnostic(self, toks, lids):
        n = len(toks)
        if n == 0:
            return np.zeros(0, dtype=np.uint8)
        cl = [str(t).strip().lower() for t in toks]
        out = np.full(n, 2, dtype=np.uint8)
        pc, sc, wc = {}, {}, {}
        ln = np.empty(n, dtype=np.int32)
        for i, w in enumerate(cl):
            ln[i] = len(w)
            wc[w] = wc.get(w, 0) + 1
            if len(w) >= 3:
                pc[w[:2]] = pc.get(w[:2], 0) + 1
                sc[w[-2:]] = sc.get(w[-2:], 0) + 1
        tp = {k for k, _ in sorted(pc.items(), key=lambda x: -x[1])[:4]}
        ts = {k for k, _ in sorted(sc.items(), key=lambda x: -x[1])[:4]}
        q75 = float(np.percentile(ln, 75))
        for i, w in enumerate(cl):
            if not w or w in ("nan", "none", "0", "cover", "s0"):
                out[i] = 0
            elif len(w) >= 3 and w[-2:] in ts:
                out[i] = 4
            elif len(w) >= 3 and w[:2] in tp:
                out[i] = 1
            elif ln[i] >= q75 and wc[w] <= 3:
                out[i] = 3
        return out

    def transduce_positional_rel35(self, seq, lids):
        s, g = np.asarray(seq, dtype=np.uint8), np.asarray(lids)
        n = s.size
        st6 = np.zeros(n, dtype=np.uint8)
        if n == 0:
            return st6
        ist = np.empty(n, dtype=bool)
        ien = np.empty(n, dtype=bool)
        ist[0] = True
        ien[-1] = True
        ist[1:] = g[1:] != g[:-1]
        ien[:-1] = ist[1:]
        st6[(s == 1) & ist] = 1
        st6[(s == 1) & (~ist)] = 2
        st6[s == 2] = 3
        st6[s == 3] = 4
        st6[(s == 4) & (~ien)] = 5
        st6[(s == 4) & ien] = 6
        return st6

    def _eval(self, s, g, lut, k, lo=True):
        m = ((g[:-1] == g[1:]) & (s[:-1] >= 1) & (s[1:] >= 1)) if lo else ((s[:-1] >= 1) & (s[1:] >= 1))
        idx = np.where(m)[0]
        tot = int(idx.size)
        if tot == 0:
            return 0.0, 0, 0
        v = int(np.sum(lut[(s[idx].astype(np.int32) - 1) * k + (s[idx + 1].astype(np.int32) - 1)]))
        return v / float(tot), v, tot

    def calculate_line_coherence(self, seq, lids):
        return self._eval(np.asarray(seq, dtype=np.uint8), np.asarray(lids), self.LUT4, 4, True)

    def calculate_rel35_coherence(self, st6, lids):
        return self._eval(np.asarray(st6, dtype=np.uint8), np.asarray(lids), self.LUT6, 6, True)

    def calculate_shannon_entropy(self, seq):
        s = np.asarray(seq, dtype=np.uint8)
        s = s[s >= 1]
        if s.size == 0:
            return 0.0
        _, c = np.unique(s, return_counts=True)
        p = c.astype(np.float64) / float(s.size)
        return float(-np.sum(p * np.log2(p)))

    def calculate_character_entropies(self, toks):
        stream = " ".join(str(t).strip().lower() for t in toks)
        if len(stream) < 2:
            return 0.0, 0.0
        arr = np.frombuffer(stream.encode("utf-8"), dtype=np.uint8)
        _, c1 = np.unique(arr, return_counts=True)
        p1 = c1.astype(np.float64) / float(arr.size)
        h1 = float(-np.sum(p1 * np.log2(p1)))
        pairs = (arr[:-1].astype(np.uint16) << 8) | arr[1:].astype(np.uint16)
        _, c2 = np.unique(pairs, return_counts=True)
        p2 = c2.astype(np.float64) / float(pairs.size)
        h2 = float(-np.sum(p2 * np.log2(p2)))
        return h1, max(0.0, h2 - h1)

    def extract_line_transition_matrix(self, seq, lids):
        s, g = np.asarray(seq, dtype=np.uint8), np.asarray(lids)
        idx = np.where((g[:-1] == g[1:]) & (s[:-1] >= 1) & (s[1:] >= 1))[0]
        mat = np.zeros((4, 4), dtype=np.int64)
        if idx.size > 0:
            np.add.at(mat, (s[idx] - 1, s[idx + 1] - 1), 1)
        return mat

    def calculate_information_metrics(self, mat):
        tot = float(np.sum(mat))
        if tot <= 0.0:
            return 0.0, 0.0, 0.0
        pxy = mat.astype(np.float64) / tot
        px = np.sum(pxy, axis=1, keepdims=True)
        py = np.sum(pxy, axis=0, keepdims=True)
        hx = float(-np.sum(px[px > 0] * np.log2(px[px > 0])))
        hy = float(-np.sum(py[py > 0] * np.log2(py[py > 0])))
        m = pxy > 0
        mi = float(np.sum(pxy[m] * np.log2(pxy[m] / (px @ py)[m])))
        return mi, max(0.0, hy - mi), (mi / hx if hx > 0.0 else 0.0)

    def calculate_cycle_dkl(self, seq, window=5000):
        s = np.asarray(seq, dtype=np.uint8)
        s = s[s >= 1]
        if s.size < 20:
            return 0.0
        w = min(window, s.size // 2)
        b, sh = s[:w], s[-w:]
        p1 = np.array([np.sum(b == k) for k in range(1, 5)], dtype=np.float64) + 1e-12
        p2 = np.array([np.sum(sh == k) for k in range(1, 5)], dtype=np.float64) + 1e-12
        p1 /= np.sum(p1)
        p2 /= np.sum(p2)
        return float(np.sum(p1 * np.log2(p1 / p2)))

    def calculate_intrinsic_boundary_selectivity(self, seq, lids):
        s, g = np.asarray(seq, dtype=np.uint8), np.asarray(lids)
        n = s.size
        if n == 0:
            return 0.0, 0.0, 0.0
        ist = np.empty(n, dtype=bool)
        ien = np.empty(n, dtype=bool)
        ist[0] = True
        ien[-1] = True
        ist[1:] = g[1:] != g[:-1]
        ien[:-1] = ist[1:]
        st, en = s[ist & (s >= 1)], s[ien & (s >= 1)]
        pa = float(np.mean(st == 1)) if st.size > 0 else 0.0
        pg = float(np.mean(en == 4)) if en.size > 0 else 0.0
        _, _, nmi = self.calculate_information_metrics(self.extract_line_transition_matrix(s, g))
        return float(0.5 * (pa + pg) * (1.0 + nmi)), pa, pg

    def compute_adjacent_levenshtein_le1(self, toks, lids):
        cl = [str(t).strip().lower() for t in toks]
        g = np.asarray(lids)
        idx = np.where(g[:-1] == g[1:])[0]
        cnt = 0
        for i in idx:
            a, b = cl[i], cl[i + 1]
            la, lb = len(a), len(b)
            if abs(la - lb) > 1:
                continue
            if a == b:
                cnt += 1
            elif la == lb:
                if sum(1 for x, y in zip(a, b) if x != y) == 1:
                    cnt += 1
            else:
                if la > lb:
                    a, b = b, a
                    la, lb = lb, la
                ia = ib = d = 0
                ok = True
                while ia < la and ib < lb:
                    if a[ia] != b[ib]:
                        d += 1
                        if d > 1:
                            ok = False
                            break
                        ib += 1
                    else:
                        ia += 1
                        ib += 1
                if ok:
                    cnt += 1
        tot = int(idx.size)
        return cnt, tot, (cnt / float(tot) if tot > 0 else 0.0)

    def compute_sections_chi2_pure(self, toks, fids):
        cl = [str(t).strip().lower() for t in toks]
        fn = np.array([int("".join(c for c in str(f) if c.isdigit()) or 0) for f in fids])
        sec = np.where((fn >= 1) & (fn <= 66), 0,
              np.where((fn >= 67) & (fn <= 73), 1,
              np.where((fn >= 75) & (fn <= 84), 2,
              np.where((fn >= 88) & (fn <= 102), 3,
              np.where((fn >= 103) & (fn <= 116), 4, -1)))))
        pref2 = np.array([w[:2] if len(w) >= 2 else w for w in cl])
        vals, counts = np.unique(pref2, return_counts=True)
        top8 = vals[np.argsort(-counts)[:8]]
        mat = np.zeros((5, len(top8)), dtype=np.int64)
        for r in range(5):
            for j, pr in enumerate(top8):
                mat[r, j] = int(np.sum((sec == r) & (pref2 == pr)))
        tot = float(np.sum(mat))
        if tot <= 0.0:
            return 0.0, 0
        exp = (np.sum(mat, axis=1, keepdims=True) @ np.sum(mat, axis=0, keepdims=True)) / tot
        m = exp > 0
        chi2 = float(np.sum(((mat[m] - exp[m]) ** 2) / exp[m]))
        df_chi = (mat.shape[0] - 1) * (mat.shape[1] - 1)
        return chi2, df_chi

    def extract_demaria_core_evo_vector_6d(self, toks, lids, seq=None, st6=None):
        if seq is None:
            seq = self.transduce_universal_agnostic(toks, lids)
        if st6 is None:
            st6 = self.transduce_positional_rel35(seq, lids)
        q1, _, _ = self.calculate_line_coherence(seq, lids)
        q2, _, _ = self.calculate_rel35_coherence(st6, lids)
        q3, _, _ = self.calculate_intrinsic_boundary_selectivity(seq, lids)
        _, h_cond = self.calculate_character_entropies(toks)
        q4 = float(np.clip(1.0 - (h_cond / np.log2(26.0)), 0.0, 1.0))
        _, _, nmi = self.calculate_information_metrics(self.extract_line_transition_matrix(seq, lids))
        q5 = float(np.clip(nmi, 0.0, 1.0))
        _, _, adj_pct = self.compute_adjacent_levenshtein_le1(toks, lids)
        q6 = float(np.clip(1.0 - adj_pct, 0.0, 1.0))
        return np.array([q1, q2, q3, q4, q5, q6], dtype=np.float32)