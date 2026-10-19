import json
from pathlib import Path

import pytest

from nova.__main__ import main
from nova.archivio import leggi_lotto

CARTELLA_DATI = Path(__file__).parent.parent / "dati"


def scrivi_lotto(cartella, righe):
    percorso = cartella / "lotto.json"
    percorso.write_text(json.dumps(righe), encoding="utf-8")
    return percorso


def test_gli_importi_arrivano_come_testo_ed_escono_in_centesimi(tmp_path):
    percorso = scrivi_lotto(
        tmp_path,
        [
            {"id": "N-001", "tenant": "nova", "oggetto": "x", "importo_centesimi": "12500", "documenti": 2},
            {"id": "N-002", "tenant": "nova", "oggetto": "y", "importo_centesimi": "", "documenti": 2},
        ],
    )
    lotto = leggi_lotto(percorso)
    assert lotto[0]["importo_centesimi"] == 12500
    assert lotto[1]["importo_centesimi"] is None


def test_un_json_rotto_dice_la_riga(tmp_path):
    percorso = tmp_path / "rotto.json"
    percorso.write_text('[\n  {"id": "N-001"}\n  {"id": "N-002"}\n]\n', encoding="utf-8")
    with pytest.raises(ValueError, match="riga 3"):
        leggi_lotto(percorso)


def test_un_importo_illeggibile_dice_quale_richiesta():
    with pytest.raises(ValueError, match=r"richiesta n\. 2 \(N-102\)"):
        leggi_lotto(CARTELLA_DATI / "lotto_con_errori.json")


def test_il_lotto_del_corso_si_legge_tutto():
    lotto = leggi_lotto(CARTELLA_DATI / "lotto.json")
    assert len(lotto) == 11


def test_un_lotto_con_errori_fa_uscire_il_programma_con_1(capsys):
    codice = main([str(CARTELLA_DATI / "lotto_con_errori.json")])
    assert codice == 1
    assert "N-102" in capsys.readouterr().err