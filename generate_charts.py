"""
===============================================================================
METODO DEMARIA® / METODO DEMARIA™ — SUITE DI GENERAZIONE GRAFICI AUDIT v3.2
===============================================================================
Modulo: generate_charts.py
Autore: Avv. Alessandro Demaria | Licenza: CC BY 4.0
===============================================================================
"""

import os
import matplotlib.pyplot as plt
import numpy as np

# Configurazione dello stile grafico accademico
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial']
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['axes.linewidth'] = 1.0

def plot_null_models():
    """1. Grafico Z-Scores dei Modelli Nulli Gerarchici (Fase 1)"""
    models = ['Global Null\n(Model 1)', 'Intra-Folio Null\n(Model 2)', 'Intra-Line Null\n(Model 3)']
    z_scores = [4.3541, 1.1882, 4.3958]
    colors = ['#1f77b4', '#7f7f7f', '#d62728']

    plt.figure(figsize=(9, 5.5), dpi=300)
    bars = plt.bar(models, z_scores, color=colors, width=0.55, edgecolor='black', linewidth=1)
    
    # Linea di soglia di significatività statistica (Z = +1.96, p = 0.05)
    plt.axhline(y=1.96, color='orange', linestyle='--', linewidth=1.5, label='Soglia di Significatività (Z = +1.96, p = 0.05)')
    plt.axhline(y=0, color='black', linewidth=0.8)

    # Etichette sui valori
    for bar, z in zip(bars, z_scores):
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.12, f'Z = +{z:.4f}', 
                 ha='center', va='bottom', fontsize=11, fontweight='bold')

    plt.title('METODO DEMARIA™ (v3.2) — Significatività Statistica Modelli Nulli (Fase 1)', fontsize=13, fontweight='bold', pad=15)
    plt.ylabel('Z-Score (Deviazioni Standard dalla Media Nulla)', fontsize=11)
    plt.ylim(0, 5.2)
    plt.grid(axis='y', linestyle=':', alpha=0.6)
    plt.legend(loc='upper right', frameon=True)
    plt.tight_layout()
    
    filename = 'chart_1_null_models_zscores.png'
    plt.savefig(filename, dpi=300)
    plt.close()
    print(f"[+] Grafico 1 salvato: {filename}")

def plot_robustness_curve():
    """2. Grafico Curva di Resilienza al Rumore (Fase 3)"""
    noise_levels = [0.0, 1.0, 5.0, 10.0, 20.0, 30.0]
    retention_rates = [100.00, 99.46, 97.37, 94.85, 90.30, 86.20]
    c_raw_values = [0.685281, 0.681574, 0.667276, 0.650001, 0.618813, 0.590724]

    fig, ax1 = plt.subplots(figsize=(9, 5.5), dpi=300)

    # Asse Principale: Ritenzione Coerenza (%)
    color = '#2ca02c'
    ax1.set_xlabel('Livello di Rumore Iniettato nel Corpus (%)', fontsize=11, labelpad=10)
    ax1.set_ylabel('Ritenzione della Coerenza Sintattica (%)', color=color, fontsize=11, fontweight='bold')
    line1 = ax1.plot(noise_levels, retention_rates, marker='o', linewidth=2.5, color=color, markersize=7, label='Ritenzione Coerenza (%)')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.set_ylim(80, 102)

    # Annotazione punto critico 10% rumore
    ax1.annotate('94.85% Ritenzione\n(10% Rumore)', xy=(10, 94.85), xytext=(12, 91),
                 arrowprops=dict(facecolor='black', shrink=0.08, width=1, headwidth=6),
                 fontsize=10, fontweight='bold', bbox=dict(boxstyle="round,pad=0.3", fc="yellow", ec="black", lw=1))

    # Asse Secondario: Valore C_raw
    ax2 = ax1.twinx()  
    color = '#1f77b4'
    ax2.set_ylabel('Coerenza Sintattica Osservata (C_raw)', color=color, fontsize=11, fontweight='bold')
    line2 = ax2.plot(noise_levels, c_raw_values, marker='s', linestyle='--', linewidth=2, color=color, markersize=6, label='C_raw Osservato')
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.set_ylim(0.50, 0.72)

    plt.title('METODO DEMARIA™ (v3.2) — Stress Test e Resilienza al Rumore (Fase 3)', fontsize=13, fontweight='bold', pad=15)
    ax1.grid(True, linestyle=':', alpha=0.6)
    fig.tight_layout()

    filename = 'chart_2_robustness_stress_test.png'
    plt.savefig(filename, dpi=300)
    plt.close()
    print(f"[+] Grafico 2 salvato: {filename}")

def plot_double_randomization():
    """3. Grafico Distribuzione Double Randomization Isomorfo (Fase 2)"""
    np.random.seed(42)
    # Simulazione della distribuzione normale dai parametri reali dell'Audit v3.2
    double_null_data = np.random.normal(loc=0.711419, scale=0.032831, size=10000)
    c_raw_real = 0.685281

    plt.figure(figsize=(9, 5.5), dpi=300)
    n, bins, patches = plt.hist(double_null_data, bins=50, color='#aec7e8', edgecolor='navy', alpha=0.7, density=True, label='Distribuzione Double Null (N=10.000)')

    # Linea del valore reale Voynich C_raw
    plt.axvline(x=c_raw_real, color='red', linestyle='-', linewidth=2.5, label=f'C_raw Voynich Reale ({c_raw_real:.6f})')
    plt.axvline(x=0.711419, color='black', linestyle='--', linewidth=1.5, label='Media Double Null (0.711419)')

    plt.title('METODO DEMARIA™ (v3.2) — Double Randomization Test Isomorfo (Fase 2)', fontsize=13, fontweight='bold', pad=15)
    plt.xlabel('Indice di Coerenza Sintattica Permutato', fontsize=11)
    plt.ylabel('Densità di Probabilità', fontsize=11)
    plt.legend(loc='upper right', frameon=True)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()

    filename = 'chart_3_double_randomization.png'
    plt.savefig(filename, dpi=300)
    plt.close()
    print(f"[+] Grafico 3 salvato: {filename}")

if __name__ == "__main__":
    print("=" * 75)
    print("METODO DEMARIA® — GENERAZIONE GRAFICI AD ALTA RISOLUZIONE (v3.2)")
    print("=" * 75 + "\n")
    plot_null_models()
    plot_robustness_curve()
    plot_double_randomization()
    print("\n[+] Tutti i 3 grafici ad alta risoluzione (300 DPI) sono stati generati con successo!")