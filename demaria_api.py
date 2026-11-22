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
import os, time, hashlib, pathlib, datetime, numpy as np, pandas as pd, uvicorn
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, Header, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from demaria_triage_c import DemariaInvariantCEngine
from demaria_parser import DemariaVectorParser
from demaria_montecarlo import DemariaMonteCarloEngine
from demaria_validation import DemariaValidationSuite
from demaria_cross_corpus import DemariaCrossCorpusBenchmark

app = FastAPI(title='DEMARIA CORE - RELEASE 3.5 (EDIZIONE SCIENTIFICA PURA)')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'], expose_headers=['*'])
dice = DemariaInvariantCEngine()
parser = DemariaVectorParser()
mc = DemariaMonteCarloEngine(parser)
val_s = DemariaValidationSuite(parser)
cc_b = DemariaCrossCorpusBenchmark(parser)
_CACHE = {}

def auth(k):
    if k != 'DEMARIA_CORE_EVO_KEY_2026':
        raise HTTPException(status_code=401, detail='Non autorizzato')

def _live(dp='voynich_eva_tokens_extended.csv'):
    if not os.path.exists(dp):
        raise HTTPException(status_code=404, detail='Dataset non trovato')
    h = hashlib.sha256(pathlib.Path(dp).read_bytes()).hexdigest()
    if h in _CACHE:
        return _CACHE[h]
    df = pd.read_csv(dp)
    df = df.loc[df['EVA_Token'].notna()].reset_index(drop=True)
    toks = df['EVA_Token'].astype(str).tolist()
    lids = df['Folio'].astype(str).to_numpy()
    fids = df['Folio'].astype(str).str.split('.').str[0].to_numpy()
    seq = parser.transduce_universal_agnostic(toks, lids)
    st6 = parser.transduce_positional_rel35(seq, lids)
    cl, _, _ = parser.calculate_line_coherence(seq, lids)
    c35, _, _ = parser.calculate_rel35_coherence(st6, lids)
    eh = parser.calculate_shannon_entropy(seq)
    h1_c, h_cond_c = parser.calculate_character_entropies(toks)
    dkl = parser.calculate_cycle_dkl(seq)
    sel_v, pa, pg = parser.calculate_intrinsic_boundary_selectivity(seq, lids)
    adj_cnt, _, adj_pct = parser.compute_adjacent_levenshtein_le1(toks, lids)
    chi2_sec, df_sec = parser.compute_sections_chi2_pure(toks, fids)
    with ThreadPoolExecutor(max_workers=2) as ex:
        f4 = ex.submit(mc.run_hierarchical_null_model, seq, lids, 2000, 42, parser.M4)
        f6 = ex.submit(mc.run_positional_rel35_null_model, seq, lids, 2000, 42)
        ml, _, zl, _ = f4.result()
        m6, _, z35, _ = f6.result()
    d4 = mc.compute_cohen_d_bernoulli(cl, ml)
    d6 = mc.compute_cohen_d_bernoulli(c35, m6)
    _, _, gap = val_s.holdout_split_validation(seq, lids, fids)
    _, ret = val_s.noise_stress_test(seq, lids)
    _, _, zdr, pdr = val_s.isomorphic_double_randomization(seq, lids, 1000, 42)
    cc_res = cc_b.evaluate(seq, lids, cl, zl, c35, z35, sel_v)
    _CACHE[h] = {
        'sha256': h,
        'c_raw_line': round(cl, 6), 'c_rel35': round(c35, 6),
        'z_line': round(zl, 4), 'z_rel35': round(z35, 4),
        'd4_cohen': round(d4, 4), 'd6_cohen': round(d6, 4),
        'entropy_state_bit': round(eh, 6), 'entropy_char_h1': round(h1_c, 6), 'entropy_char_cond': round(h_cond_c, 6),
        'dkl_bit': round(dkl, 6), 'selectivity': round(sel_v, 4), 'pa': round(pa, 4), 'pg': round(pg, 4),
        'adj_levenshtein_le1': adj_cnt, 'adj_levenshtein_pct': round(adj_pct * 100.0, 2),
        'sections_chi2': round(chi2_sec, 2), 'sections_df': df_sec,
        'holdout_gap_pct': round(gap, 2), 'noise_retention_pct': round(ret, 4),
        'sens_z': round(zdr, 4), 'sens_p': round(pdr, 5),
        'controls_benchmark': cc_res
    }
    return _CACHE[h]

@app.get('/', response_class=HTMLResponse)
async def home():
    return pathlib.Path('dashboard_collaudo_zerocopy.html').read_text(encoding='utf-8') if os.path.exists('dashboard_collaudo_zerocopy.html') else '<h1>DEMARIA CORE - RELEASE 3.5 (EDIZIONE SCIENTIFICA PURA)</h1>'

@app.get('/api/v1/health')
async def health(x_demaria_api_key: str = Header(None, alias='x-demaria-api-key')):
    auth(x_demaria_api_key)
    return {'status': 'OK', 'system_name': 'DEMARIA CORE RELEASE 3.5 (SCIENTIFICA PURA)', 'mother_concept_doi': '10.5281/zenodo.22789343', 'uibm_trademark': '302026000161716'}

@app.post('/api/v1/triage/binary')
async def triage_bin(req: Request, x_demaria_api_key: str = Header(None, alias='x-demaria-api-key')):
    auth(x_demaria_api_key)
    b = await req.body()
    if len(b) == 0 or len(b) % 8 != 0:
        raise HTTPException(status_code=400, detail='Buffer non valido')
    t0 = time.perf_counter()
    v = np.frombuffer(b, dtype=np.float32).reshape(-1, 2)
    td = time.perf_counter() - t0
    cl, _, el = dice.process_stream_vectorized(v)
    n = len(v)
    hd = {
        'X-DICE-Total-Vectors': str(n),
        'X-DICE-Kernel-Throughput-MVS': f'{(n / el) / 1e6:.2f}',
        'X-DICE-Latency-NS': f'{(el / n) * 1e9:.2f}',
        'X-DICE-Kernel-Elapsed-Sec': f'{el:.6f}',
        'X-DICE-ZeroCopy-Decode-Sec': f'{td:.6f}',
        'X-DICE-Class-0-OK': str(int(np.sum(cl == 0))),
        'X-DICE-Class-1-WARN': str(int(np.sum(cl == 1))),
        'X-DICE-Class-2-CRIT': str(int(np.sum(cl == 2))),
        'X-DICE-Protocol': 'ZERO-COPY-BINARY-OCTET-STREAM'
    }
    return Response(content=cl.tobytes(), media_type='application/octet-stream', headers=hd)

@app.post('/api/v1/audit/full-run')
async def full_run(x_demaria_api_key: str = Header(None, alias='x-demaria-api-key')):
    auth(x_demaria_api_key)
    live = _live()
    v = np.random.default_rng(42).random((100000, 2), dtype=np.float32)
    cls_b, _, el = dice.process_stream_vectorized(v)
    return {
        'timestamp': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'author': 'Avv. Alessandro Demaria',
        'release': '3.5-PURA',
        'metrics': live,
        'dice_mvs': round((1e5 / el) / 1e6, 2),
        'dice_crit_emp_pct': round(float(np.mean(cls_b == 2)) * 100.0, 4),
        'dice_crit_ana_pct': round(dice.analytical_tail_probability() * 100.0, 4)
    }

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)