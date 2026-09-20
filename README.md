[![Validation Suite](https://github.com/Alessandro-Demaria/METODO.DEMARIA/actions/workflows/validate.yml/badge.svg)](https://github.com/Alessandro-Demaria/METODO.DEMARIA/actions/workflows/validate.yml)
# METODO DEMARIA (Release v2.0)

**Corpus**: Voynich Manuscript (EVA Transcription in IVTFF format)
**Author**: Alessandro Demaria
**Zenodo DOI**: 10.5281/zenodo.22856418
**License**: MIT License (Code) / CC BY 4.0 (Documentation & Data)

---

## 1. Model Description

The **Metodo Demaria** implements an exploratory closed-loop cybernetic architecture for the quantitative modeling and structural analysis of non-phonetic symbolic corpora.

### Operating Model Parameters
* **Nominal Clock Frequency ($\omega_0$)**: $0.0416 \text{ Hz}$ (Input parameter)
* **Nominal Dwell Time ($T_0$)**: $\approx 24.0 \text{ seconds}$ (Derived model scale)
* **Coherence Threshold ($C^*$ Peak)**: $\ge 0.94$

> **Note on Methodology**: The nominal clock frequency ($\omega_0 = 0.0416 \text{ Hz}$) and dynamic load parameters ($Z$) are operational input values defined within the computational model to simulate topological constraint stability. They represent exploratory parameters rather than empirically extracted physical frequencies.

---

## 2. Mathematical Formulation

### Dynamic Load Index ($Z$)
The symbolic load index $Z$ evaluates positional, length, and prefix/suffix topological markers (such as `qo`, `qok`, `in`, `edy`) modulated across token sequences:

$$Z_i = f(\text{length}, \text{position}, \text{affixes}) \cdot \left[1.0 + 0.2 \cdot \sin(\omega_0 \cdot t_i)\right]$$

### Composite Coherence Metric ($C^*$)
Line-loop structural stability is quantified via the weighted composite coherence index:

$$C^* = 0.6 \cdot \left(\frac{Z_{\text{mean}}}{Z_{\text{max}}}\right) + 0.4 \cdot T_{\text{weight}}$$

Where $T_{\text{weight}}$ evaluates trigger-header compliance and closure-reset topology.

---

## 3. Pipeline & Reproducibility

The entire pipeline is open-source and fully automated.

### Environment Setup
```bash
python batch_runner.py
