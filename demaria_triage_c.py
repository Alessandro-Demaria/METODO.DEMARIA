# ==============================================================================
# DEMARIA CORE EVO (DCE) - MODULO 3: DEMARIA INVARIANT C ENGINE (DICE)
# File: demaria_triage_c.py
# Laboratorio Scientifico Metodo Demaria
# Autore, Responsabile Scientifico ed Inventore Unico: Avv. Alessandro Demaria
# Marchio Registrato UIBM N. 302026000161716 - Concept DOI Madre: 10.5281/zenodo.22789343
# Release DOI Ufficiale 3.4 Optimum: 10.5281/zenodo.23836177
# Tutela del Segreto Industriale: Articolo 98 CPI (Decreto Legislativo 30 del 2005)
# ==============================================================================

import time
import numpy as np

class DemariaInvariantCEngine:
    def __init__(self, w1=0.5824, w2=0.4176, offset=0.0, t1=0.33, t2=0.66):
        self.w1 = np.float32(w1)
        self.w2 = np.float32(w2)
        self.offset = np.float32(offset)
        self.t1 = np.float32(t1)
        self.t2 = np.float32(t2)

    def process_stream_simd(self, vectors_r2):
        t0 = time.perf_counter()
        c_values = (vectors_r2[:, 0] * self.w1) + (vectors_r2[:, 1] * self.w2) + self.offset
        classes = np.zeros(len(vectors_r2), dtype=np.uint8)
        classes[c_values >= self.t1] = 1
        classes[c_values >= self.t2] = 2
        t1 = time.perf_counter()
        elapsed = t1 - t0
        return classes, c_values, elapsed

    def process_stream_simd_rd(self, vectors_rd, weights_d):
        t0 = time.perf_counter()
        weights_array = np.array(weights_d, dtype=np.float32)
        c_values = np.dot(vectors_rd, weights_array) + self.offset
        classes = np.zeros(len(vectors_rd), dtype=np.uint8)
        classes[c_values >= self.t1] = 1
        classes[c_values >= self.t2] = 2
        t1 = time.perf_counter()
        elapsed = t1 - t0
        return classes, c_values, elapsed
