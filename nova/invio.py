"""Il client: legge il lotto, toglie i duplicati che conosce e lo invia al servizio, più richieste insieme.

Si lancia con `uv run python -m nova.invio [percorso]`, con il servizio già in ascolto.
"""

import asyncio
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import httpx

from nova.archivio import leggi_lotto
from nova.impostazioni import Impostazioni
from nova.modelli import Richiesta
from nova.smistamento import smista

PERCORSO_PREDEFINITO = Path("dati") / "lotto.jsonl"


@dataclass(frozen=True)
class Esito:
    """Che cosa è successo a una richiesta inviata al servizio."""

    tenant: str
    id: str
    stato: str
    categoria: str | None
    dettaglio: str


async def invia_una(client: httpx.AsyncClient, richiesta: Richiesta, limite: asyncio.Semaphore) -> Esito:
    """Invia una richiesta e traduce le risposte attese in un esito; le altre risalgono come errori."""
    async with limite:
        try:
            risposta = await client.post("/pratiche", json=richiesta.model_dump())
        except httpx.TimeoutException:
            return Esito(richiesta.tenant, richiesta.id, "scaduta", None, "nessuna risposta entro il tempo massimo")
    if risposta.status_code == 201:
        return Esito(richiesta.tenant, richiesta.id, "smistata", risposta.json()["categoria"], "")
    if risposta.status_code == 409:
        return Esito(richiesta.tenant, richiesta.id, "duplicata", None, risposta.json()["detail"])
    if risposta.status_code == 422:
        return Esito(richiesta.tenant, richiesta.id, "rifiutata", None, "il servizio ha rifiutato i dati")
    risposta.raise_for_status()
    raise RuntimeError(f"risposta inattesa dal servizio: {risposta.status_code}")


async def invia_lotto(lotto: Sequence[Richiesta], client: httpx.AsyncClient, concorrenza: int) -> list[Esito]:
    """Invia tutto il lotto, al massimo `concorrenza` richieste insieme. Gli esiti seguono l'ordine del lotto."""
    limite = asyncio.Semaphore(concorrenza)
    async with asyncio.TaskGroup() as gruppo:
        compiti = [gruppo.create_task(invia_una(client, richiesta, limite)) for richiesta in lotto]
    return [compito.result() for compito in compiti]


async def invia(percorso: Path, impostazioni: Impostazioni) -> list[Esito]:
    """Legge il lotto, toglie i duplicati e lo invia con un client condiviso da tutte le richieste."""
    lotto, _ = leggi_lotto(percorso)
    smistate, _ = smista(lotto)
    unici = [pratica.richiesta for pratica in smistate]
    async with httpx.AsyncClient(
        base_url=impostazioni.url_servizio,
        timeout=impostazioni.timeout_secondi,
        headers={"X-Chiave-Servizio": impostazioni.chiave_servizio.get_secret_value()},
    ) as client:
        return await invia_lotto(unici, client, impostazioni.concorrenza_massima)


def main(argomenti: list[str]) -> int:
    """Invia il lotto indicato, o quello predefinito, e restituisce il codice di uscita."""
    percorso = Path(argomenti[0]) if argomenti else PERCORSO_PREDEFINITO
    try:
        esiti = asyncio.run(invia(percorso, Impostazioni()))
    except (FileNotFoundError, ValueError) as errore:
        print(f"Invio non partito. {errore}", file=sys.stderr)
        return 1
    except ExceptionGroup as gruppo:
        primo = gruppo.exceptions[0]
        print(f"Invio interrotto. {type(primo).__name__}: {primo}", file=sys.stderr)
        return 1

    for esito in esiti:
        print(f"{esito.tenant:<7} {esito.id:<6} {esito.stato:<10} {esito.categoria or esito.dettaglio}")
    print()
    for stato in ("smistata", "duplicata", "rifiutata", "scaduta"):
        print(f"  {stato:<10} {sum(1 for esito in esiti if esito.stato == stato)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))