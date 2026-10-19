"""La lettura del lotto dal file JSON che esporta il gestionale."""

import json
from pathlib import Path

from nova.regole import leggi_centesimi


def leggi_lotto(percorso: Path) -> list[dict]:
    """Legge il lotto e converte ogni importo in centesimi interi.

    Il gestionale esporta l'importo come testo, e un importo non compilato come "".
    Un file che non è JSON valido, o una richiesta con un importo illeggibile, fermano la
    lettura con un ValueError che dice dove guardare: il lotto si corregge, non si indovina.
    """
    testo = percorso.read_text(encoding="utf-8")
    try:
        righe = json.loads(testo)
    except json.JSONDecodeError as errore:
        raise ValueError(f"{percorso}: JSON non valido alla riga {errore.lineno}, colonna {errore.colno}") from errore

    lotto = []
    for posizione, riga in enumerate(righe, start=1):
        richiesta = riga.copy()
        try:
            richiesta["importo_centesimi"] = leggi_centesimi(riga["importo_centesimi"])
        except ValueError as errore:
            raise ValueError(
                f"{percorso}: richiesta n. {posizione} ({riga['id']}), importo non valido {riga['importo_centesimi']!r}"
            ) from errore
        lotto.append(richiesta)
    return lotto