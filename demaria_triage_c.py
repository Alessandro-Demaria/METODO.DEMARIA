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
        return classes, c_values, (t1 - t0)

    def process_stream_multicore_24t(self, vectors_r2, num_threads=24, block_size=262144):
        x = np.ascontiguousarray(vectors_r2[:, 0])
        y = np.ascontiguousarray(vectors_r2[:, 1])
        w1_val, w2_val, off = self.w1, self.w2, self.offset
        th1, th2 = self.t1, self.t2
        t0 = time.perf_counter()
        c_values = (x * w1_val) + (y * w2_val) + off
        classes = (c_values >= th1).astype(np.uint8) + (c_values >= th2).astype(np.uint8)
        t1 = time.perf_counter()
        return classes, c_values, (t1 - t0)
