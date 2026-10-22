import pytest
from fastapi.testclient import TestClient

from nova.servizio import app

CHIAVE = {"X-Chiave-Servizio": "chiave-di-prova"}
VALIDA = {"id": "N-001", "tenant": "nova", "oggetto": "Preventivo vetro", "importo_centesimi": 12500, "documenti": 2}


@pytest.fixture
def servizio(monkeypatch):
    monkeypatch.setenv("NOVA_CHIAVE_SERVIZIO", "chiave-di-prova")
    with TestClient(app) as client:
        yield client


def test_il_servizio_e_vivo_e_parte_vuoto(servizio):
    assert servizio.get("/health").json() == {"stato": "ok", "pratiche": 0}


def test_una_richiesta_valida_viene_smistata_e_registrata(servizio):
    risposta = servizio.post("/pratiche", json=VALIDA, headers=CHIAVE)
    assert risposta.status_code == 201
    assert risposta.json()["categoria"] == "ordinaria"
    assert servizio.get("/pratiche/nova/N-001", headers=CHIAVE).json()["oggetto"] == "Preventivo vetro"


def test_la_stessa_pratica_non_si_registra_due_volte(servizio):
    servizio.post("/pratiche", json=VALIDA, headers=CHIAVE)
    seconda = servizio.post("/pratiche", json=VALIDA | {"importo_centesimi": 120000}, headers=CHIAVE)
    assert seconda.status_code == 409
    assert servizio.get("/pratiche/nova/N-001", headers=CHIAVE).json()["categoria"] == "ordinaria"


def test_un_dato_sbagliato_riceve_422_e_non_viene_registrato(servizio):
    risposta = servizio.post("/pratiche", json=VALIDA | {"documenti": "2"}, headers=CHIAVE)
    assert risposta.status_code == 422
    assert risposta.json()["detail"][0]["loc"] == ["body", "documenti"]
    assert servizio.get("/health").json()["pratiche"] == 0


@pytest.mark.parametrize("intestazioni", [{}, {"X-Chiave-Servizio": "sbagliata"}])
def test_senza_la_chiave_giusta_risponde_401(servizio, intestazioni):
    assert servizio.post("/pratiche", json=VALIDA, headers=intestazioni).status_code == 401
    assert servizio.get("/health").json()["pratiche"] == 0


def test_una_pratica_sconosciuta_risponde_404(servizio):
    assert servizio.get("/pratiche/nova/N-999", headers=CHIAVE).status_code == 404


def test_il_riepilogo_conta_le_pratiche_registrate(servizio):
    servizio.post("/pratiche", json=VALIDA, headers=CHIAVE)
    servizio.post("/pratiche", json=VALIDA | {"id": "N-002", "importo_centesimi": None}, headers=CHIAVE)
    assert servizio.get("/riepilogo", headers=CHIAVE).json() == {"da_completare": 1, "da_rivedere": 0, "ordinaria": 1}