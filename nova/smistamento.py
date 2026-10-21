"""Lo smistamento: deduplica, regola, conteggi. Lavora su richieste già validate e non stampa."""

from collections.abc import Iterable

from nova.modelli import PraticaSmistata, Richiesta
from nova.regole import categoria

CATEGORIE = ("da_completare", "da_rivedere", "ordinaria")


def smista(lotto: Iterable[Richiesta]) -> tuple[list[PraticaSmistata], list[tuple[str, str]]]:
    """Restituisce le pratiche smistate, nella loro prima occorrenza, e le chiavi dei duplicati."""
    visti: set[tuple[str, str]] = set()
    smistate: list[PraticaSmistata] = []
    duplicati: list[tuple[str, str]] = []
    for richiesta in lotto:
        chiave = richiesta.chiave()
        if chiave in visti:
            duplicati.append(chiave)
            continue
        visti.add(chiave)
        smistate.append(PraticaSmistata(richiesta, categoria(richiesta.importo_centesimi, richiesta.documenti)))
    return smistate, duplicati


def conteggi(smistate: Iterable[PraticaSmistata]) -> dict[str, int]:
    """Quante pratiche per categoria, con tutte le categorie presenti, anche a zero."""
    risultato = {nome: 0 for nome in CATEGORIE}
    for pratica in smistate:
        risultato[pratica.categoria] += 1
    return risultato