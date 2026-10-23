# nova-smistamento

Smista le richieste di rimborso di Nova Assicurazioni: ogni pratica esce con una categoria (`da_completare`,
`da_rivedere`, `ordinaria`). Funziona in due modi: come comando che smista un lotto in locale, e come servizio HTTP
che riceve le pratiche una alla volta, con un client che gli invia un lotto intero. I dati sono sintetici e le
categorie sono convenzioni di laboratorio: non autorizzano rimborsi.

## Requisiti

- [uv](https://docs.astral.sh/uv/) installato. Python 3.12 lo procura uv da sé.

## Configurazione

```bash
cp .env.example .env          # su Windows: Copy-Item .env.example .env
uv run python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Incolla il valore generato in `.env`, dopo `NOVA_CHIAVE_SERVIZIO=`. Il file `.env` resta sulla tua macchina: è
escluso da Git. Ogni variabile si può anche impostare nell'ambiente, che prevale sul file.

| Variabile | Che cosa fa | Predefinito |
| --- | --- | --- |
| `NOVA_CHIAVE_SERVIZIO` | la chiave che il client manda e il servizio controlla | nessuno: obbligatoria |
| `NOVA_URL_SERVIZIO` | dove il client trova il servizio | `http://127.0.0.1:8000` |
| `NOVA_CONCORRENZA_MASSIMA` | quante richieste il client manda insieme | `4` |
| `NOVA_TIMEOUT_SECONDI` | quanto il client aspetta ogni operazione di rete | `5` |

## Come si avvia

Dalla cartella del progetto:

```bash
uv run python -m nova                          # smista dati/lotto.jsonl in locale
uv run uvicorn nova.servizio:app               # il servizio, su http://127.0.0.1:8000
uv run python -m nova.invio                    # in un secondo terminale: invia il lotto al servizio
```

La documentazione interattiva del servizio è su `http://127.0.0.1:8000/docs`. `python -m nova` esce con `1` se il
lotto non si legge o una riga è rifiutata. `python -m nova.invio` esce con `1` se l'invio non parte o si interrompe, e con `0` anche
quando qualche pratica è scaduta o rifiutata: gli esiti dicono quali.

## Il servizio

| Metodo e percorso | Che cosa fa | Risposte |
| --- | --- | --- |
| `GET /health` | stato e numero di pratiche registrate | `200` |
| `POST /pratiche` | smista e registra una richiesta | `201`, `401`, `409` se già registrata, `422` se i dati non vanno |
| `GET /pratiche/{tenant}/{id}` | legge una pratica registrata | `200`, `401`, `404` |
| `GET /riepilogo` | conteggi per categoria | `200`, `401` |

Tutto tranne `/health` richiede l'intestazione `X-Chiave-Servizio`. Il registro vive in memoria e si svuota quando
il servizio si ferma.

## Controlli

```bash
uv run pytest
uv run mypy nova
uv run ruff check .
uv run ruff format --check .
```

## La regola

| condizione, nell'ordine | categoria |
| --- | --- |
| importo assente (`None`) | `da_completare` |
| importo di almeno 100000 centesimi, oppure meno di 2 documenti | `da_rivedere` |
| altrimenti | `ordinaria` |

Una pratica è identificata dalla coppia `(tenant, id)`. Nel lotto si conserva la prima occorrenza; il servizio
rifiuta con `409` una pratica già registrata, quindi rilanciare l'invio non crea doppioni. Il client riprova una sola volta
quando il primo invio scade; se il retry riceve `409`, verifica la pratica già registrata per non segnalarla come duplicata
quando la prima risposta si è persa.
