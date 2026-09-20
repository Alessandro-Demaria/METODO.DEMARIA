import csv
import os
from voynich_parser import VoynichParser
from load_engine import LoadEngine
from coherence_evaluator import CoherenceEvaluator

def run_batch():
    parser = VoynichParser("voynich_eva.txt")
    engine = LoadEngine()
    evaluator = CoherenceEvaluator()

    output_csv = "voynich_batch_measurements.csv"

    try:
        data = parser.parse()
    except Exception as e:
        print(f"Errore nella lettura del corpus: {e}")
        return

    print("=== METODO DEMARIA: Scansione Batch 100% in corso ===")
    
    fieldnames = [
        "folio", "line_num", "tokens_count", 
        "Z_mean", "Z_max", "C_star", "status"
    ]

    records = []
    
    for entry in data:
        folio = entry["folio"]
        line_num = entry["line_num"]
        tokens = entry["tokens"]
        
        load_data = engine.calculate_line_load(tokens)
        c_star = evaluator.evaluate(load_data, tokens)
        status = evaluator.get_status(c_star)
        
        records.append({
            "folio": folio,
            "line_num": line_num,
            "tokens_count": len(tokens),
            "Z_mean": load_data["Z_mean"],
            "Z_max": load_data["Z_max"],
            "C_star": c_star,
            "status": status
        })

    with open(output_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"Completato! Elaborate {len(records)} righe testuali reali.")
    print(f"Dataset salvato in {output_csv}")

if __name__ == "__main__":
    run_batch()
