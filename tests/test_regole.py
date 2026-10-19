import pytest

from nova.regole import categoria, leggi_centesimi, leggi_importo_euro, normalizza_oggetto


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


@pytest.mark.parametrize(
    ("testo", "atteso"),
    [
        ("125,50", 12550),
        ("1.250,00", 125000),
        ("€ 45", 4500),
        ("0,29", 29),
        ("1.250", 125000),
        ("45,5", 4550),
        ("  €45,05  ", 4505),
        ("", None),
        ("   ", None),
    ],
)
def test_leggere_importo_in_formato_italiano(testo, atteso):
    assert leggi_importo_euro(testo) == atteso


@pytest.mark.parametrize(
    "testo",
    [
        "dodici",
        "-1",
        "-0,01",
        "+45",
        "1,",
        ",50",
        "0,290",
        "1.25",
        "12.50,00",
        "1.25,00",
        "1,000.00",
        "45 €",
        "€",
    ],
)
def test_rifiutare_importi_in_formato_italiano_non_validi(testo):
    with pytest.raises(ValueError):
        leggi_importo_euro(testo)


def test_normalizzare_due_volte_non_cambia_niente():
    una_volta = normalizza_oggetto("  Preventivo vetro  ")
    assert una_volta == "Preventivo vetro"
    assert normalizza_oggetto(una_volta) == una_volta
