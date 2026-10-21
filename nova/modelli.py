"""Le forme dei dati: la richiesta validata al confine e la pratica smistata."""

from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict, Field


class Richiesta(BaseModel):
    """Una richiesta come il programma la accetta: ogni campo dichiarato, nessuna conversione permissiva."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    id: str = Field(min_length=1)
    tenant: str = Field(min_length=1)
    oggetto: str = Field(min_length=1)
    importo_centesimi: int | None = Field(ge=0)
    documenti: int = Field(ge=0)

    def chiave(self) -> tuple[str, str]:
        """L'identità della pratica: l'organizzazione e l'identificativo, insieme."""
        return (self.tenant, self.id)


@dataclass(frozen=True)
class PraticaSmistata:
    """Una richiesta con la categoria che la regola le ha assegnato."""

    richiesta: Richiesta
    categoria: str