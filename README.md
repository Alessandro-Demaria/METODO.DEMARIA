# METODO DEMARIA™ Release v3.2 (Audit-Master-Optimum)

[![Validation Suite - Metodo Demaria](https://github.com/Alessandro-Demaria/METODO.DEMARIA/actions/workflows/validate.yml/badge.svg)](https://github.com/Alessandro-Demaria/METODO.DEMARIA/actions/workflows/validate.yml)
[![Zenodo DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23236183.svg)](https://doi.org/10.5281/zenodo.23236183)
[![Concept DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22789343.svg)](https://doi.org/10.5281/zenodo.22789343)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

* **Corpus**: Voynich Manuscript (Beinecke MS 408) – EVA Transcription in IVTFF format
* **Author, Scientific Director, and Sole Inventor**: Avv. Alessandro Demaria
* **Registered Trademark & Methodology**: METODO DEMARIA™
* **Standard**: Standard Demaria v3.2 (Ottobre 2026)
* **Source Document**: [METODO DEMARIA™ Release v3.2 (Audit-Master-Optimum).pdf](./METODO%20DEMARIA™%20Release%20v3.2%20(Audit-Master-Optimum).pdf)
* **Zenodo DOI (Official Release v3.2)**: [10.5281/zenodo.23236183](https://doi.org/10.5281/zenodo.23236183)
* **Concept DOI (Permanent Archive)**: [10.5281/zenodo.22789343](https://doi.org/10.5281/zenodo.22789343)
* **License**: CC BY 4.0 (Documentation & Data) / Trade Secret (Hardware & Proprietary Backend Engine C*)
* **Official Contacts**: metodo.demaria@gmail.com | avv.alessandrodemaria@pec.it

### Release v3.2 Updates
* **Audit-Master Metric Consolidation ($C_{obs} = 0.714583$)**: Misurazione quantitativa della Coerenza Sintattica Grezza osservata reale pari al 71,46% su 35.483 token EVA e 227 folii.
* **Hierarchical Null Models Suite ($Z_{Global} = -8.1676, Z_{Line} = -7.5066$)**: Dimostrazione dei vincoli di transizione globale e di rigo tramite permutazione Monte Carlo ($N = 10.000$, Seed 42, $p = 1.000000$).
* **Fixed-Corpus Matrix Sweep Test ($Z = +0.7823$)**: Validazione avversariale su $N = 10.000$ simulazioni ($p = 0.232077$) attestante la stretta e specifica selettività dell'accoppiamento tra la matrice canonica 4x4 e il corpus reale.
* **Uniform State Replacement Robustness Test ($94.01\%$)**: Straordinaria stabilità e resilienza del sensore cibernetico al $10\%$ di perturbazione sintattica discreta.
* **Audit-Master Frozen Cryptographic Hashes**: Sigillo crittografico Master ZIP (`adc04fdfbaeaef650877b8b9f84e1e486c730599e8a6abffa903979f7f0dc06e`) e Master Dataset (`dec87e784290ad5b404bd5ed0110349a2f379c7fb386adb0bca2d7a4b1890999`).

### Architettura a 7 Moduli Core (Master Dataset: voynich_eva_tokens_extended.csv – 35.483 Tokens)

1. **1_voynich_parser.py**: Parsing, filtraggio e normalizzazione del testo EVA/IVTFF con tracciamento esplicito della Composite_Line_Key e re-indexing codicologico.
2. **2_null_model_test.py**: Generazione e computazione dei Modelli Nulli Gerarchici Monte Carlo ($N = 10.000$, Global, Intra-Folio, Intra-Line).
3. **3_double_randomization_test.py**: Esecuzione della suite dei test avversariali isomorfi e Fixed-Corpus Matrix Sweep su $10.000$ simulazioni a doppia permutazione.
4. **4_robustness_stress_test.py**: Valutazione della resilienza e della tenuta del sensore al rumore sintattico discreto tramite Uniform State Replacement ($0\%-30\%$).
5. **5_train_test_split_validation.py**: Validazione di stabilità spaziale Holdout e Sensitivity Analysis su 227 folii canonici ($N = 1.000$ MC).
6. **6_generate_charts.py**: Generazione deterministica delle rappresentazioni grafiche ad alta risoluzione per i report dell'audit suite.
7. **7_batch_runner.py**: Orchestratore sequenziale e runner batch unico v3.2 per l'esecuzione automatizzata dell'intera suite di audit master.

© METODO DEMARIA™ DEPOSITATO - Tutti i diritti riservati.