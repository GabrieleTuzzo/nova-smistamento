import asyncio
import json

import httpx
import pytest

from nova.invio import invia_lotto
from nova.modelli import Richiesta


def richiesta(id_pratica, importo=12500):
    return Richiesta(id=id_pratica, tenant="nova", oggetto="x", importo_centesimi=importo, documenti=2)


def esegui(lotto, gestore, concorrenza=3):
    async def con_client():
        async with httpx.AsyncClient(transport=httpx.MockTransport(gestore), base_url="http://servizio") as client:
            return await invia_lotto(lotto, client, concorrenza)

    return asyncio.run(con_client())


def test_le_risposte_attese_diventano_esiti_nell_ordine_del_lotto():
    def gestore(request):
        id_pratica = json.loads(request.content)["id"]
        if id_pratica == "N-002":
            return httpx.Response(409, json={"detail": "pratica nova/N-002 già registrata"})
        if id_pratica == "N-003":
            return httpx.Response(422, json={"detail": []})
        if id_pratica == "N-004":
            raise httpx.ReadTimeout("nessuna risposta", request=request)
        return httpx.Response(201, json={"categoria": "ordinaria"})

    esiti = esegui([richiesta("N-001"), richiesta("N-002"), richiesta("N-003"), richiesta("N-004")], gestore)
    assert [e.stato for e in esiti] == ["smistata", "duplicata", "rifiutata", "scaduta"]
    assert esiti[0].categoria == "ordinaria"


def test_non_piu_di_tre_richieste_insieme():
    attive = 0
    massimo = 0

    async def gestore(request):
        nonlocal attive, massimo
        attive += 1
        massimo = max(massimo, attive)
        await asyncio.sleep(0.01)
        attive -= 1
        return httpx.Response(201, json={"categoria": "ordinaria"})

    esiti = esegui([richiesta(f"N-{n:03d}") for n in range(10)], gestore, concorrenza=3)
    assert len(esiti) == 10
    assert 1 < massimo <= 3


def test_una_chiave_rifiutata_ferma_tutto_l_invio():
    def gestore(request):
        return httpx.Response(401, json={"detail": "chiave del servizio mancante o non valida"})

    with pytest.raises(ExceptionGroup) as gruppo:
        esegui([richiesta("N-001"), richiesta("N-002")], gestore)
    assert isinstance(gruppo.value.exceptions[0], httpx.HTTPStatusError)


def test_il_client_invia_json_e_non_la_rappresentazione_python():
    corpi = []

    def gestore(request):
        corpi.append(request.content.decode("utf-8"))
        return httpx.Response(201, json={"categoria": "da_completare"})

    esegui([richiesta("N-001", importo=None)], gestore)
    assert '"importo_centesimi":null' in corpi[0]