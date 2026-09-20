import pandas as pd
import numpy as np
import math

def analyze_markov_matrix():
    print("=== METODO DEMARIA: MARKOV CHAIN & STOCHASTIC ANALYSIS ===")
    
    try:
        # 1. Caricamento della matrice di Markov
        df = pd.read_csv("matrix_markov_voynich.csv", index_col=0)
        states = list(df.columns)
        P = df.values # Matrice delle probabilita' di transizione
        
        print(f"[+] Stati identificati ({len(states)}): {states}")
        
        # 2. Verifica stocastica (la somma di ogni riga deve essere 1)
        row_sums = P.sum(axis=1)
        for i, state in enumerate(states):
            print(f"  - Somma riga {state}: {row_sums[i]:.4f}")
            assert math.isclose(row_sums[i], 1.0, abs_tol=1e-3), f"La riga {state} non e' stocastica!"
            
        # 3. Calcolo della Distribuzione Stazionaria (Eigenvector per eigenvalue = 1)
        eigenvalues, eigenvectors = np.linalg.eig(P.T)
        stationary_idx = np.argmin(np.abs(eigenvalues - 1.0))
        pi = np.real(eigenvectors[:, stationary_idx])
        pi = pi / np.sum(pi) # Normalizzazione
        
        print("\n--- DISTRIBUZIONE STAZIONARIA (Attraversamento a lungo termine) ---")
        for state, prob in zip(states, pi):
            print(f"[+] Probabilita' stazionaria pi({state}): {prob:.4f}")
            
        # 4. Calcolo Entropia del processo
        entropy_per_state = []
        for i in range(len(states)):
            h_i = 0.0
            for j in range(len(states)):
                p_ij = P[i, j]
                if p_ij > 0:
                    h_i -= p_ij * math.log2(p_ij)
            entropy_per_state.append(h_i)
            
        process_entropy = sum(pi[i] * entropy_per_state[i] for i in range(len(states)))
        max_entropy = math.log2(len(states)) # Entropia massima teorica per 4 stati = 2.0 bits
        
        print("\n--- ENTROPIA DI PROCESSO & RIDONDANZA ---")
        print(f"[+] Entropia di Markov H(P): {process_entropy:.4f} bits/simbolo")
        print(f"[+] Entropia Massima Teorica H_max: {max_entropy:.4f} bits/simbolo")
        print(f"[+] Ridondanza Sintattica R: {(1.0 - (process_entropy / max_entropy)) * 100:.2f}%")
        
        # Assert scientifici vincolanti
        assert pi[1] > 0.50, "FALLITO: BETA non e' l'attrattore stocastico principale!"
        assert process_entropy < max_entropy, "FALLITO: Il sistema e' equiprobabile (rumore casuale)!"
        
        print("====================================================")
        print("✅ ANALISI DI MARKOV E STRUTTURA STOCASTICA VALIDATE!")
        print("====================================================")
        
    except Exception as e:
        print(f"[-] Errore nell'analisi della matrice di Markov: {e}")
        raise e

if __name__ == "__main__":
    analyze_markov_matrix()
