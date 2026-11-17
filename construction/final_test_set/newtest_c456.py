"""New test set, blocks C4 (intersection), C5 (self-join), C6 (negation): 18 questions.

Derived seeds (cells whose question needs a second value drawn from the first seed's answer) use their own
RNG random.Random(f"20261110-{cell}-...") over the sorted candidates:
  C4-03 two hyponyms of 'rilievo' -> 'dosso', 'tumulo';  C5-01 an Italian word translated by 'greja' -> 'mandria';
  C5-03 a hyponym of 'scrittore' -> 'novelliere';  C4-06 emotion pairs tried in sampled order until non-empty.
Cells redefined before writing (documented):
  C5-05: CompL-it derivational links are one-to-one (no adjective has two derived words in the sample), so
         "same base" is impossible -> self-join on the dialect side: other Sicilian lemmas sharing an Italian
         translation with the Sicilian X (Italian word drawn from sic_transl n 3..6 -> 'fallire' -> X 'arrùmpiri').
  C6-05: "without a CompL-it definition" would need a per-row federated NOT EXISTS -> "without a linked CompL-it
         entry" (links are in the LiITA graph <http://liita.it/compl-it>).
Fixes after the first run (empty or trivial answers -> next reserve, documented):
  C5-02 'principale' (prinsipäl) gives 0 rows -> reserve 1 'baracón', Italian word drawn among its translations
        (baracca, crapulone) -> 'crapulone'.
  C5-04 'sistema' and both reserves give 0 rows (parts shared by two wholes are rare in CompL-it) -> pool rebuilt for
        this cell (words sharing a part with 2..15 other words, 415 candidates), redrawn with RNG "C5-04-redraw" -> 'insalata'.
  C6-06 NOT EXISTS inside SERVICE is refused by Virtuoso (SPARQL_SD_PROBE permission) -> OPTIONAL + !BOUND;
        'bosco' and reserve 'verdura' return all their hyponyms (trivial) -> reserve 2 'valore' (12 of 13).
  C5-01/C5-02: "same translation" = same dialect WRITTEN FORM. Neither the shared lexical entry nor the shared lemma
        works: Parmigiano has one entry per Italian sense and even distinct lemmas with the same spelling
        ('baracón' for crapulone and for baracca).
usage: python newtest_c456.py -> runs every gold, writes newtest_c456.json
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newtest_s import PFX, IT, SIC, PAR, CL, av, run, HERE
from newtest_c123 import LINK_SIC, LINK_PAR, EMO, POL

NO_SIC = f"""FILTER NOT EXISTS {{
    ?sicItEntry ontolex:canonicalForm ?italianLemma ; vartrans:translatableAs ?sicEntry .
    ?sicEntry ontolex:canonicalForm ?sicilianLemma . ?sicilianLemma dcterms:isPartOf {SIC} .
  }}"""
NO_PAR = f"""FILTER NOT EXISTS {{
    ?parItEntry ontolex:canonicalForm ?italianLemma ; vartrans:translatableAs ?parEntry .
    ?parEntry ontolex:canonicalForm ?parmigianoLemma . ?parmigianoLemma dcterms:isPartOf {PAR} .
  }}"""
HAS_SIC = f"""?sicItEntry ontolex:canonicalForm ?italianLemma ; vartrans:translatableAs ?sicEntry .
  ?sicEntry ontolex:canonicalForm ?sicilianLemma . ?sicilianLemma dcterms:isPartOf {SIC} ."""
HAS_PAR = f"""?parItEntry ontolex:canonicalForm ?italianLemma ; vartrans:translatableAs ?parEntry .
  ?parEntry ontolex:canonicalForm ?parmigianoLemma . ?parmigianoLemma dcterms:isPartOf {PAR} ."""


def seed_cl(word, var="seed", sense="seedSense"):
    return f"""?{var} ontolex:canonicalForm [ ontolex:writtenRep ?{var}Wr ] ; ontolex:sense ?{sense} .
    FILTER(STR(?{var}Wr) = "{word}")"""


Q = [
 # ---------------- C4 intersection
 dict(id=4037, cell="C4-01", seed_used=0, register="studente",
      nl_it="Quali parole esprimono insieme gioia e rabbia secondo ELIta?",
      nl_en="Which words express both joy and anger according to ELIta?",
      sparql=f"""SELECT DISTINCT ?italianWord WHERE {{
  GRAPH <http://liita.it/data> {{ {IT} }}
  {EMO} elita:Gioia , elita:Rabbia .
}}""", answer_variables=av(["italianWord"])),
 dict(id=4038, cell="C4-02", seed_used=0, register="tecnico",
      nl_it="Tra le parole associate in ELIta sia a Disgusto sia a Sorpresa, quali hanno una polarità Sentix negativa?",
      nl_en="Among the words associated in ELIta with both Disgust and Surprise, which have a negative Sentix polarity?",
      sparql=f"""SELECT DISTINCT ?italianWord WHERE {{
  GRAPH <http://liita.it/data> {{ {IT} }}
  {EMO} elita:Disgusto , elita:Sorpresa .
  ?polarityEntry ontolex:canonicalForm ?italianLemma ; marl:hasPolarity ?polarity .
  FILTER(CONTAINS(LCASE(STR(?polarity)), "negative"))
}}""", answer_variables=av(["italianWord"])),
 dict(id=4039, cell="C4-03", seed_used=0, register="tecnico",
      nl_it="Quali iperonimi hanno in comune 'dosso' e 'tumulo' in CompL-it?",
      nl_en="Which hypernyms do 'dosso' and 'tumulo' have in common in CompL-it?",
      sparql=f"""SELECT DISTINCT ?hypernymWord ?italianWord WHERE {{
  {CL} {{
    {seed_cl("dosso", "a", "aSense")}
    {seed_cl("tumulo", "b", "bSense")}
    ?aSense lexinfo:hyponym ?relSense . ?bSense lexinfo:hyponym ?relSense .
    ?hypernymWord ontolex:sense ?relSense ; ontolex:canonicalForm [ ontolex:writtenRep ?italianWord ] .
  }}
}}""", answer_variables=av(["hypernymWord"], equivalents={"hypernymWord": "italianWord"})),
 dict(id=4040, cell="C4-04", seed_used=0, register="studente",
      nl_it="Quali nomi che finiscono in '-glio' si possono dire sia in siciliano sia in parmigiano?",
      nl_en="Which nouns ending in '-glio' can be said both in Sicilian and in Parmigiano?",
      sparql=f"""SELECT DISTINCT ?italianWord WHERE {{
  GRAPH <http://liita.it/data> {{ {IT} ?italianLemma lila:hasPOS lila:noun . }}
  FILTER(STRENDS(STR(?italianWord), "glio"))
  {HAS_SIC}
  {HAS_PAR}
}}""", answer_variables=av(["italianWord"])),
 dict(id=4041, cell="C4-05", seed_used=None, register="studente",
      nl_it="Quanti verbi italiani si possono tradurre sia in siciliano sia in parmigiano?",
      nl_en="How many Italian verbs can be translated both into Sicilian and into Parmigiano?",
      sparql=f"""SELECT (COUNT(DISTINCT ?italianLemma) AS ?count) WHERE {{
  GRAPH <http://liita.it/data> {{ {IT} ?italianLemma lila:hasPOS lila:verb . }}
  {HAS_SIC}
  {HAS_PAR}
}}""", answer_variables=av(aggregates=["count"])),
 dict(id=4042, cell="C4-06", seed_used=0, register="tecnico",
      nl_it="Quali iponimi CompL-it di 'essere' sono associati in ELIta sia a Paura sia a Disgusto?",
      nl_en="Which CompL-it hyponyms of 'essere' are associated in ELIta with both Fear and Disgust?",
      sparql=f"""SELECT DISTINCT ?italianWord WHERE {{
  {CL} {{
    {seed_cl("essere")}
    ?seedSense lexinfo:hypernym ?relSense . ?relWord ontolex:sense ?relSense .
  }}
  ?relWord ontolex:canonicalForm ?italianLemma .
  GRAPH <http://liita.it/data> {{ {IT} }}
  {EMO} elita:Paura , elita:Disgusto .
}}""", answer_variables=av(["italianWord"])),
 # ---------------- C5 self-join
 dict(id=4043, cell="C5-01", seed_used=0, register="studente",
      nl_it="Quali altre parole italiane si traducono in siciliano con la stessa parola usata per 'mandria'?",
      nl_en="Which other Italian words are translated into Sicilian with the same word used for 'mandria' (herd)?",
      sparql=f"""SELECT ?italianWord (SAMPLE(?sicilianWord) AS ?sharedSicilianWord) WHERE {{
  GRAPH <http://liita.it/data> {{ ?seedLemma a ?seedType ; ontolex:writtenRep ?seedWr . FILTER(?seedType IN (lila:Lemma, lila:Hypolemma)) }}
  FILTER(STR(?seedWr) = "mandria")
  ?seedEntry ontolex:canonicalForm ?seedLemma ; vartrans:translatableAs ?sicEntry .
  ?sicEntry ontolex:canonicalForm ?sicilianLemma .
  ?sicilianLemma dcterms:isPartOf {SIC} ; ontolex:writtenRep ?sicilianWord .
  ?otherSicLemma dcterms:isPartOf {SIC} ; ontolex:writtenRep ?otherSicWr . FILTER(STR(?otherSicWr) = STR(?sicilianWord))
  ?otherSicEntry ontolex:canonicalForm ?otherSicLemma .
  ?otherEntry vartrans:translatableAs ?otherSicEntry ; ontolex:canonicalForm ?italianLemma .
  GRAPH <http://liita.it/data> {{ {IT} }}
  FILTER(?italianLemma != ?seedLemma && STR(?italianWord) != "mandria")
}}
GROUP BY ?italianWord""", answer_variables=av(["italianWord"], ["sharedSicilianWord"])),
 dict(id=4044, cell="C5-02", seed_used=1, register="tecnico",
      nl_it="Quali altre parole italiane condividono con 'crapulone' una traduzione parmigiana?",
      nl_en="Which other Italian words share a Parmigiano translation with 'crapulone'?",
      sparql=f"""SELECT ?italianWord (SAMPLE(?parmigianoWord) AS ?sharedParmigianoWord) WHERE {{
  GRAPH <http://liita.it/data> {{ ?seedLemma a ?seedType ; ontolex:writtenRep ?seedWr . FILTER(?seedType IN (lila:Lemma, lila:Hypolemma)) }}
  FILTER(STR(?seedWr) = "crapulone")
  ?seedEntry ontolex:canonicalForm ?seedLemma ; vartrans:translatableAs ?parEntry .
  ?parEntry ontolex:canonicalForm ?parmigianoLemma .
  ?parmigianoLemma dcterms:isPartOf {PAR} ; ontolex:writtenRep ?parmigianoWord .
  ?otherParLemma dcterms:isPartOf {PAR} ; ontolex:writtenRep ?otherParWr . FILTER(STR(?otherParWr) = STR(?parmigianoWord))
  ?otherParEntry ontolex:canonicalForm ?otherParLemma .
  ?otherEntry vartrans:translatableAs ?otherParEntry ; ontolex:canonicalForm ?italianLemma .
  GRAPH <http://liita.it/data> {{ {IT} }}
  FILTER(?italianLemma != ?seedLemma && STR(?italianWord) != "crapulone")
}}
GROUP BY ?italianWord""", answer_variables=av(["italianWord"], ["sharedParmigianoWord"])),
 dict(id=4045, cell="C5-03", seed_used=0, register="tecnico",
      nl_it="Quali sono i co-iponimi di 'novelliere' in CompL-it, cioè le altre parole che hanno un suo stesso iperonimo?",
      nl_en="What are the co-hyponyms of 'novelliere' in CompL-it, i.e. the other words sharing one of its hypernyms?",
      sparql=f"""SELECT DISTINCT ?relatedWord ?italianWord WHERE {{
  {CL} {{
    {seed_cl("novelliere")}
    ?seedSense lexinfo:hyponym ?hyperSense . ?relSense lexinfo:hyponym ?hyperSense .
    FILTER(?relSense != ?seedSense)
    ?relatedWord ontolex:sense ?relSense ; ontolex:canonicalForm [ ontolex:writtenRep ?italianWord ] .
    FILTER(?relatedWord != ?seed)
  }}
}}""", answer_variables=av(["relatedWord"], equivalents={"relatedWord": "italianWord"})),
 dict(id=4046, cell="C5-04", seed_used=None, register="tecnico",
      nl_it="Quali altre parole hanno in CompL-it almeno una parte (meronimo) in comune con 'insalata'?",
      nl_en="Which other words have at least one part (meronym) in common with 'insalata' in CompL-it?",
      sparql=f"""SELECT DISTINCT ?relatedWord ?italianWord WHERE {{
  {CL} {{
    {seed_cl("insalata")}
    ?partSense lexinfo:partMeronym ?seedSense . ?partSense lexinfo:partMeronym ?relSense .
    FILTER(?relSense != ?seedSense)
    ?relatedWord ontolex:sense ?relSense ; ontolex:canonicalForm [ ontolex:writtenRep ?italianWord ] .
    FILTER(?relatedWord != ?seed)
  }}
}}""", answer_variables=av(["relatedWord"], equivalents={"relatedWord": "italianWord"})),
 dict(id=4047, cell="C5-05", seed_used=None, register="tecnico",
      nl_it="Quali altri lemmi siciliani traducono almeno una delle parole italiane tradotte da 'arrùmpiri'?",
      nl_en="Which other Sicilian lemmas translate at least one of the Italian words translated by 'arrùmpiri'?",
      sparql=f"""SELECT DISTINCT ?sicilianWord WHERE {{
  ?seedLemma dcterms:isPartOf {SIC} ; ontolex:writtenRep ?seedWr . FILTER(STR(?seedWr) = "arrùmpiri")
  ?seedEntry ontolex:canonicalForm ?seedLemma .
  ?itEntry vartrans:translatableAs ?seedEntry ; ontolex:canonicalForm ?italianLemma .
  ?itEntry2 ontolex:canonicalForm ?italianLemma ; vartrans:translatableAs ?sicEntry .
  ?sicEntry ontolex:canonicalForm ?sicilianLemma .
  ?sicilianLemma dcterms:isPartOf {SIC} ; ontolex:writtenRep ?sicilianWord .
  FILTER(?sicilianLemma != ?seedLemma)
}}""", answer_variables=av(["sicilianWord"])),
 # ---------------- C6 negation
 dict(id=4048, cell="C6-01", seed_used=0, register="studente",
      nl_it="Quali modi di parlare elencati da CompL-it non hanno una traduzione in siciliano?",
      nl_en="Which ways of 'parlare' (speaking) listed by CompL-it have no translation into Sicilian?",
      sparql=f"""SELECT DISTINCT ?hyponymWord ?italianWord WHERE {{
  {CL} {{
    {seed_cl("parlare")}
    ?seedSense lexinfo:hypernym ?relSense .
    ?hyponymWord ontolex:sense ?relSense ; ontolex:canonicalForm [ ontolex:writtenRep ?italianWord ] .
  }}
  FILTER NOT EXISTS {{
    ?hyponymWord ontolex:canonicalForm ?italianLemma .
    ?sicItEntry ontolex:canonicalForm ?italianLemma ; vartrans:translatableAs ?sicEntry .
    ?sicEntry ontolex:canonicalForm ?sicilianLemma . ?sicilianLemma dcterms:isPartOf {SIC} .
  }}
}}""", answer_variables=av(["hyponymWord"], equivalents={"hyponymWord": "italianWord"})),
 dict(id=4049, cell="C6-02", seed_used=0, register="studente",
      nl_it="Quali verbi legati all'emozione Aspettativa non hanno un corrispondente in parmigiano?",
      nl_en="Which verbs linked to the emotion Anticipation have no equivalent in Parmigiano?",
      sparql=f"""SELECT DISTINCT ?italianWord WHERE {{
  GRAPH <http://liita.it/data> {{ {IT} ?italianLemma lila:hasPOS lila:verb . }}
  {EMO} elita:Aspettativa .
  {NO_PAR}
}}""", answer_variables=av(["italianWord"])),
 dict(id=4050, cell="C6-03", seed_used=0, register="tecnico",
      nl_it="Quali verbi in '-cere' hanno un valore di polarità in Sentix ma nessuna emozione in ELIta?",
      nl_en="Which verbs ending in '-cere' have a polarity value in Sentix but no emotion in ELIta?",
      sparql=f"""SELECT DISTINCT ?italianWord WHERE {{
  GRAPH <http://liita.it/data> {{ {IT} ?italianLemma lila:hasPOS lila:verb . }}
  FILTER(STRENDS(STR(?italianWord), "cere"))
  ?polarityEntry ontolex:canonicalForm ?italianLemma ; marl:hasPolarity ?polarityClass ; marl:hasPolarityValue ?polarityRaw .
  FILTER NOT EXISTS {{ ?emotionEntry ontolex:canonicalForm ?italianLemma ; elita:HasEmotion ?emotion . }}
}}""", answer_variables=av(["italianWord"])),
 dict(id=4051, cell="C6-04", seed_used=0, register="tecnico",
      nl_it="Quali verbi in '-nere' hanno una traduzione siciliana ma nessuna traduzione parmigiana?",
      nl_en="Which verbs ending in '-nere' have a Sicilian translation but no Parmigiano translation?",
      sparql=f"""SELECT DISTINCT ?italianWord WHERE {{
  GRAPH <http://liita.it/data> {{ {IT} ?italianLemma lila:hasPOS lila:verb . }}
  FILTER(STRENDS(STR(?italianWord), "nere"))
  {HAS_SIC}
  {NO_PAR}
}}""", answer_variables=av(["italianWord"])),
 dict(id=4052, cell="C6-05", seed_used=None, register="tecnico",
      nl_it="Quali parole associate all'emozione Rabbia in ELIta non sono collegate a nessuna voce di CompL-it?",
      nl_en="Which words associated with the emotion Anger in ELIta are not linked to any CompL-it entry?",
      sparql=f"""SELECT DISTINCT ?italianWord WHERE {{
  GRAPH <http://liita.it/data> {{ {IT} }}
  {EMO} elita:Rabbia .
  FILTER NOT EXISTS {{ GRAPH <http://liita.it/compl-it> {{ ?complitWord ontolex:canonicalForm ?italianLemma }} }}
}}""", answer_variables=av(["italianWord"])),
 dict(id=4053, cell="C6-06", seed_used=2, register="tecnico",
      nl_it="Quali iponimi di 'valore' in CompL-it non hanno a loro volta iponimi?",
      nl_en="Which hyponyms of 'valore' (value) in CompL-it have no hyponyms of their own?",
      sparql=f"""SELECT DISTINCT ?hyponymWord ?italianWord WHERE {{
  {CL} {{
    {seed_cl("valore")}
    ?seedSense lexinfo:hypernym ?relSense .
    ?hyponymWord ontolex:sense ?relSense ; ontolex:canonicalForm [ ontolex:writtenRep ?italianWord ] .
    OPTIONAL {{ ?hyponymWord ontolex:sense ?anySense . ?anySense lexinfo:hypernym ?subSense . }}
    FILTER(!BOUND(?subSense))
  }}
}}""", answer_variables=av(["hyponymWord"], equivalents={"hyponymWord": "italianWord"})),
 dict(id=4054, cell="C6-07", seed_used=None, register="studente",
      nl_it="Quali aggettivi hanno almeno un valore di polarità Sentix superiore a 0,5 ma non sono associati a nessuna emozione in ELIta?",
      nl_en="Which adjectives have at least one Sentix polarity value above 0.5 but are not associated with any emotion in ELIta?",
      sparql=f"""SELECT DISTINCT ?italianWord WHERE {{
  GRAPH <http://liita.it/data> {{ {IT} ?italianLemma lila:hasPOS lila:adjective . }}
  {POL}
  FILTER(?polarityValue > 0.5)
  FILTER NOT EXISTS {{ ?emotionEntry ontolex:canonicalForm ?italianLemma ; elita:HasEmotion ?emotion . }}
}}""", answer_variables=av(["italianWord"])),
]


def main(only=None):
    cells = {c["id"]: c for c in json.load(open(os.path.join(HERE, "cells_sampled.json"), encoding="utf-8"))["cells"]}
    out = []
    for q in Q:
        c = cells[q["cell"]]
        su = q.pop("seed_used")
        q = {**q, "group": c["group"], "resources": c["resources"], "ops": c["ops"],
             "seed": c["seeds"][su] if su is not None and c.get("seeds") else None, "params": c.get("params"),
             "sparql": PFX + "\n" + q["sparql"]}
        try:
            rows = run(q["sparql"], prefixes=False)
            q["gold_rows"] = len(rows)
            print(f"{q['id']} {q['cell']:6s} rows={len(rows):4d}  {rows[:3]}")
        except Exception as e:  # noqa: BLE001
            q["gold_rows"] = None
            print(f"{q['id']} {q['cell']:6s} ERROR {str(e)[:300]}")
        out.append(q)
    json.dump(out, open(os.path.join(HERE, "newtest_c456.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
