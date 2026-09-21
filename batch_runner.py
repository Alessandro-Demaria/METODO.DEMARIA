import csv
import sys
from typing import List, Dict, Any
import voynich_parser
import load_engine
import coherence_evaluator

def run_batch_processing(
    eva_filepath: str = "voynich_eva.txt", 
    output_csv: str = "voynich_batch_measurements.csv"
) -> None:
    """
    Esegue l'elaborazione a batch del manoscritto Voynich.
    Estrae le righe, calcola i carichi dinamici e valuta la coerenza vettoriale C*.
    """
    print(f"[+] Starting batch processing on {eva_filepath}...")

    # Inizializzazione parser e moduli
    parser = voynich_parser.VoynichParser() if hasattr(voynich_parser, "VoynichParser") else voynich_parser
    evaluator = coherence_evaluator.CoherenceEvaluator() if hasattr(coherence_evaluator, "CoherenceEvaluator") else coherence_evaluator

    # Estrazione record
    if hasattr(parser, "parse"):
        try:
            records = parser.parse()
        except TypeError:
            records = parser.parse(eva_filepath)
    elif hasattr(parser, "parse_voynich_eva"):
        records = parser.parse_voynich_eva(eva_filepath)
    else:
        print("[-] Error: Unable to locate suitable parse method in voynich_parser.")
        return

    if not records:
        print("[-] Error: No records extracted from transcription file.")
        return

    processed_rows: List[Dict[str, Any]] = []

    for idx, rec in enumerate(records):
        # Gestione robusta delle chiavi per compatibilità tra versioni di parser
        line_id = rec.get('line') or rec.get('line_num') or f"line_{idx+1}"
        folio = rec.get('folio') or rec.get('page') or "unknown"
        tokens = rec.get('tokens', [])

        if not tokens and isinstance(rec, dict) and 'text' in rec:
            tokens = rec['text'].split()

        # Calcolo del carico dinamico tramite load_engine
        if hasattr(load_engine, "compute_line_load"):
            load_data = load_engine.compute_line_load(tokens)
        elif hasattr(load_engine, "calculate_line_load"):
            load_data = load_engine.calculate_line_load(tokens)
        else:
            load_data = {"mean_load": 0.0, "max_load": 0.0}

        # Calcolo coerenza vettoriale C*
        if hasattr(evaluator, "evaluate_sequence"):
            c_star = evaluator.evaluate_sequence(tokens)
        elif hasattr(evaluator, "compute_coherence"):
            c_star = evaluator.compute_coherence(tokens)
        else:
            c_star = 0.0

        mean_load = load_data.get("mean_load", 0.0) if isinstance(load_data, dict) else 0.0
        max_load = load_data.get("max_load", 0.0) if isinstance(load_data, dict) else 0.0

        processed_rows.append({
            "Folio": folio,
            "Line": line_id,
            "Token_Count": len(tokens),
            "Mean_Load": round(mean_load, 6),
            "Max_Load": round(max_load, 6),
            "Coherence_C_Star": round(c_star, 6)
        })

    # Scrittura del CSV di output
    fieldnames = ["Folio", "Line", "Token_Count", "Mean_Load", "Max_Load", "Coherence_C_Star"]
    try:
        with open(output_csv, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(processed_rows)
        print(f"[+] Batch processing successfully completed. {len(processed_rows)} rows written to {output_csv}.")
    except Exception as e:
        print(f"[-] Error writing CSV output: {e}")

if __name__ == "__main__":
    run_batch_processing()
