# METODO DEMARIA (Release v2.02)

[![Validation Suite - Metodo Demaria](https://github.com/Alessandro-Demaria/METODO.DEMARIA/actions/workflows/validate.yml/badge.svg)](https://github.com/Alessandro-Demaria/METODO.DEMARIA/actions)

* **Corpus**: Voynich Manuscript (EVA Transcription in IVTFF format)
* **Author**: Alessandro Demaria
* **Standard**: Standard Demaria v2.02 (2026)
* **Source Document**: [Demaria_2026_Metodo_Demaria_v2.02.pdf](./Demaria_2026_Metodo_Demaria_v2.02.pdf)
* **Zenodo DOI**: [10.5281/zenodo.22856418](https://doi.org/10.5281/zenodo.22856418)
* **License**: MIT License (Code) / CC BY 4.0 (Documentation & Data)

### Architettura a 6 Moduli Core

1. **voynich_parser.py**: Parsing, filtraggio e normalizzazione del testo EVA/IVTFF.
2. **batch_runner.py**: Esecuzione batch per il calcolo e la misurazione delle metriche.
3. **coherence_evaluator.py**: Valutazione euristica e quantitativa della coerenza statistico-linguistica.
4. **null_model_runner.py**: Generazione dei modelli nulli di controllo per il confronto benchmark.
5. **verify_markov.py**: Verifica della stazionarietà e delle transizioni della catena di Markov.
6. **load_engine.py**: Motore di caricamento rapido e preparazione dei dati.

© METODO DEMARIA DEPOSITATO - Tutti i diritti riservati.
