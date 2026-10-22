"""La configurazione: i valori che cambiano fra una macchina e l'altra, letti dall'ambiente o dal file .env."""

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Impostazioni(BaseSettings):
    """Ogni campo si legge dalla variabile d'ambiente con il prefisso NOVA_, oppure dal file .env.

    La chiave del servizio non ha un valore predefinito, e un valore vuoto vale come assente:
    se manca, il programma si rifiuta di partire.
    """

    model_config = SettingsConfigDict(env_prefix="NOVA_", env_file=".env", env_ignore_empty=True, extra="ignore")

    chiave_servizio: SecretStr
    url_servizio: str = "http://127.0.0.1:8000"
    concorrenza_massima: int = 4
    timeout_secondi: float = 5.0