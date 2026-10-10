# METODO DEMARIA® Release v3.3 (Audit-Master Unificato)
### Quantitative Audit & Vector Topology of the Voynich Manuscript (Beinecke MS 408)

[![Validation Suite - Metodo Demaria](https://github.com/Alessandro-Demaria/METODO-DEMARIA-v3.3-VOYNICH-AUDIT-MASTER/actions/workflows/validate.yml/badge.svg)](https://github.com/Alessandro-Demaria/METODO-DEMARIA-v3.3-VOYNICH-AUDIT-MASTER/actions/workflows/validate.yml)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Autore, Responsabile Scientifico e Inventore Unico**: Avv. Alessandro Demaria (Molochio, RC)  
**Concept DOI Madre (Archivio Permanente)**: [10.5281/zenodo.22789343](https://doi.org/10.5281/zenodo.22789343)  
**DOI Ufficiale Release v3.3 (Audit-Master)**: [10.5281/zenodo.23242996](https://doi.org/10.5281/zenodo.23242996)  
**Licenza del Trattato e dei Dati**: Creative Commons Attribution 4.0 International (CC BY 4.0)  
**Licenza Codebase Pubblica**: MIT License  
**Privativa Industriale e Segreto Algoritmico**: Art. 98 D.Lgs. 30/2005 (Codice della Proprietà Industriale)  
**Marchio Registrato e Metodologia**: METODO DEMARIA®  
**Contatti Ufficiali**: metodo.demaria@gmail.com | avv.alessandrodemaria@pec.it  

---

## 1. PREMESSA EPISTEMOLOGICA E CAMBIO DI PARADIGMA

La presente Release v3.3 (Audit-Master Unificato) del METODO DEMARIA® formalizza e consolida il cambio di paradigma epistemologico nello studio dei corpora simbolici storici non decifrati, con specifico riferimento al Manoscritto Voynich (Beinecke MS 408).

Rigettando l'ipotesi linguistico-fonetica tradizionale (Symbol-to-Sound / Symbol-to-Meaning), il METODO DEMARIA® formalizza il modello vettoriale e cibernetico (Symbol-to-Vector / Symbol-to-State): il corpus grafico costituisce un Instruction Set deterministico e calcolabile, concepito per la regolazione e il monitoraggio di uno spazio degli stati all'interno di un sistema temporizzato ad anello chiuso (Closed-Loop Timed Automaton).

---

## 2. RECAP BENCHMARK EMPIRICI FROZEN (RELEASE v3.3)

- **Corpus Analizzato**: 35.483 EVA tokens validati su 227 folii unici.
- **Coerenza Sintattica Grezza Reale Osservata (Craw)**: 0.786597 (78.66%).
- **Model 1 (Global Null Model - Monte Carlo N=10.000, Seed 42)**: Z-Score = +19.8404, p-value < 10^-15.
- **Model 2 (Intra-Folio Null Model - Monte Carlo N=10.000, Seed 42)**: Z-Score = +16.3961, p-value < 10^-15.
- **Model 3 (Intra-Line Null Model / Smoking Gun - Monte Carlo N=10.000, Seed 42)**: Z-Score = +14.5202, p-value < 10^-15 (Prova Regina).
- **Isomorphic Double Randomization Test**: Double Null Z-Score = +1.5239, p-value = 0.032000 (p < 0.05).
- **Stress Test di Sensibilità al Rumore Sintattico**: 97.35% di ritenzione del segnale al 10.0% di rumore sintattico inoculato (Craw' = 0.765738).
- **Holdout Stability (Out-of-Sample)**: Delta C inferiore al 2.59% (In-Sample +0.58%, Out-of-Sample -0.58%).

---

## 3. STRUTTURA DEL REPOSITORY DI LABORATORIO (13 FILE FROZEN)

### Codebase Python Vettorizzata Pure-Array (7 Moduli Integrati)
1. `core_parser1.py`: Parser deterministico dell'alfabeto EVA e mappatura biunivoca sulle regole della quadrupla degli stati minimi (Alpha: 10.00%, Beta: 54.99%, Delta: 19.51%, Gamma: 15.50%).
2. `core_matrix2.py`: Gestore C-native della Matrice Canonica 4x4 e calcolo della Coerenza Sintattica Grezza (Craw = 0.786597) su coordinata di rigo pergamenaceo.
3. `utils_preflight3.py`: Checker d'integrità crittografica SHA-256 e verifica di immutabilità del dataset master (`dec87e784290ad5b404bd5ed0110349a2f379c7fb386adb0bca2d7a4b1890999`).
4. `audit_nullmodels4.py`: Motore stocastico Monte Carlo per l'audit dei tre modelli nulli gerarchici (N=10.000, Seed 42).
5. `audit_doublerand5.py`: Test avversariale di doppia randomizzazione isomorfa (N=10.000, Seed 42).
6. `audit_robustness6.py`: Test di sensibilità e resilienza al rumore sintattico inoculato (0.0% -> 30.0%).
7. `batch_runner7.py`: Orchestratore Master unificato per la riesecuzione automatica dell'intera suite e l'esportazione dei report.

### Dataset e Report di Audit (3 File CSV)
- `voynich_eva_tokens_extended.csv`: Dataset Master di 35.483 EVA tokens (Hash SHA-256: `dec87e784290ad5b404bd5ed0110349a2f379c7fb386adb0bca2d7a4b1890999`).
- `audit_master_summary_results.csv`: Report sintetico congelato contenente i benchmark della Release v3.3.
- `robustness_test_results.csv`: Report analitico dei livelli di ritenzione della coerenza al rumore.

### Apparato Iconografico Scientifico (3 Tavole .png / .jpg a 300 DPI)
- `METODO DEMARIA Release v3.3 - Tavola 1 - Automa Temporizzato ad Anello Chiuso e Matrice 4.4 - Equazione Armonia.jpg`: Automa Temporizzato ad Anello Chiuso, Matrice Canonica 4x4 ed Equazione dell'Invariante di Armonia.
- `METODO DEMARIA Release v3.3 - Tavola 2 - Tipologia Rigo Pergamenaceo e Tripartizione Sintattica.png`: Topologia di Rigo Pergamenaceo e Tripartizione Sintattica (Smoking Gun).
- `METODO DEMARIA Release v3.3 - Tavola 3 - Diagnostica Computazionale e Benchmarking degli Audit Stocastici.png`: Diagnostica Computazionale, Z-Score dei Modelli Nulli e Curva di Resilienza al Rumore.

---

## 4. ESECUZIONE RAPIDA (QUICK START)

Per rieseguire l'intero audit e verificare in modo deterministico la baseline di laboratorio (Seed 42):

```bash
# Esecuzione dell'Orchestratore Master
python batch_runner7.py
```

---

## 5. NOTE LEGALI, PATERNITÀ E SEGRETO INDUSTRIALE (ART. 98 CPI)

1. **Diritto d'Autore (L. 633/1941)**: La struttura teorica del METODO DEMARIA®, i trattati scientifici, i dataset quantitativi, la codebase di laboratorio, il design del dispositivo analogico Volvelle e la formalizzazione dell'Invariante di Armonia costituiscono opera d'ingegno originale tutelata ai sensi della Legge 22 aprile 1941 n. 633 e delle Convenzioni Internazionali WIPO / Berna.
2. **Marchio Registrato (D.Lgs. 30/2005)**: La denominazione, il logo e la metodologia METODO DEMARIA® costituiscono marchio registrato ai sensi del D.Lgs. 10 febbraio 2005, n. 30 (Codice della Proprietà Industriale).
3. **Segreto Industriale (Art. 98 CPI)**: Gli algoritmi di simulazione avanzata, i motori commerciali backend, le matrici proprietarie dell'Invariante di Armonia (Phi_alpha) e la struttura analitica del motore di calcolo C* **rimangono coperti da Segreto Industriale ed esclusiva proprietà dell'Autore Avv. Alessandro Demaria (Art. 98 D.Lgs. 30/2005 - CPI)**. La messa a disposizione della presente suite risponde ai requisiti di trasparenza Open Science e riproducibilità popperiana, senza concedere alcuna licenza d'uso o di sfruttamento commerciale sulla codebase proprietaria e sul motore sottostante.

© METODO DEMARIA DEPOSITATO - Tutti i diritti riservati (L. 633/1941, D.Lgs. 30/2005, Art. 98 CPI).
