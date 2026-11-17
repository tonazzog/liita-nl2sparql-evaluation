# Evaluation Methodology

This document summarises the evaluation design of the thesis (Chapter 6). The thesis is the authoritative description; this file explains how the material in this repository fits it.

## 1. Why the evaluation was redesigned

A first evaluation (March 2026) compared the systems on a single set of 100 questions. Three problems made it unreliable:

1. **Inconsistent gold queries and evaluators.** Each system had its own copy of the test set; corrections made in two copies never reached the third (44 of 100 gold queries differed), and the three evaluators mapped variables differently.
2. **No separation between development and test.** The same questions had been used to correct the systems.
3. **Narrow coverage.** The 100 questions have only 30 distinct structural signatures; almost all composite questions are conjunctions of constraints. Negation, union, intersection, chains of relations and comparisons are absent.

## 2. Three question sets with distinct roles

| Set | File | n | Role |
|---|---|---|---|
| Development set | `datasets/development_set.json` | 71 | diagnosing errors and designing revisions |
| Regression set | `datasets/regression_set.json` | 100 | the first evaluation's questions, with one canonical gold; checks that revisions do not degrade performance |
| Final test set | `datasets/final_test_set.json` | 86 | measuring generalisation; frozen before any revision, used for a single run |

## 3. Freezing protocol

- The final test set was frozen before any system was revised and identified by its SHA-256 hash.
- One correction was made before its first use: the gold queries of 12 questions on Sentix polarity were rewritten to read only Sentix entries (section 6). The hash was updated (old file: `datasets/final_test_set.pre_sentix.json`).
- The revised systems were frozen under the tag `thesis-final-2026-11-15`. The run script (`runs/scripts/run_final_v2.sh`) checked the hash of the test file and that each repository was at the tag with no local changes before every run.
- Each configuration was run once. Questions that ended without a query because of an error outside the system (provider API error, unavailable command-line interface) were run a second time; failures that recurred were kept. No system, gold query or evaluator setting was changed after any score on the final test set had been seen.
- An infrastructure incident during the final run (a run believed to be stopped kept running, so two copies ran in parallel for part of the time) is documented in `runs/final/interruption_note.txt`; it did not affect the reports.

## 4. The final test set

**Perimeter.** The questions a system for LiITA should answer were defined along four axes: resources (LiITA lemma bank, CompL-it, ELIta, Sentix, Sicilian and Parmigiano lexicons), elementary operations (morphological filter, semantic relation, definition, translation, emotion, polarity, counts, ...), composition operators, and answer forms. Question types were anchored to questions asked of LiITA and of the Latin knowledge base LiLA in published studies and on the LiITA website. The working documents are in `construction/final_test_set/` (in Italian: `perimeter_definition_it.md`, `question_type_sources_it.md`).

**Groups.**

| Group | Operation | n |
|---|---|---|
| S | simple (one resource, one operation) | 20 |
| C1 | conjunction across resources | 8 |
| C2 | disjunction of values | 3 |
| C3 | chain | 5 |
| C4 | intersection | 6 |
| C5 | self-join | 5 |
| C6 | negation | 7 |
| C7 | union | 4 |
| C8 | aggregation by group, ranking | 6 |
| C9 | filter on an aggregate (HAVING) | 4 |
| C10 | comparison with a reference value | 3 |
| C11 | comparison between variables | 5 |
| C12 | nested aggregation | 3 |
| C13 | multiple statistics | 4 |
| M | metadata | 3 |

**Construction.** The grid of cells (`cells.py`) was fixed before any question was written. Seeds (words, emotions, affixes, thresholds) were sampled at random from pools extracted from the endpoint (`pools.py`, `pools/`) with fixed seeds, under constraints on the size of the answer; a seed was replaced only when it no longer satisfied its cell. Questions and gold queries were written by generator scripts (`newtest_*.py`) and assembled by `assemble.py`; every gold query was executed and reviewed (`review_it.md`). The 86 questions have 79 distinct structural signatures. Each question has an English and an Italian formulation and a register (57 technical, 29 student). The final evaluation used the English formulations.

**Threat to validity.** The questions were written by the author of the systems. Fixing the cells first, sampling the seeds, taking question types from published sources and freezing the set before the revisions limit, but do not remove, this bias.

## 5. The evaluator

`evaluator/f1_evaluator.py` is the evaluator of the thesis; an identical copy is used by each system (`evaluator/check_copies.py` verifies it). For each question:

1. Gold and predicted queries are executed on the endpoint (timeout 60 s, at most 10,000 rows); `LIMIT` and `OFFSET` are removed from both.
2. **Column mapping by value**: each primary gold column is matched to the predicted column whose value set overlaps most with it (Dice coefficient ≥ 0.1, one-to-one assignment maximising the total overlap); name-based matching is a fallback.
3. **Answer columns**: when a gold answer is an IRI and the gold names a literal equivalent, a predicted column of literals is compared with the literal; an **echo column** (one value on every row, written as a literal in the gold query — typically the seed word) is not required.
4. Rows of the mapped primary columns are compared as **multisets**; precision, recall and F1 follow.
5. Aggregates are compared on the first row (averages within 1% relative tolerance); questions with aggregates only score the proportion of matching aggregates.

Both queries returning no rows score 1; a failed or missing predicted query scores 0. The mean F1 of a configuration averages over all questions of a set.

**Known limitations**: superlatives answered with the top item where the gold has a ranking; extra columns with several values per item repeat rows and lower precision; aggregates compared on the first row only.

## 6. Gold-query conventions

- Lemmas are selected as `lila:Lemma` **or** `lila:Hypolemma` (the endpoint performs no inference).
- **Sentix polarity** means the value of the Sentix entry, selected through `marl:hasPolarity`; ELIta entries carry their own polarity value, which a query reading `marl:hasPolarityValue` from any entry would mix in.
- Superlatives in the final test set are written with `HAVING` on the maximum, never with `LIMIT`; questions asking for several statistics name their columns.
- IRI answers name a literal equivalent where one exists.

## 7. Disclosures

- **Sentix correction.** The effect of the correction in section 3 is measured in the thesis (Section 6.6.5): with the original gold, the mean F1 of every configuration would be 0.03–0.04 lower; the reports `runs/final/*_presentix.json` contain the ten affected questions re-scored against `final_test_set.pre_sentix.json`.
- **Overlap between MoSAIC's prompt examples and the final test set.** Three of the eight example plans in MoSAIC's revised prompt reproduce, with different words, the form of questions 4044, 4060 and 4062. Excluding those questions changes no conclusion (Section 6.6.6 of the thesis): every configuration gains slightly.
