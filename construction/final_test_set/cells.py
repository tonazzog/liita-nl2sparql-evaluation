"""Step 2 of the new test set: the grid of 86 cells and the random sampling of their seeds.

Each cell fixes group (operator), resources, elementary operations and the shape of the question; the seed
(word, suffix, emotion, semantic type, threshold...) is drawn at random from a pool built by pools.py,
among candidates whose answer size lies in the cell's range. Sampling is reproducible: one RNG per cell,
seeded with f"{SEED}-{cell_id}", so adding or editing a cell never changes the seeds of the others.
usage: python cells.py   -> writes cells_sampled.json and prints a summary
"""
import json, os, random

SEED = 20261110
HERE = os.path.dirname(os.path.abspath(__file__))
EMOTIONS = ["Gioia", "Tristezza", "Paura", "Rabbia", "Disgusto", "Sorpresa", "Fiducia", "Aspettativa", "Amore"]
POS = ["noun", "verb", "adjective", "adverb"]
POL_THRESHOLDS = [-0.9, -0.8, -0.7, -0.6, -0.5, 0.5, 0.6, 0.7, 0.8, 0.9]


def pool(name):
    return json.load(open(os.path.join(HERE, "pools", name + ".json"), encoding="utf-8"))


def short(v):
    return v.rsplit("#", 1)[-1].rsplit("/", 1)[-1] if str(v).startswith("http") else v


def n_in(lo, hi, key="n"):
    return lambda r: lo <= float(r[key]) <= hi


def word_ok(key="wr"):  # plain lower-case single words: avoids multiword, abbreviations, proper nouns
    return lambda r: r[key].isalpha() and r[key].islower() and len(r[key]) >= 4


def both(*fs):
    return lambda r: all(f(r) for f in fs)


def emo_ok(*keys):
    return lambda r: all(short(r[k]) in EMOTIONS for k in keys)


# id, group, resources, ops, idea (Italian), pool, filter, k = seeds to draw (0 = no seed)
C = []
def cell(cid, group, res, ops, idea, pool_name=None, flt=None, k=1, extra=None):
    C.append(dict(id=cid, group=group, resources=res, ops=ops, idea=idea, pool=pool_name,
                  flt=flt or (lambda r: True), k=k if pool_name else 0, extra=extra))

W = word_ok()
# ---------------- S: simple (one resource, one elementary operation) ---------------- 20
cell("S01", "S", ["LiITA"], ["B11"], "varianti di lemma registrate per X", "it_variant", both(W, n_in(1, 6)))
cell("S02", "S", ["LiITA"], ["B11"], "ipolemmi (participi, avverbi) collegati al lemma X", "it_hypolemma", both(W, n_in(2, 6)))
cell("S03", "S", ["LiITA"], ["B2", "B3"], "lemmi con POS P che terminano in -X", "it_suffix", n_in(30, 300))
cell("S04", "S", ["LiITA"], ["B2", "B3", "B10"], "quanti lemmi con POS P iniziano con X-", "it_prefix", n_in(30, 400))
# S05 changed 2026-11-10 before writing: the degree pool has only superlative/positive adjectives, and
# "superlative adjectives" is already dev question 3003 -> inflection type (a B3 property not covered elsewhere)
cell("S05", "S", ["LiITA"], ["B3", "B10"], "quanti lemmi con POS P hanno tipo di flessione F (studente)", "it_inflection", n_in(20, 5000))
cell("S06", "S", ["CompL-it"], ["B4"], "iponimi di X", "cl_hyponyms", both(W, n_in(5, 60)))
cell("S07", "S", ["CompL-it"], ["B4"], "parti (meronimi) di X", "cl_meronyms", both(W, n_in(3, 30)))
cell("S08", "S", ["CompL-it"], ["B4"], "antonimi di X", "cl_antonyms", both(W, n_in(2, 8)))
cell("S09", "S", ["CompL-it"], ["B5"], "parole la cui definizione inizia con X", "cl_def_words", both(word_ok("tok"), n_in(10, 150)))
cell("S10", "S", ["CompL-it"], ["B6", "B10"], "quanti sensi ha X (studente)", "cl_senses", both(W, n_in(4, 20)))
cell("S11", "S", ["CompL-it"], ["B12"], "parole del tipo semantico T", "cl_semtype", n_in(15, 300))
cell("S12", "S", ["CompL-it"], ["B12"], "sensi con il tratto T", "cl_traits", n_in(10, 130))
cell("S13", "S", ["CompL-it"], ["B13"], "a che cosa serve X (relazione usedFor)", "cl_usedfor", both(W, n_in(2, 10)))
cell("S14", "S", ["CompL-it"], ["B13"], "nomi deaggettivali / aggettivi denominali collegati a X", "cl_deadj", both(W, n_in(1, 5)))
cell("S15", "S", ["LiITA", "Sicil."], ["B7"], "traduzioni siciliane di X (studente)", "sic_transl", both(W, n_in(2, 6)))
cell("S16", "S", ["Sicil.", "LiITA"], ["B7"], "quali parole italiane traduce la parola siciliana X", "sic_shared", both(word_ok("dwr"), n_in(3, 12)))
cell("S17", "S", ["Sicil."], ["B2"], "lemmi siciliani che terminano in -X", "sic_suffix", n_in(20, 300))
cell("S18", "S", ["Parm."], ["B2", "B10"], "quanti lemmi parmigiani terminano in -X", "par_suffix", n_in(20, 300))
cell("S19", "S", ["LiITA", "ELIta"], ["B8"], "emozioni associate a X", "emotion_lemmas", both(W, n_in(2, 6)))
cell("S20", "S", ["LiITA", "Sentix"], ["B9"], "valore di polarità massimo e minimo di X", "polarity_lemmas", both(W, n_in(2, 6)))
# ---------------- C1: conjunction across resources ---------------- 8
cell("C1-01", "C1", ["CompL-it", "LiITA", "Sicil."], ["B4", "B7"], "iponimi di X con la loro traduzione siciliana", "cl_hyponyms", both(W, n_in(10, 80)))
cell("C1-02", "C1", ["CompL-it", "LiITA", "Parm."], ["B5", "B7"], "parole la cui definizione inizia con X, con traduzione parmigiana", "cl_def_words", both(word_ok("tok"), n_in(20, 150)))
cell("C1-03", "C1", ["LiITA", "ELIta", "Parm."], ["B3", "B8", "B7"], "parole con POS P ed emozione E, con traduzione parmigiana", "emotion_pos", both(emo_ok("em"), n_in(80, 700)))
cell("C1-04", "C1", ["LiITA", "Sentix", "Sicil."], ["B3", "B9", "B7"], "parole con POS P e polarità massima oltre la soglia t, con traduzione siciliana", None, extra={"pos": POS, "threshold": POL_THRESHOLDS})
cell("C1-05", "C1", ["LiITA", "ELIta", "Sentix"], ["B8", "B9"], "parole con emozione E e classe di polarità Positive/Negative", "emotion_pos", emo_ok("em"), extra={"label": ["Positive", "Negative"]})
cell("C1-06", "C1", ["CompL-it", "LiITA", "ELIta"], ["B12", "B8"], "parole del tipo semantico T associate a un'emozione, con l'emozione", "cl_semtype", n_in(100, 2000))
cell("C1-07", "C1", ["CompL-it", "LiITA", "ELIta"], ["B4", "B8"], "parti di X associate a un'emozione", "cl_meronyms", both(W, n_in(8, 30)))
cell("C1-08", "C1", ["LiITA", "Sentix", "Parm."], ["B2", "B9", "B7"], "lemmi in -X con polarità e traduzione parmigiana (4 colonne)", "it_suffix", n_in(100, 500))
# ---------------- C2: disjunction of values ---------------- 3
cell("C2-01", "C2", ["LiITA", "ELIta"], ["B3", "B8"], "aggettivi associati a E1 o E2", "emotion_pairs", both(emo_ok("a", "b"), n_in(1, 400)))
# C2-02: Sentix condition added 2026-11-10 when writing the questions (Sentix was in 14 cells, target 15); seed unchanged
cell("C2-02", "C2", ["LiITA", "Sentix"], ["B2", "B3", "B9"], "nomi o aggettivi che terminano in -X con polarità negativa", "it_suffix", n_in(20, 300))
cell("C2-03", "C2", ["CompL-it"], ["B4"], "iponimi o meronimi di X", "cl_meronyms", both(W, n_in(3, 30)))
# ---------------- C3: chain ---------------- 5
cell("C3-01", "C3", ["CompL-it"], ["B4"], "iponimi degli iponimi di X", "cl_hyponyms2", both(W, n_in(5, 150)))
cell("C3-02", "C3", ["CompL-it"], ["B4"], "iperonimi degli iperonimi di X", "cl_hypernyms2", both(W, n_in(2, 10)))
cell("C3-03", "C3", ["Sicil.", "LiITA", "CompL-it"], ["B7", "B4"], "iperonimi CompL-it delle parole italiane tradotte dalla parola siciliana X", "sic_shared", both(word_ok("dwr"), n_in(2, 6)))
cell("C3-04", "C3", ["CompL-it", "LiITA", "Parm."], ["B4", "B7"], "traduzioni parmigiane dei sinonimi approssimati di X", "cl_synonyms", both(W, n_in(3, 12)))
cell("C3-05", "C3", ["CompL-it"], ["B13", "B4"], "iperonimi del nome deaggettivale di X", "cl_deadj", both(W, lambda r: r["rel"].endswith("deadjectivalNoun")))
# ---------------- C4: intersection ---------------- 6
cell("C4-01", "C4", ["LiITA", "ELIta"], ["B8"], "parole associate sia a E1 sia a E2", "emotion_pairs", both(emo_ok("a", "b"), n_in(15, 200)))
cell("C4-02", "C4", ["LiITA", "ELIta", "Sentix"], ["B8", "B9"], "parole con sia E1 sia E2 e polarità negativa (Di Palma 2025)", "emotion_pairs", both(emo_ok("a", "b"), n_in(30, 300)))
cell("C4-03", "C4", ["CompL-it"], ["B4"], "iperonimi comuni a X e Y (due co-iponimi)", "cl_hyponyms", both(W, n_in(4, 15)))
cell("C4-04", "C4", ["LiITA", "Sicil.", "Parm."], ["B2", "B7"], "lemmi in -X con traduzione sia siciliana sia parmigiana", "it_suffix", n_in(60, 400))
cell("C4-05", "C4", ["LiITA", "Sicil.", "Parm."], ["B3", "B7"], "quanti verbi hanno traduzione sia siciliana sia parmigiana (studente)", None)
cell("C4-06", "C4", ["CompL-it", "LiITA", "ELIta"], ["B4", "B8"], "iponimi di X associati sia a E1 sia a E2", "cl_hyponyms", both(W, n_in(40, 300)))
# ---------------- C5: self-join ---------------- 5
cell("C5-01", "C5", ["LiITA", "Sicil."], ["B7"], "altre parole italiane con la stessa traduzione siciliana di X", "sic_shared", both(word_ok("dwr"), n_in(3, 10)))
cell("C5-02", "C5", ["LiITA", "Parm."], ["B7"], "altre parole italiane con la stessa traduzione parmigiana di X", "par_shared", both(word_ok("dwr"), n_in(2, 10)))
cell("C5-03", "C5", ["CompL-it"], ["B4"], "co-iponimi di X (altre parole con lo stesso iperonimo)", "cl_hyponyms", both(W, n_in(4, 25)))
cell("C5-04", "C5", ["CompL-it"], ["B4"], "parole che condividono una parte con X (stesso meronimo)", "cl_meronyms", both(W, n_in(3, 15)))
cell("C5-05", "C5", ["CompL-it"], ["B13"], "parole derivate dallo stesso aggettivo da cui deriva X", "cl_deadj", both(W, lambda r: r["rel"].endswith("deadjectivalNoun")))
# ---------------- C6: negation ---------------- 7
cell("C6-01", "C6", ["CompL-it", "LiITA", "Sicil."], ["B4", "B7"], "iponimi di X senza traduzione siciliana", "cl_hyponyms", both(W, n_in(15, 80)))
cell("C6-02", "C6", ["LiITA", "ELIta", "Parm."], ["B3", "B8", "B7"], "parole con POS P ed emozione E senza traduzione parmigiana", "emotion_pos", both(emo_ok("em"), n_in(50, 400)))
cell("C6-03", "C6", ["LiITA", "Sentix", "ELIta"], ["B2", "B9", "B8"], "lemmi in -X con polarità Sentix ma senza emozione ELIta", "it_suffix", n_in(50, 300))
cell("C6-04", "C6", ["LiITA", "Sicil.", "Parm."], ["B2", "B7"], "lemmi in -X tradotti in siciliano ma non in parmigiano", "it_suffix", n_in(60, 400))
cell("C6-05", "C6", ["LiITA", "ELIta", "CompL-it"], ["B8", "B5"], "parole con emozione E senza definizione in CompL-it", None, extra={"emotion": ["Disgusto", "Sorpresa", "Tristezza", "Rabbia"]})
cell("C6-06", "C6", ["CompL-it"], ["B4"], "iponimi di X che non hanno a loro volta iponimi", "cl_hyponyms", both(W, n_in(5, 40)))
cell("C6-07", "C6", ["LiITA", "Sentix", "ELIta"], ["B3", "B9", "B8"], "aggettivi con polarità oltre t non associati a nessuna emozione", None, extra={"threshold": POL_THRESHOLDS})
# ---------------- C7: union ---------------- 4
cell("C7-01", "C7", ["LiITA", "Sicil.", "Parm."], ["B2", "B7"], "lemmi in -X con traduzione siciliana o parmigiana", "it_suffix", n_in(30, 200))
cell("C7-02", "C7", ["LiITA", "ELIta", "Sentix"], ["B8", "B9"], "quante parole sono associate a E o hanno polarità sotto t", None, extra={"emotion": EMOTIONS, "threshold": [-0.9, -0.8, -0.7]})
cell("C7-03", "C7", ["CompL-it"], ["B4", "B5"], "parti di X o parole la cui definizione cita X", "cl_meronyms", both(W, n_in(3, 20)))
cell("C7-04", "C7", ["CompL-it"], ["B12", "B4"], "parole del tipo semantico T o iponimi di X", "cl_semtype", n_in(15, 150), k=1)
# ---------------- C8: group-by / ranking ---------------- 6
cell("C8-01", "C8", ["LiITA", "ELIta"], ["B3", "B8"], "per ogni POS, quante parole associate a E", None, extra={"emotion": EMOTIONS})
cell("C8-02", "C8", ["LiITA", "ELIta"], ["B2", "B8"], "per ogni emozione, quanti lemmi in -X", "it_suffix", n_in(150, 500))
cell("C8-03", "C8", ["CompL-it"], ["B4", "B12"], "iponimi di X raggruppati per tipo semantico", "cl_hyponyms", both(W, n_in(20, 80)))
cell("C8-04", "C8", ["LiITA", "Sicil.", "Parm."], ["B3", "B7"], "per ciascun dialetto, quante parole italiane con POS P sono tradotte", None, extra={"pos": POS})
cell("C8-05", "C8", ["LiITA", "Sicil."], ["B2", "B7"], "il lemma in -X con più traduzioni siciliane (HAVING = MAX)", "it_suffix", n_in(60, 400))
cell("C8-06", "C8", ["LiITA", "ELIta", "Sentix"], ["B8", "B9"], "parole con emozione E per classe di polarità", None, extra={"emotion": EMOTIONS})
# ---------------- C9: HAVING ---------------- 4
cell("C9-01", "C9", ["LiITA", "Parm."], ["B3", "B7"], "parole italiane con POS P con più di N traduzioni parmigiane (Parma 2025)", None, extra={"pos": POS, "N": [3, 4, 5]})
cell("C9-02", "C9", ["CompL-it"], ["B6", "B12"], "parole del tipo semantico T con più di N sensi", "cl_semtype", n_in(100, 2000), extra={"N": [3, 4, 5]})
cell("C9-03", "C9", ["LiITA", "ELIta"], ["B3", "B8"], "aggettivi associati a più di N emozioni", None, extra={"N": [4, 5, 6]})
cell("C9-04", "C9", ["CompL-it"], ["B4"], "parole con più di N iponimi", None, extra={"N": [30, 40, 50]})
# ---------------- C10: comparison with a reference ---------------- 3
cell("C10-01", "C10", ["LiITA", "ELIta", "Sentix"], ["B8", "B9"], "parole con emozione E e polarità massima maggiore di quella di X", "polarity_lemmas", both(W, n_in(1, 1)), extra={"emotion": EMOTIONS})
cell("C10-02", "C10", ["CompL-it"], ["B6", "B12"], "parole del tipo semantico T con più sensi di X", "cl_senses", both(W, n_in(5, 9)))
cell("C10-03", "C10", ["LiITA", "ELIta"], ["B3", "B8"], "emozioni con più aggettivi dell'emozione E", None, extra={"emotion": EMOTIONS})
# ---------------- C11: comparison between variables ---------------- 5
cell("C11-01", "C11", ["LiITA", "Parm."], ["B2", "B7"], "parole italiane che iniziano con X la cui traduzione parmigiana inizia con Y (Parma 2025)", "par_initial_pairs", n_in(10, 300))
cell("C11-02", "C11", ["LiITA", "Sicil."], ["B2", "B7"], "parole italiane in -X la cui traduzione siciliana termina in -Y", "sic_suffix_pairs", n_in(10, 300))
cell("C11-03", "C11", ["LiITA", "Sicil."], ["B3", "B7"], "verbi italiani con traduzione siciliana identica nella grafia", None)
cell("C11-04", "C11", ["Sicil."], ["B11"], "lemmi siciliani con due grafie che differiscono solo nell'iniziale (Ciallabacialla 2025)", None)
cell("C11-05", "C11", ["LiITA", "Sentix"], ["B3", "B9"], "parole con POS P che hanno sia un valore di polarità positivo sia uno negativo", None, extra={"pos": ["noun", "verb", "adjective"]})
# ---------------- C12: nested aggregation ---------------- 3
cell("C12-01", "C12", ["LiITA", "Sicil."], ["B3", "B7"], "numero medio di traduzioni siciliane per verbo tradotto", None)
cell("C12-02", "C12", ["CompL-it"], ["B6", "B12"], "numero medio di sensi delle parole del tipo semantico T", "cl_semtype", n_in(50, 1000))
cell("C12-03", "C12", ["LiITA", "ELIta", "Sentix"], ["B8", "B9"], "numero medio di emozioni dei lemmi con polarità massima oltre t", None, extra={"threshold": [0.5, 0.6, 0.7, 0.8]})
# ---------------- C13: multi-statistic ---------------- 4
cell("C13-01", "C13", ["LiITA", "ELIta", "Sentix", "Sicil."], ["B8", "B9", "B7"], "per emozione: n. lemmi, polarità media, n. con traduzione siciliana", None)
cell("C13-02", "C13", ["LiITA", "Sicil.", "Parm."], ["B3", "B7"], "per POS: n. lemmi, n. tradotti in siciliano, n. tradotti in parmigiano", None)
cell("C13-03", "C13", ["LiITA", "ELIta", "Sentix"], ["B8", "B9"], "per emozione: n. lemmi positivi e n. negativi (polarità massima)", None)
cell("C13-04", "C13", ["CompL-it", "LiITA", "ELIta"], ["B6", "B8"], "aggettivi con emozione: n. e media di emozioni per monosemici vs polisemici", None)
# ---------------- M: metadata ---------------- 3
cell("M-01", "M", ["LiITA"], [], "quali lemma bank contiene LiITA", None)
cell("M-02", "M", ["LiITA"], ["B10"], "quanti lemmi contiene ciascuna lemma bank", None)
cell("M-03", "M", ["ELIta"], [], "quali categorie emotive usa ELIta (con etichetta)", None)


def sample():
    out = []
    for c in C:
        rng = random.Random(f"{SEED}-{c['id']}")
        rec = {k: c[k] for k in ("id", "group", "resources", "ops", "idea", "pool")}
        if c["pool"]:
            cands = [r for r in pool(c["pool"]) if c["flt"](r)]
            rec["candidates"] = len(cands)
            rec["seeds"] = rng.sample(cands, min(max(c["k"], 1) + 2, len(cands)))  # chosen + 2 reserves
        if c["extra"]:
            rec["params"] = {k: rng.choice(v) for k, v in c["extra"].items()}
        out.append(rec)
    return out


if __name__ == "__main__":
    s = sample()
    assert len(s) == 86, len(s)
    json.dump({"seed": SEED, "cells": s}, open(os.path.join(HERE, "cells_sampled.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    import collections
    print(collections.Counter(c["group"] for c in s))
    res = collections.Counter(r for c in s for r in c["resources"])
    print(dict(res))
    for c in s:
        seed = c.get("seeds", [None])[0]
        print(f"{c['id']:7s} cand={c.get('candidates', '-'):>5}  seed={ {k: short(v) for k, v in seed.items()} if seed else '-'}"
              f"  params={c.get('params', '')}")
