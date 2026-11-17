"""New test set, blocks C1 (conjunction), C2 (disjunction of values), C3 (chain): 16 questions.

Seed rule applied here: when a cell's first seed duplicates the seed of an earlier cell, the next reserve is used
(C1-05: Fiducia/noun already used by C1-03 -> reserve 1, Aspettativa/noun).
Empty or trivial answers -> next reserve: C1-06 type 'Ideo' gives 0 rows -> reserve 1 'RelationalProperty' (12 rows);
C1-08 '-bile' nouns give 1 row (only 'bile' itself) -> reserve 1, adjectives in '-noso' (8 rows).
Cell change before writing: C2-02 gets a Sentix condition (Sentix was in 14 cells, target 15).
usage: python newtest_c123.py -> runs every gold, writes newtest_c123.json
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newtest_s import PFX, IT, SIC, PAR, CL, av, run, HERE

LINK_SIC = f"""?sicItEntry ontolex:canonicalForm ?italianLemma ; vartrans:translatableAs ?sicEntry .
  ?sicEntry ontolex:canonicalForm ?sicilianLemma .
  ?sicilianLemma dcterms:isPartOf {SIC} ; ontolex:writtenRep ?sicilianWord ."""
LINK_PAR = f"""?parItEntry ontolex:canonicalForm ?italianLemma ; vartrans:translatableAs ?parEntry .
  ?parEntry ontolex:canonicalForm ?parmigianoLemma .
  ?parmigianoLemma dcterms:isPartOf {PAR} ; ontolex:writtenRep ?parmigianoWord ."""
EMO = "?emotionEntry ontolex:canonicalForm ?italianLemma ; elita:HasEmotion"
POL = "?polarityEntry ontolex:canonicalForm ?italianLemma ; marl:hasPolarity ?polarityClass ; marl:hasPolarityValue ?polarityRaw . BIND(xsd:float(?polarityRaw) AS ?polarityValue)"

Q = [
 # ---------------- C1 conjunction
 dict(id=4021, cell="C1-01", seed_used=0, register="studente",
      nl_it="Che tipi di formaggio registra CompL-it, e come si dicono in siciliano?",
      nl_en="What kinds of 'formaggio' (cheese) does CompL-it record, and how are they said in Sicilian?",
      sparql=f"""SELECT DISTINCT ?italianWord ?sicilianWord WHERE {{
  {CL} {{
    ?seed ontolex:canonicalForm [ ontolex:writtenRep ?seedWr ] ; ontolex:sense ?seedSense .
    FILTER(STR(?seedWr) = "formaggio")
    ?seedSense lexinfo:hypernym ?relSense .
    ?relWord ontolex:sense ?relSense .
  }}
  ?relWord ontolex:canonicalForm ?italianLemma .
  GRAPH <http://liita.it/data> {{ {IT} }}
  {LINK_SIC}
}}""", answer_variables=av(["italianWord", "sicilianWord"])),
 dict(id=4022, cell="C1-02", seed_used=0, register="tecnico",
      nl_it="Quali parole italiane hanno in CompL-it una definizione che inizia con 'usare', e qual è la loro traduzione parmigiana?",
      nl_en="Which Italian words have a CompL-it definition beginning with 'usare', and what is their Parmigiano translation?",
      sparql=f"""SELECT DISTINCT ?italianWord ?parmigianoWord WHERE {{
  {CL} {{
    ?word ontolex:sense ?sense . ?sense skos:definition ?definition .
    FILTER(STRSTARTS(LCASE(STR(?definition)), "usare"))
  }}
  ?word ontolex:canonicalForm ?italianLemma .
  GRAPH <http://liita.it/data> {{ {IT} }}
  {LINK_PAR}
}}""", answer_variables=av(["italianWord", "parmigianoWord"])),
 dict(id=4023, cell="C1-03", seed_used=0, register="studente",
      nl_it="Come si dicono in parmigiano i sostantivi che in ELIta esprimono fiducia?",
      nl_en="How are the nouns that express trust in ELIta said in Parmigiano?",
      sparql=f"""SELECT DISTINCT ?italianWord ?parmigianoWord WHERE {{
  GRAPH <http://liita.it/data> {{ {IT} ?italianLemma lila:hasPOS lila:noun . }}
  {EMO} elita:Fiducia .
  {LINK_PAR}
}}""", answer_variables=av(["italianWord", "parmigianoWord"])),
 dict(id=4024, cell="C1-04", seed_used=None, register="tecnico",
      nl_it="Quali aggettivi italiani hanno un valore di polarità Sentix superiore a 0,5 e hanno una traduzione siciliana? Indica anche la traduzione.",
      nl_en="Which Italian adjectives have a Sentix polarity value above 0.5 and a Sicilian translation? Give the translation too.",
      sparql=f"""SELECT DISTINCT ?italianWord ?sicilianWord WHERE {{
  GRAPH <http://liita.it/data> {{ {IT} ?italianLemma lila:hasPOS lila:adjective . }}
  {POL}
  FILTER(?polarityValue > 0.5)
  {LINK_SIC}
}}""", answer_variables=av(["italianWord", "sicilianWord"])),
 dict(id=4025, cell="C1-05", seed_used=1, register="tecnico",
      nl_it="Quali sostantivi associati all'emozione Aspettativa in ELIta hanno polarità Sentix positiva?",
      nl_en="Which nouns associated with the emotion Anticipation in ELIta have a positive Sentix polarity?",
      sparql=f"""SELECT DISTINCT ?italianWord WHERE {{
  GRAPH <http://liita.it/data> {{ {IT} ?italianLemma lila:hasPOS lila:noun . }}
  {EMO} elita:Aspettativa .
  ?polarityEntry ontolex:canonicalForm ?italianLemma ; marl:hasPolarity ?polarity .
  FILTER(CONTAINS(LCASE(STR(?polarity)), "positive"))
}}""", answer_variables=av(["italianWord"])),
 dict(id=4026, cell="C1-06", seed_used=1, register="tecnico",
      nl_it="Quali parole del tipo semantico SIMPLE 'RelationalProperty' (proprietà relazionali) sono associate a un'emozione in ELIta, e a quale?",
      nl_en="Which words of the SIMPLE semantic type 'RelationalProperty' are associated with an emotion in ELIta, and with which one?",
      sparql=f"""SELECT DISTINCT ?italianWord ?emotion ?emotionLabel WHERE {{
  {CL} {{ ?word ontolex:sense ?sense . ?sense complit:hasSemanticType <http://simpleOntology#A26-RelationalProperty> . }}
  ?word ontolex:canonicalForm ?italianLemma .
  GRAPH <http://liita.it/data> {{ {IT} }}
  {EMO} ?emotion . ?emotion rdfs:label ?emotionLabel .
}}""", answer_variables=av(["italianWord", "emotion"], equivalents={"emotion": "emotionLabel"})),
 dict(id=4027, cell="C1-07", seed_used=0, register="studente",
      nl_it="Quali parti dello 'zodiaco', secondo CompL-it, suscitano un'emozione in ELIta?",
      nl_en="Which parts of the 'zodiaco' (zodiac), according to CompL-it, evoke an emotion in ELIta?",
      sparql=f"""SELECT DISTINCT ?italianWord WHERE {{
  {CL} {{
    ?seed ontolex:canonicalForm [ ontolex:writtenRep ?seedWr ] ; ontolex:sense ?seedSense .
    FILTER(STR(?seedWr) = "zodiaco")
    ?relSense lexinfo:partMeronym ?seedSense .
    ?relWord ontolex:sense ?relSense .
  }}
  ?relWord ontolex:canonicalForm ?italianLemma .
  GRAPH <http://liita.it/data> {{ {IT} }}
  {EMO} ?emotion .
}}""", answer_variables=av(["italianWord"])),
 dict(id=4028, cell="C1-08", seed_used=1, register="tecnico",
      nl_it="Per gli aggettivi in '-noso' che hanno sia un valore di polarità Sentix sia una traduzione parmigiana, elenca la parola, la traduzione e il valore di polarità massimo.",
      nl_en="For the adjectives ending in '-noso' that have both a Sentix polarity value and a Parmigiano translation, list the word, the translation and the highest polarity value.",
      sparql=f"""SELECT ?italianWord ?parmigianoWord (MAX(?polarityValue) AS ?maxValue) WHERE {{
  GRAPH <http://liita.it/data> {{ {IT} ?italianLemma lila:hasPOS lila:adjective . }}
  FILTER(STRENDS(STR(?italianWord), "noso"))
  {POL}
  {LINK_PAR}
}}
GROUP BY ?italianWord ?parmigianoWord""", answer_variables=av(["italianWord", "parmigianoWord"], numeric=["maxValue"])),
 # ---------------- C2 disjunction of values
 dict(id=4029, cell="C2-01", seed_used=0, register="tecnico",
      nl_it="Quali aggettivi sono associati in ELIta all'emozione Amore oppure all'emozione Disgusto?",
      nl_en="Which adjectives are associated in ELIta with the emotion Love or with the emotion Disgust?",
      sparql=f"""SELECT DISTINCT ?italianWord WHERE {{
  GRAPH <http://liita.it/data> {{ {IT} ?italianLemma lila:hasPOS lila:adjective . }}
  {EMO} ?emotion . VALUES ?emotion {{ elita:Amore elita:Disgusto }}
}}""", answer_variables=av(["italianWord"])),
 dict(id=4030, cell="C2-02", seed_used=0, register="tecnico",
      nl_it="Quali sostantivi o aggettivi in '-iuto' hanno almeno un valore di polarità Sentix negativo?",
      nl_en="Which nouns or adjectives ending in '-iuto' have at least one negative Sentix polarity value?",
      sparql=f"""SELECT DISTINCT ?italianWord WHERE {{
  GRAPH <http://liita.it/data> {{ {IT} ?italianLemma lila:hasPOS ?pos . VALUES ?pos {{ lila:noun lila:adjective }} }}
  FILTER(STRENDS(STR(?italianWord), "iuto"))
  {POL}
  FILTER(?polarityValue < 0)
}}""", answer_variables=av(["italianWord"])),
 dict(id=4031, cell="C2-03", seed_used=0, register="tecnico",
      nl_it="Quali parole sono in CompL-it iponimi oppure meronimi di 'capinera'?",
      nl_en="Which words are hyponyms or meronyms of 'capinera' (blackcap) in CompL-it?",
      sparql=f"""SELECT DISTINCT ?relatedWord ?italianWord WHERE {{
  {CL} {{
    ?seed ontolex:canonicalForm [ ontolex:writtenRep ?seedWr ] ; ontolex:sense ?seedSense .
    FILTER(STR(?seedWr) = "capinera")
    {{ ?seedSense lexinfo:hypernym ?relSense }} UNION {{ ?relSense lexinfo:partMeronym ?seedSense }}
    ?relatedWord ontolex:sense ?relSense ; ontolex:canonicalForm [ ontolex:writtenRep ?italianWord ] .
  }}
}}""", answer_variables=av(["relatedWord"], equivalents={"relatedWord": "italianWord"})),
 # ---------------- C3 chain
 dict(id=4032, cell="C3-01", seed_used=0, register="studente",
      nl_it="Scendendo di due livelli sotto 'cibo' nella gerarchia di CompL-it, quali tipi di cibo si trovano?",
      nl_en="Going two levels down below 'cibo' (food) in the CompL-it hierarchy, which kinds of food are found?",
      sparql=f"""SELECT DISTINCT ?hyponymWord ?italianWord WHERE {{
  {CL} {{
    ?seed ontolex:canonicalForm [ ontolex:writtenRep ?seedWr ] ; ontolex:sense ?seedSense .
    FILTER(STR(?seedWr) = "cibo")
    ?seedSense lexinfo:hypernym ?midSense . ?midSense lexinfo:hypernym ?relSense .
    ?hyponymWord ontolex:sense ?relSense ; ontolex:canonicalForm [ ontolex:writtenRep ?italianWord ] .
  }}
}}""", answer_variables=av(["hyponymWord"], equivalents={"hyponymWord": "italianWord"})),
 dict(id=4033, cell="C3-02", seed_used=0, register="studente",
      nl_it="Risalendo di due livelli nella gerarchia di CompL-it, quali sono gli iperonimi degli iperonimi di 'menu'?",
      nl_en="Going up two levels in the CompL-it hierarchy, what are the hypernyms of the hypernyms of 'menu'?",
      sparql=f"""SELECT DISTINCT ?hypernymWord ?italianWord WHERE {{
  {CL} {{
    ?seed ontolex:canonicalForm [ ontolex:writtenRep ?seedWr ] ; ontolex:sense ?seedSense .
    FILTER(STR(?seedWr) = "menu")
    ?seedSense lexinfo:hyponym ?midSense . ?midSense lexinfo:hyponym ?relSense .
    ?hypernymWord ontolex:sense ?relSense ; ontolex:canonicalForm [ ontolex:writtenRep ?italianWord ] .
  }}
}}""", answer_variables=av(["hypernymWord"], equivalents={"hypernymWord": "italianWord"})),
 dict(id=4034, cell="C3-03", seed_used=0, register="tecnico",
      nl_it="Quali sono, in CompL-it, gli iperonimi delle parole italiane tradotte dal lemma siciliano 'abbattimentu'?",
      nl_en="In CompL-it, what are the hypernyms of the Italian words translated by the Sicilian lemma 'abbattimentu'?",
      sparql=f"""SELECT DISTINCT ?hypernymWord ?hypernymWr WHERE {{
  ?sicilianLemma dcterms:isPartOf {SIC} ; ontolex:writtenRep ?sicilianWord . FILTER(STR(?sicilianWord) = "abbattimentu")
  ?sicEntry ontolex:canonicalForm ?sicilianLemma .
  ?itEntry vartrans:translatableAs ?sicEntry ; ontolex:canonicalForm ?italianLemma .
  GRAPH <http://liita.it/data> {{ {IT} }}
  ?word ontolex:canonicalForm ?italianLemma .
  {CL} {{
    ?word ontolex:sense ?sense . ?sense lexinfo:hyponym ?relSense .
    ?hypernymWord ontolex:sense ?relSense ; ontolex:canonicalForm [ ontolex:writtenRep ?hypernymWr ] .
  }}
}}""", answer_variables=av(["hypernymWord"], equivalents={"hypernymWord": "hypernymWr"})),
 dict(id=4035, cell="C3-04", seed_used=0, register="tecnico",
      nl_it="Quali sono le traduzioni parmigiane dei sinonimi approssimati di 'conclusivo' registrati in CompL-it?",
      nl_en="What are the Parmigiano translations of the approximate synonyms of 'conclusivo' recorded in CompL-it?",
      sparql=f"""SELECT DISTINCT ?italianWord ?parmigianoWord WHERE {{
  {CL} {{
    ?seed ontolex:canonicalForm [ ontolex:writtenRep ?seedWr ] ; ontolex:sense ?seedSense .
    FILTER(STR(?seedWr) = "conclusivo")
    {{ ?seedSense lexinfo:approximateSynonym ?relSense }} UNION {{ ?relSense lexinfo:approximateSynonym ?seedSense }}
    ?relWord ontolex:sense ?relSense .
  }}
  ?relWord ontolex:canonicalForm ?italianLemma .
  GRAPH <http://liita.it/data> {{ {IT} }}
  {LINK_PAR}
}}""", answer_variables=av(["italianWord", "parmigianoWord"])),
 dict(id=4036, cell="C3-05", seed_used=0, register="tecnico",
      nl_it="Quali sono gli iperonimi del nome deaggettivale derivato dall'aggettivo 'pervicace' in CompL-it?",
      nl_en="What are the hypernyms of the deadjectival noun derived from the adjective 'pervicace' in CompL-it?",
      sparql=f"""SELECT DISTINCT ?hypernymWord ?italianWord WHERE {{
  {CL} {{
    ?adj ontolex:canonicalForm [ ontolex:writtenRep ?adjWr ] ; ontolex:sense ?adjSense .
    FILTER(STR(?adjWr) = "pervicace")
    ?nounSense complit:deadjectivalNoun ?adjSense .
    ?nounSense lexinfo:hyponym ?relSense .
    ?hypernymWord ontolex:sense ?relSense ; ontolex:canonicalForm [ ontolex:writtenRep ?italianWord ] .
  }}
}}""", answer_variables=av(["hypernymWord"], equivalents={"hypernymWord": "italianWord"})),
]


def main():
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
    json.dump(out, open(os.path.join(HERE, "newtest_c123.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
