import pytest

from nova.regole import categoria, leggi_centesimi, normalizza_oggetto


@pytest.mark.parametrize(
    ("importo", "documenti", "attesa"),
    [
        (None, 2, "da_completare"),
        (0, 2, "ordinaria"),
        (99999, 2, "ordinaria"),
        (100000, 2, "da_rivedere"),
        (4500, 1, "da_rivedere"),
        (None, 0, "da_completare"),
    ],
)
def test_categoria_sui_confini(importo, documenti, attesa):
    assert categoria(importo, documenti) == attesa


def test_la_stringa_vuota_e_un_assenza_e_lo_zero_un_importo():
    assert leggi_centesimi("") is None
    assert leggi_centesimi("0") == 0
    assert leggi_centesimi("12500") == 12500


@pytest.mark.parametrize("testo", ["dodici", "-1", "125,50"])
def test_un_importo_illeggibile_o_negativo_si_rifiuta(testo):
    with pytest.raises(ValueError):
        leggi_centesimi(testo)


def test_normalizzare_due_volte_non_cambia_niente():
    una_volta = normalizza_oggetto("  Preventivo vetro  ")
    assert una_volta == "Preventivo vetro"
    assert normalizza_oggetto(una_volta) == una_volta