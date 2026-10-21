import inspect
from contextlib import closing

import pytest

from nova.flussi import RigaJSONL, leggi_jsonl


def scrivi(cartella, testo):
    percorso = cartella / "lotto.jsonl"
    percorso.write_text(testo, encoding="utf-8")
    return percorso


def test_le_righe_vuote_si_saltano_e_i_numeri_restano_quelli_del_file(tmp_path):
    percorso = scrivi(tmp_path, '{"id": "N-001"}\n\n{"id": "N-002"}\n')
    assert list(leggi_jsonl(percorso)) == [
        RigaJSONL(1, valore={"id": "N-001"}),
        RigaJSONL(3, valore={"id": "N-002"}),
    ]


def test_una_riga_json_non_valida_non_interrompe_la_lettura(tmp_path):
    percorso = scrivi(tmp_path, '{"id": "N-001"}\n{"id": \n{"id": "N-003"}\n')
    assert list(leggi_jsonl(percorso)) == [
        RigaJSONL(1, valore={"id": "N-001"}),
        RigaJSONL(2, errore="JSON non valido"),
        RigaJSONL(3, valore={"id": "N-003"}),
    ]


def test_un_generatore_consumato_non_riparte(tmp_path):
    righe = leggi_jsonl(scrivi(tmp_path, '{"id": "N-001"}\n'))
    assert len(list(righe)) == 1
    assert list(righe) == []


def test_il_lettore_si_chiude_anche_se_chi_legge_si_ferma_con_un_errore(tmp_path):
    righe = leggi_jsonl(scrivi(tmp_path, '{"id": "N-001"}\n{"id": "N-002"}\n'))
    with pytest.raises(RuntimeError), closing(righe):
        next(righe)
        raise RuntimeError("la validazione si è fermata qui")
    assert inspect.getgeneratorstate(righe) == inspect.GEN_CLOSED
