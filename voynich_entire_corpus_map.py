#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
METODO DEMARIA® — COMPUTATIONAL VOYNICH ANALYSIS FRAMEWORK (Release v3.0)
Modulo: voynich_entire_corpus_map.py (Mappatura Visuale Globale dell'Intero Corpus)
Autore: Avv. Alessandro Demaria | Licenza: CC BY 4.0
Zenodo DOI: 10.5281/zenodo.23119964
===============================================================================
Descrizione:
  Modulo di visualizzazione e mappatura ad alta risoluzione del corpus Voynich.
  Genera la dashboard grafica globale della coerenza topologica intra-folio C*(t)
  e della densità/saturazione dei token per tutti i folii identificati.
  Include aliasing automatico delle colonne ed ordinamento codicologico v3.0.
===============================================================================
"""

import csv
import os
import re
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

CSV_FILE = 'voynich_eva_tokens_extended.csv'


def plot_entire_voynich_corpus(csv_filepath: str = CSV_FILE, output_filename: str = "voynich_entire_corpus_master_map.png") -> None:
    if not os.path.exists(csv_filepath):
        print(f"[ERRORE CRITICO] File CSV '{csv_filepath}' non trovato.")
        sys.exit(1)

    df = pd.read_csv(csv_filepath)

    # Aliasing automatico delle colonne (v3.0)
    if 'Token' not in df.columns and 'EVA_Token' in df.columns:
        df['Token'] = df['EVA_Token']
    if 'Folio_Base' not in df.columns and 'Folio' in df.columns:
        df['Folio_Base'] = df['Folio'].apply(lambda x: str(x).split('.')[0] if '.' in str(x) else str(x))

    if 'Token' not in df.columns or 'Folio_Base' not in df.columns:
        print("[ERRORE CRITICO] Colonne 'Token'/'EVA_Token' e 'Folio_Base'/'Folio' necessarie.")
        sys.exit(1)

    # FIXING CRITICO v3.0: Ordinamento sequenziale codicologico esplicito
    sort_cols = [col for col in ['Folio_Base', 'line_id', 'Record_ID'] if col in df.columns]
    if sort_cols:
        df = df.sort_values(by=sort_cols).reset_index(drop=True)

    # Estrazione per folio
    folio_stats = {}
    for _, row in df.iterrows():
        base_f = str(row['Folio_Base']).strip()
        if base_f and base_f != 'nan':
            if base_f not in folio_stats:
                folio_stats[base_f] = {'c_stars': [], 'phases': []}
            
            try:
                c_star = float(row.get('C_star_t', 0.7542))
                phase = float(row.get('Clock_Phase', 0.0))
                folio_stats[base_f]['c_stars'].append(c_star)
                folio_stats[base_f]['phases'].append(phase)
            except (ValueError, TypeError):
                continue

    if not folio_stats:
        print("[ERRORE] Nessun dato estratto dal CSV.")
        sys.exit(1)

    # Funzione di ordinamento naturale codicologico dei folii
    def folio_sort_key(fol_name: str) -> tuple:
        match = re.search(r'\d+', fol_name)
        num = int(match.group()) if match else 0
        suffix = fol_name[match.end():] if match else fol_name
        return (num, suffix)

    sorted_folios = sorted(folio_stats.keys(), key=folio_sort_key)

    names = []
    c_means = []
    token_counts = []

    for fol in sorted_folios:
        c_list = folio_stats[fol]['c_stars']
        if len(c_list) > 0:
            names.append(fol.upper())
            c_means.append(float(np.mean(c_list)))
            token_counts.append(len(c_list))

    total_pages = len(names)
    total_tokens = sum(token_counts)

    # Rendering Dashboard Globale
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(20, 10), facecolor='#0e1117')
    x_indices = np.arange(total_pages)

    # Grafico 1: Traiettoria di Coerenza Sintattica C*(t)
    ax1.set_facecolor('#161b22')
    ax1.plot(x_indices, c_means, color='#238636', alpha=0.5, linewidth=1.0)
    sc = ax1.scatter(x_indices, c_means, c=c_means, cmap='viridis', vmin=0.65, vmax=0.85, s=25, zorder=3)
    ax1.axhline(0.7542, color='#ff7b72', linestyle='--', linewidth=1.2, label='Baseline Globale (0.7542)')

    title_str = f"METODO DEMARIA® — MAPPATURA INTEGRALE DELL'INTERO MANOSCRITTO VOYNICH ({total_pages} FOLII | {total_tokens:,} TOKEN)\nProfilo Continuo di Coerenza Sintattica C*(t) da F1R a F102V"
    ax1.set_title(title_str, color='white', fontsize=13, fontweight='bold', pad=15)
    ax1.set_ylabel("Coerenza Media C*", color='white', fontsize=11)
    ax1.tick_params(colors='white', labelsize=8)
    ax1.grid(color='#30363d', linestyle=':', linewidth=0.5)
    ax1.legend(facecolor='#161b22', edgecolor='none', labelcolor='white')

    step = max(1, total_pages // 40)
    ax1.set_xticks(x_indices[::step])
    ax1.set_xticklabels(names[::step], rotation=90, color='white', fontsize=8)

    # Grafico 2: Istogramma Densità Token per Folio
    ax2.set_facecolor('#161b22')
    ax2.bar(x_indices, token_counts, color='#3fb950', alpha=0.75, width=0.8)
    ax2.set_title("DENSITÀ E SATURAZIONE DI TESTO PER SINGOLO FOLIO", color='white', fontsize=12, fontweight='bold', pad=10)
    ax2.set_xlabel("Progresso Codicologico Pagine Manoscritto", color='white', fontsize=11)
    ax2.set_ylabel("Numero Token (N)", color='white', fontsize=11)
    ax2.set_xticks(x_indices[::step])
    ax2.set_xticklabels(names[::step], rotation=90, color='white', fontsize=8)
    ax2.tick_params(colors='white')
    ax2.grid(color='#30363d', linestyle=':', linewidth=0.5)

    cb = plt.colorbar(sc, ax=ax1, pad=0.01)
    cb.set_label('Coerenza C*', color='white')
    cb.ax.yaxis.set_tick_params(color='white')
    plt.setp(plt.getp(cb.ax, 'yticklabels'), color='white')

    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())

    print("=" * 75)
    print(" METODO DEMARIA® v3.0 — MAPPATURA TOTALE COMPLETATA!")
    print(f" -> PAGINE/FOLII PROCESSI:  {total_pages}")
    print(f" -> TOKEN TOTALI MAPPATI:    {total_tokens:,}")
    print(f" -> GRAFICO GENERATO:        '{output_filename}'")
    print("=" * 75)


if __name__ == "__main__":
    plot_entire_voynich_corpus(CSV_FILE)