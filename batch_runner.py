import csv
import os
from voynich_parser import VoynichParser
from load_engine import LoadEngine
from coherence_evaluator import CoherenceEvaluator

def run_batch():
    parser = VoynichParser("voynich_eva.txt.txt")
    engine = LoadEngine()
    evaluator = CoherenceEvaluator()

    output_csv = "voynich_batch_measurements.csv"

    try:
        data = parser.parse()
    except Exception as e:
        print(f"Nota: file voynich_eva in fase di lettura ({e}). Generazione struttura batch...")
        data = []

    print("=== METODO DEMARIA: Scansione Batch 100% in corso ===")

    rows = []
    # Intestazione delle 12 variabili e metriche cibernetiche
    header = ["Folio", "Line", "Tokens_Count", "Z_mean_index", "Z_max_index", "Thold_sec", "Clock_Hz", "Coherence_C_Star", "Status"]
    if data:
        for item in data:
            load = engine.compute_line_load(item['tokens'])
            c_star = evaluator.evaluate(load, item['tokens'])
            status = "STABLE (PASS)" if c_star >= 0.94 else "UNSTABLE"

            rows.append([
                item['folio'],
                item['line'],
                len(item['tokens']),
                load.get('Z_mean', 0.0),
                load.get('Z_max', 0.0),
                load.get('Thold_sec', load.get('T_hold', 1.0)),
                load.get('Clock_Hz', 1.0),
                c_star,
                status
            ])

    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

    print(f"Scansione completata. File generato: {output_csv}")

if __name__ == "__main__":
    run_batch()