# METODO DEMARIA™ (Release v3.2 – Audit-Master)

[![Validation Suite - Metodo Demaria](https://github.com/Alessandro-Demaria/METODO.DEMARIA/actions/workflows/validate.yml/badge.svg)](https://github.com/Alessandro-Demaria/METODO.DEMARIA/actions/workflows/validate.yml)
[![Zenodo DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23199718.svg)](https://doi.org/10.5281/zenodo.23199718)
[![Concept DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22789343.svg)](https://doi.org/10.5281/zenodo.22789343)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

* **Corpus**: Voynich Manuscript (Beinecke MS 408) – EVA Transcription in IVTFF format
* **Author, Scientific Director, and Sole Inventor**: Avv. Alessandro Demaria
* **Registered Trademark & Methodology**: METODO DEMARIA™
* **Standard**: Standard Demaria v3.2 (Ottobre 2026)
* **Source Document**: [METODO DEMARIA Release v3.2 Audit Master.pdf](./METODO_DEMARIA_Release_v3.2_Audit_Master.pdf)
* **Zenodo DOI (Official Release v3.2)**: [10.5281/zenodo.23199718](https://doi.org/10.5281/zenodo.23199718)
* **Concept DOI (Permanent Archive)**: [10.5281/zenodo.22789343](https://doi.org/10.5281/zenodo.22789343)
* **License**: CC BY 4.0 (Documentation & Data) / Trade Secret (Hardware & Proprietary Backend Engine C*)
* **Official Contacts**: metodo.demaria@gmail.com | avv.alessandrodemaria@pec.it

### Release v3.2 Updates
* **Audit-Master Metric Consolidation ($C_{raw} = 0,685281$)**: Misurazione quantitativa della Coerenza Sintattica Grezza osservata reale pari al 68,53% su 35.483 token EVA e 227 folii.
* **Model 3 Intra-Line Null Test ($Z_{Line} = +4,3958$)**: Dimostrazione del vincolo sintattico di rigo tramite permutazione locale Monte Carlo ($N = 10.000$, Seed 42, $p < 0,000001$).
* **Isomorphic Double Randomization Test ($Z = -0,7961$)**: Validazione avversariale su $N = 10.000$ simulazioni ($p = 0,664300$) attestante la perfetta e specifica selettività dell'accoppiamento topologico.
* **Resilience & Noise Stress Test ($94,85\%$)**: Straordinaria stabilità del sensore cibernetico al $10\%$ di rumore sintattico di trascrizione.
* **Audit-Master Frozen Cryptographic Hashes**: Sigillo crittografico Master ZIP (`adc04fdfbaeaef650877b8b9f84e1e486c730599e8a6abffa903979f7f0dc06e`) e Master Dataset (`dec87e784290ad5b404bd5ed0110349a2f379c7fb386adb0bca2d7a4b1890999`).

### Architettura a 7 Moduli Core (Master Dataset: voynich_eva_tokens_extended.csv – 35.483 Tokens)

1. **voynich_parser.py**: Parsing, filtraggio e normalizzazione del testo EVA/IVTFF con tracciamento esplicito del line_id e re-indexing codicologico.
2. **batch_runner.py**: Orchestratore sequenziale e runner batch unico v3.2 per l'esecuzione automatizzata delle metriche di audit.
3. **null_model_test.py**: Generazione e computazione dei Modelli Nulli Gerarchici Monte Carlo ($N = 10.000$, Global, Intra-Folio, Intra-Line).
4. **double_randomization_test.py**: Esecuzione del test avversariale isomorfo su $10.000$ simulazioni a doppia permutazione.
5. **robustness_stress_test.py**: Valutazione della resilienza e della tenuta del sensore al rumore sintattico di trascrizione ($0\%-30\%$).
6. **generate_charts.py**: Generazione deterministica delle rappresentazioni grafiche ad alta risoluzione per i report dell'audit suite.
7. **seal_archive.py**: Calcolo e verifica automatica delle impronte crittografiche SHA-256 e del manifesto di sigillo del pacchetto.

© METODO DEMARIA™ DEPOSITATO - Tutti i diritti riservati.