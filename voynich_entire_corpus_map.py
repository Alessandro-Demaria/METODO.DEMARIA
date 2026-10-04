#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
METODO DEMARIA® — COMPUTATIONAL VOYNICH ANALYSIS FRAMEWORK (Release v3.0)
Modulo: voynich_entire_corpus_map.py (Mappatura Visuale Globale dell'Intero Corpus)
Autore: Avv. Alessandro Demaria
===============================================================================
"""

import csv
import os
import numpy as np
import matplotlib.pyplot as plt

CSV_FILE = 'voynich_eva_tokens_extended.csv'

def plot_entire_voynich_corpus(csv_filepath):
    if not os.path.exists(csv_filepath):
        print(f"[ERRORE CRITICO] File CSV '{csv_filepath}' non trovato.")
        return

    folio_stats = {}

    with open(csv_filepath, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_f = row.get('Folio', '').strip()
            base_f = raw_f.split('.')[0] if '.' in raw_f else raw_f
            
            if base_f:
                if base_f not in folio_stats:
                    folio_stats[base_f] = {'c_stars': [], 'phases': []}
                
                try:
                    c_star = float(row.get('C_star_t', 0.7542))
                    phase = float(row.get('Clock_Phase', 0.0))
                    folio_stats[base_f]['c_stars'].append(c_star)
                    folio_stats[base_f]['phases'].append(phase)
                except ValueError:
                    continue

    if not folio_stats:
        print("[ERRORE] Nessun dato estratto dal CSV.")
        return

    # Ordinamento naturale dei folii
    def folio_sort_key(fol_name):
        import re
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
            c_means.append(np.mean(c_list))
            token_counts.append(len(c_list))

    total_pages = len(names)
    total_tokens = sum(token_counts)

    # Rendering Dashboard Globale
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(20, 10), facecolor='#0e1117')
    
    x_indices = np.arange(total_pages)

    # Grafico 1: Traiettoria di Coerenza Sintattica su TUTTE le pagine
    ax1.set_facecolor('#161b22')
    ax1.plot(x_indices, c_means, color='#238636', alpha=0.5, linewidth=1.0)
    sc = ax1.scatter(x_indices, c_means, c=c_means, cmap='viridis', vmin=0.65, vmax=0.85, s=25, zorder=3)
    ax1.axhline(0.7542, color='#ff7b72', linestyle='--', linewidth=1.2, label='Baseline Globale (0.7542)')

    ax1.set_title(f"METODO DEMARIA® — MAPPATURA INTEGRALE DELL'INTERO MANOSCRITTO VOYNICH ({total_pages} FOLII | {total_tokens:,} TOKEN)\n"
                  f"Profilo Continuo di Coerenza Sintattica C*(t) da F1R a F102V", color='white', fontsize=13, fontweight='bold', pad=15)
    ax1.set_ylabel("Coerenza Medio C*", color='white', fontsize=11)
    ax1.tick_params(colors='white', labelsize=8)
    ax1.grid(color='#30363d', linestyle=':', linewidth=0.5)
    ax1.legend(facecolor='#161b22', edgecolor='none', labelcolor='white')

    # Riduzione delle etichette dell'asse X per pulizia visiva
    step = max(1, total_pages // 40)
    ax1.set_xticks(x_indices[::step])
    ax1.set_xticklabels(names[::step], rotation=90, color='white', fontsize=8)

    # Grafico 2: Istogramma Densità Token per Oggetto/Pagina
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
    output_filename = "voynich_entire_corpus_master_map.png"
    plt.savefig(output_filename, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
    
    print("="*75)
    print(f" -> MAPPATURA TOTALE COMPLETATA!")
    print(f" -> PAGINE/FOLII PROCESSI:  {total_pages}")
    print(f" -> TOKEN TOTALI MAPPATI:    {total_tokens:,}")
    print(f" -> GRAFICO GENERATO:        '{output_filename}'")
    print("="*75)
    
    plt.show()

if __name__ == "__main__":
    plot_entire_voynich_corpus(CSV_FILE)