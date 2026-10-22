import asyncio

from nova.impostazioni import Impostazioni
from nova.invio import invia
from nova.modelli import Richiesta


def test_invia_legge_e_smista_le_richieste_validate(tmp_path, monkeypatch):
    percorso = tmp_path / "lotto.jsonl"
    percorso.write_text(
        '{"id":"N-001","tenant":"nova","oggetto":"Vetro","importo_centesimi":"12500","documenti":2}\n',
        encoding="utf-8",
    )
    inviate = []

    async def intercetta(lotto, client, concorrenza):
        inviate.extend(lotto)
        return []

    monkeypatch.setattr("nova.invio.invia_lotto", intercetta)
    impostazioni = Impostazioni(_env_file=None, chiave_servizio="chiave-di-prova")

    esiti = asyncio.run(invia(percorso, impostazioni))

    assert esiti == []
    assert inviate == [
        Richiesta(
            id="N-001",
            tenant="nova",
            oggetto="Vetro",
            importo_centesimi=12500,
            documenti=2,
        )
    ]
