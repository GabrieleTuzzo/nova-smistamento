import json
from pathlib import Path

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
    lotto, rifiutate = leggi_lotto(CARTELLA_DATI / "lotto.jsonl")
    assert len(lotto) == 11
    assert rifiutate == []
    assert lotto[0].oggetto == "Preventivo vetro"
    assert lotto[1].importo_centesimi is None


def test_il_lotto_raccoglie_tutte_le_ragioni_e_prosegue_dopo_json_non_valido(tmp_path):
    valida = {
        "tenant": "nova",
        "oggetto": "Preventivo",
        "importo_centesimi": "12500",
        "documenti": 2,
    }
    righe = [json.dumps(valida | {"id": f"N-{numero:03}"}) for numero in (1, 3, 4, 5)]
    riga_con_errori = valida | {
        "id": 2,
        "importo_centesimi": "dodici",
        "documenti": "due",
        "extra": True,
    }
    righe.insert(1, json.dumps(riga_con_errori))
    righe.append('{"id":')
    righe.extend(json.dumps(valida | {"id": f"N-{numero:03}"}) for numero in (7, 8))
    percorso = tmp_path / "lotto.jsonl"
    percorso.write_text("\n".join(righe) + "\n", encoding="utf-8")

    lotto, rifiutate = leggi_lotto(percorso)

    assert [richiesta.id for richiesta in lotto] == ["N-001", "N-003", "N-004", "N-005", "N-007", "N-008"]
    assert [riga.numero for riga in rifiutate] == [2, 6]
    assert any("importo_centesimi" in ragione for ragione in rifiutate[0].ragioni)
    assert any("id" in ragione for ragione in rifiutate[0].ragioni)
    assert any("documenti" in ragione for ragione in rifiutate[0].ragioni)
    assert any("extra" in ragione for ragione in rifiutate[0].ragioni)
    assert rifiutate[1].ragioni == ("JSON non valido",)


def test_un_oggetto_di_soli_spazi_si_rifiuta(tmp_path):
    percorso = tmp_path / "lotto.jsonl"
    percorso.write_text(
        '{"id": "N-1", "tenant": "nova", "oggetto": "   ", "importo_centesimi": "1", "documenti": 2}\n',
        encoding="utf-8",
    )
    lotto, rifiutate = leggi_lotto(percorso)
    assert lotto == []
    assert len(rifiutate) == 1
    assert any("oggetto" in ragione for ragione in rifiutate[0].ragioni)


def test_un_lotto_con_errori_fa_uscire_il_programma_con_1(capsys):
    assert main([str(CARTELLA_DATI / "lotto_con_errori.jsonl")]) == 1
    assert "riga 2" in capsys.readouterr().err


def test_un_lotto_valido_fa_uscire_il_programma_con_0():
    assert main([str(CARTELLA_DATI / "lotto.jsonl")]) == 0


def test_la_cli_smista_le_righe_valide_e_stampa_tutti_i_rifiuti(tmp_path, capsys):
    valida = '{"id": "N-1", "tenant": "nova", "oggetto": "Vetro", "importo_centesimi": "100", "documenti": 2}'
    percorso = tmp_path / "lotto.jsonl"
    percorso.write_text(
        valida
        + '\n{"id": "N-2", "tenant": 3, "oggetto": "", "importo_centesimi": "no", "documenti": "2"}\n'
        + '{"id":\n'
        + valida.replace("N-1", "N-3")
        + "\n",
        encoding="utf-8",
    )

    assert main([str(percorso)]) == 1
    captured = capsys.readouterr()
    assert "N-1" in captured.out
    assert "N-3" in captured.out
    assert "Rifiutate: 2" in captured.out
    assert "riga 2" in captured.err
    assert "riga 3" in captured.err
    assert "tenant" in captured.err
    assert "oggetto" in captured.err
    assert "importo_centesimi" in captured.err
    assert "documenti" in captured.err
    assert "JSON non valido" in captured.err
