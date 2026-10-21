"""La lettura progressiva di un file JSONL: una riga alla volta, senza caricare tutto in memoria."""

import json
from collections.abc import Generator
from pathlib import Path
from typing import Any


def leggi_jsonl(percorso: Path) -> Generator[tuple[int, Any], None, None]:
    """Produce, per ogni riga non vuota, il suo numero e il valore JSON che contiene.

    Una riga che non è JSON valido solleva ValueError con il suo numero nel momento in cui viene
    richiesta, non quando il generatore viene creato. Il file resta aperto finché il generatore
    è sospeso, e si chiude quando il generatore finisce o viene chiuso.
    """
    with percorso.open(encoding="utf-8") as file:
        for numero, linea in enumerate(file, start=1):
            if not linea.strip():
                continue
            try:
                valore = json.loads(linea)
            except json.JSONDecodeError as errore:
                raise ValueError(f"{percorso}, riga {numero}: JSON non valido") from errore
            yield numero, valore