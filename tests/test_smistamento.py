from nova.modelli import Richiesta
from nova.smistamento import conteggi, smista


def richiesta(id_pratica, tenant="nova", importo=12500, documenti=2, oggetto="Preventivo"):
    return Richiesta(id=id_pratica, tenant=tenant, oggetto=oggetto, importo_centesimi=importo, documenti=documenti)


def lotto_di_prova():
    return [
        richiesta("N-001"),
        richiesta("N-001", importo=120000),
        richiesta("N-001", tenant="aurora"),
        richiesta("N-002", importo=None),
    ]


def test_la_stessa_pratica_arrivata_due_volte_resta_una():
    smistate, duplicati = smista(lotto_di_prova())
    assert duplicati == [("nova", "N-001")]
    assert [p.richiesta.chiave() for p in smistate] == [("nova", "N-001"), ("aurora", "N-001"), ("nova", "N-002")]


def test_si_conserva_la_prima_occorrenza():
    smistate, _ = smista(lotto_di_prova())
    assert smistate[0].richiesta.importo_centesimi == 12500


def test_smista_accetta_anche_un_generatore():
    smistate, _ = smista(r for r in lotto_di_prova())
    assert len(smistate) == 3


def test_i_conteggi_mostrano_anche_le_categorie_vuote():
    smistate, _ = smista([richiesta("N-001")])
    assert conteggi(smistate) == {"da_completare": 0, "da_rivedere": 0, "ordinaria": 1}