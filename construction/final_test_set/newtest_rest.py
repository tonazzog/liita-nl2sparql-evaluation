"""New test set, remaining blocks C7–C13 and M: 32 questions.

Group-by answers follow the held-out convention: primary = [group key, count], count also listed as numeric;
group keys that are IRIs (pos, emotion) get a literal equivalent.
Cells changed before writing (documented):
  C7-04: X = 'frutto' (the generic noun of the sampled type 'Fruit'); a random X would make an incoherent question,
         and the hyponyms of the Fruit words themselves are all Fruit (union = the type alone).
  C9-03: "adjectives with more than 6 emotions" (N=6 drawn) duplicates dev question 3048 -> "words with more than N
         Sentix polarity values", N drawn from [3, 4] with RNG "C9-03-new".
  C10-02: semantic type drawn with RNG "C10-02-type" among cl_semtype n 50..1000 -> '94-Act'.
  C13-03: "per emotion, positive and negative lemmas" duplicates dev 3067 -> per Sentix polarity class:
          n. lemmas, n. with an ELIta emotion, n. with a Parmigiano translation.
  C13-04: "polysemous vs monosemous adjectives" duplicates dev 3071 -> per dialect: n. lemmas in the dialect lemma bank,
          n. of those linked to an Italian lemma, n. of distinct Italian lemmas they translate.
Fixes after the first run (documented):
  C7-01 nouns '-ridi': 0 rows -> reserve 1, nouns '-polo' (6).   C8-02 nouns '-iano': 0 rows -> reserve 1, adjectives '-ente'.
  C8-05 nouns '-tite': 1 row with count 1 (trivial); reserve 1 '-lidi' 0 rows -> reserve 2 nouns '-ente' (2 tied rows).
  C9-01 adverbs > 4 Parmigiano translations: 0 rows (also > 3) -> POS redrawn: nouns are polluted by abbreviations
        ('d', 'den'), verbs give 17 rows -> verbs.
  C9-04 "words with more than 50 hyponyms" times out (504) through SERVICE in every formulation, and subqueries inside
        SERVICE are refused -> scoped version: hyponyms of X with more than 5 hyponyms; X redrawn with RNG "C9-04-redraw"
        among cl_hyponyms n 20..80, first non-empty: 'regione' 0 rows -> 'personaggio' (2 rows).
  C11-04 any initial letter gives 541 rows, mostly accent variants (autru/àutru) -> the d~r alternation attested in
        Sprugnoli et al. 2025 (Ciallabacialla): 41 rows.
usage: python newtest_rest.py -> runs every gold, writes newtest_rest.json
"""
import json, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newtest_s import PFX, IT, SIC, PAR, CL, av, run, HERE
from newtest_c123 import LINK_SIC, LINK_PAR, EMO, POL
from newtest_c456 import HAS_SIC, HAS_PAR, seed_cl

N_C903 = random.Random("20261110-C9-03-new").choice([3, 4])
POS_TEXT = 'BIND(STRAFTER(STR(?pos), "lila/") AS ?posText)'

Q = [
 # ---------------- C7 union
 dict(id=4055, cell="C7-01", seed_used=1, register="studente",
      nl_it="Quali nomi che finiscono in '-polo' hanno un equivalente in siciliano o in parmigiano?",
      nl_en="Which nouns ending in '-polo' have an equivalent in Sicilian or in Parmigiano?",
      sparql=f"""SELECT DISTINCT ?italianWord WHERE {{
  GRAPH <http://liita.it/data> {{ {IT} ?italianLemma lila:hasPOS lila:noun . }}
  FILTER(STRENDS(STR(?italianWord), "polo"))
  {{ {HAS_SIC} }} UNION {{ {HAS_PAR} }}
}}""", answer_variables=av(["italianWord"])),
 dict(id=4056, cell="C7-02", seed_used=None, register="studente",
      nl_it="Quante parole sono associate alla Tristezza in ELIta oppure hanno in Sentix un valore di polarità inferiore a -0,8?",
      nl_en="How many words are associated with Sadness in ELIta or have a Sentix polarity value below -0.8?",
      sparql=f"""SELECT (COUNT(DISTINCT ?italianLemma) AS ?count) WHERE {{
  GRAPH <http://liita.it/data> {{ {IT} }}
  {{ {EMO} elita:Tristezza . }}
  UNION
  {{ {POL} FILTER(?polarityValue < -0.8) }}
}}""", answer_variables=av(aggregates=["count"])),
 dict(id=4057, cell="C7-03", seed_used=0, register="tecnico",
      nl_it="Quali parole sono in CompL-it parti di 'galletto' oppure hanno una definizione che cita 'galletto'?",
      nl_en="Which words are, in CompL-it, parts of 'galletto' or have a definition mentioning 'galletto'?",
      sparql=f"""SELECT DISTINCT ?word ?writtenRep WHERE {{
  {CL} {{
    {{ {seed_cl("galletto")}
      ?relSense lexinfo:partMeronym ?seedSense . ?word ontolex:sense ?relSense . }}
    UNION
    {{ ?word ontolex:sense ?defSense . ?defSense skos:definition ?definition .
      FILTER(REGEX(STR(?definition), "\\\\bgalletto\\\\b", "i")) }}
    ?word ontolex:canonicalForm [ ontolex:writtenRep ?writtenRep ] .
  }}
}}""", answer_variables=av(["word"], equivalents={"word": "writtenRep"})),
 dict(id=4058, cell="C7-04", seed_used=0, register="tecnico",
      nl_it="Quali parole hanno in CompL-it un senso del tipo semantico SIMPLE 'Fruit' oppure sono iponimi di 'frutto'?",
      nl_en="Which words have a CompL-it sense of the SIMPLE semantic type 'Fruit' or are hyponyms of 'frutto'?",
      sparql=f"""SELECT DISTINCT ?word ?writtenRep WHERE {{
  {CL} {{
    {{ ?word ontolex:sense ?typedSense . ?typedSense complit:hasSemanticType <http://simpleOntology#5733-Fruit> . }}
    UNION
    {{ {seed_cl("frutto")}
      ?seedSense lexinfo:hypernym ?relSense . ?word ontolex:sense ?relSense . }}
    ?word ontolex:canonicalForm [ ontolex:writtenRep ?writtenRep ] .
  }}
}}""", answer_variables=av(["word"], equivalents={"word": "writtenRep"})),
 # ---------------- C8 group-by / ranking
 dict(id=4059, cell="C8-01", seed_used=None, register="tecnico",
      nl_it="Per ciascuna parte del discorso, quanti lemmi sono associati alla Tristezza in ELIta?",
      nl_en="For each part of speech, how many lemmas are associated with Sadness in ELIta?",
      sparql=f"""SELECT ?pos ?posText (COUNT(DISTINCT ?italianLemma) AS ?count) WHERE {{
  GRAPH <http://liita.it/data> {{ {IT} ?italianLemma lila:hasPOS ?pos . }}
  {EMO} elita:Tristezza .
  {POS_TEXT}
}}
GROUP BY ?pos ?posText""", answer_variables=av(["pos", "count"], numeric=["count"], equivalents={"pos": "posText"})),
 dict(id=4060, cell="C8-02", seed_used=1, register="tecnico",
      nl_it="Per ogni emozione di ELIta, quanti aggettivi in '-ente' vi sono associati?",
      nl_en="For each ELIta emotion, how many adjectives ending in '-ente' are associated with it?",
      sparql=f"""SELECT ?emotion ?emotionLabel (COUNT(DISTINCT ?italianLemma) AS ?count) WHERE {{
  GRAPH <http://liita.it/data> {{ {IT} ?italianLemma lila:hasPOS lila:adjective . }}
  FILTER(STRENDS(STR(?italianWord), "ente"))
  {EMO} ?emotion . ?emotion rdfs:label ?emotionLabel .
}}
GROUP BY ?emotion ?emotionLabel""", answer_variables=av(["emotion", "count"], numeric=["count"], equivalents={"emotion": "emotionLabel"})),
 dict(id=4061, cell="C8-03", seed_used=0, register="tecnico",
      nl_it="Raggruppa gli iponimi di 'libro' in CompL-it per tipo semantico SIMPLE: quanti iponimi ci sono per ciascun tipo?",
      nl_en="Group the CompL-it hyponyms of 'libro' (book) by SIMPLE semantic type: how many hyponyms are there for each type?",
      sparql=f"""SELECT ?semanticType (COUNT(DISTINCT ?relWord) AS ?count) WHERE {{
  {CL} {{
    {seed_cl("libro")}
    ?seedSense lexinfo:hypernym ?relSense . ?relWord ontolex:sense ?relSense .
    ?relSense complit:hasSemanticType ?semanticType .
  }}
}}
GROUP BY ?semanticType""", answer_variables=av(["semanticType", "count"], numeric=["count"])),
 dict(id=4062, cell="C8-04", seed_used=None, register="studente",
      nl_it="Quanti verbi italiani hanno una traduzione in siciliano e quanti in parmigiano?",
      nl_en="How many Italian verbs have a Sicilian translation, and how many a Parmigiano one?",
      sparql=f"""SELECT ?dialect (COUNT(DISTINCT ?italianLemma) AS ?count) WHERE {{
  GRAPH <http://liita.it/data> {{ {IT} ?italianLemma lila:hasPOS lila:verb . }}
  ?itEntry ontolex:canonicalForm ?italianLemma ; vartrans:translatableAs ?dEntry .
  ?dEntry ontolex:canonicalForm ?dLemma . ?dLemma dcterms:isPartOf ?dialect .
  FILTER(?dialect IN ({SIC}, {PAR}))
}}
GROUP BY ?dialect""", answer_variables=av(["dialect", "count"], numeric=["count"])),
 dict(id=4063, cell="C8-05", seed_used=2, register="tecnico",
      nl_it="Quale sostantivo in '-ente' ha il maggior numero di traduzioni siciliane, e quante sono?",
      nl_en="Which noun ending in '-ente' has the largest number of Sicilian translations, and how many?",
      sparql=f"""SELECT ?italianWord ?count WHERE {{
  {{ SELECT ?italianWord (COUNT(DISTINCT ?sicilianWord) AS ?count) WHERE {{
      GRAPH <http://liita.it/data> {{ {IT} ?italianLemma lila:hasPOS lila:noun . }}
      FILTER(STRENDS(STR(?italianWord), "ente"))
      {LINK_SIC}
  }} GROUP BY ?italianWord }}
  {{ SELECT (MAX(?c) AS ?count) WHERE {{
      {{ SELECT ?italianWord (COUNT(DISTINCT ?sicilianWord) AS ?c) WHERE {{
          GRAPH <http://liita.it/data> {{ {IT} ?italianLemma lila:hasPOS lila:noun . }}
          FILTER(STRENDS(STR(?italianWord), "ente"))
          {LINK_SIC}
      }} GROUP BY ?italianWord }}
  }} }}
}}""", answer_variables=av(["italianWord", "count"], numeric=["count"])),
 dict(id=4064, cell="C8-06", seed_used=None, register="tecnico",
      nl_it="Come si distribuiscono tra le classi di polarità Sentix i lemmi associati ad Amore in ELIta?",
      nl_en="How are the lemmas associated with Love in ELIta distributed across the Sentix polarity classes?",
      sparql=f"""SELECT ?polarity (COUNT(DISTINCT ?italianLemma) AS ?count) WHERE {{
  GRAPH <http://liita.it/data> {{ {IT} }}
  {EMO} elita:Amore .
  ?polarityEntry ontolex:canonicalForm ?italianLemma ; marl:hasPolarity ?polarity .
}}
GROUP BY ?polarity""", answer_variables=av(["polarity", "count"], numeric=["count"])),
 # ---------------- C9 HAVING
 dict(id=4065, cell="C9-01", seed_used=None, register="studente",
      nl_it="Quali verbi italiani si possono dire in parmigiano in più di 4 modi diversi?",
      nl_en="Which Italian verbs can be said in Parmigiano in more than 4 different ways?",
      sparql=f"""SELECT ?italianWord (COUNT(DISTINCT ?parmigianoWord) AS ?count) WHERE {{
  GRAPH <http://liita.it/data> {{ {IT} ?italianLemma lila:hasPOS lila:verb . }}
  {LINK_PAR}
}}
GROUP BY ?italianWord
HAVING (COUNT(DISTINCT ?parmigianoWord) > 4)""", answer_variables=av(["italianWord", "count"], numeric=["count"])),
 dict(id=4066, cell="C9-02", seed_used=0, register="tecnico",
      nl_it="Quali parole del tipo semantico SIMPLE '3_D_location' hanno più di 3 sensi in CompL-it?",
      nl_en="Which words of the SIMPLE semantic type '3_D_location' have more than 3 senses in CompL-it?",
      sparql=f"""SELECT ?word ?writtenRep (COUNT(DISTINCT ?sense) AS ?count) WHERE {{
  {CL} {{
    ?word ontolex:sense ?typedSense . ?typedSense complit:hasSemanticType <http://simpleOntology#511-3_D_location> .
    ?word ontolex:sense ?sense ; ontolex:canonicalForm [ ontolex:writtenRep ?writtenRep ] .
  }}
}}
GROUP BY ?word ?writtenRep
HAVING (COUNT(DISTINCT ?sense) > 3)""", answer_variables=av(["word", "count"], numeric=["count"], equivalents={"word": "writtenRep"})),
 dict(id=4067, cell="C9-03", seed_used=None, register="tecnico",
      nl_it=f"Quali parole hanno in Sentix più di {N_C903} valori di polarità diversi?",
      nl_en=f"Which words have more than {N_C903} different polarity values in Sentix?",
      sparql=f"""SELECT ?italianWord (COUNT(DISTINCT ?polarityValue) AS ?count) WHERE {{
  GRAPH <http://liita.it/data> {{ {IT} }}
  {POL}
}}
GROUP BY ?italianWord
HAVING (COUNT(DISTINCT ?polarityValue) > {N_C903})""", answer_variables=av(["italianWord", "count"], numeric=["count"])),
 dict(id=4068, cell="C9-04", seed_used=None, register="studente",
      nl_it="Quali iponimi di 'personaggio' in CompL-it hanno a loro volta più di 5 iponimi?",
      nl_en="Which hyponyms of 'personaggio' (character) in CompL-it have more than 5 hyponyms of their own?",
      sparql=f"""SELECT ?hyponymWord ?italianWord (COUNT(DISTINCT ?subSense) AS ?count) WHERE {{
  {CL} {{
    {seed_cl("personaggio")}
    ?seedSense lexinfo:hypernym ?relSense .
    ?hyponymWord ontolex:sense ?relSense ; ontolex:canonicalForm [ ontolex:writtenRep ?italianWord ] .
    ?hyponymWord ontolex:sense ?anySense . ?anySense lexinfo:hypernym ?subSense .
  }}
}}
GROUP BY ?hyponymWord ?italianWord
HAVING (COUNT(DISTINCT ?subSense) > 5)""", answer_variables=av(["hyponymWord", "count"], numeric=["count"], equivalents={"hyponymWord": "italianWord"})),
 # ---------------- C10 comparison with a reference value
 dict(id=4069, cell="C10-01", seed_used=0, register="tecnico",
      nl_it="Quali parole associate a Rabbia in ELIta hanno una polarità Sentix massima superiore a quella di 'protozoo'?",
      nl_en="Which words associated with Anger in ELIta have a higher maximum Sentix polarity than 'protozoo'?",
      sparql=f"""SELECT ?italianWord (MAX(?polarityValue) AS ?maxValue) WHERE {{
  {{ SELECT (MAX(?refValue) AS ?refMax) WHERE {{
      GRAPH <http://liita.it/data> {{ ?refLemma ontolex:writtenRep ?refWr . }} FILTER(STR(?refWr) = "protozoo")
      ?refEntry ontolex:canonicalForm ?refLemma ; marl:hasPolarity ?refClass ; marl:hasPolarityValue ?refRaw . BIND(xsd:float(?refRaw) AS ?refValue)
  }} }}
  GRAPH <http://liita.it/data> {{ {IT} }}
  {EMO} elita:Rabbia .
  {POL}
}}
GROUP BY ?italianWord ?refMax
HAVING (MAX(?polarityValue) > ?refMax)""", answer_variables=av(["italianWord"], numeric=["maxValue"])),
 dict(id=4070, cell="C10-02", seed_used=0, register="tecnico",
      nl_it="Quali parole del tipo semantico SIMPLE 'Act' hanno in CompL-it più sensi di 'base'?",
      nl_en="Which words of the SIMPLE semantic type 'Act' have more senses in CompL-it than 'base'?",
      sparql=f"""SELECT ?word ?writtenRep ?count WHERE {{
  {{ SELECT (COUNT(DISTINCT ?refSense) AS ?refCount) WHERE {{
      {CL} {{ ?ref ontolex:canonicalForm [ ontolex:writtenRep ?refWr ] ; ontolex:sense ?refSense . FILTER(STR(?refWr) = "base") }}
  }} }}
  {{ SELECT ?word ?writtenRep (COUNT(DISTINCT ?sense) AS ?count) WHERE {{
      {CL} {{
        ?word ontolex:sense ?typedSense . ?typedSense complit:hasSemanticType <http://simpleOntology#94-Act> .
        ?word ontolex:sense ?sense ; ontolex:canonicalForm [ ontolex:writtenRep ?writtenRep ] .
      }}
  }} GROUP BY ?word ?writtenRep }}
  FILTER(?count > ?refCount)
}}""", answer_variables=av(["word"], numeric=["count"], equivalents={"word": "writtenRep"})),
 dict(id=4071, cell="C10-03", seed_used=None, register="studente",
      nl_it="Quali emozioni di ELIta sono associate a più aggettivi rispetto alla Rabbia?",
      nl_en="Which ELIta emotions are associated with more adjectives than Anger?",
      sparql=f"""SELECT ?emotion ?emotionLabel ?count WHERE {{
  {{ SELECT (COUNT(DISTINCT ?refLemma) AS ?refCount) WHERE {{
      GRAPH <http://liita.it/data> {{ ?refLemma a ?refType ; lila:hasPOS lila:adjective . FILTER(?refType IN (lila:Lemma, lila:Hypolemma)) }}
      ?refEntry ontolex:canonicalForm ?refLemma ; elita:HasEmotion elita:Rabbia .
  }} }}
  {{ SELECT ?emotion ?emotionLabel (COUNT(DISTINCT ?italianLemma) AS ?count) WHERE {{
      GRAPH <http://liita.it/data> {{ {IT} ?italianLemma lila:hasPOS lila:adjective . }}
      {EMO} ?emotion . ?emotion rdfs:label ?emotionLabel .
  }} GROUP BY ?emotion ?emotionLabel }}
  FILTER(?count > ?refCount)
}}""", answer_variables=av(["emotion"], numeric=["count"], equivalents={"emotion": "emotionLabel"})),
 # ---------------- C11 comparison between variables
 dict(id=4072, cell="C11-01", seed_used=0, register="studente",
      nl_it="Quali parole italiane che cominciano con 'pu' in parmigiano cominciano invece con 'po'?",
      nl_en="Which Italian words starting with 'pu' start with 'po' instead in Parmigiano?",
      sparql=f"""SELECT DISTINCT ?italianWord ?parmigianoWord WHERE {{
  GRAPH <http://liita.it/data> {{ {IT} }}
  FILTER(STRSTARTS(LCASE(STR(?italianWord)), "pu"))
  {LINK_PAR}
  FILTER(STRSTARTS(LCASE(STR(?parmigianoWord)), "po"))
}}""", answer_variables=av(["italianWord", "parmigianoWord"])),
 dict(id=4073, cell="C11-02", seed_used=0, register="tecnico",
      nl_it="Quali parole italiane in '-ena' hanno una traduzione siciliana in '-ina'?",
      nl_en="Which Italian words ending in '-ena' have a Sicilian translation ending in '-ina'?",
      sparql=f"""SELECT DISTINCT ?italianWord ?sicilianWord WHERE {{
  GRAPH <http://liita.it/data> {{ {IT} }}
  FILTER(STRENDS(LCASE(STR(?italianWord)), "ena"))
  {LINK_SIC}
  FILTER(STRENDS(LCASE(STR(?sicilianWord)), "ina"))
}}""", answer_variables=av(["italianWord", "sicilianWord"])),
 dict(id=4074, cell="C11-03", seed_used=None, register="studente",
      nl_it="Quali verbi italiani si scrivono esattamente come la loro traduzione siciliana?",
      nl_en="Which Italian verbs are spelled exactly like their Sicilian translation?",
      sparql=f"""SELECT DISTINCT ?italianWord WHERE {{
  GRAPH <http://liita.it/data> {{ {IT} ?italianLemma lila:hasPOS lila:verb . }}
  {LINK_SIC}
  FILTER(STR(?italianWord) = STR(?sicilianWord))
}}""", answer_variables=av(["italianWord"])),
 dict(id=4075, cell="C11-04", seed_used=None, register="tecnico",
      nl_it="Quali lemmi siciliani hanno una grafia con 'd' iniziale e un'altra con 'r' iniziale, per il resto identiche?",
      nl_en="Which Sicilian lemmas have one spelling with initial 'd' and another with initial 'r', otherwise identical?",
      sparql=f"""SELECT DISTINCT ?sicilianWord ?otherSpelling WHERE {{
  ?sicilianLemma dcterms:isPartOf {SIC} ; ontolex:writtenRep ?sicilianWord , ?otherSpelling .
  FILTER(STRSTARTS(STR(?sicilianWord), "d") && STRSTARTS(STR(?otherSpelling), "r"))
  FILTER(SUBSTR(STR(?sicilianWord), 2) = SUBSTR(STR(?otherSpelling), 2))
}}""", answer_variables=av(["sicilianWord"], ["otherSpelling"])),
 dict(id=4076, cell="C11-05", seed_used=None, register="tecnico",
      # Rewritten 2026-11-13 (decision A): with Sentix alone no lemma of any POS has values of opposite sign (the
      # previous answers, 264 verbs, came from mixing the ELIta and the Sentix value). Same cell: two Sentix values
      # of the same lemma compared (POS noun: no verb or adjective has more than one Sentix value).
      nl_it="Quali sostantivi hanno in Sentix due valori di polarità che differiscono di più di 0,25?",
      nl_en="Which nouns have in Sentix two polarity values that differ by more than 0.25?",
      sparql=f"""SELECT DISTINCT ?italianWord WHERE {{
  GRAPH <http://liita.it/data> {{ {IT} ?italianLemma lila:hasPOS lila:noun . }}
  ?aEntry ontolex:canonicalForm ?italianLemma ; marl:hasPolarity ?aClass ; marl:hasPolarityValue ?aRaw .
  ?bEntry ontolex:canonicalForm ?italianLemma ; marl:hasPolarity ?bClass ; marl:hasPolarityValue ?bRaw .
  FILTER(xsd:float(?aRaw) > xsd:float(?bRaw) + 0.25)
}}""", answer_variables=av(["italianWord"])),
 # ---------------- C12 nested aggregation
 dict(id=4077, cell="C12-01", seed_used=None, register="tecnico",
      nl_it="In media, quante traduzioni siciliane diverse ha un verbo italiano che ne ha almeno una?",
      nl_en="On average, how many different Sicilian translations does an Italian verb have, among verbs with at least one?",
      sparql=f"""SELECT (AVG(?n) AS ?avgTranslations) WHERE {{
  {{ SELECT ?italianLemma (COUNT(DISTINCT ?sicilianWord) AS ?n) WHERE {{
      GRAPH <http://liita.it/data> {{ {IT} ?italianLemma lila:hasPOS lila:verb . }}
      {LINK_SIC}
  }} GROUP BY ?italianLemma }}
}}""", answer_variables=av(aggregates=["avgTranslations"])),
 dict(id=4078, cell="C12-02", seed_used=0, register="tecnico",
      nl_it="Qual è il numero medio di sensi delle parole che hanno un senso del tipo semantico SIMPLE 'Cause_Change_Location'?",
      nl_en="What is the average number of senses of the words having a sense of the SIMPLE semantic type 'Cause_Change_Location'?",
      sparql=f"""SELECT (AVG(?n) AS ?avgSenses) WHERE {{
  {{ SELECT ?word (COUNT(DISTINCT ?sense) AS ?n) WHERE {{
      {CL} {{
        ?word ontolex:sense ?typedSense . ?typedSense complit:hasSemanticType <http://simpleOntology#972-Cause_Change_Location> .
        ?word ontolex:sense ?sense .
      }}
  }} GROUP BY ?word }}
}}""", answer_variables=av(aggregates=["avgSenses"])),
 dict(id=4079, cell="C12-03", seed_used=None, register="tecnico",
      nl_it="Tra i lemmi con un valore di polarità Sentix superiore a 0,8, quante emozioni ELIta hanno in media quelli associati ad almeno un'emozione?",
      nl_en="Among the lemmas with a Sentix polarity value above 0.8, how many ELIta emotions on average do those associated with at least one emotion have?",
      sparql=f"""SELECT (AVG(?n) AS ?avgEmotions) WHERE {{
  {{ SELECT ?italianLemma (COUNT(DISTINCT ?emotion) AS ?n) WHERE {{
      GRAPH <http://liita.it/data> {{ {IT} }}
      {POL} FILTER(?polarityValue > 0.8)
      {EMO} ?emotion . ?emotion rdfs:label ?emotionLabel .
  }} GROUP BY ?italianLemma }}
}}""", answer_variables=av(aggregates=["avgEmotions"])),
 # ---------------- C13 multi-statistic
 dict(id=4080, cell="C13-01", seed_used=None, register="tecnico",
      nl_it="Per ogni emozione di ELIta indica, in quest'ordine, il numero di lemmi associati (lemmaCount), la loro polarità Sentix media (avgPolarity) e quanti di essi hanno una traduzione siciliana (withSicilian).",
      nl_en="For each ELIta emotion give, in this order, the number of associated lemmas (lemmaCount), their average Sentix polarity (avgPolarity) and how many of them have a Sicilian translation (withSicilian).",
      sparql=f"""SELECT ?emotion ?emotionLabel ?lemmaCount ?avgPolarity ?withSicilian WHERE {{
  {{ SELECT ?emotion ?emotionLabel (COUNT(DISTINCT ?italianLemma) AS ?lemmaCount) WHERE {{
      GRAPH <http://liita.it/data> {{ {IT} }}
      {EMO} ?emotion . ?emotion rdfs:label ?emotionLabel .
  }} GROUP BY ?emotion ?emotionLabel }}
  {{ SELECT ?emotion (AVG(?polarityValue) AS ?avgPolarity) WHERE {{
      GRAPH <http://liita.it/data> {{ {IT} }}
      {EMO} ?emotion .
      {POL}
  }} GROUP BY ?emotion }}
  {{ SELECT ?emotion (COUNT(DISTINCT ?italianLemma) AS ?withSicilian) WHERE {{
      GRAPH <http://liita.it/data> {{ {IT} }}
      {EMO} ?emotion .
      {HAS_SIC}
  }} GROUP BY ?emotion }}
}}""", answer_variables=av(["emotion", "lemmaCount", "withSicilian"], numeric=["lemmaCount", "avgPolarity", "withSicilian"],
                          equivalents={"emotion": "emotionLabel"})),
 dict(id=4081, cell="C13-02", seed_used=None, register="tecnico",
      nl_it="Per ciascuna parte del discorso indica, in quest'ordine, il numero di lemmi italiani (lemmaCount), quanti hanno una traduzione siciliana (withSicilian) e quanti una traduzione parmigiana (withParmigiano).",
      nl_en="For each part of speech give, in this order, the number of Italian lemmas (lemmaCount), how many have a Sicilian translation (withSicilian) and how many a Parmigiano one (withParmigiano).",
      sparql=f"""SELECT ?pos ?posText ?lemmaCount ?withSicilian ?withParmigiano WHERE {{
  {{ SELECT ?pos (COUNT(DISTINCT ?italianLemma) AS ?lemmaCount) WHERE {{
      GRAPH <http://liita.it/data> {{ {IT} ?italianLemma lila:hasPOS ?pos . }}
  }} GROUP BY ?pos }}
  OPTIONAL {{ SELECT ?pos (COUNT(DISTINCT ?italianLemma) AS ?withSicilian) WHERE {{
      GRAPH <http://liita.it/data> {{ {IT} ?italianLemma lila:hasPOS ?pos . }}
      {HAS_SIC}
  }} GROUP BY ?pos }}
  OPTIONAL {{ SELECT ?pos (COUNT(DISTINCT ?italianLemma) AS ?withParmigiano) WHERE {{
      GRAPH <http://liita.it/data> {{ {IT} ?italianLemma lila:hasPOS ?pos . }}
      {HAS_PAR}
  }} GROUP BY ?pos }}
  {POS_TEXT}
}}""", answer_variables=av(["pos", "lemmaCount", "withSicilian", "withParmigiano"],
                          numeric=["lemmaCount", "withSicilian", "withParmigiano"], equivalents={"pos": "posText"})),
 dict(id=4082, cell="C13-03", seed_used=None, register="tecnico",
      nl_it="Per ciascuna classe di polarità Sentix indica, in quest'ordine, il numero di lemmi (lemmaCount), quanti sono associati a un'emozione ELIta (withEmotion) e quanti hanno una traduzione parmigiana (withParmigiano).",
      nl_en="For each Sentix polarity class give, in this order, the number of lemmas (lemmaCount), how many are associated with an ELIta emotion (withEmotion) and how many have a Parmigiano translation (withParmigiano).",
      sparql=f"""SELECT ?polarity ?lemmaCount ?withEmotion ?withParmigiano WHERE {{
  {{ SELECT ?polarity (COUNT(DISTINCT ?italianLemma) AS ?lemmaCount) WHERE {{
      GRAPH <http://liita.it/data> {{ {IT} }}
      ?polarityEntry ontolex:canonicalForm ?italianLemma ; marl:hasPolarity ?polarity .
  }} GROUP BY ?polarity }}
  OPTIONAL {{ SELECT ?polarity (COUNT(DISTINCT ?italianLemma) AS ?withEmotion) WHERE {{
      GRAPH <http://liita.it/data> {{ {IT} }}
      ?polarityEntry ontolex:canonicalForm ?italianLemma ; marl:hasPolarity ?polarity .
      {EMO} ?emotion . ?emotion rdfs:label ?emotionLabel .
  }} GROUP BY ?polarity }}
  OPTIONAL {{ SELECT ?polarity (COUNT(DISTINCT ?italianLemma) AS ?withParmigiano) WHERE {{
      GRAPH <http://liita.it/data> {{ {IT} }}
      ?polarityEntry ontolex:canonicalForm ?italianLemma ; marl:hasPolarity ?polarity .
      {HAS_PAR}
  }} GROUP BY ?polarity }}
}}""", answer_variables=av(["polarity", "lemmaCount", "withEmotion", "withParmigiano"],
                          numeric=["lemmaCount", "withEmotion", "withParmigiano"])),
 dict(id=4083, cell="C13-04", seed_used=None, register="tecnico",
      nl_it="Per ciascun dialetto (siciliano e parmigiano) indica, in quest'ordine, il numero di lemmi della sua lemma bank (lemmaCount), quanti sono collegati come traduzione a un lemma italiano (linkedLemmas) e quanti lemmi italiani distinti traducono (italianLemmas).",
      nl_en="For each dialect (Sicilian and Parmigiano) give, in this order, the number of lemmas in its lemma bank (lemmaCount), how many are linked as a translation to an Italian lemma (linkedLemmas) and how many distinct Italian lemmas they translate (italianLemmas).",
      sparql=f"""SELECT ?dialect ?lemmaCount ?linkedLemmas ?italianLemmas WHERE {{
  VALUES ?dialect {{ {SIC} {PAR} }}
  {{ SELECT ?dialect (COUNT(DISTINCT ?dLemma) AS ?lemmaCount) WHERE {{ ?dLemma dcterms:isPartOf ?dialect . }} GROUP BY ?dialect }}
  {{ SELECT ?dialect (COUNT(DISTINCT ?dLemma) AS ?linkedLemmas) (COUNT(DISTINCT ?italianLemma) AS ?italianLemmas) WHERE {{
      ?dLemma dcterms:isPartOf ?dialect . ?dEntry ontolex:canonicalForm ?dLemma .
      ?itEntry vartrans:translatableAs ?dEntry ; ontolex:canonicalForm ?italianLemma .
      GRAPH <http://liita.it/data> {{ {IT} }}
  }} GROUP BY ?dialect }}
}}""", answer_variables=av(["dialect", "lemmaCount", "linkedLemmas", "italianLemmas"],
                          numeric=["lemmaCount", "linkedLemmas", "italianLemmas"])),
 # ---------------- M metadata
 dict(id=4084, cell="M-01", seed_used=None, register="studente",
      nl_it="Quali lemma bank sono presenti nella knowledge base LiITA?",
      nl_en="Which lemma banks are in the LiITA knowledge base?",
      sparql="""SELECT DISTINCT ?lemmaBank WHERE { ?lemma dcterms:isPartOf ?lemmaBank . ?lemmaBank a ?type . }""",
      answer_variables=av(["lemmaBank"])),
 dict(id=4085, cell="M-02", seed_used=None, register="tecnico",
      nl_it="Quanti lemmi contiene ciascuna lemma bank di LiITA?",
      nl_en="How many lemmas does each LiITA lemma bank contain?",
      sparql="""SELECT ?lemmaBank (COUNT(DISTINCT ?lemma) AS ?count) WHERE { ?lemma dcterms:isPartOf ?lemmaBank . }
GROUP BY ?lemmaBank""", answer_variables=av(["lemmaBank", "count"], numeric=["count"])),
 dict(id=4086, cell="M-03", seed_used=None, register="studente",
      nl_it="Quali categorie emotive usa ELIta?",
      nl_en="Which emotion categories does ELIta use?",
      sparql="""SELECT DISTINCT ?emotion ?emotionLabel WHERE { ?entry elita:HasEmotion ?emotion . ?emotion rdfs:label ?emotionLabel . }""",
      answer_variables=av(["emotion"], equivalents={"emotion": "emotionLabel"})),
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
            print(f"{q['id']} {q['cell']:6s} rows={len(rows):4d}  {str(rows[:3])[:230]}", flush=True)
        except Exception as e:  # noqa: BLE001
            q["gold_rows"] = None
            print(f"{q['id']} {q['cell']:6s} ERROR {str(e)[:300]}", flush=True)
        out.append(q)
    json.dump(out, open(os.path.join(HERE, "newtest_rest.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
