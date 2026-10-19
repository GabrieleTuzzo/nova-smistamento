# nova-smistamento

Smista il lotto di richieste che il gestionale di Nova Assicurazioni esporta ogni mattina: ogni pratica esce con
una categoria (`da_completare`, `da_rivedere`, `ordinaria`) e in fondo si leggono i conteggi. I dati sono sintetici
e le categorie sono convenzioni di laboratorio: non autorizzano rimborsi.

## Requisiti

- [uv](https://docs.astral.sh/uv/) installato. Python 3.12 lo procura uv da sé.

## Come si avvia

Dalla cartella del progetto, quella che contiene `pyproject.toml`:

```bash
uv run python -m nova                              # smista dati/lotto.json
uv run python -m nova dati/lotto_con_errori.json   # si ferma e dice quale richiesta correggere
```

Il codice di uscita è `0` se il lotto è stato smistato, `1` se il file non si legge o una richiesta non è valida.

## Controlli

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

## Com'è fatto

| Modulo | Che cosa fa |
|---|---|
| `nova/regole.py` | la regola di smistamento e la conversione degli importi: non legge file e non stampa |
| `nova/smistamento.py` | deduplica, applica la regola, conta: non legge file e non stampa |
| `nova/archivio.py` | legge il lotto dal file JSON e converte gli importi al bordo |
| `nova/__main__.py` | il programma: legge, smista, stampa, restituisce il codice di uscita |

## La regola

| condizione, nell'ordine | categoria |
|---|---|
| importo assente (`None`) | `da_completare` |
| importo di almeno 100000 centesimi, oppure meno di 2 documenti | `da_rivedere` |
| altrimenti | `ordinaria` |

Una pratica è identificata dalla coppia `(tenant, id)`. Se arriva due volte, si conserva la prima occorrenza.
Il gestionale esporta l'importo come testo in centesimi e un importo non compilato come stringa vuota; un importo che
non è un intero o è negativo ferma la lettura del lotto. Per gli importi inseriti a mano, `leggi_importo_euro`
accetta invece il formato italiano (per esempio `1.250,00` o `€ 45`) e restituisce centesimi interi.