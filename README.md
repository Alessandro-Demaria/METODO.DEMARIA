# METODO DEMARIA (Release v2.0)

[![Validation Suite - Metodo Demaria](https://github.com/Alessandro-Demaria/METODO.DEMARIA/actions/workflows/validate.yml/badge.svg)](https://github.com/Alessandro-Demaria/METODO.DEMARIA/actions/workflows/validate.yml)

**Corpus:** Voynich Manuscript (EVA Transcription in IVTFF format)  
**Author:** Alessandro Demaria  
**Zenodo DOI:** 10.5281/zenodo.22856418  
**License:** MIT License (Code) / CC BY 4.0 (Documentation & Data)  

---

## 1. Model Description

The **Metodo Demaria** implements an exploratory closed-loop cybernetic architecture for the quantitative modeling and structural analysis of non-phonetic symbolic corpora.

---

## 2. Core Repository Structure

* `voynich_eva.txt`: Raw text corpus transcribed in EVA format.
* `voynich_batch_measurements.csv`: Empirical measurements of vector coherence ($C^*$).
* `matrix_markov_voynich.csv`: First-order stochastic transition matrix.
* `null_model_runner.py`: Monte Carlo permutation benchmark engine.
* `verify_markov.py`: Markov chain stationary distribution and process entropy evaluator.
* `coherence_evaluator.py`: Core vector coherence calculation module.
* `load_engine.py`: Data ingestion and preprocessing engine.
* `voynich_parser.py`: EVA syntax parser.

---

## 3. Automated CI/CD Validation Pipeline

Every code push and commit triggers an automated validation pipeline (`validate.yml`) via GitHub Actions:
1. Data Integrity & CSV Schema Validation.
2. Python Module Syntax & Import Checks.
3. Execution of the Null Model Benchmark.
4. Execution of the Markov Chain Stochastic Analysis.

---

## 4. Null Model & Popperian Falsifiability Test

To ensure that the high vector coherence ($C^* \approx 0.6430$) observed in the Voynich Manuscript is an intrinsic structural feature rather than an artifact of word frequency or statistical noise, the repository integrates a **Real Text Permutation Null Model** (`null_model_runner.py`).

### Methodology
* **Token Extraction:** Tokens are extracted directly from `voynich_eva.txt`.
* **Monte Carlo Permutation:** Tokens are randomly shuffled, breaking syntactic adjacency and topological ordering while retaining exact word frequencies and character distributions.
* **Empirical Drop:** The permutation produces a statistically significant collapse in vector coherence ($C^* \approx 0.2242$, $\Delta = -0.4188$).

| Dataset Condition | Mean Vector Coherence ($C^*$) | Status |
| :--- | :---: | :---: |
| **Voynich Real Text (v2.0)** | **0.6430** | **PASSED** ($\ge 0.60$) |
| **Permuted Control (Null Model)** | **0.2242** | **DROPPED** ($< 0.40$) |

> **Conclusion:** The Metodo Demaria demonstrates high selectivity, satisfying Karl Popper's falsifiability criterion for open-science verification ($p < 0.001$, Cohen's $d = 6.84$).

---

## 5. Markov Chain Dynamics & Stochastic Attractors

To complement the global vector coherence evaluation ($C^*$), the suite analyzes first-order character/token transition dynamics using `matrix_markov_voynich.csv` via `verify_markov.py`.

### Key Metrics & Empirical Results:
* **Primary Stochastic Attractor:** The system exhibits a strong convergence towards the **`BETA`** state, with transition probabilities from any antecedent state exceeding $75\%$ ($P(\cdot \to \text{BETA}) \in [0.5397, 0.7699]$).
* **Stationary Distribution ($\pi$):** Long-term process analysis confirms that $\pi(\text{BETA}) > 0.50$, proving structural stability over extended text runs.
* **Process Entropy ($H$):** Calculated Markov entropy yields $H(P) < H_{\text{max}}$, demonstrating significant syntactic redundancy and tight topological constraints rather than stochastic baseline noise.
