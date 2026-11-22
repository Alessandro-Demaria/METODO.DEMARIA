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
import time, numpy as np

class DemariaInvariantCEngine:
    def __init__(self, w1=0.5824, w2=0.4176, t1=0.8500, t2=0.984414):
        self.w = np.array([w1, w2], dtype=np.float32)
        self.t1 = np.float32(t1)
        self.t2 = np.float32(t2)

    def analytical_tail_probability(self):
        num = float((1.0 - float(self.t2)) ** 2)
        den = float(2.0 * float(self.w[0]) * float(self.w[1]))
        return num / den

    def process_stream_vectorized(self, v):
        t0 = time.perf_counter()
        x = np.ascontiguousarray(v, dtype=np.float32)
        c = x @ self.w
        cl = (c >= self.t1).astype(np.uint8) + (c >= self.t2).astype(np.uint8)
        return cl, c, max(time.perf_counter() - t0, 1e-9)

    def verify_cover_ground_state(self):
        cl, c, _ = self.process_stream_vectorized(np.zeros((1, 2), dtype=np.float32))
        return int(cl[0]), float(c[0])
