# Evaluation of NL-to-SPARQL Systems for LiITA

This repository contains the evaluation material of the master's thesis *Querying LiITA in Natural Language: Three Neuro-Symbolic Approaches to NL-to-SPARQL Translation*: the question sets with their gold SPARQL queries, the evaluator, the scripts that ran the final evaluation, the reports of every run reported in the thesis, and the scripts that compute the tables of Chapter 6.

The three systems evaluated are published in their own repositories; the versions evaluated are tagged **`thesis-final-2026-11-15`** in each of them:

| System | Approach | Repository |
|---|---|---|
| PRISMA | the LLM classifies the intent, SPARQL is assembled by rules | <https://github.com/tonazzog/prisma-per-liita> |
| MoSAIC | the LLM composes typed blocks, SPARQL is assembled deterministically | <https://github.com/tonazzog/mosaic-liita> |
| NL2SPARQL | the LLM generates SPARQL, grounded by retrieved examples and constraints | <https://github.com/tonazzog/nl2sparql> |

All queries target the LiITA SPARQL endpoint (<https://liita.it/sparql>), which federates the CompL-it lexicon through a `SERVICE` clause.

## Contents

```
datasets/          the three question sets (JSON) and their SHA-256 checksums
evaluator/         the evaluator used by all three systems, re-scoring and copy-check scripts
construction/      how the final test set and the development set were built (cells, sampling, generators)
runs/final/        reports of the final evaluation on the final test set (86 questions)
runs/development/  reports behind the development results (development and regression sets)
runs/scripts/      the scripts that ran the final evaluation
analysis/          the script and the outputs behind the tables of Chapter 6 and Appendix C
docs/              methodology and a map from every reported number to the file it comes from
```

## The question sets

| File | Questions | Role in the thesis |
|---|---|---|
| `datasets/development_set.json` | 71 | diagnosing the systems and designing their revisions |
| `datasets/regression_set.json` | 100 | checking that revisions do not degrade performance on the questions of the first evaluation |
| `datasets/final_test_set.json` | 86 | final evaluation; frozen before any revision, used for a single run |

The final test set (SHA-256 `4e63a354d393dd425f11d28b9196831b6578b8ec0140956062c5c23c962ce7ea`) covers fifteen groups of questions — simple questions, thirteen composition operators (conjunction, disjunction, chain, intersection, self-join, negation, union, aggregation by group, filter on aggregates, comparison with a reference, comparison between variables, nested aggregation, multiple statistics) and metadata — each in an English and an Italian formulation. See [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) and [`datasets/README.md`](datasets/README.md).

## Results on the final test set

Mean F1 on the 86 questions (English formulations); 95% percentile-bootstrap confidence intervals over questions.

| System | Mode | Model | Mean F1 | 95% CI |
|---|---|---|---|---|
| NL2SPARQL | basic | Mistral Large 4 | 0.778 | [0.698, 0.852] |
| MoSAIC | agentic | Mistral Large 4 | 0.789 | [0.700, 0.869] |
| NL2SPARQL | basic | Claude Sonnet 4.6 | 0.784 | [0.704, 0.858] |
| MoSAIC | agentic | Claude Sonnet 4.6 | 0.814 | [0.731, 0.887] |
| NL2SPARQL | agentic | Claude Sonnet 4.6 | 0.815 | [0.740, 0.883] |

No pairwise difference is statistically significant (paired permutation tests, smallest p = 0.25). The systems differ in *which* questions they answer: see `analysis/ch6/summary.md` and [`docs/RESULTS.md`](docs/RESULTS.md).

## Reproducing

Requirements: Python 3.10+ and `SPARQLWrapper` (`pip install SPARQLWrapper`). The analysis scripts use only the standard library.

```bash
# Tables of Chapter 6 (group, register, bootstrap, paired tests, outcomes) from the stored reports
python analysis/ch6_extract.py

# Re-score stored predictions with the evaluator (executes gold and predicted queries on the endpoint)
python evaluator/rescore.py datasets/final_test_set.json runs/final/cc_mosaic.json /tmp/cc_mosaic_rs.json

# Check that the evaluator copies in the three systems are identical to evaluator/f1_evaluator.py
python evaluator/check_copies.py ../nl2sparql ../mosaic-liita ../prisma-per-liita
```

To run a system on a question set, use the system's own evaluation script at the tag, for example
`python scripts/run_f1_evaluation.py --dataset <path>/final_test_set.json ...`; the exact commands of the final evaluation are in `runs/scripts/run_final_v2.sh`.

**Note on reproducibility.** Gold queries are executed against the live endpoint, so re-scoring can give slightly different values if the data of LiITA or CompL-it change. The stored reports record, for every question, the number of gold rows at the time of the evaluation (`gold_count`).

## License

The code in this repository is released under the MIT License (see `LICENSE`). The question sets and gold queries are released under the same terms; the answers they return come from LiITA and the resources linked to it, which keep their own licenses.
