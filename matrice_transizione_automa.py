"""
METODO DEMARIA™ - Modulo di Decomposizione Spettrale (v3.1)
File: matrice_transizione_automa.py
Descrizione: Calcolo della Matrice di Transizione 4x4 sulla colonna EVA_Token,
             decomposizione spettrale e verifica di C* = 0.5557.
"""

import numpy as np
import pandas as pd

# Mappatura Grafemi EVA -> Stati Automa (\alpha, \beta, \delta, \gamma)
STATE_MAPPING = {
    'a': 0, 'o': 0, 'e': 0, 'y': 0, 'v': 0,       # Alpha (\alpha)
    'k': 1, 't': 1, 'p': 1, 'f': 1,             # Beta (\beta)
    'ch': 2, 'sh': 2, 'c': 2, 's': 2, 'd': 2,    # Delta (\delta)
    'i': 3, 'in': 3, 'r': 3, 'l': 3, 'm': 3      # Gamma (\gamma)
}

STATE_NAMES = ['Alpha (\u03b1)', 'Beta (\u03b2)', 'Delta (\u03b4)', 'Gamma (\u03b3)']

def map_token_to_state(token):
    token = str(token).lower()
    for key, state in STATE_MAPPING.items():
        if token.startswith(key) or key in token:
            return state
    return 0

def compute_spectral_analysis(df_tokens):
    # Selezione mirata della colonna EVA_Token
    if 'EVA_Token' in df_tokens.columns:
        token_col = 'EVA_Token'
    else:
        # Fallback ricerca case-insensitive
        cols_lower = {c.lower(): c for c in df_tokens.columns}
        token_col = cols_lower.get('eva_token', df_tokens.columns[0])

    states = df_tokens[token_col].apply(map_token_to_state).values
    lines = df_tokens['line_id'].values if 'line_id' in df_tokens.columns else np.zeros(len(states))

    N = np.zeros((4, 4), dtype=float)

    for i in range(len(states) - 1):
        if lines[i] == lines[i + 1]:
            src = states[i]
            dst = states[i + 1]
            N[src, dst] += 1.0

    row_sums = N.sum(axis=1, keepdims=True)
    P = np.divide(N, row_sums, out=np.zeros_like(N), where=row_sums != 0)

    eigenvalues, eigenvectors = np.linalg.eig(P.T)

    idx_pi = np.argmin(np.abs(eigenvalues - 1.0))
    pi = np.real(eigenvectors[:, idx_pi])
    pi = pi / np.sum(pi)

    sorted_evals = np.sort(np.real(eigenvalues))[::-1]
    lambda_2 = sorted_evals[1]

    c_star_computed = np.dot(pi, np.diag(P)) + (1.0 - lambda_2) / 2.0

    return P, pi, sorted_evals, c_star_computed, token_col

if __name__ == "__main__":
    print("=============================================================")
    print(" METODO DEMARIA™ - DECOMPOSIZIONE SPETTRALE DELL'AUTOMA")
    print("=============================================================")

    try:
        df = pd.read_csv("voynich_eva_tokens_extended.csv")
        print(f"[*] Dataset caricato con successo: {len(df)} righe.")
    except FileNotFoundError:
        print("[!] File 'voynich_eva_tokens_extended.csv' non trovato.")
        exit()

    P, pi, evals, c_star, col_used = compute_spectral_analysis(df)
    print(f"[*] Colonna analizzata: '{col_used}'")

    print("\n[1] MATRICE DI TRANSIZIONE P (4x4):")
    print(pd.DataFrame(P, index=STATE_NAMES, columns=['-> \u03b1', '-> \u03b2', '-> \u03b4', '-> \u03b3']).round(4))

    print("\n[2] VETTORE STAZIONARIO DEGLI STATI (\u03c0):")
    for name, val in zip(STATE_NAMES, pi):
        print(f"  * \u03c0_{name}: {val:.4f}")

    print("\n[3] SPETTRO DEGLI AUTOVALORI (\u03bb):")
    for i, lam in enumerate(evals, 1):
        print(f"  * \u03bb_{i}: {lam:.6f}")

    print(f"\n[4] RISULTATO FINALE:")
    print(f"  * Seconda Frequenza di Risonanza (\u03bb_2): {evals[1]:.6f}")
    print(f"  * Coerenza Coassiale Teorica (C*): {c_star:.4f}")
    print(f"  * Target di Riferimento Stazionario: 0.5557")
    print("=============================================================")