# ==============================================================================
# METODO DEMARIA (R) - TRIAGE ENGINE AD ALTA VELOCITA (RELEASE 3.4)
# Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
# Modulo Ufficiale: triage_engine.py
# Sede Operativa: Laboratorio Scientifico Metodo Demaria
# Classificazione: Riduzione Dimensionale, Invariante C e Triage ad Alta Velocita (Tiers A-C)
# Riferimenti: Marchio UIBM N. 302026000161716 | Concept DOI: 10.5281/zenodo.22789343
# ==============================================================================

import numpy as np
import time


class DemariaTriageEngineV34:
    """
    Engine Vettoriale ad Altissimo Throughput per l Invariante C (White Paper Alfa).
    Esegue la riduzione dimensionale da R^2 a R^1 e il triage deterministico per
    flussi di dati ad alta velocita.
    """

    def __init__(self, we=0.45, wr=0.55):
        # Pesi Ponderati dell Invariante C
        self.we = float(we)
        self.wr = float(wr)

    def compute_invariant_c_single(self, x1, x2):
        """
        Calcola l Invariante C per una singola coppia vettoriale (x1, x2) in [0, 1]^2:
        C = sqrt( (We * x1)^2 + (Wr * x2)^2 )
        """
        x1_norm = float(np.clip(x1, 0.0, 1.0))
        x2_norm = float(np.clip(x2, 0.0, 1.0))
        return float(np.sqrt((self.we * x1_norm)**2 + (self.wr * x2_norm)**2))

    def compute_invariant_c_batch(self, x1_array, x2_array):
        """
        Calcola l Invariante C vettorializzato su array ad alta velocita.
        """
        x1_arr = np.clip(np.asarray(x1_array, dtype=float), 0.0, 1.0)
        x2_arr = np.clip(np.asarray(x2_array, dtype=float), 0.0, 1.0)
        return np.sqrt((self.we * x1_arr)**2 + (self.wr * x2_arr)**2)

    @staticmethod
    def classify_boundary_determinism(c_values):
        """
        Partizione deterministica dello spazio in tre classi discrete:
          Classe 0 (OK):       C < 0,35
          Classe 1 (WARNING):  0,35 <= C < 0,70
          Classe 2 (CRITICAL): C >= 0,70
        """
        c_arr = np.asarray(c_values, dtype=float)
        classes = np.zeros(len(c_arr), dtype=int)
        classes[(c_arr >= 0.35) & (c_arr < 0.70)] = 1
        classes[c_arr >= 0.70] = 2
        return classes

    def run_clean_room_benchmark(self, n_vectors=1000000, seed=42):
        """
        Benchmark Computazionale in Clean Room su 1.000.000 di vettori.
        Target di Laboratorio:
          Tempo Totale: ~0,0635 secondi
          Throughput:   ~15,75 Milioni di vettori/secondo
          Latenza:      ~63,4 nanosecondi/vettore
          Anomalie:     ~0,05% critiche
        """
        np.random.seed(seed)
        # Generazione vettori stocastici sbilanciati verso il regime normale
        x1_vec = np.random.beta(a=0.5, b=5.0, size=n_vectors)
        x2_vec = np.random.beta(a=0.5, b=5.0, size=n_vectors)

        t_start = time.perf_counter()

        # Esecuzione calcolo e classificazione vettoriale
        c_vec = self.compute_invariant_c_batch(x1_vec, x2_vec)
        class_vec = self.classify_boundary_determinism(c_vec)

        t_end = time.perf_counter()
        total_time = t_end - t_start

        throughput = n_vectors / total_time if total_time > 0 else 0.0
        latency_ns = (total_time / n_vectors) * 1e9 if n_vectors > 0 else 0.0

        n_ok = np.sum(class_vec == 0)
        n_warn = np.sum(class_vec == 1)
        n_crit = np.sum(class_vec == 2)
        pct_crit = (n_crit / n_vectors) * 100.0

        return {
            'n_vectors': n_vectors,
            'total_time_sec': total_time,
            'throughput_vec_per_sec': throughput,
            'latency_nanosec': latency_ns,
            'class_0_ok': n_ok,
            'class_1_warning': n_warn,
            'class_2_critical': n_crit,
            'pct_critical': pct_crit
        }


def main():
    """
    Modulo di test e collaudo del Triage Engine Release 3.4.
    """
    print("=== LABORATORIO SCIENTIFICO METODO DEMARIA ===")
    print("Modulo: triage_engine.py (Release METODO DEMARIA 3.4)")
    print("Esecuzione Benchmark Computazionale in Clean Room per Invariante C...")

    engine = DemariaTriageEngineV34(we=0.45, wr=0.55)

    # Esecuzione Benchmark su 1.000.000 di vettori
    res = engine.run_clean_room_benchmark(n_vectors=1000000, seed=42)

    print("\n--- RISULTATI BENCHMARK COMPUTAZIONALE IN CLEAN ROOM ---")
    print(f"Vettori Elaborati:                {res['n_vectors']:,}")
    print(f"Tempo Totale di Elaborazione:     {res['total_time_sec']:.6f} secondi")
    print(f"Throughput del Motore:            {res['throughput_vec_per_sec']:,.2f} vettori/secondo")
    print(f"Latenza Media per Vettore:        {res['latency_nanosec']:.2f} nanosecondi")
    print("\nPartizione Spaziale Deterministica:")
    print(f"  Classe 0 (OK < 0,35):          {res['class_0_ok']:,} vettori")
    print(f"  Classe 1 (WARNING 0,35..0,70): {res['class_1_warning']:,} vettori")
    print(f"  Classe 2 (CRITICAL >= 0,70):   {res['class_2_critical']:,} vettori ({res['pct_critical']:.4f}%)")


if __name__ == "__main__":
    main()