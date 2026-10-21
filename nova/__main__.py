"""Il programma: `uv run python -m nova [percorso]` smista un lotto e stampa il riepilogo."""

import sys
from pathlib import Path

from nova.archivio import leggi_lotto
from nova.smistamento import conteggi, smista

PERCORSO_PREDEFINITO = Path("dati") / "lotto.jsonl"


def main(argomenti: list[str]) -> int:
    """Smista il lotto indicato, o quello predefinito, e restituisce il codice di uscita."""
    percorso = Path(argomenti[0]) if argomenti else PERCORSO_PREDEFINITO
    try:
        lotto, rifiutate = leggi_lotto(percorso)
    except (OSError, ValueError) as errore:
        print(f"Lotto non leggibile. {errore}", file=sys.stderr)
        return 1

    smistate, duplicati = smista(lotto)
    for pratica in smistate:
        richiesta = pratica.richiesta
        print(f"{richiesta.tenant:<7} {richiesta.id:<6} {pratica.categoria:<14} {richiesta.oggetto}")
    print()
    print(
        f"Lette: {len(lotto) + len(rifiutate)}   Smistate: {len(smistate)}   "
        f"Duplicati scartati: {len(duplicati)}   Rifiutate: {len(rifiutate)}"
    )
    for nome, numero in conteggi(smistate).items():
        print(f"  {nome:<14} {numero}")
    for riga in rifiutate:
        print(f"{percorso}, riga {riga.numero}: {'; '.join(riga.ragioni)}", file=sys.stderr)
    return int(bool(rifiutate))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
