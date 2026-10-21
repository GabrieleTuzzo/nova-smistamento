import pytest
from pydantic import ValidationError

from nova.modelli import PraticaSmistata, Richiesta

VALIDA = {"id": "N-001", "tenant": "nova", "oggetto": "Preventivo vetro", "importo_centesimi": 12500, "documenti": 2}


def test_una_richiesta_valida_si_crea():
    richiesta = Richiesta.model_validate(VALIDA)
    assert richiesta.documenti == 2
    assert richiesta.chiave() == ("nova", "N-001")


def test_l_importo_assente_va_dichiarato_ma_puo_essere_none():
    assert Richiesta.model_validate(VALIDA | {"importo_centesimi": None}).importo_centesimi is None
    senza_importo = dict(VALIDA)
    del senza_importo["importo_centesimi"]
    with pytest.raises(ValidationError, match="Field required"):
        Richiesta.model_validate(senza_importo)


@pytest.mark.parametrize(
    "modifica",
    [
        {"documenti": "2"},
        {"documenti": True},
        {"importo_centesimi": -1},
        {"rimborso": True},
        {"oggetto": ""},
    ],
)
def test_il_modello_rifiuta_un_campo_sbagliato(modifica):
    with pytest.raises(ValidationError):
        Richiesta.model_validate(VALIDA | modifica)


def test_una_richiesta_non_si_puo_modificare():
    richiesta = Richiesta.model_validate(VALIDA)
    with pytest.raises(ValidationError, match="frozen"):
        richiesta.documenti = 3


def test_una_dataclass_non_controlla_i_tipi():
    pratica = PraticaSmistata(Richiesta.model_validate(VALIDA), 42)
    assert pratica.categoria == 42