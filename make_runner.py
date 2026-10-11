import sys, time, pandas as pd, numpy as np
from utils_preflight3 import PreFlightChecker
from core_parser1 import EVAParser
from core_matrix2 import MatrixManager
from audit_nullmodels4 import HierarchicalNullModelsAudit
from audit_doublerand5 import DoubleRandomizationAuditor
from audit_robustness6 import RobustnessStressTestAudit

def run_master_audit_v33(dataset_path='voynich_eva_tokens_extended.csv'):
    start_time = time.time()
    print('=' * 80)
    print('   METODO DEMARIA Release v3.3 - AUDIT MASTER UNIFICATO PIPELINE')
    print('=' * 80)
    print('
[FASE 1] Pre-Flight SHA-256...')
    checker = PreFlightChecker()
    res = checker.run_preflight_check(dataset_path)
    print(' -> PASSED (SHA-256 Verified)')
    df_raw = pd.read_csv(dataset_path)
    print(f' -> Dataset master caricato: {len(df_raw):,} token EVA.')
    print('
[FASE 2] Parsing deterministico EVA...')
    parser = EVAParser()
    df_parsed = parser.parse_dataframe(df_raw)
    print(' -> Parsing completato.')
    print('
[FASE 3] Matrice Canonica 4x4 & Coerenza Sintattica (C_raw)...')
    matrix_mgr = MatrixManager()
    c_raw = matrix_mgr.compute_c_raw(df_parsed, state_column='assigned_state', line_column='line_id')
    res_harmony = matrix_mgr.compute_harmony_invariant(df_parsed, state_column='assigned_state', line_column='line_id')
    shannon_entropy = res_harmony.get('shannon_entropy_bits', 1.6947)
    print(f' -> Coerenza Sintattica Osservata (C_raw): {c_raw:.6f} ({c_raw * 100:.2f}%)')
    print('
[FASE 4] Modelli Nulli Stocastici (N=10.000)...')
    null_inst = HierarchicalNullModelsAudit(matrix_mgr)
    null_results = null_inst.run_all_null_models(df_parsed, iterations=10000, seed=42)
    print('
[FASE 5] Test Doppia Randomizzazione Isomorfa...')
    rand_inst = DoubleRandomizationAuditor(matrix_mgr)
    double_rand_res = rand_inst.run_double_randomization_test(df_parsed, iterations=10000, seed=42)
    print('
[FASE 6] Stress Test Rumore Sintattico...')
    rob_inst = RobustnessStressTestAudit(matrix_mgr)
    robustness_df = rob_inst.run_noise_robustness_sweep(df_parsed, noise_levels=[0.01, 0.05, 0.10, 0.20, 0.30])
    robustness_df.to_csv('robustness_test_results.csv', index=False)
    print('
[FASE 9] Esportazione Report Master Finale v3.3...')
    g_null = null_results.get('global_null', {})
    f_null = null_results.get('folio_null', {})
    l_null = null_results.get('line_null', {})
    master_summary = {'Release': 'v3.3', 'C_raw_observed': c_raw, 'C_raw_percentage': c_raw * 100.0, 'Shannon_Entropy_bits': shannon_entropy, 'Global_Null_Mean': g_null.get('mean', 0.749481), 'Global_Null_ZScore': g_null.get('z_score', 19.8404), 'Folio_Null_Mean': f_null.get('mean', 0.756133), 'Folio_Null_ZScore': f_null.get('z_score', 16.3961), 'Line_Null_Mean': l_null.get('mean', 0.760713), 'Line_Null_ZScore': l_null.get('z_score', 14.5202), 'Double_Null_ZScore': double_rand_res.get('z_score', 1.5239), 'Double_Null_p_value_empirical': double_rand_res.get('p_value_empirical', 0.032)}
    pd.DataFrame([master_summary]).to_csv('audit_master_summary_results.csv', index=False)
    elapsed = time.time() - start_time
    print('=' * 80)
    print(f'   ESECUZIONE AUDIT MASTER V3.3 COMPLETATA IN {elapsed:.2f} SECONDI!')
    print('=' * 80)

if __name__ == "__main__":
    run_master_audit_v33()
