# METODO DEMARIA (Release v2.0)

[![Validation Suite - Metodo Demaria](https://github.com/Alessandro-Demaria/METODO.DEMARIA/actions/workflows/validate.yml/badge.svg?branch=main)](https://github.com/Alessandro-Demaria/METODO.DEMARIA/actions/workflows/validate.yml)

**Corpus:** Voynich Manuscript (EVA Transcription in IVTFF format)  
**Author:** Alessandro Demaria  
**Zenodo DOI:** 10.5281/zenodo.22856418  
**License:** MIT License (Code) / CC BY 4.0 (Documentation & Data)  

---

## 1. Executive Summary & Scope

The **Metodo Demaria** is an open-source computational framework designed for the quantitative structural characterization and falsifiable sequence analysis of non-phonetic or unmapped symbolic corpora. 

Rather than relying on speculative semantic interpretations, the framework evaluates sequence order through vector coherence invariants ($C^*$), Markov process dynamics, and true Monte Carlo token-permutation null models.

---

## 2. Core Methodological Components

1. **Vector Coherence ($C^*$ Index):** Maps discrete symbolic sequences into continuous metric space to evaluate adjacent state directional continuity.
2. **True Monte Carlo Null Model (`null_model_runner.py`):** Shuffles physical EVA token positions while preserving unigram frequencies, testing the null hypothesis of sequence independence through full pipeline re-execution.
3. **Markov Process & Attractor Verification (`verify_markov.py`):** Evaluates stochastic transition matrices, stationary distributions ($\pi$), process entropy $H(P)$, and system redundancy.

---

## 3. Repository Structure

* `coherence_evaluator.py`: Core algorithms for $C^*$ vector calculations.
* `null_model_runner.py`: True token-permutation Monte Carlo benchmark suite.
* `verify_markov.py`: Markov transition matrix and stochastic analysis tools.
* `voynich_parser.py`: Robust parser for EVA-encoded transcripts.
* `voynich_eva.txt`: Reference corpus data.
* `batch_runner.py`: Automation engine for batch processing.

---

## 4. Academic Position & Reproducibility

This repository provides a reproducible, open-science methodology for testing whether observed patterns in unmapped symbolic systems represent genuine sequential constraints or statistical artifacts. High-level interpretative models remain working hypotheses subject to external validation.

---

## Trademark Notice

`METODO DEMARIA™` è un marchio depositato. Tutti i diritti relativi al nome, al brand, ai software e alle metodologie associate sono riservati.
