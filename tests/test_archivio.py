from pathlib import Path

import pytest

from nova.__main__ import main
from nova.archivio import adatta, leggi_lotto

CARTELLA_DATI = Path(__file__).parent.parent / "dati"


def test_l_adattatore_converte_solo_importo_e_oggetto():
    riga = {"id": "N-001", "tenant": "nova", "oggetto": "  Vetro  ", "importo_centesimi": "", "documenti": 2}
    assert adatta(riga) == {
        "id": "N-001",
        "tenant": "nova",
        "oggetto": "Vetro",
        "importo_centesimi": None,
        "documenti": 2,
    }
    assert riga["oggetto"] == "  Vetro  "


def test_il_lotto_del_corso_diventa_undici_richieste_validate():
    lotto = leggi_lotto(CARTELLA_DATI / "lotto.jsonl")
    assert len(lotto) == 11
    assert lotto[0].oggetto == "Preventivo vetro"
    assert lotto[1].importo_centesimi is None


def test_la_prima_riga_rifiutata_dice_riga_e_campo():
    with pytest.raises(ValueError, match=r"riga 2: documenti"):
        leggi_lotto(CARTELLA_DATI / "lotto_con_errori.jsonl")


def test_un_oggetto_di_soli_spazi_si_rifiuta(tmp_path):
    percorso = tmp_path / "lotto.jsonl"
    percorso.write_text(
        '{"id": "N-1", "tenant": "nova", "oggetto": "   ", "importo_centesimi": "1", "documenti": 2}\n',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="oggetto"):
        leggi_lotto(percorso)


def test_un_lotto_con_errori_fa_uscire_il_programma_con_1(capsys):
    assert main([str(CARTELLA_DATI / "lotto_con_errori.jsonl")]) == 1
    assert "riga 2" in capsys.readouterr().err