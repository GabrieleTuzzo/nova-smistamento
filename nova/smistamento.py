"""Lo smistamento di un lotto: deduplica, regola, conteggi. Non legge file e non stampa."""

from nova.regole import categoria, normalizza_oggetto

CATEGORIE = ("da_completare", "da_rivedere", "ordinaria")


def chiave_pratica(richiesta: dict) -> tuple[str, str]:
    """L'identità di una pratica: l'organizzazione e l'identificativo, insieme."""
    return (richiesta["tenant"], richiesta["id"])


def smista(lotto: list[dict]) -> tuple[list[dict], list[tuple[str, str]]]:
    """Restituisce le pratiche smistate, nella loro prima occorrenza, e le chiavi dei duplicati.

    Il lotto ricevuto non viene modificato: ogni pratica smistata è una copia.
    """
    visti = set()
    smistate = []
    duplicati = []
    for richiesta in lotto:
        chiave = chiave_pratica(richiesta)
        if chiave in visti:
            duplicati.append(chiave)
            continue
        visti.add(chiave)
        pulita = richiesta.copy()
        pulita["oggetto"] = normalizza_oggetto(richiesta["oggetto"])
        pulita["categoria"] = categoria(pulita["importo_centesimi"], pulita["documenti"])
        smistate.append(pulita)
    return smistate, duplicati


def conteggi(smistate: list[dict]) -> dict[str, int]:
    """Quante pratiche per categoria, con tutte le categorie presenti, anche a zero."""
    risultato = {}
    for nome in CATEGORIE:
        risultato[nome] = 0
    for pratica in smistate:
        risultato[pratica["categoria"]] += 1
    return risultato