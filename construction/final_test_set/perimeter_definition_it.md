# Perimetro del problema NL→SPARQL su LiITA (bozza, 2026-11-10)

Scopo: definire quali domande un sistema deve saper tradurre, prima di scrivere il nuovo test set e prima di modificare i sistemi. Il perimetro ha quattro assi:
- A. risorse;
- B. operazioni elementari;
- C. operatori di composizione;
- D. forma della risposta.

Ogni domanda di test corrisponde a una combinazione di valori sui quattro assi.

Fonti dei conteggi:
- domande: test principale (100) e held-out (71);
- etichette: estrazione automatica dalle query gold (`features.py`, approssimata) per gli assi A e B; classificazione manuale per l'asse C (per l'held-out, il campo `structure`).

## Principio di delimitazione (da confermare)
Sono nel perimetro le domande:
- che un utente non esperto può porre sul **contenuto lessicale** delle risorse collegate a LiITA;
- la cui risposta è il risultato di **una sola query SPARQL**: una lista, un valore, un conteggio o una tabella.

Sono fuori perimetro:
- le domande sulla struttura dei dati (classi, proprietà, grafi);
- le domande che richiedono conoscenza esterna alle risorse;
- le analisi che richiedono più query o calcoli successivi.

## Asse A — Risorse e che cosa espongono

| Risorsa | Contenuto interrogabile | Main | Held-out |
|---|---|---|---|
| LiITA (lemma bank) | lemmi e ipolemmi, forme scritte e varianti, POS, genere, tipo di flessione, grado | 99* | 53 |
| CompL-it (SERVICE) | parole, sensi, definizioni; relazioni iponimo/iperonimo, meronimo/olonimo, sinonimo approssimato, antonimo | 50 | 25 |
| ELIta | 9 categorie emotive associate ai lemmi | 35 | 23 |
| Sentix | polarità (etichetta e valore; un lemma può averne più di uno) | 14 | 15 |
| Siciliano | lemma bank dialettale + traduzioni (`vartrans:translatableAs`) | 15 | 17 |
| Parmigiano | idem | 15 | 11 |

\* Nel test principale quasi tutte le query passano da LiITA anche quando la domanda riguarda solo CompL-it.

Numero di risorse per domanda:

| Risorse | Main | Held-out |
|---|---|---|
| 1 | 17 | 25 |
| 2 | 54 | 24 |
| 3 | 21 | 19 |
| ≥4 | 8 | 3 |

## Asse B — Operazioni elementari

| ID | Operazione | Esempio | Main | Held-out |
|---|---|---|---|---|
| B1 | lookup di una parola | traduzione di 'pane' | (molte) | (molte) |
| B2 | filtro morfologico (prefisso/suffisso/contiene) | verbi in 'ri-' | ~26 | 8 |
| B3 | filtro grammaticale (POS, genere, grado, flessione) | aggettivi superlativi | 24 | 26 |
| B4 | relazione semantica (un passo) | parti di 'nave' | 16 | 14 |
| B5 | definizioni (di una parola / che contengono X) | definizioni con 'cavallo' | 19 | 6 |
| B6 | conteggio dei sensi | sensi di 'corrente' | 14 | 4 |
| B7 | traduzione (italiano → dialetto, dialetto → italiano) | 'picciriddu' → italiano | 32 | 20 |
| B8 | emozione (di una parola / parole con emozione E) | parole con Paura | 35 | 23 |
| B9 | polarità (valore, soglia) | verbi con polarità < −0.7 | 14 | 15 |
| B10 | aggregazione semplice (COUNT, AVG su tutto il risultato) | quanti nomi propri | 34 | 25 |

Operazioni aggiunte dopo l'analisi delle fonti e le verifiche sull'endpoint (`fonti_tipi_domanda.md`):

| ID | Operazione | Esempio | Main | Held-out |
|---|---|---|---|---|
| B11 | varianti di lemma e ipolemmi (LiITA; varianti grafiche siciliane) | varianti di *arrabbiare*; lemmi siciliani con variante *ed*/*ied* | 0 | 1 |
| B12 | tipo semantico e tratti CompL-it (`hasSemanticType`, `trait`) | nomi di tipo Professione | 0 | 0 |
| B13 | relazioni funzionali e derivazionali CompL-it (`usedFor`, `createdBy`, `deadjectivalNoun`, ...) | a che cosa serve un *martello* | 0 | 0 |
| B14 | esempi d'uso (CompL-it) e note d'uso (parmigiano) | traduzioni di *donna* con note d'uso | 0 | 0 |

Da decidere se B12–B14 entrano nel perimetro: sono dati reali dell'endpoint e interessano ai linguisti, ma nessun sistema li conosce.

Lacune del test principale sull'asse B:
- solo `lila:Lemma`, mai gli ipolemmi;
- genere, grado e varianti di lemma assenti;
- nessuna traduzione dialetto → italiano;
- nessuna domanda solo dialettale;
- antonimi e sinonimi quasi assenti (1 domanda);
- soglie di polarità quasi assenti.

## Asse C — Operatori di composizione

| ID | Operatore | Esempio | Main | Held-out |
|---|---|---|---|---|
| C1 | congiunzione di vincoli su risorse diverse | traduzioni siciliane di parole con Rabbia | 83† | 46† |
| C2 | disgiunzione di valori (VALUES) | parole con Gioia **o** Fiducia | 5 | 0 |
| C3 | catena (stessa relazione iterata) | iponimi degli iponimi | 0 | 3 |
| C4 | intersezione (stesso vincolo, due valori, stessa entità) | Paura **e** Rabbia; iperonimi comuni | 0 | 3 |
| C5 | self-join (entità diverse che condividono un valore) | altre parole con la stessa traduzione | 0 | 3 |
| C6 | negazione | verbi senza traduzione parmigiana | 0 | 4 |
| C7 | unione strutturale | traduzione siciliana **o** parmigiana | 0 | 3 |
| C8 | aggregazione per gruppo (GROUP BY) | per ogni emozione, quanti avverbi | 13 | 4 + 7 |
| C9 | filtro su aggregato (HAVING) | parole con più di 6 emozioni | 2 | 3 |
| C10 | confronto con un valore di riferimento (sottoquery) | polarità maggiore di 'scrivere' | 0 | 3 |
| C11 | confronto tra variabili | grafia uguale in siciliano e parmigiano | 1 | 2 |
| C12 | aggregazione annidata (media di conteggi) | forme medie per lemma verbale | 4 | 1 |
| C13 | analisi multi-statistica (più indicatori in una risposta) | positivi e negativi per emozione | 0 | 3 |

† Domande con almeno 2 risorse; si sovrappongono agli altri operatori.

Attestazione degli operatori nelle fonti (dettagli in `fonti_tipi_domanda.md`):

| Operatore | Famiglia LiITA | LiLa |
|---|---|---|
| C3 catena | CompL-it 2025 (iponimi → LiITA → traduzione) | Passarotti & Litta 2026 |
| C4 intersezione | Di Palma 2025 (Gioia **e** Tristezza) | 4 query; Passarotti & Litta 2026 |
| C5 self-join | Parma 2025 (implicito) | 3 query; PBML 2020; P&L 2026 |
| C6 negazione | — | 6 query; P&L 2026 (MINUS); PBML 2020 |
| C7 unione | — | P&L 2026 |
| C8/C9 gruppo, classifica | sito LiITA; Di Palma 2025; Parma 2025 | 6 query; PBML 2020 |
| C11 confronto tra variabili | Siciliano 2025 (*ed*/*ied*); Parma 2025 (*s*→*z*) | — |
| C13 multi-statistica | Di Palma 2025 | 3 query; PBML 2020; LaReS 2026 |
| C10 confronto con riferimento | (solo soglie fisse di polarità) | — |

- C10 è l'unico operatore dell'held-out senza un'attestazione diretta: si può tenere, ma con meno domande.
- C11 nelle fonti LiITA ha una forma precisa che l'held-out non copriva: confronto di stringhe tra le due parti di una coppia di traduzione (fonetica e morfologia dialettale). Va aggiunto.

**Risultato principale.**
- Il test principale copre di fatto solo C1, C2 e C8, più pochissimi casi di C9, C11 e C12.
- È anche molto ripetitivo: 100 domande hanno solo **30** firme strutturali distinte (le prime due ne contano 13 ciascuna).
- L'held-out ne ha 53 su 71.
- I sistemi sono stati sviluppati e messi a punto su una porzione stretta del perimetro.

## Asse D — Forma della risposta
- D1 lista di parole: IRI o letterale, con la convenzione fissata: IRI primaria più letterale equivalente.
- D2 lista con attributi (parola + traduzione/emozione/valore).
- D3 singolo valore (conteggio, media).
- D4 classifica o tabella per gruppo.
- D5 sì/no o confronto: assente da entrambi i test; da decidere se è nel perimetro.

Le convenzioni del gold per ciascuna forma vanno fissate qui, prima di scrivere le domande (lezione IRI/letterale).

Fatti sui dati che vincolano le domande (verificati sull'endpoint il 2026-11-10):
- Sentix: il 14,6% dei lemmi ha più valori di polarità. "La polarità di X" va sempre scritta con l'aggregazione esplicita.
- Parmigiano: niente genere e niente varianti.
- ELIta: 9 categorie, cioè le 8 di Plutchik più Amore.

## Proposta: fuori perimetro (da discutere)
- ~~C13 fuori perimetro~~: superato dalla decisione 1, C13 è dentro.
- Domande sui metadati e sulla struttura dei grafi.
- Più di 4 risorse in una domanda: pochissimi casi realistici.

## Implicazioni per il nuovo test set (proposta)
- Stratificazione sull'asse C: per ogni operatore C1–C12 almeno 5 domande, distribuite su risorse diverse (asse A) e operazioni diverse (asse B), così che nessuna firma strutturale si ripeta più di 2 volte.
- Copertura esplicita delle lacune B: ipolemmi, dialetto → italiano, antonimi/sinonimi, soglie di polarità.
- Dimensione indicativa: 70–90 domande.
- Gold scritto e verificato sull'endpoint; convenzioni D fissate in anticipo; file congelato con hash prima di qualunque modifica ai sistemi.
- Una parte (15–20) scritta da persone che non conoscono i sistemi.

## Decisioni (2026-11-10)
1. **Utenti target.** Principalmente linguisti, in misura minore studenti; il pubblico generico è escluso. Conseguenze:
   - le domande possono usare la terminologia tecnica (lemma, ipolemma, iponimo, meronimo, polisemia, POS, polarità);
   - C13 (analisi multi-statistica) **rientra nel perimetro**: sono domande tipiche di un linguista che studia le risorse. Si scrive con ordine fisso degli indicatori e nomi di colonna dichiarati nella domanda, così che resti valutabile;
   - D5 (sì/no) resta fuori: per un linguista conta la lista o il conteggio, non il sì/no;
   - le domande degli studenti sono rappresentate da formulazioni meno tecniche delle stesse celle.
2. **Lingua.** Il nuovo test include domande in italiano.
   - Proposta: ogni domanda ha una formulazione italiana (`nl_it`) e una inglese (`nl_en`), scritte entrambe in modo naturale, non tradotte parola per parola.
   - La valutazione principale è sull'italiano; l'inglese serve al confronto con la valutazione 1.
   - Oggi nessuno dei due test ha varianti italiane. Il supporto all'italiano dei tre sistemi va verificato:
     - NL2SPARQL ha l'opzione `--language`;
     - MoSAIC riconosce alcune formule italiane in `utils.py` ("inizia con", "finisce con");
     - PRISMA ha prompt in inglese.
3. **Autori.** Nessun autore esterno: le domande le scrive la stessa persona che ha sviluppato i sistemi. Mitigazioni:
   - **celle prima delle domande**: la griglia A×B×C×D si fissa per prima e le domande si scrivono per riempire le celle, non a partire dai sistemi;
   - **semi estratti a caso**: parole, emozioni, prefissi e soglie si scelgono per campionamento dalle risorse (con risposta non vuota e non enorme), non a mano;
   - **tipi di domanda da fonti esterne**: si ricavano tipi di domanda dagli studi pubblicati che usano LiITA, CompL-it, ELIta, Sentix e i lessici dialettali, cioè domande che i linguisti si sono effettivamente posti;
   - **congelamento**: il gold si congela (con hash) prima di toccare i sistemi; nessuna domanda si rimuove o modifica dopo aver visto gli output, salvo errori del gold documentati;
   - il limite va dichiarato nella tesi.
5. **Nuove operazioni CompL-it (decisione del 2026-11-10).**
   - Entrano B12 (tipi semantici e tratti) e B13 (relazioni funzionali e derivazionali), con poche domande.
   - B14 (esempi e note d'uso) resta fuori, perché la risposta è testo libero.
6. **Metadati (decisione del 2026-11-10).** Le domande sui metadati entrano in una piccola categoria a parte (M), del tipo "quali risorse/lessici contiene LiITA".
4. **Held-out → set di sviluppo.** I miglioramenti si mettono a punto sull'held-out (71 domande). Il nuovo test resta l'unica misura di generalizzazione.

## Griglia del nuovo test (proposta, 2026-11-10)

### Quote per operatore (86 domande)

| Gruppo | N | Vincoli di copertura |
|---|---|---|
| S — semplici (una risorsa, un'operazione B) | 20 | ogni B1–B13 almeno una volta; B11 (varianti/ipolemmi) 2, B12 2, B13 2; almeno 3 sul lato dialettale (morfologia dialettale, dialetto → italiano) |
| C1 congiunzione tra risorse | 8 | tutte le coppie tra le 6 risorse rappresentate almeno una volta tra C1 e gli altri gruppi; massimo 4 risorse |
| C2 disgiunzione di valori | 3 | emozioni, POS, relazioni |
| C3 catena | 5 | relazione iterata (2), relazione → traduzione → altra risorsa (2), derivazione → relazione (1) |
| C4 intersezione | 6 | due emozioni (2), iperonimo comune (1), presente in entrambi i dialetti (2), due condizioni di polarità/emozione (1) |
| C5 self-join | 5 | stessa traduzione dialettale (2), stesso iperonimo / co-iponimi (2), stessa base derivazionale CompL-it (1) |
| C6 negazione | 7 | "in X ma non in Y" tra risorse diverse (5), negazione di relazione (1), di emozione (1) |
| C7 unione | 4 | due dialetti (1), emozione ∪ polarità (1), due relazioni (1), due tipi semantici (1) |
| C8 per gruppo / classifica | 6 | per POS, per emozione, per tipo semantico, per dialetto; "il più ..." espresso con HAVING = MAX, non con LIMIT |
| C9 filtro su aggregato | 4 | più di N traduzioni, più di N sensi, più di N emozioni, più di N iponimi |
| C10 confronto con riferimento | 3 | polarità, numero di sensi, conteggio per emozione |
| C11 confronto tra variabili | 5 | coppia di traduzione italiano–dialetto (3: fonetica, suffisso), varianti dialettali (1), valori di polarità (1) |
| C12 aggregazione annidata | 3 | media di conteggi per elemento |
| C13 multi-statistica | 4 | indicatori e ordine delle colonne dichiarati nella domanda |
| M metadati | 3 | lessici e lemma bank presenti, conteggi per risorsa |

Altri vincoli:
- nessuna firma strutturale ripetuta più di 2 volte;
- ogni risorsa compare in almeno 15 domande;
- circa 2/3 delle formulazioni sono tecniche (linguisti) e 1/3 discorsive (studenti), distribuite su tutti i gruppi.

### Convenzioni del gold (asse D), fissate prima di scrivere le domande
1. **Liste di parole** (corretto il 2026-11-10 durante la scrittura del blocco S, per allineamento al valutatore congelato): liste di lemmi LiITA e dialettali → letterale primario (`italianWord`, `sicilianWord`, `parmigianoWord`) con SELECT DISTINCT; liste di parole CompL-it → IRI primario + letterale equivalente; emozioni → IRI `emotion` + `emotionLabel` equivalente. È esattamente la convenzione del test principale e dell'held-out allineato.
2. **Lemmi italiani** = `lila:Lemma` ∪ `lila:Hypolemma`, salvo che la domanda dica esplicitamente "lemmi" in senso stretto.
3. **Conteggi**: `COUNT(DISTINCT ...)` sull'entità dichiarata nella domanda (lemmi, parole, sensi, traduzioni).
4. **Polarità**: la domanda dichiara sempre l'aggregazione ("valore massimo", "media", "tutti i valori"); i valori si confrontano come `xsd:float`.
5. **"Il più/il meno"**: gold con sottoquery MAX/MIN e pareggi inclusi, mai `ORDER BY ... LIMIT 1` (il valutatore toglie LIMIT).
6. **C13**: i nomi delle colonne sono fissati nel gold e la domanda elenca gli indicatori in quell'ordine.
7. **Senza risposta**: non sono ammesse domande con risposta vuota; le domande con più di 500 righe si evitano o si restringono.
8. **Lingue**: `nl_it` (principale) e `nl_en`, scritte entrambe in modo naturale.
9. **Semi**: estratti per campionamento casuale (seed fisso registrato), tra quelli con risposta compresa fra 1 e 500 righe.

### Procedura
1. Script di campionamento dei semi per cella (seed registrato).
2. Scrittura di domande e gold cella per cella, con esecuzione sull'endpoint.
3. Revisione: ogni gold controllato su 3 righe a campione.
4. Congelamento: file JSON + hash SHA-256 in `observations.md`, **prima** di qualunque modifica ai sistemi.
