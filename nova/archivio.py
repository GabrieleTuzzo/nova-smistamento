"""Il confine: dal file JSONL del gestionale alle richieste validate."""

from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from nova.flussi import leggi_jsonl
from nova.modelli import Richiesta
from nova.regole import leggi_centesimi, normalizza_oggetto


@dataclass(frozen=True)
class RigaRifiutata:
    """Una riga del lotto rifiutata e tutti i motivi del rifiuto."""

    numero: int
    ragioni: tuple[str, ...]


def _adatta_con_errori(riga: Any) -> tuple[Any, list[str]]:
    if not isinstance(riga, dict):
        return riga, []
    adattata = dict(riga)
    ragioni = []
    if isinstance(riga.get("importo_centesimi"), str):
        try:
            adattata["importo_centesimi"] = leggi_centesimi(riga["importo_centesimi"])
        except ValueError:
            valore = riga["importo_centesimi"]
            ragioni.append(f"importo_centesimi: importo non valido {valore!r}")
            adattata["importo_centesimi"] = None
    if isinstance(riga.get("oggetto"), str):
        adattata["oggetto"] = normalizza_oggetto(riga["oggetto"])
    return adattata, ragioni


def adatta(riga: Any) -> Any:
    """Porta una riga del gestionale nella forma del modello, con due conversioni dichiarate.

    Il gestionale esporta l'importo come testo in centesimi, e l'oggetto così come è stato digitato:
    qui l'importo diventa un intero o None, e l'oggetto perde gli spazi esterni. Tutto il resto passa
    com'è, e lo giudica il modello.
    """
    adattata, ragioni = _adatta_con_errori(riga)
    if ragioni:
        raise ValueError(ragioni[0])
    return adattata


def descrivi(errore: ValidationError) -> list[str]:
    """Tutti i problemi di una validazione, ciascuno con il campo e che cosa non va."""
    ragioni = []
    for problema in errore.errors():
        campo = ".".join(str(parte) for parte in problema["loc"]) or "richiesta"
        ragioni.append(f"{campo}: {problema['msg']}")
    return ragioni


def leggi_lotto(percorso: Path) -> tuple[list[Richiesta], list[RigaRifiutata]]:
    """Legge il lotto riga per riga, adatta e valida ogni richiesta.

    Restituisce le richieste valide e tutte le righe rifiutate con i relativi motivi. Il lotto si
    valida tutto prima di essere smistato.
    """
    lotto = []
    rifiutate = []
    with closing(leggi_jsonl(percorso)) as righe:
        for riga in righe:
            if riga.errore is not None:
                rifiutate.append(RigaRifiutata(riga.numero, (riga.errore,)))
                continue

            adattata, ragioni = _adatta_con_errori(riga.valore)
            try:
                richiesta = Richiesta.model_validate(adattata)
            except ValidationError as errore:
                ragioni.extend(descrivi(errore))
            else:
                if not ragioni:
                    lotto.append(richiesta)
                    continue

            rifiutate.append(RigaRifiutata(riga.numero, tuple(ragioni)))
    return lotto, rifiutate
