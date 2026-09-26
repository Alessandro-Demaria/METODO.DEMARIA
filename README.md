# METODO DEMARIA (Release v2.03)

[![Validation Suite - Metodo Demaria](https://github.com/Alessandro-Demaria/METODO.DEMARIA/actions/workflows/validate.yml/badge.svg)](https://github.com/Alessandro-Demaria/METODO.DEMARIA/actions/workflows/validate.yml)

* **Corpus**: Voynich Manuscript (EVA Transcription in IVTFF format)
* **Author**: Alessandro Demaria
* **Standard**: Standard Demaria v2.03 (Settembre 2026)
* **Source Document**: [Demaria_2026_Metodo_Demaria_v2.03.pdf](./Demaria_2026_Metodo_Demaria_v2.03.pdf)
* **Zenodo DOI**: [10.5281/zenodo.22975532](https://doi.org/10.5281/zenodo.22975532)
* **License**: MIT License (Code) / CC BY 4.0 (Documentation & Data)

### Release v2.03 Updates
* **Line-ID Codicological Fixing**: Risoluzione dell'anomalia di tracciamento sostituendo l'indicizzazione per-token con l'estrazione rigorosa del `line_id` reale codicologico dal parser.
* **Epistemological Tiering**: Distinzione formale dei risultati computazionali in 4 Tier (Tier A: Evidenza Stocastica, Tier B: Selettività Adversarial, Tier C: Modello ad Automa, Tier D: Ipotesi Ermeneutica).

### Architettura a 7 Moduli Core

1. **voynich_parser.py**: Parsing, filtraggio e normalizzazione del testo EVA/IVTFF con tracciamento `line_id`.
2. **batch_runner.py**: Esecuzione batch per il calcolo e la misurazione delle metriche con esportazione `voynich_token_by_token_measurements.csv`.
3. **coherence_evaluator.py**: Valutazione euristica e quantitativa della coerenza topologica (\(C^*\) raw e filtered).
4. **null_model_runner.py**: Generazione dei modelli nulli di controllo Monte Carlo per il confronto benchmark (\(p\)-value).
5. **verify_markov.py**: Verifica della stazionarietà e delle transizioni della catena di Markov (matrice \(4 \times 4\)).
6. **adversarial_mapping_test.py**: Test cieco adversarial su 10.000 mappature casuali per la misura della selettività (CR-04).
7. **load_engine.py**: Motore di caricamento rapido e preparazione dei dati.

© METODO DEMARIA DEPOSITATO - Tutti i diritti riservati.
