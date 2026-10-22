"""Il servizio HTTP: riceve una richiesta alla volta, la valida, la smista e la registra."""

import secrets
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel

from nova.impostazioni import Impostazioni
from nova.modelli import PraticaSmistata, Richiesta
from nova.regole import categoria
from nova.smistamento import conteggi


class PraticaRegistrata(BaseModel):
    """La risposta del servizio: chi è la pratica, e in quale categoria è finita."""

    tenant: str
    id: str
    oggetto: str
    categoria: str


@asynccontextmanager
async def ciclo_di_vita(app: FastAPI) -> AsyncIterator[None]:
    """Prima dello yield si prepara il servizio, dopo lo yield si rilascia quello che ha preso."""
    app.state.impostazioni = Impostazioni()
    app.state.registro = {}
    yield
    app.state.registro.clear()


app = FastAPI(title="Smistamento Nova", lifespan=ciclo_di_vita)


def registro(request: Request) -> dict[tuple[str, str], PraticaSmistata]:
    """Il registro delle pratiche ricevute, creato all'avvio del servizio."""
    valore: dict[tuple[str, str], PraticaSmistata] = request.app.state.registro
    return valore


def verifica_chiave(request: Request, chiave: str | None) -> None:
    """Rifiuta con 401 una richiesta senza la chiave del servizio, o con una chiave sbagliata."""
    attesa = request.app.state.impostazioni.chiave_servizio.get_secret_value()
    if chiave is None or not secrets.compare_digest(chiave, attesa):
        raise HTTPException(status_code=401, detail="chiave del servizio mancante o non valida")


def risposta(pratica: PraticaSmistata) -> PraticaRegistrata:
    r = pratica.richiesta
    return PraticaRegistrata(tenant=r.tenant, id=r.id, oggetto=r.oggetto, categoria=pratica.categoria)


@app.get("/health")
async def salute(request: Request) -> dict[str, str | int]:
    """Dice che il servizio è vivo e quante pratiche ha registrato."""
    return {"stato": "ok", "pratiche": len(registro(request))}


@app.post("/pratiche", status_code=201)
async def registra(
    richiesta: Richiesta,
    request: Request,
    x_chiave_servizio: str | None = Header(default=None),
) -> PraticaRegistrata:
    """Smista e registra una richiesta. La stessa pratica non si registra due volte."""
    verifica_chiave(request, x_chiave_servizio)
    pratiche = registro(request)
    chiave = richiesta.chiave()
    if chiave in pratiche:
        raise HTTPException(status_code=409, detail=f"pratica {richiesta.tenant}/{richiesta.id} già registrata")
    pratica = PraticaSmistata(richiesta, categoria(richiesta.importo_centesimi, richiesta.documenti))
    pratiche[chiave] = pratica
    return risposta(pratica)


@app.get("/pratiche/{tenant}/{id_pratica}")
async def leggi(
    tenant: str,
    id_pratica: str,
    request: Request,
    x_chiave_servizio: str | None = Header(default=None),
) -> PraticaRegistrata:
    """Restituisce una pratica registrata, o 404 se il servizio non la conosce."""
    verifica_chiave(request, x_chiave_servizio)
    pratica = registro(request).get((tenant, id_pratica))
    if pratica is None:
        raise HTTPException(status_code=404, detail=f"pratica {tenant}/{id_pratica} non registrata")
    return risposta(pratica)


@app.get("/riepilogo")
async def riepilogo(request: Request, x_chiave_servizio: str | None = Header(default=None)) -> dict[str, int]:
    """Quante pratiche registrate per categoria."""
    verifica_chiave(request, x_chiave_servizio)
    return conteggi(registro(request).values())