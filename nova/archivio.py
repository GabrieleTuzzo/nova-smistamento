"""Il confine: dal file JSONL del gestionale alle richieste validate."""

from contextlib import closing
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from nova.flussi import leggi_jsonl
from nova.modelli import Richiesta
from nova.regole import leggi_centesimi, normalizza_oggetto


def adatta(riga: Any) -> Any:
    """Porta una riga del gestionale nella forma del modello, con due conversioni dichiarate.

    Il gestionale esporta l'importo come testo in centesimi, e l'oggetto così come è stato digitato:
    qui l'importo diventa un intero o None, e l'oggetto perde gli spazi esterni. Tutto il resto passa
    com'è, e lo giudica il modello.
    """
    if not isinstance(riga, dict):
        return riga
    adattata = dict(riga)
    if isinstance(riga.get("importo_centesimi"), str):
        adattata["importo_centesimi"] = leggi_centesimi(riga["importo_centesimi"])
    if isinstance(riga.get("oggetto"), str):
        adattata["oggetto"] = normalizza_oggetto(riga["oggetto"])
    return adattata


def descrivi(errore: ValidationError) -> str:
    """Il primo problema di una validazione, in una riga: il campo e che cosa non va."""
    primo = errore.errors()[0]
    campo = ".".join(str(parte) for parte in primo["loc"]) or "richiesta"
    return f"{campo}: {primo['msg']}"


def leggi_lotto(percorso: Path) -> list[Richiesta]:
    """Legge il lotto riga per riga, adatta e valida ogni richiesta.

    Si ferma alla prima riga che non è JSON valido, che ha un importo illeggibile o che il modello
    rifiuta, con un ValueError che dice quale riga e perché. Il lotto si valida tutto prima di
    essere smistato.
    """
    lotto = []
    with closing(leggi_jsonl(percorso)) as righe:
        for numero, riga in righe:
            dove = f"{percorso}, riga {numero}"
            try:
                richiesta = Richiesta.model_validate(adatta(riga))
            except ValidationError as errore:
                raise ValueError(f"{dove}: {descrivi(errore)}") from errore
            except ValueError as errore:
                raise ValueError(f"{dove}: importo non valido {riga.get('importo_centesimi')!r}") from errore
            lotto.append(richiesta)
    return lotto