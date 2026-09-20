# METODO DEMARIA (Release v2.0)

[![Validation Suite - Metodo Demaria](https://github.com/Alessandro-Demaria/METODO.DEMARIA/actions/workflows/validate.yml/badge.svg)](https://github.com/Alessandro-Demaria/METODO.DEMARIA/actions/workflows/validate.yml)

**Corpus:** Voynich Manuscript (EVA Transcription in IVTFF format)  
**Author:** Alessandro Demaria  
**Zenodo DOI:** 10.5281/zenodo.22856418  
**License:** MIT License (Code) / CC BY 4.0 (Documentation & Data)

---

## 1. Model Description

The **Metodo Demaria** implements an exploratory closed-loop cybernetic architecture for the quantitative modeling and structural analysis of non-phonetic symbolic corpora.

### Operating Model Parameters
* **Target Corpus:** Voynich Manuscript (`voynich_eva.txt`)
* **Core Metric:** Vectorial Coherence Index ($C^*$)
* **Threshold Criteria:** $C^* \ge 0.60$ for structural stability

---

## 2. Repository Structure

* `load_engine.py`: Primary data extraction and pre-processing pipeline.
* `coherence_evaluator.py`: Mathematical module for $C^*$ vector calculations.
* `batch_runner.py`: Execution runner for full corpus evaluation.
* `null_model_runner.py`: **Popperian Falsifiability Test Suite** (Monte Carlo Permutation Model).
* `voynich_batch_measurements.csv`: Empirical output dataset (5,612 sequence samples).

---

## 3. Automated CI/CD Validation Pipeline

Every code push and commit triggers an automated validation pipeline (`validate.yml`) via GitHub Actions:
1. Data Integrity & CSV Schema Validation.
2. Python Module Syntax & Import Checks.
3. Execution of the Null Model Benchmark.

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

> **Conclusion:** The Metodo Demaria demonstrates high selectivity, satisfying Karl Popper's falsifiability criterion for open-science verification.
