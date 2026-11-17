"""Step 1 of the new test set: build pools of candidate seeds from the live endpoints.

Each pool is a list of candidates with the size of the answer they would produce, so that seeds can later
be sampled at random among those with 1..500 result rows (gold convention 7). Results are cached in pools/.
usage: python pools.py [pool_name ...]   (no argument = all pools)
"""
import json, os, sys, time
import requests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from sparql import run, PREFIXES  # LiITA Virtuoso helper

COMPLIT = "https://klab.ilc.cnr.it/graphdb-compl-it/"
OUT = os.path.join(os.path.dirname(__file__), "pools")
os.makedirs(OUT, exist_ok=True)
CPX = PREFIXES + "PREFIX complit: <http://klab/lexicon/vocabulary/compl-it#>\n"
SIC = "<http://liita.it/data/id/DialettoSiciliano/lemma/LemmaBank>"
PAR = "<http://liita.it/data/id/DialettoParmigiano/lemma/LemmaBank>"
IT = "GRAPH <http://liita.it/data> { ?l a ?lt ; ontolex:writtenRep ?wr . FILTER(?lt IN (lila:Lemma, lila:Hypolemma)) }"


def complit(q, timeout=300):
    r = requests.get(COMPLIT, params={"query": CPX + q}, headers={"Accept": "application/sparql-results+json"},
                     timeout=timeout)
    r.raise_for_status()
    return [{k: v["value"] for k, v in b.items()} for b in r.json()["results"]["bindings"]]


# name -> (endpoint, query). Every query returns one row per candidate seed, with ?n = size of its answer.
POOLS = {
    # --- LiITA lemma bank
    "it_suffix": ("liita", """SELECT ?suf ?pos (COUNT(DISTINCT ?l) AS ?n) WHERE { GRAPH <http://liita.it/data> {
        ?l a lila:Lemma ; ontolex:writtenRep ?wr ; lila:hasPOS ?pos . } BIND(SUBSTR(STR(?wr), STRLEN(STR(?wr))-3) AS ?suf)
        FILTER(STRLEN(STR(?wr)) > 6) } GROUP BY ?suf ?pos HAVING (COUNT(DISTINCT ?l) >= 10 && COUNT(DISTINCT ?l) <= 500)"""),
    "it_prefix": ("liita", """SELECT ?pre ?pos (COUNT(DISTINCT ?l) AS ?n) WHERE { GRAPH <http://liita.it/data> {
        ?l a lila:Lemma ; ontolex:writtenRep ?wr ; lila:hasPOS ?pos . } BIND(SUBSTR(STR(?wr), 1, 4) AS ?pre)
        FILTER(STRLEN(STR(?wr)) > 6) } GROUP BY ?pre ?pos HAVING (COUNT(DISTINCT ?l) >= 10 && COUNT(DISTINCT ?l) <= 500)"""),
    "it_variant": ("liita", """SELECT ?wr (COUNT(DISTINCT ?v) AS ?n) WHERE { GRAPH <http://liita.it/data> {
        ?l a lila:Lemma ; ontolex:writtenRep ?wr ; lila:lemmaVariant ?v . } } GROUP BY ?wr"""),
    "it_hypolemma": ("liita", """SELECT ?wr (COUNT(DISTINCT ?h) AS ?n) WHERE { GRAPH <http://liita.it/data> {
        ?l a lila:Lemma ; ontolex:writtenRep ?wr . ?h lila:isHypolemma ?l . } } GROUP BY ?wr"""),
    "it_degree": ("liita", """SELECT ?deg ?pos (COUNT(DISTINCT ?l) AS ?n) WHERE { GRAPH <http://liita.it/data> {
        ?l a lila:Lemma ; lila:hasDegree ?deg ; lila:hasPOS ?pos } } GROUP BY ?deg ?pos"""),
    "it_inflection": ("liita", """SELECT ?infl ?pos (COUNT(DISTINCT ?l) AS ?n) WHERE { GRAPH <http://liita.it/data> {
        ?l a lila:Lemma ; lila:hasInflectionType ?infl ; lila:hasPOS ?pos } } GROUP BY ?infl ?pos"""),
    "par_initial_pairs": ("liita", f"""SELECT ?i ?d (COUNT(*) AS ?n) WHERE {{ {IT}
        ?e ontolex:canonicalForm ?l ; vartrans:translatableAs ?de . ?de ontolex:canonicalForm ?x . ?x dcterms:isPartOf {PAR} ; ontolex:writtenRep ?xwr .
        BIND(LCASE(SUBSTR(STR(?wr),1,2)) AS ?i) BIND(LCASE(SUBSTR(STR(?xwr),1,2)) AS ?d) FILTER(?i != ?d) }} GROUP BY ?i ?d HAVING (COUNT(*) >= 10)"""),
    "sic_suffix_pairs": ("liita", f"""SELECT ?i ?d (COUNT(*) AS ?n) WHERE {{ {IT}
        ?e ontolex:canonicalForm ?l ; vartrans:translatableAs ?de . ?de ontolex:canonicalForm ?x . ?x dcterms:isPartOf {SIC} ; ontolex:writtenRep ?xwr .
        BIND(LCASE(SUBSTR(STR(?wr),STRLEN(STR(?wr))-2)) AS ?i) BIND(LCASE(SUBSTR(STR(?xwr),STRLEN(STR(?xwr))-2)) AS ?d) FILTER(?i != ?d) }}
        GROUP BY ?i ?d HAVING (COUNT(*) >= 10)"""),
    "sic_variants": ("liita", f"""SELECT ?d (COUNT(DISTINCT ?w) AS ?n) WHERE {{ ?d dcterms:isPartOf {SIC} ; ontolex:writtenRep ?w }}
        GROUP BY ?d HAVING (COUNT(DISTINCT ?w) >= 2)"""),
    # --- dialects
    "sic_transl": ("liita", f"""SELECT ?wr (COUNT(DISTINCT ?d) AS ?n) WHERE {{ {IT}
        ?e ontolex:canonicalForm ?l ; vartrans:translatableAs ?de . ?de ontolex:canonicalForm ?d . ?d dcterms:isPartOf {SIC} }} GROUP BY ?wr"""),
    "par_transl": ("liita", f"""SELECT ?wr (COUNT(DISTINCT ?d) AS ?n) WHERE {{ {IT}
        ?e ontolex:canonicalForm ?l ; vartrans:translatableAs ?de . ?de ontolex:canonicalForm ?d . ?d dcterms:isPartOf {PAR} }} GROUP BY ?wr"""),
    "sic_shared": ("liita", f"""SELECT ?dwr (COUNT(DISTINCT ?l) AS ?n) WHERE {{ {IT}
        ?e ontolex:canonicalForm ?l ; vartrans:translatableAs ?de . ?de ontolex:canonicalForm ?d .
        ?d dcterms:isPartOf {SIC} ; ontolex:writtenRep ?dwr }} GROUP BY ?dwr HAVING (COUNT(DISTINCT ?l) >= 2)"""),
    "par_shared": ("liita", f"""SELECT ?dwr (COUNT(DISTINCT ?l) AS ?n) WHERE {{ {IT}
        ?e ontolex:canonicalForm ?l ; vartrans:translatableAs ?de . ?de ontolex:canonicalForm ?d .
        ?d dcterms:isPartOf {PAR} ; ontolex:writtenRep ?dwr }} GROUP BY ?dwr HAVING (COUNT(DISTINCT ?l) >= 2)"""),
    "sic_suffix": ("liita", f"""SELECT ?suf (COUNT(DISTINCT ?d) AS ?n) WHERE {{ ?d dcterms:isPartOf {SIC} ; ontolex:writtenRep ?wr .
        BIND(SUBSTR(STR(?wr), STRLEN(STR(?wr))-2) AS ?suf) FILTER(STRLEN(STR(?wr)) > 5) }}
        GROUP BY ?suf HAVING (COUNT(DISTINCT ?d) >= 10 && COUNT(DISTINCT ?d) <= 500)"""),
    "par_suffix": ("liita", f"""SELECT ?suf (COUNT(DISTINCT ?d) AS ?n) WHERE {{ ?d dcterms:isPartOf {PAR} ; ontolex:writtenRep ?wr .
        BIND(SUBSTR(STR(?wr), STRLEN(STR(?wr))-2) AS ?suf) FILTER(STRLEN(STR(?wr)) > 5) }}
        GROUP BY ?suf HAVING (COUNT(DISTINCT ?d) >= 10 && COUNT(DISTINCT ?d) <= 500)"""),
    # --- affective
    "emotion_lemmas": ("liita", f"""SELECT ?wr (COUNT(DISTINCT ?em) AS ?n) WHERE {{ {IT}
        ?e ontolex:canonicalForm ?l ; elita:HasEmotion ?em }} GROUP BY ?wr"""),
    "emotion_pos": ("liita", """SELECT ?em ?pos (COUNT(DISTINCT ?l) AS ?n) WHERE { GRAPH <http://liita.it/data> {
        ?l a ?lt ; lila:hasPOS ?pos . FILTER(?lt IN (lila:Lemma, lila:Hypolemma)) }
        ?e ontolex:canonicalForm ?l ; elita:HasEmotion ?em } GROUP BY ?em ?pos"""),
    "emotion_pairs": ("liita", """SELECT ?a ?b (COUNT(DISTINCT ?l) AS ?n) WHERE { ?e ontolex:canonicalForm ?l ; elita:HasEmotion ?a , ?b .
        FILTER(STR(?a) < STR(?b)) } GROUP BY ?a ?b"""),
    "polarity_lemmas": ("liita", f"""SELECT ?wr (COUNT(DISTINCT ?v) AS ?n) (MIN(xsd:float(?v)) AS ?min) (MAX(xsd:float(?v)) AS ?max)
        WHERE {{ {IT} ?e ontolex:canonicalForm ?l ; marl:hasPolarity ?c ; marl:hasPolarityValue ?v }} GROUP BY ?wr"""),  # Sentix only (decision A, 2026-11-13)
    # --- CompL-it (queried directly on GraphDB)
    "cl_hyponyms": ("complit", """SELECT ?wr (COUNT(DISTINCT ?h) AS ?n) WHERE { ?w ontolex:canonicalForm/ontolex:writtenRep ?wr ;
        ontolex:sense ?s . ?s lexinfo:hypernym ?hs . ?h ontolex:sense ?hs } GROUP BY ?wr"""),
    "cl_hyponyms2": ("complit", """SELECT ?wr (COUNT(DISTINCT ?h) AS ?n) WHERE { ?w ontolex:canonicalForm/ontolex:writtenRep ?wr ;
        ontolex:sense ?s . ?s lexinfo:hypernym ?ms . ?ms lexinfo:hypernym ?hs . ?h ontolex:sense ?hs } GROUP BY ?wr"""),
    "cl_hypernyms2": ("complit", """SELECT ?wr (COUNT(DISTINCT ?h) AS ?n) WHERE { ?w ontolex:canonicalForm/ontolex:writtenRep ?wr ;
        ontolex:sense ?s . ?s lexinfo:hyponym ?ms . ?ms lexinfo:hyponym ?hs . ?h ontolex:sense ?hs } GROUP BY ?wr"""),
    "cl_meronyms": ("complit", """SELECT ?wr (COUNT(DISTINCT ?p) AS ?n) WHERE { ?w ontolex:canonicalForm/ontolex:writtenRep ?wr ;
        ontolex:sense ?s . ?ps lexinfo:partMeronym ?s . ?p ontolex:sense ?ps } GROUP BY ?wr"""),
    "cl_senses": ("complit", """SELECT ?wr (COUNT(DISTINCT ?s) AS ?n) WHERE { ?w ontolex:canonicalForm/ontolex:writtenRep ?wr ;
        ontolex:sense ?s } GROUP BY ?wr HAVING (COUNT(DISTINCT ?s) >= 3)"""),
    "cl_semtype": ("complit", """SELECT ?type (COUNT(DISTINCT ?w) AS ?n) WHERE { ?w ontolex:sense ?s . ?s complit:hasSemanticType ?type }
        GROUP BY ?type"""),
    "cl_usedfor": ("complit", """SELECT ?wr (COUNT(DISTINCT ?o) AS ?n) WHERE { ?w ontolex:canonicalForm/ontolex:writtenRep ?wr ;
        ontolex:sense ?s . ?s complit:usedFor ?os . ?o ontolex:sense ?os } GROUP BY ?wr"""),
    "cl_derivational": ("complit", """SELECT ?rel (COUNT(*) AS ?n) WHERE { ?s ?rel ?o .
        FILTER(?rel IN (complit:deadjectivalNoun, complit:denominalAdjective, complit:derivational, complit:deverbalNoun,
                        complit:agentNoun, complit:relatedTo)) } GROUP BY ?rel"""),
    "cl_antonyms": ("complit", """SELECT ?wr (COUNT(DISTINCT ?o) AS ?n) WHERE { ?w ontolex:canonicalForm/ontolex:writtenRep ?wr ;
        ontolex:sense ?s . ?s lexinfo:antonym ?os . ?o ontolex:sense ?os } GROUP BY ?wr"""),
    "cl_synonyms": ("complit", """SELECT ?wr (COUNT(DISTINCT ?o) AS ?n) WHERE { ?w ontolex:canonicalForm/ontolex:writtenRep ?wr ;
        ontolex:sense ?s . ?s lexinfo:approximateSynonym ?os . ?o ontolex:sense ?os } GROUP BY ?wr"""),
    "cl_traits": ("complit", """SELECT ?t (COUNT(DISTINCT ?s) AS ?n) WHERE { ?s complit:trait ?t } GROUP BY ?t"""),
    "cl_deadj": ("complit", """SELECT ?wr ?rel (COUNT(DISTINCT ?o) AS ?n) WHERE { ?w ontolex:canonicalForm/ontolex:writtenRep ?wr ;
        ontolex:sense ?s . ?s ?rel ?os . ?o ontolex:sense ?os
        FILTER(?rel IN (complit:deadjectivalNoun, complit:denominalAdjective)) } GROUP BY ?wr ?rel"""),
    "cl_def_words": ("complit", """SELECT ?tok (COUNT(DISTINCT ?s) AS ?n) WHERE { ?s skos:definition ?d .
        BIND(LCASE(STRBEFORE(CONCAT(STR(?d), " "), " ")) AS ?tok) FILTER(STRLEN(?tok) > 4) }
        GROUP BY ?tok HAVING (COUNT(DISTINCT ?s) >= 5 && COUNT(DISTINCT ?s) <= 300)"""),
}


def build(name):
    ep, q = POOLS[name]
    t = time.time()
    rows = run(q) if ep == "liita" else complit(q)
    json.dump(rows, open(os.path.join(OUT, name + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print(f"{name:16s} {len(rows):7d} rows  {time.time() - t:5.1f}s", flush=True)


if __name__ == "__main__":
    for name in (sys.argv[1:] or POOLS):
        try:
            build(name)
        except Exception as e:  # noqa: BLE001
            print(f"{name:16s} ERROR {str(e)[:200]}", flush=True)
