import pytest
from pydantic import ValidationError

from nova.impostazioni import Impostazioni


def test_senza_chiave_la_configurazione_si_rifiuta_di_partire(monkeypatch):
    monkeypatch.delenv("NOVA_CHIAVE_SERVIZIO", raising=False)
    with pytest.raises(ValidationError, match="chiave_servizio"):
        Impostazioni(_env_file=None)


def test_una_chiave_vuota_vale_come_assente(monkeypatch):
    monkeypatch.setenv("NOVA_CHIAVE_SERVIZIO", "")
    with pytest.raises(ValidationError, match="chiave_servizio"):
        Impostazioni(_env_file=None)


def test_l_ambiente_prevale_e_la_chiave_non_si_stampa(monkeypatch):
    monkeypatch.setenv("NOVA_CHIAVE_SERVIZIO", "valore-segreto")
    monkeypatch.setenv("NOVA_CONCORRENZA_MASSIMA", "2")
    impostazioni = Impostazioni(_env_file=None)
    assert impostazioni.concorrenza_massima == 2
    assert impostazioni.chiave_servizio.get_secret_value() == "valore-segreto"
    assert "valore-segreto" not in repr(impostazioni)
