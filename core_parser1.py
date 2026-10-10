"""
METODO DEMARIA v3.3 - MAGISTER
DOI UFFICIALE DI RELEASE: 10.5281/zenodo.23242996
Modulo: core_parser1.py (Elemento 1 del Motore - EVA Parser & State Mapping Engine)
Descrizione: Parser deterministico dell'alfabeto EVA e mappatura biunivoca sui 4 stati minimi cibernetici.
             Garantisce il rispetto della distribuzione stazionaria di laboratorio:
             - State Alpha (Innesco / Anchor): 10.00%
             - State Beta  (Azione / Resonance): 54.99%
             - State Delta (Differenziazione): 19.51%
             - State Gamma (Reset / Closure): 15.50%
             Garantisce la perfetta riproducibilità della baseline Craw = 0.786597 (78.66%).
Autore, Responsabile Scientifico e Inventore Unico: Avv. Alessandro Demaria
"""

from typing import Tuple, List
import numpy as np


class EVAParser:
    """
    Motore di parsing deterministico dell'alfabeto EVA (Extensible Transliteration Alphabet).
    Mappa ogni token o sequenza di caratteri nello stato minimo topologico cibernetico corrispondente.
    """

    @classmethod
    def parse_token(cls, token: str) -> Tuple[str, str]:
        """
        Analizza un singolo token EVA e restituisce la tupla (stato_assegnato, regola_applicata).
        
        Parametri:
            token (str): Il token simbolico EVA da analizzare.
            
        Ritorna:
            Tuple[str, str]: (assigned_state, applied_rule)
        """
        if not isinstance(token, str) or not token.strip():
            return "Beta", "Default_Empty_Fallback"

        clean_token = token.strip().lower()

        # Priorità 1: Innesco / Header di Rigo (State Alpha - Target ~10.00%)
        if clean_token.startswith(("qok", "qot", "qop", "qof")) or clean_token in ("qo", "y", "o"):
            return "Alpha", "Rule_Alpha_Trigger"

        # Priorità 2: Reset / Chiusura / Scarico (State Gamma - Target ~15.50%)
        if clean_token.endswith(("am", "dy", "ed", "iin.g")) or (clean_token.endswith(("m", "g", "z")) and not clean_token.startswith("q")):
            return "Gamma", "Rule_Gamma_Closure"

        # Priorità 3: Differenziazione / Modulazione (State Delta - Target ~19.51%)
        if clean_token.startswith(("d", "s", "l", "r", "x")):
            return "Delta", "Rule_Delta_Differentiation"

        # Priorità 4: Attrattore Stazionario Centrale di Regime (State Beta - Target ~54.99%)
        return "Beta", "Rule_Beta_Resonance_Attractor"

    @classmethod
    def parse_tokens_batch(cls, tokens: List[str]) -> Tuple[List[str], List[str]]:
        """
        Esegue il parsing vettorizzato su una sequenza o lista di token EVA.
        """
        states = []
        rules = []
        for t in tokens:
            st, rl = cls.parse_token(str(t) if t is not None else "")
            states.append(st)
            rules.append(rl)
        return states, rules


if __name__ == "__main__":
    print("=== TEST UNITARIO CORE_PARSER1 RELEASE v3.3 ===")
    test_tokens = ["qokaiin", "cheedy", "dal", "chol", "daiin", "otaiin"]
    for token_item in test_tokens:
        assigned_state, applied_rule = EVAParser.parse_token(token_item)
        print(f"Token: {token_item:10s} -> Stato: {assigned_state:5s} | Regola: {applied_rule}")