"""New test set, block S (20 simple questions): questions and gold queries written from cells_sampled.json.

Answer-variable conventions (same as main test and held-out, so the frozen evaluator applies unchanged):
LiITA / dialect word lists -> literal primary (italianWord, sicilianWord, parmigianoWord), SELECT DISTINCT;
CompL-it word lists -> IRI primary with literal equivalent; emotions -> emotion IRI with emotionLabel equivalent;
counts -> aggregate `count`; polarity -> aggregation stated in the question.
usage: python newtest_s.py   -> runs every gold, prints row counts and samples, writes newtest_s.json
"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from sparql import run

HERE = os.path.dirname(os.path.abspath(__file__))
PFX = """PREFIX ontolex: <http://www.w3.org/ns/lemon/ontolex#>
PREFIX lila: <http://lila-erc.eu/ontologies/lila/>
PREFIX elita: <http://w3id.org/elita/>
PREFIX marl: <http://www.gsi.upm.es/ontologies/marl/ns#>
PREFIX vartrans: <http://www.w3.org/ns/lemon/vartrans#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX lexinfo: <http://www.lexinfo.net/ontology/3.0/lexinfo#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX complit: <http://klab/lexicon/vocabulary/compl-it#>
"""
IT = "?italianLemma a ?italianLemmaType ; ontolex:writtenRep ?italianWord . FILTER(?italianLemmaType IN (lila:Lemma, lila:Hypolemma))"
SIC = "<http://liita.it/data/id/DialettoSiciliano/lemma/LemmaBank>"
PAR = "<http://liita.it/data/id/DialettoParmigiano/lemma/LemmaBank>"
CL = "SERVICE <https://klab.ilc.cnr.it/graphdb-compl-it/>"


def av(primary=(), secondary=(), aggregates=(), equivalents=None, numeric=()):
    """aggregates = whole-answer values (scored); numeric = per-row values shown but not scored (held-out practice)."""
    return {"primary": list(primary), "secondary": list(secondary), "aggregates": list(aggregates),
            "numeric": list(numeric), "equivalents": equivalents or {}}


def rel_query(seed, triple, var):  # CompL-it relation from a seed word, IRI primary + literal equivalent
    return f"""SELECT DISTINCT ?{var} ?italianWord WHERE {{
  {CL} {{
    ?seed ontolex:canonicalForm [ ontolex:writtenRep ?seedWr ] ; ontolex:sense ?seedSense .
    FILTER(STR(?seedWr) = "{seed}")
    {triple}
    ?{var} ontolex:sense ?relSense ; ontolex:canonicalForm [ ontolex:writtenRep ?italianWord ] .
  }}
}}"""


Q = [
 dict(id=4001, cell="S01", register="tecnico",
      nl_it="Quali varianti di lemma registra LiITA per il verbo 'distribuire'?",
      nl_en="Which lemma variants does LiITA record for the verb 'distribuire'?",
      sparql=f"""SELECT DISTINCT ?italianWord WHERE {{
  GRAPH <http://liita.it/data> {{
    ?seed a lila:Lemma ; ontolex:writtenRep ?seedWr ; lila:hasPOS lila:verb .
    FILTER(STR(?seedWr) = "distribuire")
    {{ ?seed lila:lemmaVariant ?italianLemma }} UNION {{ ?italianLemma lila:lemmaVariant ?seed }}
    ?italianLemma ontolex:writtenRep ?italianWord .
  }}
}}""", answer_variables=av(["italianWord"])),
 dict(id=4002, cell="S02", register="tecnico",
      nl_it="Quali ipolemmi sono collegati al lemma 'manifestare' in LiITA?",
      nl_en="Which hypolemmas are linked to the lemma 'manifestare' in LiITA?",
      sparql=f"""SELECT DISTINCT ?italianWord WHERE {{
  GRAPH <http://liita.it/data> {{
    ?seed a lila:Lemma ; ontolex:writtenRep ?seedWr . FILTER(STR(?seedWr) = "manifestare")
    ?italianLemma lila:isHypolemma ?seed ; ontolex:writtenRep ?italianWord .
  }}
}}""", answer_variables=av(["italianWord"])),
 dict(id=4003, cell="S03", register="tecnico",
      nl_it="Quali sostantivi italiani terminano in '-oria'?",
      nl_en="Which Italian nouns end in '-oria'?",
      sparql=f"""SELECT DISTINCT ?italianWord WHERE {{
  GRAPH <http://liita.it/data> {{ {IT} ?italianLemma lila:hasPOS lila:noun . }}
  FILTER(STRENDS(STR(?italianWord), "oria"))
}}""", answer_variables=av(["italianWord"])),
 dict(id=4004, cell="S04", register="tecnico",
      nl_it="Quanti sostantivi della lemma bank di LiITA iniziano con 'antr'?",
      nl_en="How many nouns in the LiITA lemma bank begin with 'antr'?",
      sparql=f"""SELECT (COUNT(DISTINCT ?italianLemma) AS ?count) WHERE {{
  GRAPH <http://liita.it/data> {{ {IT} ?italianLemma lila:hasPOS lila:noun . }}
  FILTER(STRSTARTS(STR(?italianWord), "antr"))
}}""", answer_variables=av(aggregates=["count"])),
 dict(id=4005, cell="S05", register="studente",
      nl_it="Quanti verbi italiani sono classificati in LiITA come irregolari della terza coniugazione (tipo di flessione c3i)?",
      nl_en="How many Italian verbs are classified in LiITA as irregular third-conjugation verbs (inflection type c3i)?",
      sparql="""SELECT (COUNT(DISTINCT ?italianLemma) AS ?count) WHERE {
  GRAPH <http://liita.it/data> { ?italianLemma lila:hasPOS lila:verb ; lila:hasInflectionType <http://liita.it/ontologies/liita/c3i> . }
}""", answer_variables=av(aggregates=["count"])),
 dict(id=4006, cell="S06", register="studente",
      nl_it="Quali tipi di fiume elenca CompL-it?",
      nl_en="What kinds of 'fiume' (river) does CompL-it list?",
      sparql=rel_query("fiume", "?seedSense lexinfo:hypernym ?relSense .", "hyponymWord"),
      answer_variables=av(["hyponymWord"], equivalents={"hyponymWord": "italianWord"})),
 dict(id=4007, cell="S07", register="tecnico",
      nl_it="Quali meronimi (parti) di 'paglia' registra CompL-it?",
      nl_en="Which meronyms (parts) of 'paglia' (straw) does CompL-it record?",
      sparql=rel_query("paglia", "?relSense lexinfo:partMeronym ?seedSense .", "partWord"),
      answer_variables=av(["partWord"], equivalents={"partWord": "italianWord"})),
 dict(id=4008, cell="S08", register="tecnico",
      nl_it="Quali antonimi di 'popolato' registra CompL-it?",
      nl_en="Which antonyms of 'popolato' (populated) does CompL-it record?",
      sparql=rel_query("popolato", "{ ?seedSense lexinfo:antonym ?relSense } UNION { ?relSense lexinfo:antonym ?seedSense }", "antonymWord"),
      answer_variables=av(["antonymWord"], equivalents={"antonymWord": "italianWord"})),
 dict(id=4009, cell="S09", register="tecnico",
      nl_it="Quali parole hanno in CompL-it una definizione che inizia con 'trattare'?",
      nl_en="Which words have a CompL-it definition that begins with 'trattare'?",
      sparql=f"""SELECT ?word ?writtenRep (SAMPLE(?definition) AS ?exampleDefinition) WHERE {{
  {CL} {{
    ?word ontolex:canonicalForm [ ontolex:writtenRep ?writtenRep ] ; ontolex:sense ?sense .
    ?sense skos:definition ?definition .
    FILTER(STRSTARTS(LCASE(STR(?definition)), "trattare"))
  }}
}}
GROUP BY ?word ?writtenRep""", answer_variables=av(["word"], ["exampleDefinition"], equivalents={"word": "writtenRep"})),
 dict(id=4010, cell="S10", register="studente",
      nl_it="In quanti significati diversi si usa 'penetrare' secondo CompL-it?",
      nl_en="In how many different meanings is 'penetrare' used according to CompL-it?",
      sparql=f"""SELECT (COUNT(DISTINCT ?sense) AS ?count) WHERE {{
  {CL} {{
    ?word ontolex:canonicalForm [ ontolex:writtenRep ?wr ] ; ontolex:sense ?sense .
    FILTER(STR(?wr) = "penetrare")
  }}
}}""", answer_variables=av(aggregates=["count"])),
 dict(id=4011, cell="S11", register="tecnico",
      nl_it="Quali parole hanno in CompL-it un senso del tipo semantico SIMPLE 'Opening'?",
      nl_en="Which words have a CompL-it sense of the SIMPLE semantic type 'Opening'?",
      sparql=f"""SELECT DISTINCT ?word ?writtenRep WHERE {{
  {CL} {{
    ?word ontolex:canonicalForm [ ontolex:writtenRep ?writtenRep ] ; ontolex:sense ?sense .
    ?sense complit:hasSemanticType <http://simpleOntology#514-Opening> .
  }}
}}""", answer_variables=av(["word"], equivalents={"word": "writtenRep"})),
 dict(id=4012, cell="S12", register="tecnico",
      nl_it="Quali parole hanno in CompL-it un senso con il tratto 'LIVESTOCK_FARMING' (allevamento)?",
      nl_en="Which words have a CompL-it sense with the trait 'LIVESTOCK_FARMING'?",
      sparql=f"""SELECT DISTINCT ?word ?writtenRep WHERE {{
  {CL} {{
    ?word ontolex:canonicalForm [ ontolex:writtenRep ?writtenRep ] ; ontolex:sense ?sense .
    ?sense complit:trait ?trait . FILTER(CONTAINS(STR(?trait), "LIVESTOCK_FARMING"))
  }}
}}""", answer_variables=av(["word"], equivalents={"word": "writtenRep"})),
 dict(id=4013, cell="S13", register="studente",
      nl_it="A che cosa serve un falò, secondo CompL-it?",
      nl_en="What is a 'falò' (bonfire) used for, according to CompL-it?",
      sparql=rel_query("falò", "?seedSense complit:usedFor ?relSense .", "relatedWord"),
      answer_variables=av(["relatedWord"], equivalents={"relatedWord": "italianWord"})),
 dict(id=4014, cell="S14", register="tecnico",
      nl_it="Da quale aggettivo deriva il nome deaggettivale 'dinamismo' secondo CompL-it?",
      nl_en="Which adjective is the deadjectival noun 'dinamismo' derived from, according to CompL-it?",
      sparql=rel_query("dinamismo", "?seedSense complit:deadjectivalNoun ?relSense .", "relatedWord"),
      answer_variables=av(["relatedWord"], equivalents={"relatedWord": "italianWord"})),
 dict(id=4015, cell="S15", register="studente",
      nl_it="Come si dice 'trovarsi' in siciliano?",
      nl_en="How do you say 'trovarsi' in Sicilian?",
      sparql=f"""SELECT DISTINCT ?sicilianWord WHERE {{
  GRAPH <http://liita.it/data> {{ {IT} }} FILTER(STR(?italianWord) = "trovarsi")
  ?itEntry ontolex:canonicalForm ?italianLemma ; vartrans:translatableAs ?sicEntry .
  ?sicEntry ontolex:canonicalForm ?sicilianLemma .
  ?sicilianLemma dcterms:isPartOf {SIC} ; ontolex:writtenRep ?sicilianWord .
}}""", answer_variables=av(["sicilianWord"])),
 dict(id=4016, cell="S16", register="tecnico",
      nl_it="Quali parole italiane traduce il lemma siciliano 'nsiccumari'?",
      nl_en="Which Italian words does the Sicilian lemma 'nsiccumari' translate?",
      sparql=f"""SELECT DISTINCT ?italianWord WHERE {{
  ?sicilianLemma dcterms:isPartOf {SIC} ; ontolex:writtenRep ?sicilianWord . FILTER(STR(?sicilianWord) = "nsiccumari")
  ?sicEntry ontolex:canonicalForm ?sicilianLemma .
  ?itEntry vartrans:translatableAs ?sicEntry ; ontolex:canonicalForm ?italianLemma .
  GRAPH <http://liita.it/data> {{ {IT} }}
}}""", answer_variables=av(["italianWord"])),
 dict(id=4017, cell="S17", register="tecnico",
      nl_it="Quali lemmi della lemma bank siciliana terminano in '-nza'?",
      nl_en="Which lemmas of the Sicilian lemma bank end in '-nza'?",
      sparql=f"""SELECT DISTINCT ?sicilianWord WHERE {{
  ?sicilianLemma dcterms:isPartOf {SIC} ; ontolex:writtenRep ?sicilianWord .
  FILTER(STRENDS(STR(?sicilianWord), "nza"))
}}""", answer_variables=av(["sicilianWord"])),
 dict(id=4018, cell="S18", register="tecnico",
      nl_it="Quanti lemmi parmigiani terminano in '-ros'?",
      nl_en="How many Parmigiano lemmas end in '-ros'?",
      sparql=f"""SELECT (COUNT(DISTINCT ?parmigianoLemma) AS ?count) WHERE {{
  ?parmigianoLemma dcterms:isPartOf {PAR} ; ontolex:writtenRep ?parmigianoWord .
  FILTER(STRENDS(STR(?parmigianoWord), "ros"))
}}""", answer_variables=av(aggregates=["count"])),
 dict(id=4019, cell="S19", register="studente",
      nl_it="Quali emozioni sono associate alla parola 'scrittura' in ELIta?",
      nl_en="Which emotions are associated with the word 'scrittura' (writing) in ELIta?",
      sparql=f"""SELECT DISTINCT ?emotion ?emotionLabel WHERE {{
  GRAPH <http://liita.it/data> {{ {IT} }} FILTER(STR(?italianWord) = "scrittura")
  ?emotionEntry ontolex:canonicalForm ?italianLemma ; elita:HasEmotion ?emotion .
  ?emotion rdfs:label ?emotionLabel .
}}""", answer_variables=av(["emotion"], equivalents={"emotion": "emotionLabel"})),
 dict(id=4020, cell="S20", register="studente",
      # seed changed 2026-11-13 (decision A): 'senzatetto' has a single Sentix value (0.0; -0.625 was ELIta); S20 resampled
      nl_it="Qual è il valore di polarità Sentix più alto e quale il più basso registrato per 'coltura'?",
      nl_en="What are the highest and the lowest Sentix polarity values recorded for 'coltura' (cultivation)?",
      sparql=f"""SELECT (MAX(?polarityValue) AS ?maxValue) (MIN(?polarityValue) AS ?minValue) WHERE {{
  GRAPH <http://liita.it/data> {{ {IT} }} FILTER(STR(?italianWord) = "coltura")
  ?polarityEntry ontolex:canonicalForm ?italianLemma ; marl:hasPolarity ?polarityClass ; marl:hasPolarityValue ?raw .
  BIND(xsd:float(?raw) AS ?polarityValue)
}}""", answer_variables=av(aggregates=["maxValue", "minValue"])),
]


def main():
    cells = {c["id"]: c for c in json.load(open(os.path.join(HERE, "cells_sampled.json"), encoding="utf-8"))["cells"]}
    out = []
    for q in Q:
        c = cells[q["cell"]]
        q = {**q, "group": c["group"], "resources": c["resources"], "ops": c["ops"],
             "seed": (c.get("seeds") or [None])[0], "params": c.get("params"), "sparql": PFX + "\n" + q["sparql"]}
        try:
            rows = run(q["sparql"], prefixes=False)
            q["gold_rows"] = len(rows)
            print(f"{q['id']} {q['cell']:4s} rows={len(rows):4d}  {rows[:3]}")
        except Exception as e:  # noqa: BLE001
            q["gold_rows"] = None
            print(f"{q['id']} {q['cell']:4s} ERROR {str(e)[:300]}")
        out.append(q)
    json.dump(out, open(os.path.join(HERE, "newtest_s.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
