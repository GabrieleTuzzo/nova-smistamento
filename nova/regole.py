"""La regola di smistamento e la lettura degli importi: funzioni senza file e senza stampe."""

SOGLIA_REVISIONE_CENTESIMI = 100000
DOCUMENTI_MINIMI = 2


def categoria(importo_centesimi: int | None, documenti: int) -> str:
    """Restituisce la categoria di una pratica secondo la regola di Nova.

    L'assenza dell'importo ha precedenza su tutto, e lo zero è un importo presente.
    """
    if importo_centesimi is None:
        return "da_completare"
    if importo_centesimi >= SOGLIA_REVISIONE_CENTESIMI or documenti < DOCUMENTI_MINIMI:
        return "da_rivedere"
    return "ordinaria"


def leggi_centesimi(testo: str) -> int | None:
    """Converte in centesimi interi l'importo che il gestionale esporta come testo.

    La stringa vuota è un importo non compilato e diventa None. Un testo che non è un
    intero, o un importo negativo, solleva ValueError: che cosa farne lo decide chi chiama.
    """
    if testo == "":
        return None
    valore = int(testo)
    if valore < 0:
        raise ValueError(f"l'importo non può essere negativo: {testo!r}")
    return valore


def normalizza_oggetto(testo: str) -> str:
    """Toglie gli spazi in testa e in coda: la forma con cui l'oggetto si conserva."""
    return testo.strip()