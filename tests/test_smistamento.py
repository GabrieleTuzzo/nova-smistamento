from nova.smistamento import conteggi, smista


def richiesta(id_pratica, tenant="nova", importo=12500, documenti=2, oggetto="Preventivo"):
    return {
        "id": id_pratica,
        "tenant": tenant,
        "oggetto": oggetto,
        "importo_centesimi": importo,
        "documenti": documenti,
    }


def lotto_di_prova():
    return [
        richiesta("N-001", oggetto="  Preventivo vetro  "),
        richiesta("N-001"),
        richiesta("N-001", tenant="aurora"),
        richiesta("N-002", importo=None),
    ]


def test_la_stessa_pratica_arrivata_due_volte_resta_una():
    smistate, duplicati = smista(lotto_di_prova())
    assert duplicati == [("nova", "N-001")]
    assert len(smistate) == 3


def test_lo_stesso_id_in_due_tenant_sono_due_pratiche():
    smistate, _ = smista(lotto_di_prova())
    tenant_di_n001 = []
    for pratica in smistate:
        if pratica["id"] == "N-001":
            tenant_di_n001.append(pratica["tenant"])
    assert tenant_di_n001 == ["nova", "aurora"]


def test_il_lotto_ricevuto_non_cambia():
    lotto = lotto_di_prova()
    smista(lotto)
    assert lotto == lotto_di_prova()


def test_i_conteggi_mostrano_anche_le_categorie_vuote():
    smistate, _ = smista([richiesta("N-001")])
    assert conteggi(smistate) == {"da_completare": 0, "da_rivedere": 0, "ordinaria": 1}