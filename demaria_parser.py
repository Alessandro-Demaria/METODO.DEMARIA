import math 
import numpy as np 
import pandas as pd 
 
class DemariaVectorParser: 
    def __init__(self): 
        self.M_admissibility = np.array([[0, 1, 1, 0], [0, 1, 1, 1], [0, 1, 1, 1], [1, 1, 1, 1]], dtype=np.int32) 
        self.alpha_headers = ('qo', 'chol', 'chor', 'shol', 'shor', 'y', 'fachys', 'ykal', 'ar', 'faiin', 'qokaiin') 
        self.delta_infixes = ('ch', 'sh', 'ok', 'ot', 'ct', 'ckhy', 'shckhy', 'okchy', 'otchy', 'cthy') 
        self.gamma_terminals = ('am', 'an', 'dy', 'edy', 'ol', 'or', 'soor', 'su', 'chedy', 'shedy')
 
    def transduce_token(self, token): 
        c = str(token).strip().lower() 
        if not c or c in ('nan', 'none', '0'): return 0 
        for h in self.alpha_headers: 
            if c.startswith(h): return 1 
        for t in self.gamma_terminals: 
            if c.endswith(t): return 4 
        for i in self.delta_infixes: 
            if i in c: return 3 
        return 2 
 
    def transduce_sequence(self, token_list): 
        return [self.transduce_token(tok) for tok in token_list] 
 
    def calculate_coherence(self, state_sequence): 
        if len(state_sequence) < 2: return 0.0, 0, 0 
        v = 0 
        t = len(state_sequence) - 1 
        for i in range(t): 
            s1, s2 = state_sequence[i], state_sequence[i + 1] 
            if s1 == 0 or s2 == 0 or self.M_admissibility[s1 - 1, s2 - 1] == 1: v += 1 
        return v / t, v, t 
 
    def calculate_shannon_entropy(self, state_sequence): 
        f = [s for s in state_sequence if s in (1, 2, 3, 4)] 
        if not f: return 0.0 
        probs = pd.Series(f).value_counts() / len(f) 
        return float(-sum(p * math.log2(p) for p in probs if p > 0))
 
    def calculate_character_entropy(self, token_list): 
        chars = [ch for tok in token_list if str(tok).strip().lower() not in ('nan', 'none', '0') for ch in str(tok).strip().lower()] 
        if not chars: return 0.0, 0 
        probs = pd.Series(chars).value_counts() / len(chars) 
        return float(-sum(p * math.log2(p) for p in probs if p > 0)), len(probs) 
 
    def extract_transition_matrix(self, state_sequence): 
        f = [s for s in state_sequence if s in (1, 2, 3, 4)] 
        m = np.zeros((4, 4), dtype=np.int64) 
        for i in range(len(f) - 1): m[f[i] - 1, f[i + 1] - 1] += 1 
        r = m.sum(axis=1, keepdims=True) 
        return m, m / np.where(r == 0, 1, r) 
 
    def calculate_mutual_information(self, state_sequence): 
        f = [s for s in state_sequence if s in (1, 2, 3, 4)] 
        if len(f) < 2: return 0.0 
        c, _ = self.extract_transition_matrix(f) 
        tot = float(c.sum()) 
        if tot == 0: return 0.0 
        pj = c / tot; ps = pj.sum(axis=1); pd = pj.sum(axis=0) 
        return float(sum(pj[i, j] * math.log2(pj[i, j] / (ps[i] * pd[j])) for i in range(4) for j in range(4) if pj[i, j] > 0 and ps[i] > 0 and pd[j] > 0))
