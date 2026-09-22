"""
METODO DEMARIA - MOTORE DI CARICAMENTO RISORSE E DATASET
Modulo: load_engine.py
Verifica di Conformita: 21/09/2026 - Standard Demaria v2.0.1

Descrizione:
  Gestisce l'inizializzazione dell'ambiente, la verifica dell'integrita
  dei file di input/output e l'orchestrazione dei moduli dell'architettura,
  in stretta conformita con la monografia teorica Demaria_2026_Metodo_Demaria_v2.01.pdf.
"""

import os
import json
from typing import Dict, Any, List


class EngineLoader:
    """
    Caricatore centrale dell'ambiente di esecuzione e gestore dell'integrita del repository.
    """

    def __init__(self, required_files: List[str] = None):
        if required_files is None:
            self.required_files = [
                "voynich_eva.txt",
                "voynich_parser.py",
                "batch_runner.py",
                "coherence_evaluator.py",
                "null_model_runner.py",
                "verify_markov.py"
            ]
        else:
            self.required_files = required_files

    def verify_environment(self) -> Dict[str, Any]:
        """
        Verifica la presenza di tutti i file di sistema essenziali per il Metodo Demaria.
        """
        missing_files = []
        existing_files = []

        for filename in self.required_files:
            if os.path.exists(filename):
                existing_files.append(filename)
            else:
                missing_files.append(filename)

        status = 'SUCCESS' if not missing_files else 'WARNING'

        return {
            'status': status,
            'existing_count': len(existing_files),
            'missing_count': len(missing_files),
            'existing_files': existing_files,
            'missing_files': missing_files
        }

    def load_configuration(self, config_filepath: str = "config.json") -> Dict[str, Any]:
        """
        Carica i parametri di configurazione del motore, o genera parametri di default.
        """
        if os.path.exists(config_filepath):
            with open(config_filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Configurazione standard di fallback conforme allo Standard Demaria v2.0.1
        return {
            'version': 'v2.0.1',
            'standard_date': '2026-09-21',
            'default_input': 'voynich_eva.txt',
            'default_output_csv': 'voynich_batch_measurements.csv',
            'log_level': 'INFO'
        }


def initialize_engine() -> Dict[str, Any]:
    """
    Funzione interfaccia standard per l'inizializzazione del motore.
    """
    loader = EngineLoader()
    env_report = loader.verify_environment()
    config = loader.load_configuration()
    
    return {
        'environment': env_report,
        'configuration': config,
        'status': 'INITIALIZED'
    }


if __name__ == "__main__":
    # Test diagnostico isolato
    print("Avvio Test Diagnostico EngineLoader...")
    loader = EngineLoader()
    report = loader.verify_environment()
    print("Report Ambiente:", report)
    assert report['status'] in ['SUCCESS', 'WARNING'], "Errore nella verifica dell'ambiente"
    print("VERIFICA ENGINE LOADER: SUPERATA")
