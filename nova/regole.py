"""La regola di smistamento e la lettura degli importi: funzioni senza file e senza stampe."""

import re

SOGLIA_REVISIONE_CENTESIMI = 100000
DOCUMENTI_MINIMI = 2

_IMPORTO_EURO = re.compile(r"(?:€\s*)?([0-9]+|[0-9]{1,3}(?:\.[0-9]{3})+)(?:,([0-9]{1,2}))?")


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


def leggi_importo_euro(testo: str) -> int | None:
    """Converte un importo scritto in formato italiano in centesimi interi.

    Accetta punti per i gruppi delle migliaia, la virgola per i decimali e il simbolo
    euro iniziale facoltativo. La stringa vuota o composta da spazi diventa None.
    """
    testo = testo.strip()
    if testo == "":
        return None

    corrispondenza = _IMPORTO_EURO.fullmatch(testo)
    if corrispondenza is None:
        raise ValueError(f"importo in euro non valido: {testo!r}")

    euro = int(corrispondenza.group(1).replace(".", ""))
    decimali = (corrispondenza.group(2) or "").ljust(2, "0")
    return euro * 100 + int(decimali or "0")


def normalizza_oggetto(testo: str) -> str:
    """Toglie gli spazi in testa e in coda: la forma con cui l'oggetto si conserva."""
    return testo.strip()
