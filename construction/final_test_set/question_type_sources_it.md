# Fonti per i tipi di domanda (perimetro, 2026-11-10)

Obiettivo: ancorare le celle del perimetro a domande che i linguisti si pongono davvero su LiITA e sulla KB gemella LiLa. Serve a compensare l'assenza di autori esterni.

## 1. Query di esempio sul sito LiITA (https://www.liita.it/?page_id=158, consultato il 2026-11-10)

| # | Domanda (parafrasi) | Risorse | Operatori |
|---|---|---|---|
| 1 | Distribuzione dei lemmi per parte del discorso | LiITA | B3, C8 |
| 2 | Quanti nomi terminano in -ione | LiITA | B2, B3, B10 |
| 3 | Lemmi che iniziano con "infra-" | LiITA | B2 |
| 4 | Parole la cui definizione CompL-it inizia con "uccello", con traduzione parmigiana | CompL-it, Parm. | B5, B7, C1 |
| 5 | Parole la cui definizione inizia con "colore" | CompL-it | B5 |
| 6 | Lemmi LiITA e parmigiani degli iponimi di "colore"\* | CompL-it, Parm. | B4, B7, C1 |
| 7 | Lemmi LiITA e parmigiani dei meronimi di "giorno" | CompL-it, Parm. | B4, B7, C1 |
| 8 | Lemmi siciliani con alternanza "ed"/"ied" | Sicil. | B2 (lato dialettale, varianti) |
| 9 | Nomi comuni siciliani in "-ìa", con traduzione italiana | Sicil., LiITA | B2, B3, B7 (dialetto → italiano) |

\* Come è scritta, la query segue `lexinfo:hypernym` dal senso di "colore", quindi restituisce iperonimi, non iponimi. È lo stesso problema di direzione visto nel gold di NL2SPARQL.

Osservazioni:
- Gli esempi del sito sono tutti C1 o C8. È la stessa porzione stretta da cui sono partiti i sistemi.
- Gli esempi 8 e 9 (morfologia sul lato dialettale e traduzione dialetto → italiano) sono assenti dal test principale.

## 2. Raccolta di query LiLa (https://github.com/CIRCSE/SPARQL-queries, 66 query, consultata il 2026-11-10)

LiLa è la KB gemella per il latino, con lo stesso modello a lemma bank. Le query sono state scritte dal gruppo di ricerca per studi linguistici reali e indicano i tipi di domanda dei linguisti. Le query su corpora e token non hanno un corrispettivo in LiITA, che oggi non collega corpora; i tipi di operatore però si trasferiscono.

| Operatore | Query LiLa (esempi) | N |
|---|---|---|
| **C6 negazione / differenza tra risorse** | lemmi usati *solo* nel De Vulgari Eloquentia, *solo* in Fibonacci, *solo* in Catullo; lemmi LASLA *privi* di voce nel Lexicala; lemmi del Lexicon Bohemorum che citano "natura" ma *assenti* dal Lewis & Short | 6 |
| **C4 intersezione tra risorse** | lemmi presenti sia in CLaSSES sia nel De bello gallico; lemmi con un affisso presenti in UDante e IT-TB; synset/sintassi comuni a UDante e IT-TB | 4 |
| **C5 self-join** (stessa base lessicale) | lemmi che condividono la base di *patior*; lemmi con la stessa base in Dante e IT-TB; voci Velez con la stessa base | 3 |
| **C3 catena** | forme del perfetto dei verbi prefissati da *pono* (word formation → flessione) | 1 |
| **C8 per gruppo / classifica** | affissi più frequenti sui nomi; lemmi per POS e genere; lemmi per micro-classe flessiva; token per secolo | 5 |
| **C9 HAVING** | synset evocati da molte voci | 1 |
| **C13 multi-statistica / confronto tra distribuzioni** | frequenze relative in Ennio vs Lucano; sentiment per testo e per paragrafo (LatinAffectus) | 3 |
| B5 definizioni | verbi con definizione Lewis & Short che contiene "grow"; lemmi con definizione Velez che contiene una parola | 3 |
| B2/B3 morfologia e POS | lemmi per POS e suffisso; lemmi con un affisso | 3 |
| B9 polarità | lemmi LASLA con polarità negativa (con conteggi); lemmi UDante con una data polarità | 2 |
| metadati (fuori perimetro) | quali corpora / lessici / documenti contiene la KB; tagset flessivo | 6 |

Osservazioni:
- Nelle domande reali dei linguisti, **negazione e intersezione tra risorse sono tra i tipi più frequenti**: "presente in X ma non in Y" e "presente sia in X sia in Y". Il test principale di LiITA non ne contiene nessuna.
- Sono domande di **confronto tra risorse**, cioè la ragione d'essere di una KB di risorse interoperabili.
- I metadati ("quali risorse contiene la KB") sono una domanda reale dei linguisti. Va deciso se rientrano nel perimetro.

## 3. Articoli (in bibliografia e più recenti)
Estrazione dai PDF (full text) fatta da un subagente il 2026-11-10; le domande sono parafrasate. [IT] = famiglia LiITA, [LA] = LiLa.

| Fonte | Domande / scenari attestati | Operatori |
|---|---|---|
| Litta et al., LDK 2025 [IT] (`littaLiITAKnowledgeBase2025`) | nessuna domanda; dati: 113.112 lemmi + 16.330 ipolemmi, genere sui nomi, `lemmaVariant` (pluralia tantum, riflessivi) | B1, B3 |
| Litta et al., AIUCD 2025 [IT] (**non in bibliografia**) | occorrenze di *andare* in più corpora; token con proprietà di più lessici (scenario futuro) | C3 |
| Di Palma et al., CLiC-it 2025 [IT] (`dipalmaLinkingEmotionsAffective2025`) | lemmi per emozione; distribuzione delle classi Sentix; polarità media per emozione ("qual è la più negativa?"); **lemmi con Gioia E Tristezza** per classe di polarità; quali di questi hanno polarità negativa | C8, C4, C13, B9 |
| Litta et al., CLiC-it 2025, CompL-it [IT] (`littaLinkingCompLitLiITA2025`) | definizione che inizia con *uccello* + traduzione parmigiana; iponimi di *colore* con definizioni, lemmi LiITA e traduzioni | B5, B4, B7, C1 |
| Sprugnoli et al., CLiC-it 2025, siciliano [IT] (`sprugnolCiallabaciallaSicilianLiITA2025`) | lemmi siciliani con varianti in *d* e in *r*; **lemmi con variante *ed* e variante *ied*** (confronto tra varianti dello stesso lemma); nomi in *-ìa* con traduzione italiana | B2 dialettale, C11, B7 inversa |
| Sprugnoli & Muscianisi 2025, parmigiano [IT] (`sprugnolLinkedDataDialectologyParma2025`) | **parole italiane in *s* con traduzione parmigiana in *z*** (266); *chi/che* → *ci*; aggettivi in *-bile* e forme dialettali; radice *vecch-*; traduzioni di *donna* con note d'uso; **parole italiane con più equivalenti dialettali** (classifica) | C11 (confronto di stringhe tra coppie di traduzione), B2, C8, C9 |
| Giovannetti et al., LREC 2026, CompL-it [IT] (**non in bibliografia**) | nessuna domanda; nuovi dati: 254 tipi semantici, 2.702 tratti, definizioni ed esempi | (nuove B) |
| Giovannetti et al., CLiC-it 2026, "Exploring CompL-it" [IT] | full text non accessibile | — |
| Passarotti & Litta 2026, Umanistica Digitale [LA] (**non in bibliografia**) | frequenza degli affissi sui nomi; lemmi di un synset **o** dei suoi iperonimi + famiglia derivazionale; lemmi con la base di *loquor* presenti **sia** in UDante **sia** in IT-TB; definizione con *natura* ma **assenti** dal Lewis & Short (MINUS); lemmi con polarità negativa in UDante, con conteggi | C8, C7, C3, C5, C4, C6, C13 |
| Litta, Passarotti, Mambrini 2020, PBML [LA] (**non in bibliografia**) | verbi con prefisso *de-* e suffisso *-sc*; lemmi con la base di *formalis* per POS; coppie di affissi più frequenti; derivati presenti in una risorsa e **mancanti** nell'altra | B2, C5, C8, C6, C13 |
| Mambrini, LDL 2026 [LA] (**non in bibliografia**) | morfemi derivazionali nei discorsi di parlanti donne vs uomini; sentiment dei discorsi | C8, C13 |

Nessuna pubblicazione 2025–2026 propone un accesso in linguaggio naturale a LiITA o LiLa. Due articoli lo indicano come obiettivo futuro: CompL-it/LiITA 2025 (RAG + few-shot) e Passarotti & Litta 2026, che propone la raccolta di query come dati di addestramento. È un buon aggancio per la motivazione della tesi.

## 4. Verifiche sull'endpoint (2026-11-10)
- **Sentix**: 3.491 dei 23.984 lemmi LiITA con polarità hanno **più di un valore** (14,6%).
  - Ha senso porre domande come "sia positiva sia negativa".
  - Le domande su "la polarità di X" devono dichiarare l'aggregazione (MAX, AVG o tutti i valori): va fissato come convenzione del gold.
- **LiITA (lemmi)**:
  - `hasGender` 82.388;
  - `hasDegree` 22.465;
  - `hasInflectionType` 16.489;
  - `lemmaVariant` 9.192.
- **Siciliano**: POS, genere (6.684), 13 `lemmaVariant`, più `writtenRep` per lemma (14.529 su 9.769 lemmi: varianti grafiche).
- **Parmigiano**: solo POS e `writtenRep`; **niente genere, niente varianti**. Le domande sul genere dei lemmi parmigiani sono fuori perimetro.
- **CompL-it (endpoint GraphDB)**: oltre alle relazioni `lexinfo` già usate, sono interrogabili:
  - tipi semantici (`complit:hasSemanticType`), tratti (`complit:trait`) ed esempi (`lexinfo:senseExample`);
  - relazioni qualia e funzionali (`usedFor`, `telic`, `instrumental`, `createdBy`, `isTheActivityOf`, ...);
  - relazioni derivazionali (`deadjectivalNoun`, `denominalAdjective`, `derivational`);
  - sinonimi (`complit:synonym`) e antonimi graduati (`antonymGrad`).
  - Attenzione: le query con predicato variabile dentro `SERVICE` da Virtuoso falliscono (errore di permessi); le verifiche sono state fatte direttamente sull'endpoint CompL-it.
