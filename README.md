# METODO DEMARIA® (Release v3.0 — Voynich-Summa Computazionale)

[![Validation Suite - Metodo Demaria](https://github.com/Alessandro-Demaria/METODO.DEMARIA/actions/workflows/validate.yml/badge.svg)](https://github.com/Alessandro-Demaria/METODO.DEMARIA/actions/workflows/validate.yml)
[![Zenodo DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23119964.svg)](https://doi.org/10.5281/zenodo.23119964)
[![Concept DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22789343.svg)](https://doi.org/10.5281/zenodo.22789343)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

* **Corpus**: Voynich Manuscript (Beinecke MS 408) — EVA Transcription in IVTFF format
* **Author, Scientific Director, and Sole Inventor**: Avv. Alessandro Demaria
* **Registered Trademark & Methodology**: METODO DEMARIA® / METODO DEMARIA™
* **Standard**: Standard Demaria v3.0 (Ottobre 2026)
* **Source Document**: [Demaria_2026_Metodo_Demaria_v3_Voynich_Summa_Demaria.pdf](./Demaria_2026_Metodo_Demaria_v3_Voynich_Summa_Demaria.pdf)
* **Zenodo DOI (Official Release v3.0)**: [10.5281/zenodo.23119964](https://doi.org/10.5281/zenodo.23119964)
* **Concept DOI (Permanent Archive)**: [10.5281/zenodo.22789343](https://doi.org/10.5281/zenodo.22789343)
* **License**: CC BY 4.0 (Documentation & Data) / Trade Secret (Hardware & Proprietary Backend)
* **Official Contacts**: metodo.demaria@gmail.com | avv.alessandrodemaria@pec.it

### Release v3.0 Updates
* **Dynamic Intra-Folio Coaxial Coherence (\(C^* = 0,5557\))**: Misurazione dinamica intra-folio della Coerenza Coassiale con isolamento delle transizioni di stato ed assenza di inter-folio leakage.
* **Codicological Sequential Fixing**: Ordinamento esplicito del corpus codicologico per `Folio_Base` -> `line_id` -> `Record_ID`.
* **Closed-Loop Timed Automaton & Harmony Invariant (\(\Phi_{\text{a}}\))**: Formalizzazione della quintupla dell'automa \(A = (S, \Sigma, X, f, \text{Inv})\), della matrice di Markov \(4 \times 4\), della quadrupla degli stati minimi \((\alpha, \beta, \delta, \gamma)\) e scomposizione della matrice a 12 variabili.
* **Master Clock & Reset Router**: Isolamento del Master Clock \(\omega_0 = 0,0416\text{ Hz}\) (\(T_0 = 24\text{ s}\)) e dell'anomalia controllata di reset su \(f57v\) (\(C^* = 0,3968\)).

### Architettura Integrata a 19 Moduli (Master Dataset: voynich_eva_tokens_extended.csv — 35.483 Tokens)

1. **voynich_parser.py**: Parsing, filtraggio e normalizzazione del testo EVA/IVTFF con tracciamento esplicito del line_id e re-indexing codicologico.
2. **batch_runner.py**: Orchestratore sequenziale e runner batch unico per l'esecuzione automatizzata delle metriche e l'esportazione di master_batch_execution_summary.csv.
3. **coherence_evaluator.py**: Valutazione dinamica intra-folio della Coerenza Coassiale (\(C^* = 0,5557\)) e stabilità di fase dello spazio degli stati.
4. **null_model_test.py**: Generazione dei modelli nulli stocastici di controllo Monte Carlo (\(N = 10.000\) permutazioni a doppio vincolo, \(p < 0,0001\)).
5. **train_test_split_validation.py**: Validazione Out-of-Sample al buio (40% Train / 60% Test) con GroupShuffleSplit raggruppato su Folio_Base (\(\Delta C^* < 0,025\)).
6. **voynich_decoder_pipeline.py**: Pipeline di decodifica inversa per lo stripping dei prefissi/suffissi EVA, isolamento delle radici native (96,45%) ed estrazione dell'Instruction Set.
7. **constrained_adversarial_test.py**: Test cieco adversarial su 10.000 mappature casuali (partizione rigida 5-5-5-5) per la misura della selettività (CR-04 > 99,9° percentile).
8. **master_framework_tester.py**: Audit di integrità end-to-end e sincronizzazione su tutti i 19 moduli della suite.
9. **voynich_summary_generator.py**: Generazione automatizzata del report sintetico di coerenza e bilancio globale del Computus Magnus.

© METODO DEMARIA® / METODO DEMARIA™ DEPOSITATO - Tutti i diritti riservati.