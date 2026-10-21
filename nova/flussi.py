"""La lettura progressiva di un file JSONL: una riga alla volta, senza caricare tutto in memoria."""

import json
from collections.abc import Generator
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RigaJSONL:
    """Una riga JSONL letta, oppure il motivo per cui non si è potuta decodificare."""

    numero: int
    valore: Any | None = None
    errore: str | None = None


def leggi_jsonl(percorso: Path) -> Generator[RigaJSONL, None, None]:
    """Produce, per ogni riga non vuota, il suo numero e il valore JSON che contiene.

    Una riga che non è JSON valido produce un errore per quella riga e la lettura continua. Il file
    resta aperto finché il generatore è sospeso, e si chiude quando il generatore finisce o viene chiuso.
    """
    with percorso.open(encoding="utf-8") as file:
        for numero, linea in enumerate(file, start=1):
            if not linea.strip():
                continue
            try:
                valore = json.loads(linea)
            except json.JSONDecodeError:
                yield RigaJSONL(numero, errore="JSON non valido")
                continue
            yield RigaJSONL(numero, valore=valore)
