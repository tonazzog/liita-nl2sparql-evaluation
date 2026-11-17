"""Held-out test set: second and third question per compositional structure (added 2026-11-07),
so that a single error does not decide the result for a structure. Imported at the end of draft.py."""

from draft import add, av, it, to_dialect, emotion, polarity, cl_word, related, CL, SIC, PAR

add(3051, "compositional", 2, "intersection",
    "Which Italian adjectives are associated with both Trust and Surprise?",
    ["EMOTION_LEXICON", "POS_FILTER"], av(["italianWord"]),
    f"""SELECT DISTINCT ?italianWord WHERE {{
  {it(extra='; lila:hasPOS lila:adjective ')}
  {emotion(entry='trustEntry', value='elita:Fiducia', label=None)}
  {emotion(entry='surpriseEntry', value='elita:Sorpresa', label=None)}
}}""")

add(3052, "compositional", 2, "self_join",
    "Which other Italian words share a Sicilian translation with 'allegria' (cheerfulness)?",
    ["TRANSLATION"], av(["otherWord"], ["sharedSicilianWord"]),
    f"""SELECT ?otherWord (SAMPLE(?sicilianWord) AS ?sharedSicilianWord) WHERE {{
  {it()}
  FILTER(STR(?italianWord) = "allegria")
  {to_dialect('italianLemma', SIC, 'sicEntry', 'sicilianLemma', 'sicilianWord')}
  ?otherEntryIt vartrans:translatableAs ?sicEntry ; ontolex:canonicalForm ?otherLemma .
  {it('otherLemma', 'otherWord')}
  FILTER(?otherLemma != ?italianLemma)
}}
GROUP BY ?otherWord""")

add(3053, "compositional", 2, "self_join",
    "Which other Italian words are translated into Sicilian with the same word as 'ansia' (anxiety)?",
    ["TRANSLATION"], av(["otherWord"], ["sharedSicilianWord"]),
    f"""SELECT ?otherWord (SAMPLE(?sicilianWord) AS ?sharedSicilianWord) WHERE {{
  {it()}
  FILTER(STR(?italianWord) = "ansia")
  {to_dialect('italianLemma', SIC, 'sicEntry', 'sicilianLemma', 'sicilianWord')}
  ?otherEntryIt vartrans:translatableAs ?sicEntry ; ontolex:canonicalForm ?otherLemma .
  {it('otherLemma', 'otherWord')}
  FILTER(?otherLemma != ?italianLemma)
}}
GROUP BY ?otherWord""")

add(3054, "compositional", 1, "chain",
    "What are the parts of the parts of an 'autoveicolo' (motor vehicle)?",
    ["SEMANTIC_RELATION", "SERVICE_INTEGRATION"], av(["italianWord"]),
    f"""SELECT DISTINCT ?italianWord WHERE {{
  {CL} {{
    {cl_word('seed', 'autoveicolo', 'seedSense')}
    ?midSense lexinfo:partMeronym ?seedSense .
    ?relSense lexinfo:partMeronym ?midSense .
    {related('relSense', 'relWord', 'italianWord')}
  }}
}}""", note="the part-of relation is followed twice")

add(3055, "compositional", 1, "chain",
    "What are the hypernyms of the hypernyms of 'salmone' (salmon)?",
    ["SEMANTIC_RELATION", "SERVICE_INTEGRATION"], av(["italianWord"]),
    f"""SELECT DISTINCT ?italianWord WHERE {{
  {CL} {{
    {cl_word('seed', 'salmone', 'seedSense')}
    ?seedSense lexinfo:hyponym ?midSense .
    ?midSense lexinfo:hyponym ?relSense .
    {related('relSense', 'relWord', 'italianWord')}
  }}
}}""", note="the relation is followed twice, upwards")

add(3056, "compositional", 2, "negation",
    "Which Italian nouns have a Sentix polarity below -0.8 but are not associated with any emotion in ELIta?",
    ["EMOTION_LEXICON", "POS_FILTER"], av(["italianWord"], numeric=["polarityValue"]),
    f"""SELECT DISTINCT ?italianWord ?polarityValue WHERE {{
  {it(extra='; lila:hasPOS lila:noun ')}
  {polarity()}
  FILTER(?polarityValue < -0.8)
  FILTER NOT EXISTS {{ ?emotionEntry ontolex:canonicalForm ?italianLemma ; elita:HasEmotion ?emotion . }}
}}""")

add(3057, "compositional", 3, "negation",
    "Which kinds of fruit ('frutto') have no Sicilian translation?",
    ["SEMANTIC_RELATION", "SERVICE_INTEGRATION", "TRANSLATION"], av(["italianWord"]),
    f"""SELECT DISTINCT ?italianWord WHERE {{
  {CL} {{
    {cl_word('seed', 'frutto', 'seedSense')}
    ?seedSense lexinfo:hypernym ?relSense .
    ?relWord ontolex:sense ?relSense .
  }}
  ?relWord ontolex:canonicalForm ?italianLemma .
  {it()}
  FILTER NOT EXISTS {{
    ?sicEntryIt ontolex:canonicalForm ?italianLemma ; vartrans:translatableAs ?sicEntry .
    ?sicEntry ontolex:canonicalForm ?sicilianLemma .
    ?sicilianLemma dcterms:isPartOf {SIC} .
  }}
}}""")

add(3058, "compositional", 2, "simple",
    "Which Italian verbs beginning with 'sc' have a Sicilian translation that also begins with 'sc'?",
    ["TRANSLATION", "MORPHO_REGEX", "POS_FILTER"], av(["italianWord", "sicilianWord"]),
    f"""SELECT DISTINCT ?italianWord ?sicilianWord WHERE {{
  {it(extra='; lila:hasPOS lila:verb ')}
  FILTER(REGEX(STR(?italianWord), "^sc"))
  {to_dialect('italianLemma', SIC, 'sicEntry', 'sicilianLemma', 'sicilianWord')}
  FILTER(REGEX(STR(?sicilianWord), "^sc"))
}}""", note="reworded 2026-11-09 from 'same three letters' (literal comparison missed o>u, e>i and accented cognates); now a filter on both sides of the translation")

add(3059, "compositional", 2, "variable_comparison",
    "Which Italian adverbs have a Sentix polarity of the opposite sign to their polarity in ELIta?",
    ["EMOTION_LEXICON", "POS_FILTER"], av(["italianWord"]),
    f"""SELECT DISTINCT ?italianWord WHERE {{
  {it(extra='; lila:hasPOS lila:adverb ')}
  {polarity(var='sentixValue')}
  GRAPH <http://w3id.org/elita> {{
    ?elitaEntry ontolex:canonicalForm ?italianLemma ; marl:hasPolarityValue ?elitaRaw .
  }}
  BIND(xsd:float(?elitaRaw) AS ?elitaValue)
  FILTER((?sentixValue > 0 && ?elitaValue < 0) || (?sentixValue < 0 && ?elitaValue > 0))
}}""", note="two values for the same lemma are compared. Rewritten 2026-11-13 (decision A): the previous question "
          "('both a positive and a negative Sentix value') only had answers by mixing ELIta and Sentix values; with "
          "Sentix alone no lemma has values of opposite sign")

add(3060, "compositional", 2, "per_item_aggregation",
    "Which Sicilian words translate more than six different Italian verbs?",
    ["TRANSLATION", "COUNT_ENTITIES", "POS_FILTER"], av(["sicilianWord"], aggregates=["count"]),
    f"""SELECT ?sicilianWord (COUNT(DISTINCT ?italianWord) AS ?count) WHERE {{
  {it(extra='; lila:hasPOS lila:verb ')}
  {to_dialect('italianLemma', SIC, 'sicEntry', 'sicilianLemma', 'sicilianWord')}
}}
GROUP BY ?sicilianWord
HAVING (COUNT(DISTINCT ?italianWord) > 6)
ORDER BY DESC(?count)""", note="count per dialect word (reverse direction), then a condition on the count; counts distinct written forms, not lemma IRIs (homographs); restricted to verbs (2026-11-09) to avoid articulated-preposition variants")

add(3061, "compositional", 2, "per_item_aggregation",
    "On average, how many of the nine ELIta emotion categories are associated with an Italian adjective that has at least one of them?",
    ["EMOTION_LEXICON", "COUNT_ENTITIES", "POS_FILTER"], av(aggregates=["avgEmotions"]),
    f"""SELECT (AVG(?emotionCount) AS ?avgEmotions) WHERE {{
  {{ SELECT ?italianLemma (COUNT(DISTINCT ?emotion) AS ?emotionCount) WHERE {{
      {it(extra='; lila:hasPOS lila:adjective ')}
      {emotion()}
  }} GROUP BY ?italianLemma }}
}}""", note="count per item, then the average of the counts; only labelled emotions. Near-miss variants (analysis only): per word 2.4313, incl. Valenza/Dominanza 2.4633, without hypolemmas 2.5036")

add(3062, "compositional", 2, "value_comparison",
    "Which Italian verbs have at least one Sentix polarity value higher than that of the verb 'studiare' (to study)?",
    ["EMOTION_LEXICON", "POS_FILTER"], av(["italianWord"], numeric=["maxPolarity"]),
    f"""SELECT ?italianWord (MAX(?polarityValue) AS ?maxPolarity) WHERE {{
  {{ SELECT (MAX(?refValue) AS ?refPolarity) WHERE {{
      ?refLemma ontolex:writtenRep ?refWord . FILTER(STR(?refWord) = "studiare")
      {polarity('refLemma', 'refPolarityEntry', 'refValue')}
  }} }}
  {it(extra='; lila:hasPOS lila:verb ')}
  {polarity()}
  FILTER(?polarityValue > ?refPolarity)
}}
GROUP BY ?italianWord""", note="reference changed 2026-11-13 (decision A): 'scrivere' has only an ELIta value (0.542), no Sentix entry; 'studiare' has a single Sentix value (0.25). Reworded 2026-11-09 to 'at least one value'. Variants for error analysis: average higher 81, all values higher (MIN) 65")

add(3063, "compositional", 2, "value_comparison",
    "Which emotions are associated with more Italian verbs than the emotion Sadness?",
    ["EMOTION_LEXICON", "COUNT_ENTITIES", "POS_FILTER"], av(["emotionLabel"], secondary=["emotion", "count"], numeric=["count"]),
    f"""SELECT ?emotion ?emotionLabel ?count WHERE {{
  {{ SELECT (COUNT(DISTINCT ?refLemma) AS ?refCount) WHERE {{
      {it('refLemma', 'refWord', '; lila:hasPOS lila:verb ')}
      {emotion(lemma='refLemma', entry='refEntry', value='elita:Tristezza', label=None)}
  }} }}
  {{ SELECT ?emotion ?emotionLabel (COUNT(DISTINCT ?italianLemma) AS ?count) WHERE {{
      {it(extra='; lila:hasPOS lila:verb ')}
      {emotion()}
  }} GROUP BY ?emotion ?emotionLabel }}
  FILTER(?count > ?refCount)
}}
ORDER BY DESC(?count)""", note="two aggregates are compared: a count per emotion against the count for Sadness. Reworded 2026-11-09 (Disgust was the minimum, so all other 8 emotions were returned); answer is the same counting lemmas or words (Fiducia 226/280 vs Tristezza 193/229); count secondary")

add(3064, "compositional", 3, "union",
    "Which Italian words beginning with 'sv' have a translation in Sicilian or in Parmigiano?",
    ["TRANSLATION", "MULTI_TRANSLATION", "MORPHO_REGEX"], av(["italianWord"]),
    f"""SELECT DISTINCT ?italianWord WHERE {{
  {it()}
  FILTER(REGEX(STR(?italianWord), "^sv"))
  {{ {to_dialect('italianLemma', SIC, 'sicEntry', 'sicilianLemma', 'sicilianWord')} }}
  UNION
  {{ {to_dialect('italianLemma', PAR, 'parEntry', 'parmigianoLemma', 'parmigianoWord')} }}
}}""")

add(3065, "compositional", 4, "union",
    "Which kinds of mammal ('mammifero') have a translation in Sicilian or in Parmigiano?",
    ["SEMANTIC_RELATION", "SERVICE_INTEGRATION", "TRANSLATION", "MULTI_TRANSLATION"], av(["italianWord"]),
    f"""SELECT DISTINCT ?italianWord WHERE {{
  {CL} {{
    {cl_word('seed', 'mammifero', 'seedSense')}
    ?seedSense lexinfo:hypernym ?relSense .
    ?relWord ontolex:sense ?relSense .
  }}
  ?relWord ontolex:canonicalForm ?italianLemma .
  {it()}
  {{ {to_dialect('italianLemma', SIC, 'sicEntry', 'sicilianLemma', 'sicilianWord')} }}
  UNION
  {{ {to_dialect('italianLemma', PAR, 'parEntry', 'parmigianoLemma', 'parmigianoWord')} }}
}}""", note="replaced 2026-11-09: the former 'fish: Joy in ELIta or positive Sentix' had an empty ELIta branch (Joy words are always Sentix-positive). Balance: 17 Sicilian only, 16 Parmigiano only, 25 both; LiITA lemma 'c' linked to a mammal sense (data anomaly)")


# ---------------------------------------------------------------- all six resources (added 2026-11-07)
add(3066, "multi_resource", 6, "simple",
    "Which Italian words whose CompL-it definition mentions 'dolore' (pain) are associated with an emotion in ELIta, "
    "have a Sentix polarity value, and have both a Sicilian and a Parmigiano translation? For each word, give one definition, "
    "the number of emotions, the highest polarity value and one Sicilian and one Parmigiano translation.",
    ["SENSE_DEFINITION", "SERVICE_INTEGRATION", "EMOTION_LEXICON", "TRANSLATION", "MULTI_TRANSLATION", "COUNT_ENTITIES"],
    av(["italianWord"], secondary=["exampleDefinition", "emotionCount", "maxPolarity", "exampleSicilian", "exampleParmigiano"],
       numeric=["emotionCount", "maxPolarity"]),
    # gold = body of superquery.rq (full cartesian version, 310 rows, kept for the thesis) grouped to one row per word
    "SELECT ?italianWord (SAMPLE(?definition) AS ?exampleDefinition) (COUNT(DISTINCT ?emotion) AS ?emotionCount)\n"
    "  (MAX(?polarityValue) AS ?maxPolarity) (SAMPLE(?sicilianWord) AS ?exampleSicilian) (SAMPLE(?parmigianoWord) AS ?exampleParmigiano)\n"
    "WHERE" + open("superquery.rq", encoding="utf-8").read().split("WHERE", 1)[1].rsplit("ORDER BY", 1)[0].replace('"sentimento"', '"dolore"').replace("; marl:hasPolarityValue ?polarityRaw", "; marl:hasPolarity ?polarityClass ; marl:hasPolarityValue ?polarityRaw")  # Sentix only (decision A, 2026-11-13)
    + "GROUP BY ?italianWord\nORDER BY ?italianWord",
    note="all six resources used by the systems: CompL-it, LiITA, ELIta, Sentix, Sicilian, Parmigiano. Reworded 2026-11-09 to one row "
         "per word (the full superquery.rq returns 310 cartesian rows for 21 words); SAMPLE columns are secondary (arbitrary values). "
         "Keyword changed 2026-11-09 from 'sentimento' (seed word of NL2SPARQL example 'hyponyms of sentimento ... polarity and translations'); superquery.rq keeps 'sentimento' as the thesis showcase. 15 words; 'sollevare' (relieve from pain) is the only off-field match")

# ---------------------------------------------------------------- resource_analysis (added 2026-11-08)
# Questions a linguist or lexicographer could ask about the resources themselves.
# nl_variants: the same question as formulated by users with different backgrounds.


add(3067, "resource_analysis", 3, "per_item_aggregation",
    "For each of the nine emotion categories in ELIta, how many of the associated Italian lemmas have a positive "
    "and how many a negative average Sentix polarity?",
    ["EMOTION_LEXICON", "COUNT_ENTITIES"],
    av(["emotionLabel", "positiveCount", "negativeCount"], secondary=["emotion"],
       numeric=["positiveCount", "negativeCount"]),
    f"""SELECT ?emotion ?emotionLabel (SUM(IF(?avgPolarity > 0, 1, 0)) AS ?positiveCount)
       (SUM(IF(?avgPolarity < 0, 1, 0)) AS ?negativeCount) WHERE {{
  {{ SELECT ?italianLemma ?emotion ?emotionLabel (AVG(?polarityValue) AS ?avgPolarity) WHERE {{
      GRAPH <http://liita.it/data> {{
        ?italianLemma a ?italianLemmaType . FILTER(?italianLemmaType IN (lila:Lemma, lila:Hypolemma))
      }}
      {emotion()}
      {polarity()}
  }} GROUP BY ?italianLemma ?emotion ?emotionLabel }}
}}
GROUP BY ?emotion ?emotionLabel""",
    note="average per lemma first, then counted by sign; shows where ELIta and Sentix diverge (e.g. Fear 137 positive vs 676 negative). Counting words instead of lemmas gives different counts (Gioia 1228/62, Paura 163/779): the linguist and student variants say 'words', so a per-word count should be accepted for them")

add(3068, "resource_analysis", 3, "per_item_aggregation",
    "Which Italian words associated with Sadness in ELIta have only positive Sentix polarity values?",
    ["EMOTION_LEXICON"], av(["italianWord"], numeric=["minPolarity"]),
    f"""SELECT ?italianWord (MIN(?polarityValue) AS ?minPolarity) WHERE {{
  {it()}
  {emotion(value='elita:Tristezza', label=None)}
  {polarity()}
}}
GROUP BY ?italianWord
HAVING (MIN(?polarityValue) > 0)""", note="real disagreement between the two affective resources (musica, famiglia, affezionato, abbraccio). "
    "Reworded 2026-11-09: the former 'Joy with a Sentix value below -0.5' only found words with one negative and one positive synset value. "
    "'only positive' = all values > 0 (MIN); checking 'at least one positive value' returns many more words")

add(3069, "resource_analysis", 3, "negation",
    "How many Italian lemmas have a Sentix polarity but no emotion in ELIta, and how many have an emotion in ELIta "
    "but no Sentix polarity?",
    ["EMOTION_LEXICON", "COUNT_ENTITIES"], av(["sentixOnly", "elitaOnly"], numeric=["sentixOnly", "elitaOnly"]),
    f"""SELECT ?sentixOnly ?elitaOnly WHERE {{
  {{ SELECT (COUNT(DISTINCT ?italianLemma) AS ?sentixOnly) WHERE {{
      GRAPH <http://liita.it/data> {{
        ?italianLemma a ?italianLemmaType . FILTER(?italianLemmaType IN (lila:Lemma, lila:Hypolemma))
      }}
      ?polarityEntry ontolex:canonicalForm ?italianLemma ; marl:hasPolarity ?anyClass ; marl:hasPolarityValue ?anyValue .
      FILTER NOT EXISTS {{ ?emotionEntry ontolex:canonicalForm ?italianLemma ; elita:HasEmotion ?anyEmotion . }}
  }} }}
  {{ SELECT (COUNT(DISTINCT ?italianLemma) AS ?elitaOnly) WHERE {{
      GRAPH <http://liita.it/data> {{
        ?italianLemma a ?italianLemmaType . FILTER(?italianLemmaType IN (lila:Lemma, lila:Hypolemma))
      }}
      ?emotionEntry ontolex:canonicalForm ?italianLemma ; elita:HasEmotion ?anyEmotion .
      FILTER NOT EXISTS {{ ?polarityEntry ontolex:canonicalForm ?italianLemma ; marl:hasPolarity ?anyClass ; marl:hasPolarityValue ?anyValue . }}
  }} }}
}}""", note="Sentix = entries with marl:hasPolarity (decision A, 2026-11-13; before, any marl:hasPolarityValue, which made elitaOnly = 0 by construction). Same with or without Valenza/Dominanza. Without hypolemmas sentixOnly = 19720; per word 23423 (acceptable for the variants that say 'words')")

add(3070, "resource_analysis", 4, "per_item_aggregation",
    "How many of the Italian lemmas annotated with an emotion in ELIta have a Sicilian translation and how many a "
    "Parmigiano one, and what share of the total is that?",
    ["EMOTION_LEXICON", "TRANSLATION", "MULTI_TRANSLATION", "COUNT_ENTITIES"],
    av(["withSicilian", "withParmigiano"], secondary=["sicilianShare", "parmigianoShare", "total"],
       numeric=["withSicilian", "withParmigiano", "sicilianShare", "parmigianoShare", "total"]),
    f"""SELECT (xsd:float(?withSicilian) / ?total AS ?sicilianShare)
       (xsd:float(?withParmigiano) / ?total AS ?parmigianoShare) ?total ?withSicilian ?withParmigiano WHERE {{
  {{ SELECT (COUNT(DISTINCT ?italianLemma) AS ?total) WHERE {{
      GRAPH <http://liita.it/data> {{ ?italianLemma a ?t1 . FILTER(?t1 IN (lila:Lemma, lila:Hypolemma)) }}
      {emotion()}
  }} }}
  {{ SELECT (COUNT(DISTINCT ?italianLemma) AS ?withSicilian) WHERE {{
      GRAPH <http://liita.it/data> {{ ?italianLemma a ?t2 . FILTER(?t2 IN (lila:Lemma, lila:Hypolemma)) }}
      {emotion()}
      ?sicEntryIt ontolex:canonicalForm ?italianLemma ; vartrans:translatableAs ?sicEntry .
      ?sicEntry ontolex:canonicalForm ?sicilianLemma . ?sicilianLemma dcterms:isPartOf {SIC} .
  }} }}
  {{ SELECT (COUNT(DISTINCT ?italianLemma) AS ?withParmigiano) WHERE {{
      GRAPH <http://liita.it/data> {{ ?italianLemma a ?t3 . FILTER(?t3 IN (lila:Lemma, lila:Hypolemma)) }}
      {emotion()}
      ?parEntryIt ontolex:canonicalForm ?italianLemma ; vartrans:translatableAs ?parEntry .
      ?parEntry ontolex:canonicalForm ?parmigianoLemma . ?parmigianoLemma dcterms:isPartOf {PAR} .
  }} }}
}}""", note="counts primary (format-independent); shares secondary, as decimals or percentages. Reworded 2026-11-09 from 'share of the words' (gold counts lemmas; per word 1255/1223 of 3469 = 0.3618/0.3526)")


add(3071, "resource_analysis", 3, "per_item_aggregation",
    "Are polysemous adjectives associated with more emotions? For the Italian adjectives in CompL-it that have an emotion "
    "in ELIta, give the number of adjectives and their average number of emotions, separately for adjectives with one "
    "CompL-it sense and for adjectives with more than one.",
    ["SERVICE_INTEGRATION", "EMOTION_LEXICON", "POS_FILTER", "COUNT_ENTITIES"],
    av(["adjectiveCount", "avgEmotions"], secondary=["polysemous"], aggregates=["avgEmotions"],
       numeric=["adjectiveCount", "avgEmotions"]),
    f"""SELECT ?polysemous (COUNT(*) AS ?adjectiveCount) (AVG(?emotionCount) AS ?avgEmotions) WHERE {{
  {{ SELECT ?italianLemma (COUNT(DISTINCT ?sense) AS ?senseCount) (COUNT(DISTINCT ?emotion) AS ?emotionCount) WHERE {{
      {CL} {{
        ?word ontolex:sense ?sense ; lexinfo:partOfSpeech [ rdfs:label ?posLabel ] .
        FILTER(STR(?posLabel) = "adjective")
      }}
      ?word ontolex:canonicalForm ?italianLemma .
      GRAPH <http://liita.it/data> {{ ?italianLemma a ?italianLemmaType . FILTER(?italianLemmaType IN (lila:Lemma, lila:Hypolemma)) }}
      {emotion()}
  }} GROUP BY ?italianLemma }}
  BIND(IF(?senseCount > 1, "yes", "no") AS ?polysemous)
}}
GROUP BY ?polysemous""",
    note="added 2026-11-09 (CompL-it polysemy vs emotions). Starts inside SERVICE (adjective senses, ~4200 rows): joining from "
         "LiITA into CompL-it fails on accented word IRIs (HTTP 400) and SERVICE subqueries/HAVING are refused (SR186). "
         "Answer: no relation (one sense 104 adj, 2.49 emotions; more senses 85 adj, 2.39). Only 189 of the 436 ELIta "
         "adjectives are CompL-it adjectives. Group label column is secondary (wording-independent)")

VARIANTS = {
    3067: {
        "linguist": "Do the emotions in ELIta agree with the polarity in Sentix? For each emotion, count the words that are on average positive and those that are on average negative.",
        "lexicographer": "Per ogni emozione di ELIta, quanti lemmi associati hanno una polarità media Sentix positiva e quanti negativa?",
        "student": "Are there words linked to sad or angry emotions that Sentix still rates as positive? Give me the numbers for every emotion.",
    },
    3068: {
        "linguist": "Which words does ELIta associate with sadness although all their Sentix polarity values are positive?",
        "lexicographer": "Quali parole associate alla tristezza in ELIta hanno solo valori di polarità Sentix positivi?",
        "student": "Find sad words that the sentiment lexicon only ever rates as positive.",
    },
    3069: {
        "linguist": "How much do the two affective lexicons overlap? Count the lemmas covered only by Sentix and those covered only by ELIta.",
        "lexicographer": "Quanti lemmi hanno una polarità in Sentix ma nessuna emozione in ELIta, e viceversa?",
        "student": "Are there words with an emotion but no sentiment score, or with a sentiment score but no emotion?",
    },
    3070: {
        "linguist": "How well do the dialect lexicons cover the emotional vocabulary? Count the ELIta lemmas with a Sicilian and with a Parmigiano translation, and give their share.",
        "lexicographer": "Quanti lemmi annotati in ELIta hanno una traduzione siciliana e quanti una parmigiana, e che percentuale rappresentano?",
        "student": "How many of the emotion lemmas can be translated into Sicilian, and how many into Parmigiano? What fraction is that?",
    },
    3071: {
        "linguist": "Is there a relation between polysemy in CompL-it and emotional richness in ELIta? Compare the average number of emotions of monosemous and polysemous adjectives.",
        "lexicographer": "Gli aggettivi con più sensi in CompL-it hanno più emozioni in ELIta? Dammi numero di aggettivi e media delle emozioni per quelli con un solo senso e per quelli con più sensi.",
        "student": "Do adjectives with many meanings carry more emotions? Compare adjectives with one meaning and with several.",
    },
}
from draft import Q  # noqa: E402
for _q in Q:
    if _q["id"] in VARIANTS:
        _q["nl_variants"] = VARIANTS[_q["id"]]


# ---------------------------------------------------------------- IRI/literal convention (2026-11-10)
# Aligns the held-out gold with the main test set convention (26/100 main questions): when the answer is an
# entity (CompL-it word, emotion), the gold primary is the IRI and the literal is accepted as an equivalent.
# Without this, systems that return IRIs (e.g. PRISMA) scored 0 on correct answers. Systems returning the
# literal are compared with the equivalent column, so their scores are unaffected.
import re as _re  # noqa: E402

IRI_RELATION = {3018: "hyponymWord", 3044: "hyponymWord",
                3020: "hypernymWord", 3045: "hypernymWord", 3055: "hypernymWord",
                3019: "partWord", 3054: "partWord", 3023: "wholeWord",
                3021: "synonymWord", 3022: "antonymWord"}
IRI_COMPLIT_WORD = {3015, 3016, 3017}
IRI_EMOTION = {3025, 3029, 3038, 3063, 3067}

for _q in Q:
    _id, _av = _q["id"], _q["answer_variables"]
    if _id in IRI_RELATION:
        _v = IRI_RELATION[_id]
        assert "?relWord" in _q["sparql"] and _av["primary"] == ["italianWord"], _id
        _q["sparql"] = _re.sub(r"\?relWord\b", "?" + _v, _q["sparql"])
        _q["sparql"] = _q["sparql"].replace("SELECT DISTINCT ?italianWord", f"SELECT DISTINCT ?{_v} ?italianWord", 1)
        _av["primary"] = [_v]
        _av["equivalents"] = {_v: "italianWord"}
    elif _id in IRI_COMPLIT_WORD:
        assert _av["primary"] == ["writtenRep"], _id
        _q["sparql"] = (_q["sparql"].replace("SELECT ?writtenRep", "SELECT ?word ?writtenRep", 1)
                        .replace("GROUP BY ?writtenRep", "GROUP BY ?word ?writtenRep"))
        _av["primary"] = ["word"]
        _av["equivalents"] = {"word": "writtenRep"}
    elif _id in IRI_EMOTION:
        assert "emotionLabel" in _av["primary"] and "?emotion " in _q["sparql"], _id
        _av["primary"] = ["emotion" if v == "emotionLabel" else v for v in _av["primary"]]
        _av["secondary"] = [v for v in _av["secondary"] if v != "emotion"]
        _av["equivalents"] = {"emotion": "emotionLabel"}

# ---------------------------------------------------------------- shared dialect translation = same spelling (2026-11-11)
# Approved by the user on 2026-11-11. "Share a Sicilian translation" was implemented as "share the same Sicilian lexical
# entry"; dialect resources have one entry per Italian sense and even distinct lemmas with the same spelling, so the
# gold missed words. Same written form is the natural reading (and the convention of test v2, questions 4043/4044).
SAME_SPELLING = {3043, 3052, 3053}
_OLD = "?otherEntryIt vartrans:translatableAs ?sicEntry ; ontolex:canonicalForm ?otherLemma ."
_NEW = ("?otherSicLemma dcterms:isPartOf <http://liita.it/data/id/DialettoSiciliano/lemma/LemmaBank> ; "
        "ontolex:writtenRep ?otherSicWr . FILTER(STR(?otherSicWr) = STR(?sicilianWord))\n"
        "  ?otherSicEntry ontolex:canonicalForm ?otherSicLemma .\n"
        "  ?otherEntryIt vartrans:translatableAs ?otherSicEntry ; ontolex:canonicalForm ?otherLemma .")
for _q in Q:
    if _q["id"] in SAME_SPELLING:
        assert _OLD in _q["sparql"], _q["id"]
        _q["sparql"] = _q["sparql"].replace(_OLD, _NEW)
