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
import os, hashlib, time, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
from demaria_parser import DemariaVectorParser
from demaria_montecarlo import DemariaMonteCarloEngine
from demaria_triage_c import DemariaInvariantCEngine
from demaria_validation import DemariaValidationSuite
from demaria_cross_corpus import DemariaCrossCorpusBenchmark

def sha256_f(fp):
    h = hashlib.sha256()
    with open(fp, 'rb') as f:
        for c in iter(lambda: f.read(65536), b''):
            h.update(c)
    return h.hexdigest()

def main():
    t0 = time.perf_counter()
    dp = 'voynich_eva_tokens_extended.csv'
    sha_ds = sha256_f(dp)
    df = pd.read_csv(dp)
    df = df.loc[df['EVA_Token'].notna()].reset_index(drop=True)
    toks = df['EVA_Token'].astype(str).tolist()
    lids = df['Folio'].astype(str).to_numpy()
    fids = df['Folio'].astype(str).str.split('.').str[0].to_numpy()

    p = DemariaVectorParser()
    # Ramo agnostico cieco non circolare (transduce_universal_agnostic)
    seq = p.transduce_universal_agnostic(toks, lids)
    st6 = p.transduce_positional_rel35(seq, lids)
    c4, v4, tot_tr = p.calculate_line_coherence(seq, lids)
    c6, v6, _ = p.calculate_rel35_coherence(st6, lids)
    h_state = p.calculate_shannon_entropy(seq)
    dkl = p.calculate_cycle_dkl(seq)
    sel_v, pa, pg = p.calculate_intrinsic_boundary_selectivity(seq, lids)

    mc = DemariaMonteCarloEngine(p)
    with ThreadPoolExecutor(max_workers=2) as ex:
        f_m4 = ex.submit(mc.run_hierarchical_null_model, seq, lids, 10000, 42, p.M4)
        f_m6 = ex.submit(mc.run_positional_rel35_null_model, seq, lids, 10000, 42)
        mu4, _, z4, p4 = f_m4.result()
        mu6, _, z6, p6 = f_m6.result()
    d4 = mc.compute_cohen_d_bernoulli(c4, mu4)
    d6 = mc.compute_cohen_d_bernoulli(c6, mu6)

    vs_s = DemariaValidationSuite(p)
    ctr, cte, gap = vs_s.holdout_split_validation(seq, lids, fids)
    _, ret = vs_s.noise_stress_test(seq, lids)
    _, _, zdr, pdr = vs_s.isomorphic_double_randomization(seq, lids, 2000, 42)

    dice = DemariaInvariantCEngine()
    vecs = np.random.default_rng(42).random((1000000, 2), dtype=np.float32)
    cls_b, _, el = dice.process_stream_vectorized(vecs)
    p_crit_emp = float(np.mean(cls_b == 2))
    p_crit_ana = dice.analytical_tail_probability()

    print('SHA-256:', sha_ds, '| Tok:', len(toks), '| Trans:', tot_tr)
    print('M4 Cieco -> C4:', round(c4, 6), f'({v4}/{tot_tr})', 'mu0:', round(mu4, 6), 'Z4:', round(z4, 4), 'p:', round(p4, 5), 'd4:', round(d4, 4))
    print('M6 Cieco -> C6:', round(c6, 6), f'({v6}/{tot_tr})', 'mu0:', round(mu6, 6), 'Z6:', round(z6, 4), 'p:', round(p6, 5), 'd6:', round(d6, 4))
    print('H_state:', round(h_state, 6), 'bit | D_KL:', round(dkl, 6), 'bit | Sel:', round(sel_v, 4), 'Pa:', round(pa, 4), 'Pg:', round(pg, 4))
    print('Holdout 80/20:', round(ctr, 6), 'vs', round(cte, 6), 'gap%:', round(gap, 2), '| NoiseRet%:', round(ret, 4), '| DoubleRand Z:', round(zdr, 4), 'p:', round(pdr, 5))
    print('DICE MVS:', round((1e6 / el) / 1e6, 2), '| CritEmp%:', round(p_crit_emp * 100, 4), 'vs CritAna%:', round(p_crit_ana * 100, 5))

    cc = DemariaCrossCorpusBenchmark(p)
    tb = cc.evaluate(seq, lids, c4, z4, c6, z6, sel_v, iterations=2000, seed=42)
    for k, v in tb.items():
        print(' -', k, ':', v)
    print('RELEASE 3.5 NON CIRCOLARE CONSOLIDATA IN', round(time.perf_counter() - t0, 3), 's')

if __name__ == '__main__':
    main()