"""Il lotto di richieste che Marta riceve stamattina. Dati sintetici di Nova Assicurazioni.

Ogni richiesta è un dizionario con cinque chiavi:
- id: l'identificativo della pratica, unico solo dentro la stessa organizzazione;
- tenant: l'organizzazione a cui la pratica appartiene;
- oggetto: la descrizione scritta da chi ha aperto la pratica, così come è arrivata;
- importo_centesimi: un intero in centesimi di euro, oppure None se non è stato indicato;
- documenti: quanti documenti sono allegati.

Le categorie che il programma assegna sono convenzioni di laboratorio: non autorizzano
rimborsi e non rappresentano condizioni assicurative reali.
"""

LOTTO = [
    {"id": "N-001", "tenant": "nova", "oggetto": "  Preventivo vetro  ", "importo_centesimi": 12500, "documenti": 2},
    {"id": "N-002", "tenant": "nova", "oggetto": "Fattura carrozzeria", "importo_centesimi": None, "documenti": 3},
    {"id": "N-003", "tenant": "nova", "oggetto": "Ricevuta farmacia", "importo_centesimi": 0, "documenti": 2},
    {"id": "N-004", "tenant": "nova", "oggetto": "Preventivo tetto", "importo_centesimi": 99999, "documenti": 2},
    {"id": "N-005", "tenant": "nova", "oggetto": "Perizia allagamento", "importo_centesimi": 100000, "documenti": 4},
    {"id": "N-006", "tenant": "nova", "oggetto": "Foto danno auto", "importo_centesimi": 4500, "documenti": 1},
    {"id": "N-001", "tenant": "nova", "oggetto": "Preventivo vetro", "importo_centesimi": 12500, "documenti": 2},
    {"id": "N-001", "tenant": "aurora", "oggetto": "Cristallo anteriore", "importo_centesimi": 30000, "documenti": 2},
    {"id": "N-007", "tenant": "nova", "oggetto": "Visita specialistica", "importo_centesimi": None, "documenti": 0},
    {"id": "N-008", "tenant": "aurora", "oggetto": "Danno da grandine", "importo_centesimi": 150000, "documenti": 1},
    {"id": "N-004", "tenant": "nova", "oggetto": "Preventivo tetto", "importo_centesimi": 120000, "documenti": 2},
]

# Lo stesso tipo di richieste, ma come le manda il modulo web del portale clienti:
# un campo può mancare del tutto, oppure arrivare con valore null (None in Python),
# e il numero dei documenti a volte arriva come testo.
LOTTO_DAL_PORTALE = [
    {"id": "W-101", "tenant": "nova", "oggetto": "Occhiali da vista", "importo_centesimi": 18900, "documenti": 2},
    {"id": "W-102", "tenant": "nova", "oggetto": "Fisioterapia", "importo_centesimi": None, "documenti": 2},
    {"id": "W-103", "tenant": "nova", "oggetto": "Visita dermatologica", "documenti": 1},
    {"id": "W-104", "tenant": "nova", "oggetto": "Analisi del sangue", "importo_centesimi": 4200, "documenti": "2"},
    {"id": "W-105", "tenant": "nova", "oggetto": "Ecografia", "importo_centesimi": 9000},
]
