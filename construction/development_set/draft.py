"""Held-out test set: draft questions with gold SPARQL (written 2026-11-04).

Conventions (same as the canonical gold of the main test set):
- Italian lemmas are read from GRAPH <http://liita.it/data> (dialect lemmas are not in it)
  and include hypolemmas: ?l a ?t . FILTER(?t IN (lila:Lemma, lila:Hypolemma)).
- Answers are returned as literals (written forms, labels) where possible.
- No LIMIT unless the question asks for a fixed number of results.
- Regex inside SERVICE always has a flags argument (Virtuoso refuses 2-argument regex there).
"""

IT = "GRAPH <http://liita.it/data> {{ ?{l} a ?{l}Type ; ontolex:writtenRep ?{w} {extra}. FILTER(?{l}Type IN (lila:Lemma, lila:Hypolemma)) }}"
SIC = "<http://liita.it/data/id/DialettoSiciliano/lemma/LemmaBank>"
PAR = "<http://liita.it/data/id/DialettoParmigiano/lemma/LemmaBank>"
CL = "SERVICE <https://klab.ilc.cnr.it/graphdb-compl-it/>"


def it(l="italianLemma", w="italianWord", extra=""):
    """Italian lemma (or hypolemma) with its written form; extra = more triples on the lemma (';'-prefixed)."""
    return IT.format(l=l, w=w, extra=extra)


def to_dialect(lemma, bank, entry, dlemma, dword):
    return (f"?{entry}It ontolex:canonicalForm ?{lemma} ; vartrans:translatableAs ?{entry} .\n"
            f"  ?{entry} ontolex:canonicalForm ?{dlemma} .\n"
            f"  ?{dlemma} dcterms:isPartOf {bank} ; ontolex:writtenRep ?{dword} .")


def emotion(lemma="italianLemma", entry="emotionEntry", emo="emotion", label="emotionLabel", value=None):
    target = value if value else f"?{emo}"
    lab = f" {target} rdfs:label ?{label} ." if label else ""
    return f"?{entry} ontolex:canonicalForm ?{lemma} ; elita:HasEmotion {target} .{lab}"


def polarity(lemma="italianLemma", entry="polarityEntry", var="polarityValue"):
    # BIND to xsd:float: the same value can be stored as distinct literals (DISTINCT would keep both)
    # marl:hasPolarity selects the Sentix entry: ELIta entries carry their own marl:hasPolarityValue (decision A, 2026-11-13)
    return (f"?{entry} ontolex:canonicalForm ?{lemma} ; marl:hasPolarity ?{var}Class ; marl:hasPolarityValue ?{var}Raw ."
            f" BIND(xsd:float(?{var}Raw) AS ?{var})")


def cl_word(word_var, text, sense_var, wr_var=None, pos=None):
    wr = wr_var or f"{word_var}Wr"
    p = f' ;\n      lexinfo:partOfSpeech [ rdfs:label ?{word_var}Pos ]' if pos else ""
    pf = f' FILTER(STR(?{word_var}Pos) = "{pos}")' if pos else ""
    return (f"?{word_var} ontolex:canonicalForm [ ontolex:writtenRep ?{wr} ] ; ontolex:sense ?{sense_var}{p} .\n"
            f'    FILTER(STR(?{wr}) = "{text}"){pf}')


def related(sense_var, word_var, text_var):
    return f"?{word_var} ontolex:sense ?{sense_var} ; ontolex:canonicalForm [ ontolex:writtenRep ?{text_var} ] ."


def av(primary=(), secondary=(), aggregates=(), numeric=(), equivalents=None):
    d = {"primary": list(primary), "secondary": list(secondary),
         "aggregates": list(aggregates), "numeric": list(numeric)}
    if equivalents:
        # IRI answer -> literal column with the same answer (accepted by the evaluator)
        d["equivalents"] = dict(equivalents)
    return d


Q = []


def add(id, category, n_resources, structure, nl, patterns, answer_variables, sparql, note=""):
    Q.append(dict(id=id, category=category, n_resources=n_resources, structure=structure,
                  nl_en=nl, patterns=patterns, answer_variables=answer_variables,
                  sparql=sparql.strip(), note=note))


# ---------------------------------------------------------------- lexical_lookup (5)
add(3001, "lexical_lookup", 1, "simple",
    "Which Italian feminine nouns end with the suffix '-ezza'?",
    ["MORPHO_REGEX", "POS_FILTER"], av(["italianWord"]),
    f"""SELECT DISTINCT ?italianWord WHERE {{
  {it(extra='; lila:hasPOS lila:noun ; lila:hasGender lila:feminine ')}
  FILTER(REGEX(STR(?italianWord), "ezza$"))
}}""")

add(3002, "lexical_lookup", 1, "simple",
    "List the Italian adjectives that begin with the prefix 'iper-'.",
    ["MORPHO_REGEX", "POS_FILTER"], av(["italianWord"]),
    f"""SELECT DISTINCT ?italianWord WHERE {{
  {it(extra='; lila:hasPOS lila:adjective ')}
  FILTER(REGEX(STR(?italianWord), "^iper"))
}}""")

add(3003, "lexical_lookup", 1, "simple",
    "Which Italian adjectives are recorded in LiITA with the superlative degree?",
    ["POS_FILTER", "LEXICAL_FORM"], av(["italianWord"]),
    f"""SELECT DISTINCT ?italianWord WHERE {{
  {it(extra='; lila:hasPOS lila:adjective ; lila:hasDegree lila:superlative ')}
}}""")

add(3004, "lexical_lookup", 1, "simple",
    "What lemma variants does LiITA record for the verb 'arrabbiare'?",
    ["LEXICAL_FORM"], av(["variantWord"]),
    f"""SELECT DISTINCT ?variantWord WHERE {{
  GRAPH <http://liita.it/data> {{
    ?italianLemma ontolex:writtenRep ?italianWord ; lila:lemmaVariant ?variant .
    FILTER(STR(?italianWord) = "arrabbiare")
    ?variant ontolex:writtenRep ?variantWord .
  }}
}}""")

add(3005, "lexical_lookup", 1, "simple",
    "Which interjections are listed in the Italian lemma bank?",
    ["POS_FILTER"], av(["italianWord"]),
    f"""SELECT DISTINCT ?italianWord WHERE {{
  {it(extra='; lila:hasPOS lila:interjection ')}
}}""")

# ---------------------------------------------------------------- aggregation (6)
add(3006, "aggregation", 1, "simple",
    "How many proper nouns does the Italian lemma bank contain?",
    ["COUNT_ENTITIES", "POS_FILTER"], av(aggregates=["count"]),
    f"""SELECT (COUNT(DISTINCT ?italianLemma) AS ?count) WHERE {{
  {it(extra='; lila:hasPOS lila:proper_noun ')}
}}""")

add(3007, "aggregation", 1, "simple",
    "How many Italian nouns are masculine and how many are feminine?",
    ["COUNT_ENTITIES", "POS_FILTER"], av(["gender", "count"], numeric=["count"], equivalents={"gender": "genderText"}),
    f"""SELECT ?gender (STRAFTER(STR(?gender), "lila/") AS ?genderText) (COUNT(DISTINCT ?italianLemma) AS ?count) WHERE {{
  {it(extra='; lila:hasPOS lila:noun ; lila:hasGender ?gender ')}
  FILTER(?gender IN (lila:masculine, lila:feminine))
}}
GROUP BY ?gender""", note="nouns with both genders (3,511) are counted in both groups; the one neuter noun is excluded")

add(3008, "aggregation", 1, "simple",
    "How many lemmas are recorded in the Sicilian dialect lemma bank?",
    ["COUNT_ENTITIES"], av(aggregates=["count"]),
    f"""SELECT (COUNT(DISTINCT ?sicilianLemma) AS ?count) WHERE {{
  ?sicilianLemma dcterms:isPartOf {SIC} .
}}""")

add(3009, "aggregation", 2, "simple",
    "What is the average Sentix polarity score of Italian adverbs?",
    ["EMOTION_LEXICON", "POS_FILTER"], av(aggregates=["avgPolarity"]),
    f"""SELECT (AVG(?polarityValue) AS ?avgPolarity) WHERE {{
  GRAPH <http://liita.it/data> {{
    ?italianLemma a ?italianLemmaType ; lila:hasPOS lila:adverb .
    FILTER(?italianLemmaType IN (lila:Lemma, lila:Hypolemma))
  }}
  {polarity()}
}}""", note="no writtenRep join (lemmas with several written forms would be counted more than once); "
            "959 of the 1,003 adverbs with a polarity are hypolemmas (-mente adverbs): without them the average is 0.016")

add(3010, "aggregation", 2, "simple",
    "How many Italian verbs have at least one translation in the Parmigiano dialect?",
    ["COUNT_ENTITIES", "TRANSLATION", "POS_FILTER"], av(aggregates=["count"]),
    f"""SELECT (COUNT(DISTINCT ?italianLemma) AS ?count) WHERE {{
  {it(extra='; lila:hasPOS lila:verb ')}
  {to_dialect('italianLemma', PAR, 'parEntry', 'parmigianoLemma', 'parmigianoWord')}
}}""")

add(3011, "aggregation", 2, "simple",
    "Which part of speech has the largest number of Italian lemmas associated with the emotion Fear?",
    ["COUNT_ENTITIES", "EMOTION_LEXICON"], av(["pos"], aggregates=["count"], equivalents={"pos": "posText"}),
    f"""SELECT ?pos (STRAFTER(STR(?pos), "lila/") AS ?posText) (COUNT(DISTINCT ?italianLemma) AS ?count) WHERE {{
  {it(extra='; lila:hasPOS ?pos ')}
  {emotion(value='elita:Paura', label=None)}
}}
GROUP BY ?pos
ORDER BY DESC(?count)
LIMIT 1""")

# ---------------------------------------------------------------- complit_senses (6)
add(3012, "complit_senses", 1, "simple",
    "How many senses does the word 'corrente' have in CompL-it?",
    ["SENSE_COUNT", "SERVICE_INTEGRATION"], av(aggregates=["count"]),
    f"""SELECT (COUNT(DISTINCT ?sense) AS ?count) WHERE {{
  {CL} {{
    {cl_word('word', 'corrente', 'sense')}
  }}
}}""")

add(3013, "complit_senses", 1, "simple",
    "Rank the words 'rete', 'carta' and 'lettera' by their number of senses.",
    ["SENSE_COUNT", "SERVICE_INTEGRATION"], av(["writtenRep", "count"], numeric=["count"]),
    f"""SELECT ?writtenRep (COUNT(DISTINCT ?sense) AS ?count) WHERE {{
  {CL} {{
    ?word ontolex:canonicalForm [ ontolex:writtenRep ?writtenRep ] ; ontolex:sense ?sense .
    FILTER(REGEX(STR(?writtenRep), "^(rete|carta|lettera)$", "i"))
  }}
}}
GROUP BY ?writtenRep
ORDER BY DESC(?count)""")

add(3014, "complit_senses", 1, "simple",
    "What definitions does CompL-it give for the adjective 'acuto'?",
    ["SENSE_DEFINITION", "SERVICE_INTEGRATION", "POS_FILTER"], av(["definition"]),
    f"""SELECT DISTINCT ?definition WHERE {{
  {CL} {{
    {cl_word('word', 'acuto', 'sense', pos='adjective')}
    ?sense skos:definition ?definition .
  }}
}}""")

add(3015, "complit_senses", 1, "simple",
    "Which words have a definition in CompL-it that mentions 'cavallo'?",
    ["SENSE_DEFINITION", "SERVICE_INTEGRATION"], av(["writtenRep"], ["exampleDefinition"]),
    f"""SELECT ?writtenRep (SAMPLE(?definition) AS ?exampleDefinition) WHERE {{
  {CL} {{
    ?word ontolex:canonicalForm [ ontolex:writtenRep ?writtenRep ] ; ontolex:sense ?sense .
    ?sense skos:definition ?definition .
    FILTER(REGEX(STR(?definition), "cavallo", "i"))
  }}
}}
GROUP BY ?writtenRep""")

add(3016, "complit_senses", 1, "simple",
    "Which verbs in CompL-it have a definition containing the word 'fuoco'?",
    ["SENSE_DEFINITION", "SERVICE_INTEGRATION", "POS_FILTER"], av(["writtenRep"], ["exampleDefinition"]),
    f"""SELECT ?writtenRep (SAMPLE(?definition) AS ?exampleDefinition) WHERE {{
  {CL} {{
    ?word ontolex:canonicalForm [ ontolex:writtenRep ?writtenRep ] ; ontolex:sense ?sense ;
          lexinfo:partOfSpeech [ rdfs:label ?pos ] .
    FILTER(STR(?pos) = "verb")
    ?sense skos:definition ?definition .
    FILTER(REGEX(STR(?definition), "fuoco", "i"))
  }}
}}
GROUP BY ?writtenRep""")

add(3017, "complit_senses", 1, "simple",
    "Which nouns have a CompL-it definition that begins with 'insieme di'?",
    ["SENSE_DEFINITION", "SERVICE_INTEGRATION", "POS_FILTER"], av(["writtenRep"], ["exampleDefinition"]),
    f"""SELECT ?writtenRep (SAMPLE(?definition) AS ?exampleDefinition) WHERE {{
  {CL} {{
    ?word ontolex:canonicalForm [ ontolex:writtenRep ?writtenRep ] ; ontolex:sense ?sense ;
          lexinfo:partOfSpeech [ rdfs:label ?pos ] .
    FILTER(STR(?pos) = "noun")
    ?sense skos:definition ?definition .
    FILTER(REGEX(STR(?definition), "^insieme di", "i"))
  }}
}}
GROUP BY ?writtenRep""")

# ---------------------------------------------------------------- semantic_relation (6)
add(3018, "semantic_relation", 1, "simple",
    "What kinds of insects are recorded in the lexical database?",
    ["SEMANTIC_RELATION", "SERVICE_INTEGRATION"], av(["italianWord"]),
    f"""SELECT DISTINCT ?italianWord WHERE {{
  {CL} {{
    {cl_word('seed', 'insetto', 'seedSense')}
    ?seedSense lexinfo:hypernym ?relSense .
    {related('relSense', 'relWord', 'italianWord')}
  }}
}}""", note="CompL-it: '?seed lexinfo:hypernym ?x' links the seed to its hyponyms")

add(3019, "semantic_relation", 1, "simple",
    "Which parts of a ship ('nave') does the lexicon list?",
    ["SEMANTIC_RELATION", "SERVICE_INTEGRATION"], av(["italianWord"]),
    f"""SELECT DISTINCT ?italianWord WHERE {{
  {CL} {{
    {cl_word('seed', 'nave', 'seedSense')}
    ?relSense lexinfo:partMeronym ?seedSense .
    {related('relSense', 'relWord', 'italianWord')}
  }}
}}""")

add(3020, "semantic_relation", 1, "simple",
    "What is a 'trota' a type of, according to the lexical database?",
    ["SEMANTIC_RELATION", "SERVICE_INTEGRATION"], av(["italianWord"]),
    f"""SELECT DISTINCT ?italianWord WHERE {{
  {CL} {{
    {cl_word('seed', 'trota', 'seedSense')}
    ?seedSense lexinfo:hyponym ?relSense .
    {related('relSense', 'relWord', 'italianWord')}
  }}
}}""", note="CompL-it: '?seed lexinfo:hyponym ?x' links the seed to its hypernyms")

add(3021, "semantic_relation", 1, "simple",
    "Which approximate synonyms of 'acuto' are recorded?",
    ["SEMANTIC_RELATION", "SERVICE_INTEGRATION"], av(["italianWord"]),
    f"""SELECT DISTINCT ?italianWord WHERE {{
  {CL} {{
    {cl_word('seed', 'acuto', 'seedSense')}
    {{ ?seedSense lexinfo:approximateSynonym ?relSense }} UNION {{ ?relSense lexinfo:approximateSynonym ?seedSense }}
    {related('relSense', 'relWord', 'italianWord')}
  }}
}}""")

add(3022, "semantic_relation", 1, "simple",
    "What are the antonyms of 'veloce'?",
    ["SEMANTIC_RELATION", "SERVICE_INTEGRATION"], av(["italianWord"]),
    f"""SELECT DISTINCT ?italianWord WHERE {{
  {CL} {{
    {cl_word('seed', 'veloce', 'seedSense')}
    {{ ?seedSense lexinfo:antonym ?relSense }} UNION {{ ?relSense lexinfo:antonym ?seedSense }}
    {related('relSense', 'relWord', 'italianWord')}
  }}
}}""")

add(3023, "semantic_relation", 1, "simple",
    "Of which larger wholes is the 'scheletro' (skeleton) a part?",
    ["SEMANTIC_RELATION", "SERVICE_INTEGRATION"], av(["italianWord"]),
    f"""SELECT DISTINCT ?italianWord WHERE {{
  {CL} {{
    {cl_word('seed', 'scheletro', 'seedSense')}
    ?seedSense lexinfo:partMeronym ?relSense .
    {related('relSense', 'relWord', 'italianWord')}
  }}
}}""")

# ---------------------------------------------------------------- affective (6)
add(3024, "affective", 2, "simple",
    "Which Italian adjectives are associated with the emotion Trust?",
    ["EMOTION_LEXICON", "POS_FILTER"], av(["italianWord"]),
    f"""SELECT DISTINCT ?italianWord WHERE {{
  {it(extra='; lila:hasPOS lila:adjective ')}
  {emotion(value='elita:Fiducia', label=None)}
}}""")

add(3025, "affective", 2, "simple",
    "Which emotions does ELIta associate with the word 'vergogna'?",
    ["EMOTION_LEXICON"], av(["emotionLabel"], secondary=["emotion"]),
    f"""SELECT DISTINCT ?emotion ?emotionLabel WHERE {{
  {it()}
  FILTER(STR(?italianWord) = "vergogna")
  {emotion()}
}}""")

add(3026, "affective", 2, "simple",
    "What Sentix polarity values are recorded for the word 'solitudine'?",
    ["EMOTION_LEXICON"], av(["polarityValue"], numeric=["polarityValue"]),
    f"""SELECT DISTINCT ?polarityValue WHERE {{
  {it()}
  FILTER(STR(?italianWord) = "solitudine")
  {polarity()}
}}""", note="'solitudine' has two Sentix entries with different values")

add(3027, "affective", 2, "simple",
    "List the Italian verbs whose Sentix polarity score is below -0.7.",
    ["EMOTION_LEXICON", "POS_FILTER"], av(["italianWord"], numeric=["minPolarity"]),
    f"""SELECT ?italianWord (MIN(?polarityValue) AS ?minPolarity) WHERE {{
  {it(extra='; lila:hasPOS lila:verb ')}
  {polarity()}
  FILTER(?polarityValue < -0.7)
}}
GROUP BY ?italianWord""")

add(3028, "affective", 3, "simple",
    "Which nouns associated with the emotion Disgust nevertheless have a positive Sentix polarity?",
    ["EMOTION_LEXICON", "POS_FILTER"], av(["italianWord"], numeric=["maxPolarity"]),
    f"""SELECT ?italianWord (MAX(?polarityValue) AS ?maxPolarity) WHERE {{
  {it(extra='; lila:hasPOS lila:noun ')}
  {emotion(value='elita:Disgusto', label=None)}
  {polarity()}
  FILTER(?polarityValue > 0)
}}
GROUP BY ?italianWord""")

add(3029, "affective", 2, "simple",
    "For each emotion, how many Italian adverbs are associated with it?",
    ["EMOTION_LEXICON", "COUNT_ENTITIES", "POS_FILTER"], av(["emotionLabel", "count"], secondary=["emotion"], numeric=["count"]),
    f"""SELECT ?emotion ?emotionLabel (COUNT(DISTINCT ?italianLemma) AS ?count) WHERE {{
  {it(extra='; lila:hasPOS lila:adverb ')}
  {emotion()}
}}
GROUP BY ?emotion ?emotionLabel
ORDER BY DESC(?count)""")

# ---------------------------------------------------------------- dialect_translation (6)
add(3030, "dialect_translation", 2, "simple",
    "What is the Sicilian word for 'cucchiaio' (spoon)?",
    ["TRANSLATION"], av(["italianWord", "sicilianWord"]),
    f"""SELECT DISTINCT ?italianWord ?sicilianWord WHERE {{
  {it()}
  FILTER(STR(?italianWord) = "cucchiaio")
  {to_dialect('italianLemma', SIC, 'sicEntry', 'sicilianLemma', 'sicilianWord')}
}}""")

add(3031, "dialect_translation", 2, "simple",
    "How do you say 'formaggio' in the Parmigiano dialect?",
    ["TRANSLATION"], av(["italianWord", "parmigianoWord"]),
    f"""SELECT DISTINCT ?italianWord ?parmigianoWord WHERE {{
  {it()}
  FILTER(STR(?italianWord) = "formaggio")
  {to_dialect('italianLemma', PAR, 'parEntry', 'parmigianoLemma', 'parmigianoWord')}
}}""")

add(3032, "dialect_translation", 2, "simple",
    "Which Italian words are translated by the Sicilian word 'picciriddu'?",
    ["TRANSLATION"], av(["italianWord"], ["sicilianWord"]),
    f"""SELECT DISTINCT ?italianWord ?sicilianWord WHERE {{
  {it()}
  {to_dialect('italianLemma', SIC, 'sicEntry', 'sicilianLemma', 'sicilianWord')}
  FILTER(STR(?sicilianWord) = "picciriddu")
}}""", note="reverse direction: from the dialect word to Italian")

add(3033, "dialect_translation", 3, "simple",
    "Give both the Sicilian and the Parmigiano translations of 'fratello'.",
    ["TRANSLATION", "MULTI_TRANSLATION"], av(["italianWord", "sicilianWord", "parmigianoWord"]),
    f"""SELECT DISTINCT ?italianWord ?sicilianWord ?parmigianoWord WHERE {{
  {it()}
  FILTER(STR(?italianWord) = "fratello")
  {to_dialect('italianLemma', SIC, 'sicEntry', 'sicilianLemma', 'sicilianWord')}
  {to_dialect('italianLemma', PAR, 'parEntry', 'parmigianoLemma', 'parmigianoWord')}
}}""")

add(3034, "dialect_translation", 1, "simple",
    "Which Parmigiano lemmas end in '-er', with or without an accent on the e (e.g. '-ér', '-èr')?",
    ["MORPHO_REGEX"], av(["parmigianoWord"]),
    f"""SELECT DISTINCT ?parmigianoWord WHERE {{
  ?parmigianoLemma dcterms:isPartOf {PAR} ; ontolex:writtenRep ?parmigianoWord .
  FILTER(REGEX(STR(?parmigianoWord), "[eéèê]r$"))
}}""")

add(3035, "dialect_translation", 2, "simple",
    "Find the Sicilian translations of Italian verbs that begin with 'lavor'.",
    ["TRANSLATION", "MORPHO_REGEX", "POS_FILTER"], av(["italianWord", "sicilianWord"]),
    f"""SELECT DISTINCT ?italianWord ?sicilianWord WHERE {{
  {it(extra='; lila:hasPOS lila:verb ')}
  FILTER(REGEX(STR(?italianWord), "^lavor"))
  {to_dialect('italianLemma', SIC, 'sicEntry', 'sicilianLemma', 'sicilianWord')}
}}""")

# ---------------------------------------------------------------- multi_resource (6)
add(3036, "multi_resource", 3, "simple",
    "Which kinds of weapon ('arma') have a Sicilian translation, and what is it?",
    ["SEMANTIC_RELATION", "SERVICE_INTEGRATION", "TRANSLATION"], av(["italianWord", "sicilianWord"]),
    f"""SELECT DISTINCT ?italianWord ?sicilianWord WHERE {{
  {CL} {{
    {cl_word('seed', 'arma', 'seedSense')}
    ?seedSense lexinfo:hypernym ?relSense .
    ?relWord ontolex:sense ?relSense .
  }}
  ?relWord ontolex:canonicalForm ?italianLemma .
  {it()}
  {to_dialect('italianLemma', SIC, 'sicEntry', 'sicilianLemma', 'sicilianWord')}
}}""")

add(3037, "multi_resource", 3, "simple",
    "What are the CompL-it definitions of Italian nouns associated with Surprise that start with 'stup'?",
    ["EMOTION_LEXICON", "SENSE_DEFINITION", "SERVICE_INTEGRATION", "MORPHO_REGEX"],
    av(["italianWord", "definition"]),
    f"""SELECT DISTINCT ?italianWord ?definition WHERE {{
  {it(extra='; lila:hasPOS lila:noun ')}
  FILTER(REGEX(STR(?italianWord), "^stup"))
  {emotion(value='elita:Sorpresa', label=None)}
  ?word ontolex:canonicalForm ?italianLemma .
  {CL} {{
    ?word ontolex:sense ?sense . ?sense skos:definition ?definition .
  }}
}}""")

add(3038, "multi_resource", 3, "simple",
    "Which parts of a theatre ('teatro') are associated with an emotion in ELIta, and with which emotions?",
    ["SEMANTIC_RELATION", "SERVICE_INTEGRATION", "EMOTION_LEXICON"], av(["italianWord", "emotionLabel"], secondary=["emotion"]),
    f"""SELECT DISTINCT ?italianWord ?emotion ?emotionLabel WHERE {{
  {CL} {{
    {cl_word('seed', 'teatro', 'seedSense')}
    ?relSense lexinfo:partMeronym ?seedSense .
    ?relWord ontolex:sense ?relSense .
  }}
  ?relWord ontolex:canonicalForm ?italianLemma .
  {it()}
  {emotion()}
}}""")

add(3039, "multi_resource", 3, "simple",
    "List the Parmigiano translations of Italian nouns with a Sentix polarity above 0.8.",
    ["EMOTION_LEXICON", "TRANSLATION", "POS_FILTER"], av(["italianWord", "parmigianoWord"], numeric=["maxPolarity"]),
    f"""SELECT ?italianWord ?parmigianoWord (MAX(?polarityValue) AS ?maxPolarity) WHERE {{
  {it(extra='; lila:hasPOS lila:noun ')}
  {polarity()}
  FILTER(?polarityValue > 0.8)
  {to_dialect('italianLemma', PAR, 'parEntry', 'parmigianoLemma', 'parmigianoWord')}
}}
GROUP BY ?italianWord ?parmigianoWord""")

add(3040, "multi_resource", 3, "simple",
    "What Sentix polarity do the different kinds of drink ('bevanda') have?",
    ["SEMANTIC_RELATION", "SERVICE_INTEGRATION", "EMOTION_LEXICON"], av(["italianWord", "polarityValue"], numeric=["polarityValue"]),
    f"""SELECT DISTINCT ?italianWord ?polarityValue WHERE {{
  {CL} {{
    {cl_word('seed', 'bevanda', 'seedSense')}
    ?seedSense lexinfo:hypernym ?relSense .
    ?relWord ontolex:sense ?relSense .
  }}
  ?relWord ontolex:canonicalForm ?italianLemma .
  {it()}
  {polarity()}
}}""")

add(3041, "multi_resource", 3, "simple",
    "Which approximate synonyms of 'crudele' (cruel) are associated with the emotion Fear?",
    ["SEMANTIC_RELATION", "SERVICE_INTEGRATION", "EMOTION_LEXICON"], av(["italianWord"]),
    f"""SELECT DISTINCT ?italianWord WHERE {{
  {CL} {{
    {cl_word('seed', 'crudele', 'seedSense')}
    {{ ?seedSense lexinfo:approximateSynonym ?relSense }} UNION {{ ?relSense lexinfo:approximateSynonym ?seedSense }}
    ?relWord ontolex:sense ?relSense .
  }}
  ?relWord ontolex:canonicalForm ?italianLemma .
  {it()}
  {emotion(value='elita:Paura', label=None)}
}}""")

# ---------------------------------------------------------------- compositional (9)
add(3042, "compositional", 2, "intersection",
    "Which Italian words are associated with both Fear and Anger?",
    ["EMOTION_LEXICON"], av(["italianWord"]),
    f"""SELECT DISTINCT ?italianWord WHERE {{
  {it()}
  {emotion(entry='fearEntry', value='elita:Paura', label=None)}
  {emotion(entry='angerEntry', value='elita:Rabbia', label=None)}
}}""", note="the same resource (ELIta) is used twice, joined on the lemma (AND, not OR)")

add(3043, "compositional", 2, "self_join",
    "Which other Italian words share a Sicilian translation with 'bambino'?",
    ["TRANSLATION"], av(["otherWord"], ["sharedSicilianWord"]),
    f"""SELECT ?otherWord (SAMPLE(?sicilianWord) AS ?sharedSicilianWord) WHERE {{
  {it()}
  FILTER(STR(?italianWord) = "bambino")
  {to_dialect('italianLemma', SIC, 'sicEntry', 'sicilianLemma', 'sicilianWord')}
  ?otherEntryIt vartrans:translatableAs ?sicEntry ; ontolex:canonicalForm ?otherLemma .
  {it('otherLemma', 'otherWord')}
  FILTER(?otherLemma != ?italianLemma)
}}
GROUP BY ?otherWord""", note="the translation relation is used twice, from two Italian lemmas to the same Sicilian entry")

add(3044, "compositional", 1, "chain",
    "What are the hyponyms of the hyponyms of 'mammifero' (mammal)?",
    ["SEMANTIC_RELATION", "SERVICE_INTEGRATION"], av(["italianWord"]),
    f"""SELECT DISTINCT ?italianWord WHERE {{
  {CL} {{
    {cl_word('seed', 'mammifero', 'seedSense')}
    ?seedSense lexinfo:hypernym ?midSense .
    ?midSense lexinfo:hypernym ?relSense .
    {related('relSense', 'relWord', 'italianWord')}
  }}
}}""", note="the same relation is followed twice (two hops)")

add(3045, "compositional", 1, "intersection",
    "Which hypernyms do 'mela' and 'pera' have in common?",
    ["SEMANTIC_RELATION", "SERVICE_INTEGRATION"], av(["italianWord"]),
    f"""SELECT DISTINCT ?italianWord WHERE {{
  {CL} {{
    {cl_word('a', 'mela', 'aSense')}
    {cl_word('b', 'pera', 'bSense')}
    ?aSense lexinfo:hyponym ?relSense .
    ?bSense lexinfo:hyponym ?relSense .
    {related('relSense', 'relWord', 'italianWord')}
  }}
}}""", note="two seed words, the relation is instantiated twice and intersected")

add(3046, "compositional", 3, "negation",
    "Which Italian verbs associated with Disgust have no Parmigiano translation?",
    ["EMOTION_LEXICON", "TRANSLATION", "POS_FILTER"], av(["italianWord"]),
    f"""SELECT DISTINCT ?italianWord WHERE {{
  {it(extra='; lila:hasPOS lila:verb ')}
  {emotion(value='elita:Disgusto', label=None)}
  FILTER NOT EXISTS {{
    ?parEntryIt ontolex:canonicalForm ?italianLemma ; vartrans:translatableAs ?parEntry .
    ?parEntry ontolex:canonicalForm ?parmigianoLemma .
    ?parmigianoLemma dcterms:isPartOf {PAR} .
  }}
}}""", note="balanced on purpose: 45 of the 96 verbs have a Parmigiano translation, 51 do not")

add(3047, "compositional", 3, "variable_comparison",
    "Which dialect words are spelled exactly the same in Sicilian and in Parmigiano when they translate the same Italian word?",
    ["TRANSLATION", "MULTI_TRANSLATION"], av(["dialectWord"], ["exampleItalianWord"]),
    f"""SELECT ?dialectWord (SAMPLE(?italianWord) AS ?exampleItalianWord) WHERE {{
  {it()}
  {to_dialect('italianLemma', SIC, 'sicEntry', 'sicilianLemma', 'dialectWord')}
  {to_dialect('italianLemma', PAR, 'parEntry', 'parmigianoLemma', 'parmigianoWord')}
  FILTER(STR(?dialectWord) = STR(?parmigianoWord))
}}
GROUP BY ?dialectWord""", note="two variables from different resources are compared with each other; the answer is the dialect form "
            "(Italian abbreviations such as p., pag. for 'pagina' would otherwise dominate the rows)")

add(3048, "compositional", 2, "per_item_aggregation",
    "Which Italian words are associated with more than six of the nine emotion categories of ELIta?",
    ["EMOTION_LEXICON", "COUNT_ENTITIES"], av(["italianWord", "count"], numeric=["count"]),
    f"""SELECT ?italianWord (COUNT(DISTINCT ?emotion) AS ?count) WHERE {{
  {it()}
  {emotion()}
}}
GROUP BY ?italianWord
HAVING (COUNT(DISTINCT ?emotion) > 6)
ORDER BY DESC(?count)""", note="count per item, then a condition on the count; only labelled emotions (Valenza/Dominanza have no label)")

add(3049, "compositional", 2, "value_comparison",
    "Which nouns associated with Trust have a higher Sentix polarity than the word 'appartenenza' (belonging)?",
    ["EMOTION_LEXICON", "POS_FILTER"], av(["italianWord"], numeric=["maxPolarity"]),
    f"""SELECT ?italianWord (MAX(?polarityValue) AS ?maxPolarity) WHERE {{
  {{ SELECT (MAX(xsd:float(?refValue)) AS ?refPolarity) WHERE {{
      ?refLemma ontolex:writtenRep ?refWord . FILTER(STR(?refWord) = "appartenenza")
      {polarity('refLemma', 'refPolarityEntry', 'refValue')}
  }} }}
  {it(extra='; lila:hasPOS lila:noun ')}
  {emotion(value='elita:Fiducia', label=None)}
  ?polarityEntry ontolex:canonicalForm ?italianLemma ; marl:hasPolarity ?polarityClass ; marl:hasPolarityValue ?rawValue .
  BIND(xsd:float(?rawValue) AS ?polarityValue)
  FILTER(?polarityValue > ?refPolarity)
}}
GROUP BY ?italianWord""", note="the comparison value is read from another word: 'appartenenza' has a single Sentix value (0.5)")

add(3050, "compositional", 2, "union",
    "How many Italian words are associated with Disgust in ELIta or have a Sentix polarity below -0.9?",
    ["EMOTION_LEXICON", "COUNT_ENTITIES"], av(aggregates=["count"]),
    f"""SELECT (COUNT(DISTINCT ?italianLemma) AS ?count) WHERE {{
  {it()}
  {{ {emotion(value='elita:Disgusto', label=None)} }}
  UNION
  {{ {polarity()} FILTER(?polarityValue < -0.9) }}
}}""")


# Second and third question per compositional structure (3051-3065), registered via add()
import draft_extra  # noqa: E402,F401
