# METODO DEMARIA™ (Release v3.0)

[![Validation Suite - Metodo Demaria](https://github.com/Alessandro-Demaria/METODO.DEMARIA/actions/workflows/validate.yml/badge.svg)](https://github.com/Alessandro-Demaria/METODO.DEMARIA/actions/workflows/validate.yml)

* **Corpus**: Voynich Manuscript (EVA Transcription in IVTFF format)
* **Author**: Avv. Alessandro Demaria
* **Standard**: Standard Demaria v3.0 (Ottobre 2026)
* **Source Document**: [Demaria_2026_Metodo_Demaria_v3_Voynich_Summa.pdf](./Demaria_2026_Metodo_Demaria_v3_Voynich_Summa.pdf)
* **Zenodo DOI**: [10.5281/zenodo.23119964](https://doi.org/10.5281/zenodo.23119964) 
* **License**: CC BY 4.0 (Documentation & Data) / Trade Secret (Hardware)

### Release v3.0 Updates
* **Line-ID Codicological Fixing**: Risoluzione dell'anomalia di tracciamento sostituendo l'indicizzazione per-token con l'estrazione rigorosa del line_id reale codicologico dal parser.
* **Epistemological Tiering**: Distinzione formale dei risultati computazionali in 4 Tier (Tier A: Evidenza Stocastica, Tier B: Selettività Adversarial, Tier C: Modello ad Automa, Tier D: Ipotesi Ermeneutica).

### Architettura Integrata a 19 Moduli (Dataset Unico: 35.483 Tokens)

1. **voynich_parser.py**: Parsing, filtraggio e normalizzazione del testo EVA/IVTFF con tracciamento line_id.
2. **batch_runner.py**: Esecuzione batch per il calcolo e la misurazione delle metriche sul Master Dataset voynich_eva_tokens_extended.csv.
3. **coherence_evaluator.py**: Valutazione euristica e quantitativa della coerenza topologica (C* = 0.7542 filtered / 0.7473 raw).
4. **null_model_runner.py**: Generazione dei modelli nulli di controllo Monte Carlo per il confronto benchmark (p-value < 0.0001).
5. **master_framework_tester.py**: Audit di integrità end-to-end e sincronizzazione su tutti i 19 moduli della suite.
6. **test_di_mappatura_avversaria.py**: Test cieco adversarial su mappature stocastiche per la misura della selettività (CR-04).
7. **voynich_summary_generator.py**: Generazione automatizzata del report sintetico di coerenza e bilancio globale.

© METODO DEMARIA DEPOSITATO - Tutti i diritti riservati.
