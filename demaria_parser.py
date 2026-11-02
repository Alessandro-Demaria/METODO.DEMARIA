# ==============================================================================
# DEMARIA CORE EVO (DCE) - MODULO 1: PARSER VETTORIALE E TRASDUZIONE
# File: demaria_parser.py
# Laboratorio Scientifico Metodo Demaria
# Autore, Responsabile Scientifico ed Inventore Unico: Avv. Alessandro Demaria
# Marchio Registrato UIBM N. 302026000161716 - Concept DOI Madre: 10.5281/zenodo.22789343
# Release DOI Ufficiale 3.4 Optimum: 10.5281/zenodo.23836177
# ==============================================================================

import math
import numpy as np
import pandas as pd

class DemariaVectorParser:
    def __init__(self):
        self.M_admissibility = np.array([
            [0, 1, 1, 0],
            [0, 1, 1, 1],
            [0, 1, 1, 1],
            [1, 1, 1, 1]
        ], dtype=np.int32)
        self.alpha_headers = ('qo', 'chol', 'chor', 'shol', 'shor', 'y', 'fachys', 'ykal', 'ar', 'faiin', 'qokaiin')
        self.delta_infixes = ('ch', 'sh', 'ok', 'ot', 'ct', 'ckhy', 'shckhy', 'okchy', 'otchy', 'cthy')
        self.gamma_terminals = ('am', 'an', 'dy', 'edy', 'ol', 'or', 'soor', 'su', 'chedy', 'shedy')

    def transduce_token(self, token):
        token_clean = str(token).strip().lower()
        if not token_clean or token_clean in ('nan', 'none', '0'):
            return 0
        for h in self.alpha_headers:
            if token_clean.startswith(h):
                return 1
        for t in self.gamma_terminals:
            if token_clean.endswith(t):
                return 4
        for i in self.delta_infixes:
            if i in token_clean:
                return 3
        return 2

    def transduce_sequence(self, token_list):
        return [self.transduce_token(tok) for tok in token_list]

    def calculate_coherence(self, state_sequence):
        if len(state_sequence) < 2:
            return 0.0, 0, 0
        valid_transitions = 0
        total_transitions = len(state_sequence) - 1
        for i in range(total_transitions):
            src_state = state_sequence[i]
            dst_state = state_sequence[i + 1]
            if src_state == 0 or dst_state == 0:
                valid_transitions += 1
                continue
            src_idx = src_state - 1
            dst_idx = dst_state - 1
            if self.M_admissibility[src_idx, dst_idx] == 1:
                valid_transitions += 1
        c_raw = valid_transitions / total_transitions
        return c_raw, valid_transitions, total_transitions

    def calculate_shannon_entropy(self, state_sequence):
        if not state_sequence:
            return 0.0
        filtered = [s for s in state_sequence if s in (1, 2, 3, 4)]
        if not filtered:
            return 0.0
        n = len(filtered)
        counts = pd.Series(filtered).value_counts()
        probs = counts / n
        return -sum(p * math.log2(p) for p in probs if p > 0)
