# METODO DEMARIA (Release v2.0)

**Corpus**: Voynich Manuscript (EVA Transcription in IVTFF format)  
**Author**: Alessandro Demaria  
**Zenodo DOI**: [10.5281/zenodo.22856418](https://doi.org/10.5281/zenodo.22856418)  
**License**: MIT License  

---

## 1. Model Description
The **Metodo De Maria** implements a closed-loop cybernetic architecture for the modeling and analysis of non-phonetic symbolic corpora.

### Nominal Input Operating Parameters
- **Nominal Clock Frequency ($\omega_0$)**: $0.0416 \text{ Hz}$
- **Nominal Dwell Time ($T_0$)**: $\approx 24.0 \text{ seconds}$

*Note*: The clock and dwell time values represent input operating parameters of the `LoadEngine` cybernetic engine and do not represent empirically extracted measurements or frequencies from the text.

---

## 2. Coherence Metric $C^*$
The cybernetic stability of each line-loop is evaluated using the **Weighted Composite Index of Load Stability and Topological Compliance ($C^*$)**:

$$C^* = 0.6 \cdot \left(\frac{Z_{\text{mean}}}{Z_{\text{max}}}\right) + 0.4 \cdot T_{\text{weight}}$$

Where:
- $Z_{\text{mean}}$ and $Z_{\text{max}}$ represent dimensionless dynamic load indices.
- $T_{\text{weight}}$ evaluates the presence of topological markers for Trigger (Header) and Closure (Reset).

---

## 3. Contextualization of Empirical Results (100% Batch)
Automated analysis conducted on **5,612 lines** of the corpus (`voynich_batch_measurements.csv` dataset) demonstrates the following stability profile:

- **Corpus Baseline Mean Coherence**: $C^*_{\text{mean}} \approx 0.6451$
- **Load Distribution**: Minimum $\approx 0.2612$, Maximum $1.0000$.
- **Strict Peak Threshold ($C^* \ge 0.94$)**: 16 lines ($0.38\%$).

### Academic & Scientific Interpretation
The acceptance threshold $C^* \ge 0.94$ identifies segments of **maximum cybernetic constraint and peak coherence**. The composite index $C^*$, devoid of artificial offsets, serves as a falsifiable metric documenting the true structural and topological variability across the entire Voynich manuscript.

---

## 4. Repository Structure & Reproducibility
Executing `python batch_runner.py` completely regenerates the output dataset from the source artifacts.

- `voynich_eva.txt`: Transcribed corpus of the Voynich Manuscript.
- `voynich_parser.py`: Token extraction and processing module per folio/line.
- `load_engine.py`: Calculation engine for the dimensionless load profile $Z$.
- `coherence_evaluator.py`: Evaluator for the composite index $C^*$.
- `batch_runner.py`: Full batch scanning orchestrator.
- `voynich_batch_measurements.csv`: Generated measurement dataset.
