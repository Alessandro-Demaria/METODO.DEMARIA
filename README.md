# METODO DEMARIA (Release v2.0.1.1)

[![Validation Suite - Metodo Demaria](https://github.com/Alessandro-Demaria/METODO.DEMARIA/actions/workflows/validate.yml/badge.svg)](https://github.com/Alessandro-Demaria/METODO.DEMARIA/actions/workflows/validate.yml)

**Corpus:** Voynich Manuscript (EVA Transcription in IVTFF format)
**Author:** Alessandro Demaria
**Standard:** Standard Demaria v2.0.1.1 (21/09/2026)
**Source Document:** `Demaria_2026_Metodo_Demaria_v2.01.pdf` (Fonte Suprema)
**Zenodo DOI:** 10.5281/zenodo.22856418
**License:** MIT License (Code) / CC BY 4.0 (Documentation & Data)
Architettura a 6 Moduli Core
L'architettura software del Metodo Demaria si compone di 6 moduli interconnessi e completamente testati tramite suite di validazione automatizzata su GitHub Actions:

voynich_parser.py: Parsing, filtraggio e normalizzazione del testo cifrato in formato EVA/IVTFF.

batch_runner.py: Gestione dell'infrastruttura di esecuzione batch per il calcolo sistematico delle metriche su larga scala.

coherence_evaluator.py: Valutazione euristica e quantitativa della coerenza statistico-linguistica del modello.

null_model_runner.py: Generazione di testi casuali di controllo e confronto con i moduli nulli (benchmark).

verify_markov.py: Verifica empirica della stazionarità e transizione di stato della matrice della catena di Markov.

load_engine.py: Motore di caricamento ad alte prestazioni per la preparazione dei dati nell'ambiente di analisi.
