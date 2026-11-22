# METODO DEMARIA® Release 3.5 (Edizione Scientifica Pura e Non Circolare)

[![Validation Suite - Metodo Demaria](https://github.com/Alessandro-Demaria/METODO.DEMARIA/actions/workflows/validate.yml/badge.svg?branch=main&cache_bust=35)](https://github.com/Alessandro-Demaria/METODO.DEMARIA/actions/workflows/validate.yml) [![DOI Concept Madre](https://zenodo.org/badge/DOI/10.5281/zenodo.22789343.svg)](https://doi.org/10.5281/zenodo.22789343) [![DOI Release 3.5](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.24444677-blue.svg)](https://doi.org/10.5281/zenodo.24444677) [![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/) [![IP: Art. 98 CPI](https://img.shields.io/badge/IP-Art.%2098%20CPI%20%7C%20UIBM%20302026000161716-red.svg)](https://doi.org/10.5281/zenodo.24444677)

## Blind Mathematical, Information-Theoretic, and Stochastic Analysis of Line-Positional Polarization in the Voynich Manuscript (Beinecke MS 408)

Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria (Molochio, RC)  
Affiliazione: Laboratorio Scientifico Metodo Demaria  
Concept DOI Madre (Archivio Permanente): [10.5281/zenodo.22789343](https://doi.org/10.5281/zenodo.22789343)  
DOI Ufficiale Release 3.5: [10.5281/zenodo.24444677](https://doi.org/10.5281/zenodo.24444677)  
Impronta Crittografica Dataset Master (35.483 Token EVA SHA-256): `dec87e784290ad5b404bd5ed0110349a2f379c7fb386adb0bca2d7a4b1890999`  
Impronta Crittografica Pacchetto Codebase e Audit Sigillato (SHA-256): `2ccfb2a24512d60e5d5383484c403a5260d01a7c4a7f97aee26d7db0fccdaf6d`  
Licenza del Trattato e dei Dati: Creative Commons Attribution 4.0 International (CC BY 4.0)  
Licenza Suite Dimostrativa Pubblica: Suite Dimostrativa Aperta Non Circolare (7 Moduli Python)  
Privativa Industriale e Segreto Algoritmi: Art. 98 D.Lgs. 30/2005 (Codice della Proprieta Industriale)  
Marchio Registrato e Metodologia: METODO DEMARIA® (Numero UIBM 302026000161716)  
Contatti Ufficiali: metodo.demaria@gmail.com | avv.alessandrodemaria@pec.it

---

## 1. PREMESSA EPISTEMOLOGICA E PERIMETRO NON CIRCOLARE (RELEASE 3.5)

La presente **Release 3.5 (Edizione Scientifica Pura e Non Circolare — Trattato Unificato Bilingue e Appendici A, B, C)** del METODO DEMARIA formalizza l'analisi matematica, topologica, informazionale e stocastica cieca dell'automa temporizzato discreto ad anello chiuso rilevato sul corpus traslitterato del Manoscritto Voynich (**Beinecke MS 408**, Yale University).

Per eliminare alla radice ogni possibile obiezione di circolarità metodologica tra regole morfologiche prefissate e matrici di transizione, l'intera pipeline della Release 3.5 adotta esclusivamente l'operatore agnostico cieco `transduce_universal_agnostic` (implementato in `demaria_parser.py`), privo di qualunque dizionario o regola lessicale specifica sul Voynich. L'operatore estrae automaticamente dal flusso stesso i **4 prefissi bigrammatici più frequenti** e i **4 suffissi bigrammatici più frequenti** (su parole di lunghezza almeno 3 caratteri), ripartendo in modo deterministico i `35.483` token EVA nei quattro stati base ancorati allo Stato Zero `S0 = 0` (Alur & Dill, 1994):

* **Stato 1 (Prefissi bigrammatici frequenti auto-estratti):** `6.726` token (`18,96%`)
* **Stato 2 (Nucleo ordinario di regime interno):** `8.997` token (`25,36%`)
* **Stato 3 (Forme lunghe a bassa frequenza, percentile >= 75 e occorrenze <= 3):** `2.059` token (`5,80%`)
* **Stato 4 (Suffissi bigrammatici frequenti auto-estratti):** `17.701` token (`49,89%`)

---

## 2. RIEPILOGO DEI BENCHMARK EMPIRICI CONSOLIDATI (RELEASE 3.5)

* **Corpus Analizzato:** `35.483` token EVA autenticati distribuiti su `227` folii fisici e `5.385` righi per complessive `30.098` transizioni intra-rigo analizzate (`SHA-256: dec87e784290ad5b404bd5ed0110349a2f379c7fb386adb0bca2d7a4b1890999`).
* **Matrice Canonica di Ammissibilita Direzionale M4 (4x4):** `12` celle ammesse e `4` transizioni proibite tassative (Densità strutturale esatta `D = 75,00%`), con divieto assoluto di ritorno dallo Stato Base (`Stato 2`) e dallo Stato Raro (`Stato 3`) allo Stato Prefisso (`Stato 1`).
* **Teorema 1 — Coerenza Sintattica Cieca Modello M4 (`N = 10.000` permutazioni gerarchiche intra-rigo, `seed = 42`):** `C4 = 0,819390` (`24.662 / 30.098` transizioni ammesse contro media nulla `mu0 = 0,811326`, scarto `Delta C4 = +0,008064`, `Z4 = +5,6216`, `p = 0,00010`, effect size bernoulliano `d4 = 0,0210`).
* **Teorema 1 Esteso — Modello Posizionale Esteso M6 (`6x6` stati):** `C6 = 0,914047` (`27.511 / 30.098` transizioni ammesse contro media nulla `mu0 = 0,907485`, scarto `Delta C6 = +0,006562`, `Z6 = +5,6924`, `p = 0,00010`, effect size bernoulliano `d6 = 0,0234`), con **Selettivita Intrinseca di Bordo Rigo** pari a `Sel = 0,3406` (`Pa = 0,1913` in apertura di rigo; `Pg = 0,4851` in chiusura di rigo).
* **Teorema 2 — Regime Entropico Condizionato e Chiusura Ciclica:** Entropia dinamica di stato `H_state = 1,695579 bit`; divergenza ciclica di Kullback-Leibler tra i primi `5.000` e gli ultimi `5.000` token pari a `D_KL = 0,106761 bit`; entropia unigrammatica di carattere `H1_char = 3,897455 bit/carattere`; entropia condizionata del primo ordine `H(c_{t+1} | c_t) = 2,191530 bit/carattere`, sensibilmente inferiore al regime tipico delle lingue naturali europee (`2,80 - 3,40 bit/carattere`).
* **Teorema 3 — Mutazioni Incrementali Adiacenti Intra-Rigo:** Su `30.098` coppie consecutive intra-rigo, `1.292` coppie (`4,29%`) presentano distanza di editing di Levenshtein `<= 1` carattere contro `1.181,47` attese dalla permutazione intra-rigo (`Z = +3,9908`, `p < 0,0001`).
* **Teorema 4 — Segregazione Morfologica Non Parametrica tra Sezioni Codicologiche:** Tabella di contingenza `5x8` tra le `5` sezioni codicologiche principali (Folii `1-66`, `67-73`, `75-84`, `88-102`, `103-116`) e gli `8` bigrammi iniziali più frequenti con `Chi-quadrato = 1.451,64` su `28` gradi di libertà (`p < 10^-280`).
* **Validazione Holdout Out-of-Sample (`Split 80/20` su `227` folii):** `C_train = 0,810525` vs `C_test = 0,849750` (`gap = 4,84%`), escludendo fenomeni di overfitting.
* **Noise Stress Test (Iniezione del `10%` di rumore uniforme casuale):** Ritenzione netta del segnale pari al `98,8484%`.
* **Falsificabilita Popperiana sui Tre Controlli Nulli Matematici Puri (`seed = 42`):** Sotto il criterio congiunto `(Z4 > 4,5 AND Z6 > 4,5 AND Sel > 0,30)`, il **Beinecke MS 408 Reale** è l'unica serie validata (`VALIDATO`), a fronte del rigetto integrale dei tre controlli nulli stocastici puri:
  1. **Manoscritto Voynich (Beinecke MS 408 Reale):** `C4 = 0,819390` | `Z4 = +5,6216` | `C6 = 0,914047` | `Z6 = +5,6924` | `Sel = 0,3406` -> **VALIDATO**
  2. **Controllo Nullo A (Flusso i.i.d. con Stessa Marginale `p`):** `C4 = 0,811017` | `Z4 = +0,3390` | `C6 = 0,908864` | `Z6 = -0,4019` | `Sel = 0,3489` -> **RIGETTATO**
  3. **Controllo Nullo B (Catena di Markov Stazionaria 1 Ordine):** `C4 = 0,821749` | `Z4 = +6,1627` | `C6 = 0,914745` | `Z6 = +2,7219` | `Sel = 0,3528` -> **RIGETTATO (`Z6 < 4,5`)**
  4. **Controllo Nullo C (Sequenza Uniforme Equidistribuita):** `C4 = 0,748222` | `Z4 = -1,8430` | `C6 = 0,820785` | `Z6 = -1,0505` | `Sel = 0,2492` -> **RIGETTATO**
* **Motore Invariante C per Triage Deterministico (`DICE`):** Kernel vettorizzato in singola precisione `float32` (`c = 0,5824 * x1 + 0,4176 * x2`) con throughput validato a `259,85 MVS` su `1.000.000` di vettori uniformi e coda critica empirica (`0,0475%`) allineata alla probabilità analitica esatta `(1 - t2)^2 / (2 * w1 * w2) = 0,04994%`.
* **Approfondimenti delle Appendici A, B e C:**
  * *Appendice A (Sotto-corpus balneologico Capitolo 3, `1.135` token, `117` righi):* `C4 = 0,8381`, `Z = +2,8904`, `p = 0,0019`.
  * *Appendice B (Metriche estrattive su MS 408):* `5.385` righi, lunghezza media `6,59` token/rigo, mutazioni unitarie `dL = 1` pari a `4,29%` (`1.292` coppie intra-rigo), `Delta H_rigo = -0,000039 bit` (stazionarietà informazionale intra-rigo), `Delta H_first = +0,166089 bit` (incremento entropico al primo token di rigo) e `52,05%` dei righi terminanti in Stato 4 (`Suffix`).
  * *Appendice C (Continuità vettoriale black-box `C*_t`):* `R^2 = 0,928571`, `Z = +4,0825`, `p < 0,0001`.
* **Presidio Crittografico SHA-256 e Catena di Custodia:** Master Dataset `35.483` Token EVA (`Hash SHA-256: dec87e784290ad5b404bd5ed0110349a2f379c7fb386adb0bca2d7a4b1890999`); Pacchetto Codebase e Audit Sigillato (`Hash SHA-256: 2ccfb2a24512d60e5d5383484c403a5260d01a7c4a7f97aee26d7db0fccdaf6d`).

---

### Suite Dimostrativa Aperta Non Circolare (7 Moduli Python)

1. `main_runner_voynich.py`: Orchestratore principale di verifica end-to-end, controllo integrità crittografica SHA-256 del dataset master, esecuzione parallela Monte Carlo (`M4` e `M6`), benchmark kernel `DICE` e tabella di falsificabilità popperiana.
2. `demaria_parser.py`: Parser vettoriale agnostico cieco (`transduce_universal_agnostic`), trasduttore posizionale `M6` (`6x6`), calcolo della coerenza sintattica, metriche entropiche di Shannon e Kullback-Leibler, selettività intrinseca di bordo rigo, distanza di editing di Levenshtein intra-rigo, test Chi-quadrato codicologico ed estrattore vettoriale `Demaria Core Evo 6D`.
3. `demaria_montecarlo.py`: Motore stocastico gerarchico intra-rigo (`N = 10.000` permutazioni bloccate per rigo fisico, `seed = 42`) per `M4` e `M6` e calcolo dell'effect size bernoulliano `d` di Cohen.
4. `demaria_triage_c.py`: Demaria Invariant C Engine (`DICE`) ad alte prestazioni in singola precisione `float32` per il triage deterministico (Classe 0, Classe 1, Classe 2), verifica dello Stato Zero Copertina (`S0`) e calcolo della coda critica analitica.
5. `demaria_validation.py`: Suite di validazione scientifica out-of-sample (`Holdout Split 80/20` sui `227` folii), `Noise Stress Test` al `10%` di rumore uniforme casuale e doppia randomizzazione isomorfa.
6. `demaria_cross_corpus.py`: Modulo comparativo per la generazione riproducibile (`seed = 42`) e valutazione sotto criterio congiunto dei tre controlli nulli matematici puri (`Controllo Nullo A` i.i.d., `Controllo Nullo B` Markov 1 ordine, `Controllo Nullo C` uniforme).
7. `demaria_api.py`: Microservizio REST FastAPI ad alte prestazioni con endpoint di health-check (`/api/v1/health`), audit completo (`/api/v1/audit/full-run`) e triage binario zero-copy (`/api/v1/triage/binary`, `application/octet-stream`).

### Dataset Master e Documentazione Ufficiale (Fascicoli Bilingue Italiano / Inglese)

* `voynich_eva_tokens_extended.csv`: Dataset Master di `35.483` token EVA autenticati (`Impronta Crittografica SHA-256: dec87e784290ad5b404bd5ed0110349a2f379c7fb386adb0bca2d7a4b1890999`).
* `METODO DEMARIA VERSIONE 3.5.pdf`: Trattato Unificato Canonico Bilingue — Edizione Scientifica Pura e Non Circolare (Italiano pp. 1–7 / Inglese pp. 8–15).
* `METODO DEMARIA Versione 3.5 - Appendice A Bilingue.pdf`: Documento Autonomo Appendice A — Analisi Sezionale Capitolo 3 (Folii `f75r–f84v`).
* `METODO DEMARIA Versione 3.5 - Appendice B Bilingue.pdf`: Documento Autonomo Appendice B — Metriche Estrattive su MS 408 e Mutazioni Unitarie `dL = 1`.
* `METODO DEMARIA Versione 3.5 - Appendice C Bilingue.pdf`: Documento Autonomo Appendice C — Teorema C.1 di Continuità Vettoriale `C*_t` e Falsificazione Black-Box.
---

## 4. ESECUZIONE RAPIDA (QUICK START)

Installazione delle dipendenze scientifiche richieste (`Python 3.10+`):

```bash
pip install numpy pandas fastapi uvicorn
```

Esecuzione dell'orchestratore principale per rieseguire l'intero audit matematico, entropico e stocastico della Release 3.5 (`seed = 42`, `N = 10.000` iterazioni reali):

```bash
python main_runner_voynich.py
```

Avvio del server API FastAPI per l'esposizione degli endpoint di audit e triage binario zero-copy:

```bash
python demaria_api.py
```

Metriche attese di validazione empirica deterministica:
* **Coerenza Sintattica Cieca M4 (`C4`):** `0,819390` (`24.662 / 30.098`, `Z4 = +5,6216`, `p = 0,00010`, `d4 = 0,0210`)
* **Coerenza Posizionale Cieca M6 (`C6`):** `0,914047` (`27.511 / 30.098`, `Z6 = +5,6924`, `p = 0,00010`, `d6 = 0,0234`, `Sel = 0,3406`)
* **DICE Kernel Throughput (`float32`):** `~259,85 MVS` su `1.000.000` di vettori (`coda critica empirica 0,0475%` vs `analitica 0,04994%`)

---

## 5. NOTE LEGALI, PATERNITA SCIENTIFICA E SEGRETO INDUSTRIALE (ART. 98 CPI)

1. **Paternita Scientifica, Diritti d'Invenzione e Fondazione della Codenetica:** L'architettura teorica, la formalizzazione algebrica, la dimostrazione del Teorema e Modello M1 di Demaria, l'identificazione della struttura sintattica ad anello chiuso del Manoscritto Voynich (Beinecke MS 408), l'operatore geometrico di soglia aurea `kappa_D = phi / 2 = cos(36 gradi) = 0,809017`, l'invenzione dell'Algoritmo del Computus Magnus, la formulazione dell'Equazione dell'Invariante di Armonia di Alessandro Demaria `Phi_alpha`, la scoperta del Master Clock a `0,0416 Hz` (`60 BPM`), la modellizzazione cibernetica bidirezionale della Volvelle a `24` settori da `15,0` gradi, delle quattro finestre frazionarie (`1/4`, `1/8`, `1/12`, `1/24`), della Griglia Parallela Ortogonale `4x4` su assi a `90,0` gradi e dei commutatori rotanti di fase angolare `Delta_theta_k`, la trasduzione sonoro-frequenziale calibrata sulla triade di LA Maggiore a `60 BPM`, il parser agnostico non circolare `transduce_universal_agnostic`, i modelli di transizione intra-rigo `M4` ed `M6`, la formulazione dell'Invariante C (`DICE`) e del `Demaria Core Evo 6D`, la fondazione della Cibernetica Codicologica (`Codenetica`) e l'intera suite software di calcolo costituiscono opere dell'ingegno originali, scoperte scientifiche ed invenzioni computazionali esclusive dell'Autore **Avv. Alessandro Demaria**, tutelate ai sensi della Legge 22 aprile 1941 n. 633, delle Convenzioni Internazionali WIPO / Berna e della normativa brevettuale.

2. **Marchio Registrato (D.Lgs. 30/2005):** La denominazione, il logo e la metodologia **METODO DEMARIA** costituiscono marchio d'impresa registrato ai sensi del D.Lgs. 10 febbraio 2005, n. 30 (Codice della Proprietà Industriale) con registrazione ufficiale **Marchio UIBM Numero 302026000161716**.

3. **Tutela del Segreto Industriale (Art. 98 CPI):** Gli algoritmi analitici completi del Demaria Core, le matrici proprietarie dell'Invariante di Armonia `Phi_alpha`, i pesi multi-dimensionali di calibrazione (`alfa`, `beta`, `gamma`) del `Demaria Core Evo 6D`, la dimostrazione integrale del Teorema M1, la struttura proprietaria interna dell'Invariante C (`DICE`) e la codebase backend avanzata rimangono rigorosamente coperti da Segreto Industriale ed esclusiva proprietà dell'Autore Avv. Alessandro Demaria (**Art. 98 D.Lgs. 30/2005 - CPI**) a presidio delle domande di brevetto UIBM ed internazionali connesse al Concept DOI Madre `10.5281/zenodo.22789343`. La messa a disposizione della suite dimostrativa risponde ai requisiti di trasparenza Open Science e riproducibilità popperiana, con obbligo formale di citazione dell'Autore, del Marchio UIBM e dei DOI ufficiali, senza concedere alcuna licenza d'uso o di sfruttamento commerciale sulla tecnologia proprietaria.

4. **Perimetro Epistemologico Autonomo e Rinvio alle Appendici A, B e C:** Il Trattato Unificato Canonico formalizza e dimostra esclusivamente i teoremi matematici, entropici e stocastici non circolari interamente riproducibili sul Beinecke MS 408. Gli approfondimenti monografici sul sotto-corpus balneologico (`Appendice A`), sulle metriche estrattive di rigo (`Appendice B`) e sulla continuità vettoriale black-box (`Appendice C`) sono raccolti in fascicoli autonomi allegati al medesimo deposito Zenodo (`DOI Specifico Release 3.5: 10.5281/zenodo.24444677`).

© METODO DEMARIA DEPOSITATO — Tutti i diritti riservati (L. 633/1941, D.Lgs. 30/2005, Art. 98 CPI, Marchio UIBM N. 302026000161716)  
Concept DOI Madre: [https://doi.org/10.5281/zenodo.22789343](https://doi.org/10.5281/zenodo.22789343)  
DOI Ufficiale Release 3.5: [https://doi.org/10.5281/zenodo.24444677](https://doi.org/10.5281/zenodo.24444677)  
Presidio SHA-256 Master Dataset: `dec87e784290ad5b404bd5ed0110349a2f379c7fb386adb0bca2d7a4b1890999`  
Presidio SHA-256 Codebase & Audit Sigillato: `2ccfb2a24512d60e5d5383484c403a5260d01a7c4a7f97aee26d7db0fccdaf6d`
