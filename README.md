# METODO DEMARIA® Release v3.4 (Trattato Unificato Bilingue)

[![Validation Suite - Metodo Demaria](https://github.com/Alessandro-Demaria/METODO.DEMARIA/actions/workflows/validate.yml/badge.svg?branch=main&cache_bust=34)](https://github.com/Alessandro-Demaria/METODO.DEMARIA/actions/workflows/validate.yml) [![DOI Concept Madre](https://zenodo.org/badge/DOI/10.5281/zenodo.22789343.svg)](https://doi.org/10.5281/zenodo.22789343) [![DOI Release v3.4](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.23437366-blue.svg)](https://doi.org/10.5281/zenodo.23437366) [![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Quantitative Audit & Vector Topology of the Voynich Manuscript (Beinecke MS 408)

Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria (Molochio, RC)
Concept DOI Madre (Archivio Permanente): [10.5281/zenodo.22789343](https://doi.org/10.5281/zenodo.22789343)
DOI Ufficiale Release v3.4 (Version DOI): [10.5281/zenodo.23437366](https://doi.org/10.5281/zenodo.23437366)
Licenza del Trattato e dei Dati: Creative Commons Attribution 4.0 International (CC BY 4.0)
Licenza Codebase Pubblica: MIT License
Privativa Industriale e Segreto Algoritmi: Art. 98 D.Lgs. 30/2005 (Codice della Proprietà Industriale)
Marchio Registrato e Metodologia: METODO DEMARIA® (Numero UIBM 302026000161716)
Contatti Ufficiali: metodo.demaria@gmail.com | avv.alessandrodemaria@pec.it

---

## 1. PREMESSA EPISTEMOLOGICA E CAMBIO DI PARADIGMA

La presente Release v3.4 (Trattato Unificato Bilingue) del METODO DEMARIA® formalizza e consolida il cambio di paradigma epistemologico nello studio dei corpora simbolici storici non decifrati, con specifico riferimento al Manoscritto Voynich (Beinecke MS 408).

Rigettando l'ipotesi linguistico-fonetica tradizionale (Symbol-to-Sound / Symbol-to-Meaning), il METODO DEMARIA® formalizza il modello vettoriale e cibernetico (Symbol-to-Vector / Symbol-to-State): il corpus grafico costituisce un Instruction Set deterministico e calcolabile, concepito per la regolazione e il monitoraggio di uno spazio degli stati all'interno di un sistema temporizzato ad anello chiuso (Closed-Loop Timed Automaton).

---

## 2. RECAP BENCHMARK EMPIRICI FROZEN (RELEASE v3.4)

- **Corpus Analizzato**: 35.483 EVA tokens validati su 227 folii unici e 5.385 righi.
- **Coerenza Sintattica Grezza Flusso Continuo (Craw_stream)**: 0.799589 (79.96%).
- **Coerenza Sintattica Vincolata al Rigo (Craw_line)**: 0.798060 (79.81%).
- **Entropia Dinamica di Shannon (H(X))**: 1.8770 bit (1.6947 bit sul campione degli stati minimi proiettati).
- **Stato Zero Copertina (Power-OFF Enclosure S0)**: Carico computazionale Z_cover = 0.0 kPa ed Entropia Dinamica H_cover(X) = 0.0000 bit, formalizzando la chiusura topologica del dominio al 100% e smentendo l'ipotesi di mutilazione codicologica.
- **Model 1 (Global Null Model - Monte Carlo N=10.000, Seed 42)**: Z-Score = +19.8404, p-value < 0.0001, Cohen d = 7.6366.
- **Model 2 (Intra-Folio Null Model - Monte Carlo N=10.000, Seed 42)**: Z-Score = +16.3961, p-value < 0.0001, Cohen d = 8.0261.
- **Model 3 (Intra-Line Null Model / Smoking Gun - Monte Carlo N=10.000, Seed 42)**: Z_Line = +14.5202, p-value = 1.20 x 10^-21, Cohen d = 9.4860 (Prova Regina).
- **Isomorphic Double Randomization Test**: Double Null Z-Score = +1.5239, p-value empirico = 0.032000 (p < 0.05).
- **Stress Test di Sensibilità al Rumore Sintattico**: 99.22% di ritenzione del segnale topologico al 10.0% di rumore sintattico inoculato.
- **Holdout Stability (Out-of-Sample 80/20)**: Scarto irrisorio dello 0.8269% (C_train = 0.799460 vs C_test = 0.792849), escludendo qualsiasi fenomeno di overfitting.
- **Benchmarking Cross-Corpus su 10 Corpora Storici (N=83.241 elementi)**: Rigetto per tutti e 9 i corpora di controllo ad anello aperto e validazione esclusiva sull'Automa del Voynich.
- **Motore Invariante C per Triage Deterministico**: Throughput validato di 15.758.504 vettori/secondo con latenza media di 63.4 nanosecondi e catalogazione della Copertina al 100% in Classe 0 (Standby Neutro).

---

## 3. STRUTTURA DEL REPOSITORY DI LABORATORIO (12 FILE FROZEN)

### Codebase Python Vettorizzata Pure-Array e Suite di Audit (9 Moduli Integrati)
1. `demaria_eva_parser_v34.py`: Parser deterministico dell'alfabeto EVA e trasduzione molti-a-uno sulle regole della quadrupla degli stati topologici minimi (Alpha: 10.00%, Beta: 54.99%, Delta: 19.51%, Gamma: 15.50% ancorati allo Stato Zero S0).
2. `demaria_core.py`: Motore algebrico vettoriale R^d e gestore della Matrice Binaria di Ammissibilità 4x4 (13 celle ammesse, D = 81.25%) per il calcolo della Coerenza Sintattica (Craw_line = 0.798060) e dell'Invariante di Armonia Phi_alpha.
3. `audit_master_trepito.py`: Modulo di verifica dell'integrità crittografica SHA-256 del master dataset e controllo dell'immutabilità della suite.
4. `monte_carlo_audit.py`: Engine stocastico Monte Carlo per l'audit dei tre modelli nulli gerarchici (Global, Intra-Folio, Intra-Line) con N=10.000, Seed 42.
5. `stress_test_holdout.py`: Modulo per la validazione Holdout Out-of-Sample 80/20 e lo stress test di resilienza al rumore sintattico inoculato (0.0% -> 30.0%).
6. `cross_corpus_benchmark.py`: Sensore matematico per il benchmarking esteso su 10 corpora storici ed extra-corpus (83.241 elementi).
7. `triage_engine.py`: Motore ad alta velocità per l'Invariante C operante ad un throughput di 15.75 milioni di vettori/secondo con latenza di 63.4 nanosecondi per il triage deterministico (Classe 0, Classe 1, Classe 2).
8. `analisi_coerenza_pagina53.py`: Modulo avanzato di analisi topologica e scomposizione di rigo.
9. `orchestrator.py`: Orchestratore Master unificato per la riesecuzione automatica dell'intera suite di Clean Room Audit e l'esportazione dei report.

### Dataset Master e Documentazione Ufficiale (3 File Core)
- `voynich_eva_tokens_extended.csv`: Dataset Master di 35.483 EVA tokens (Impronta Crittografica SHA-256: `dec87e784290ad5b404bd5ed0110349a2f379c7fb386adb0bca2d7a4b1890999`).
- `METODO_DEMARIA_3.4_Unified_Treatise_DOI_10.5281_zenodo.23437366.pdf`: Trattato Unificato Canonico Bilingue (24 pagine: Italiano pp. 1-12 / Inglese pp. 13-24).
- `METODO_DEMARIA_3.4_APPENDICE_A_APPENDIX_A_DOI_10.5281_zenodo.23437366.pdf`: Documento Autonomo Appendice A (102 pagine) contenente le Tavole Omni-Grafiche 600 DPI, l'analisi dei folii, le 6 sezioni, i 7 Comandi ed il Titolo Reale COMPUTUS MAGNUS - REGULA AQUARUM ET CALORIS CIRCULATIONIS.

---

## 4. ESECUZIONE RAPIDA (QUICK START)

Per rieseguire l'intero audit e verificare in modo deterministico la baseline di laboratorio (Seed 42):

```bash
# Esecuzione dell'Orchestratore Master
python orchestrator.py
```

---

## 5. NOTE LEGALI, PATERNITÀ E SEGRETO INDUSTRIALE (ART. 98 CPI)

1. **Diritto d'Autore (L. 633/1941)**: La struttura teorica del METODO DEMARIA®, i trattati scientifici, i dataset quantitativi, la codebase di laboratorio, il design del dispositivo analogico Volvelle e la formalizzazione dell'Invariante di Armonia costituiscono opera d'ingegno originale tutelata ai sensi della Legge 22 aprile 1941 n. 633 e delle Convenzioni Internazionali WIPO / Berna.
2. **Marchio Registrato (D.Lgs. 30/2005)**: La denominazione, il logo e la metodologia METODO DEMARIA® costituiscono marchio registrato ai sensi del D.Lgs. 10 febbraio 2005, n. 30 (Codice della Proprietà Industriale).
3. **Segreto Industriale (Art. 98 CPI)**: Gli algoritmi di simulazione avanzata, i motori commerciali backend, le matrici proprietarie dell'Invariante di Armonia (Phi_alpha) e la struttura analitica del motore di calcolo C* **rimangono coperti da Segreto Industriale ed esclusiva proprietà dell'Autore Avv. Alessandro Demaria (Art. 98 D.Lgs. 30/2005 - CPI)**. La messa a disposizione della presente suite risponde ai requisiti di trasparenza Open Science e riproducibilità popperiana, senza concedere alcuna licenza d'uso o di sfruttamento commerciale sulla codebase proprietaria e sul motore sottostante.

© METODO DEMARIA DEPOSITATO - Tutti i diritti riservati (L. 633/1941, D.Lgs. 30/2005, Art. 98 CPI).
