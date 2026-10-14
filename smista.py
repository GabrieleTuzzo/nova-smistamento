"""Smistamento delle richieste di Nova: un lotto entra, ogni pratica esce con una categoria."""

from lotto import LOTTO

SOGLIA_REVISIONE_CENTESIMI = 100000
DOCUMENTI_MINIMI = 2


def formatta_euro(centesimi):
    segno = "-" if centesimi < 0 else ""
    euro, resto = divmod(abs(centesimi), 100)
    intero_formattato = f"{euro:,}".replace(",", ".")
    return f"{segno}{intero_formattato},{resto:02d}"


# 1. Una pratica si riconosce dalla coppia (tenant, id): conserviamo la prima occorrenza.
visti = set()
smistate = []
duplicati = []

for richiesta in LOTTO:
    chiave = (richiesta["tenant"], richiesta["id"])
    if chiave in visti:
        duplicati.append(chiave)
        continue
    visti.add(chiave)

    # 2. Lavoriamo su una copia: il lotto che è arrivato resta com'era.
    pulita = richiesta.copy()
    pulita["oggetto"] = richiesta["oggetto"].strip()

    # 3. La regola. L'assenza viene prima di tutto, e l'assenza non è lo zero.
    importo = pulita["importo_centesimi"]
    if importo is None:
        categoria = "da_completare"
    elif importo >= SOGLIA_REVISIONE_CENTESIMI or pulita["documenti"] < DOCUMENTI_MINIMI:
        categoria = "da_rivedere"
    else:
        categoria = "ordinaria"

    pulita["categoria"] = categoria
    smistate.append(pulita)

# 4. Le prove sui confini, prima di stampare: se una di queste righe diventa falsa,
#    il programma si ferma qui, e il riepilogo sbagliato non esce.
categoria_di = {}
for pratica in smistate:
    categoria_di[(pratica["tenant"], pratica["id"])] = pratica["categoria"]

assert categoria_di[("nova", "N-002")] == "da_completare"  # importo assente
assert categoria_di[("nova", "N-003")] == "ordinaria"  # zero è un importo presente
assert categoria_di[("nova", "N-004")] == "ordinaria"  # 99999: un centesimo sotto la soglia
assert categoria_di[("nova", "N-005")] == "da_rivedere"  # 100000: sulla soglia
assert categoria_di[("nova", "N-006")] == "da_rivedere"  # un documento solo
assert categoria_di[("aurora", "N-001")] == "ordinaria"  # stesso id, altro tenant: un'altra pratica
assert LOTTO[0]["oggetto"] == "  Preventivo vetro  "  # il lotto originale non è stato toccato

# 5. Il riepilogo che Marta legge.
conteggi = {"da_completare": 0, "da_rivedere": 0, "ordinaria": 0}
totali_centesimi = {"da_completare": 0, "da_rivedere": 0, "ordinaria": 0}
importi_mancanti = 0
for pratica in smistate:
    categoria = pratica["categoria"]
    conteggi[categoria] += 1
    importo = pratica["importo_centesimi"]
    if importo is None:
        importi_mancanti += 1
    else:
        totali_centesimi[categoria] += importo

for pratica in smistate:
    print(f"{pratica['tenant']:<7} {pratica['id']:<6} {pratica['categoria']:<14} {pratica['oggetto']}")

print()
print(f"Lette: {len(LOTTO)}   Smistate: {len(smistate)}   Duplicati scartati: {len(duplicati)}")
print("Totali in euro: somma degli importi indicati; gli importi mancanti sono esclusi.")
for categoria, numero in conteggi.items():
    print(f"  {categoria:<14} {numero}   Totale: {formatta_euro(totali_centesimi[categoria])}")

print(f"Importi mancanti esclusi: {importi_mancanti}")

da_rivedere = sorted(
    (pratica for pratica in smistate if pratica["categoria"] == "da_rivedere"),
    key=lambda pratica: pratica["importo_centesimi"],
    reverse=True,
)

assert formatta_euro(254500) == "2.545,00"
assert [pratica["id"] for pratica in da_rivedere] == ["N-008", "N-005", "N-006"]

print("\nPratiche da rivedere (importi in euro, ordine decrescente):")
for pratica in da_rivedere:
    print(
        f"  {pratica['tenant']:<7} {pratica['id']:<6} "
        f"{formatta_euro(pratica['importo_centesimi'])}  {pratica['oggetto']}"
    )
    
print("\nProve sui confini: tutte superate.")