# nova-smistamento

Smista il lotto di richieste che il gestionale di Nova Assicurazioni esporta ogni mattina: ogni pratica esce con
una categoria (`da_completare`, `da_rivedere`, `ordinaria`) e in fondo si leggono i conteggi. I dati sono sintetici
e le categorie sono convenzioni di laboratorio: non autorizzano rimborsi.

## Requisiti

- [uv](https://docs.astral.sh/uv/) installato. Python 3.12 lo procura uv da sé.

## Come si avvia

Dalla cartella del progetto, quella che contiene `pyproject.toml`:

```bash
uv run python -m nova                               # smista dati/lotto.jsonl
uv run python -m nova dati/lotto_con_errori.jsonl   # smista le righe buone e segnala tutte quelle rifiutate
```

Il codice di uscita è `0` se il lotto è stato smistato, `1` se il file non si legge o una riga viene rifiutata.
Le righe non valide non fermano la lettura: il programma stampa su `stderr` il numero di ogni riga rifiutata
e tutti i relativi motivi, mentre smista normalmente le righe valide.

## Controlli

```bash
uv run pytest
uv run mypy nova
uv run ruff check .
uv run ruff format --check .
```

## Com'è fatto

| Modulo | Che cosa fa |
|---|---|
| `nova/modelli.py` | `Richiesta`, il modello Pydantic che valida al confine, e `PraticaSmistata`, la richiesta con la sua categoria |
| `nova/flussi.py` | il lettore JSONL: un generatore che consegna una riga alla volta, con il suo numero o l'errore JSON |
| `nova/archivio.py` | l'adattatore del formato del gestionale e la lettura validata delle righe buone e rifiutate |
| `nova/regole.py` | la regola di smistamento e la conversione degli importi |
| `nova/smistamento.py` | deduplica, applica la regola, conta |
| `nova/__main__.py` | il programma: legge, smista, stampa, restituisce il codice di uscita |

## La regola

| condizione, nell'ordine | categoria |
|---|---|
| importo assente (`None`) | `da_completare` |
| importo di almeno 100000 centesimi, oppure meno di 2 documenti | `da_rivedere` |
| altrimenti | `ordinaria` |

Una pratica è identificata dalla coppia `(tenant, id)`. Se arriva due volte, si conserva la prima occorrenza.

## Il formato del lotto

Un documento JSON per riga. Il gestionale esporta l'importo come testo in centesimi, con la stringa vuota per un
importo non compilato, e l'oggetto così come è stato digitato. L'adattatore converte l'importo e toglie gli spazi
esterni dall'oggetto; tutto il resto lo giudica il modello, in modalità stretta e senza campi in più.