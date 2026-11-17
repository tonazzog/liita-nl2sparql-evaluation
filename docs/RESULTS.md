# Where Each Reported Number Comes From

Mean F1 is the average of the per-question F1 (`results[*].f1`) over all questions of a report. `analysis/ch6_extract.py` recomputes every table of Section 6.6 and Appendix C from the files below.

## Final test set (thesis Table 6.5, Section 6.6, Appendix C)

| Configuration | Report used in the thesis | Notes |
|---|---|---|
| NL2SPARQL basic, Mistral Large 4 | `runs/final/mi_nl2s_rsm.json` | `mi_nl2s.json` re-scored (`_rs`) with question 4083 from the retry (`mi_nl2s_retry.json`) merged (`_rsm`) |
| MoSAIC agentic, Mistral Large 4 | `runs/final/mi_mosaic_rs.json` | retry of 4076 failed again (`mi_mosaic_retry.json`) |
| NL2SPARQL basic, Claude Sonnet 4.6 | `runs/final/cc_nl2s_rs.json` | |
| MoSAIC agentic, Claude Sonnet 4.6 | `runs/final/cc_mosaic_rs.json` | retry of 4076 failed again (`cc_mosaic_retry.json`) |
| NL2SPARQL agentic, Claude Sonnet 4.6 | `runs/final/cc_nl2s_agent_rsm.json` | questions 4052–4058 from the retry after a CLI update (`cc_nl2s_agent_retry.json`) merged (`_m`) and re-scored |

- `*.json` (without suffix) are the reports written by the run; `_rs` / `_rsm` were re-scored sequentially with `evaluator/rescore.py` after the run, because parallel runs had caused endpoint timeouts.
- `*.calls.jsonl` log every model call (requested and returned model, tokens or duration); `*.plans.jsonl` log MoSAIC's plans.
- **Sentix sensitivity** (Section 6.6.5): the ten questions 4024, 4028, 4030, 4050, 4054, 4056, 4067, 4069, 4079, 4080 of `*_presentix.json`, re-scored against `datasets/final_test_set.pre_sentix.json`, replace the corresponding questions of the reports above.
- **Prompt overlap** (Section 6.6.6): means without questions 4044, 4060, 4062.

## Development results (thesis Table 6.4)

| Row | Development set | Regression set |
|---|---|---|
| MoSAIC deterministic (original) | `runs/development/original_mistral_rescored/mdet_ho.json` | `.../mdet_ma.json` |
| PRISMA, Mistral Large 4 (original) | `.../prisma_ho.json` | `.../prisma_ma.json` |
| MoSAIC agentic, Mistral Large 4 (original) | `.../old_mv1_ho.json` | `.../old_mv1_ma.json` |
| MoSAIC agentic, Claude Sonnet 4.6 (original) | `runs/development/echo_rescored_20261114.json` → `heldout.mosaic_v1` | → `main.mosaic_v1` |
| NL2SPARQL basic, Mistral Large 4 (original) | `.../old_nl2s_ho.json` | `.../old_nl2s_ma.json` |
| NL2SPARQL basic, Claude Sonnet 4.6 (original) | `echo_rescored_20261114.json` → `heldout.nl2s_v1` | → `main.nl2s_v1` |
| NL2SPARQL agentic, Mistral Large 4 (original) | `.../nl2s_agent_ho.json` | `.../nl2s_agent_ma.json` |
| NL2SPARQL basic, Mistral Large 4 (revised) | `runs/development/mi_nl2s_r3b_heldout_rs.json` | `mi_nl2s_r3b_main_rs.json` |
| NL2SPARQL basic, Claude Sonnet 4.6 (revised) | `echo_rescored_20261114.json` → `heldout.nl2s_r3b` | → `main.nl2s_r3b` |
| MoSAIC agentic, Mistral Large 4 (revised, before builder corrections F4g–F4h) | `mi_v2f_heldout_rs.json` | `mi_v2f_mainm.json` |
| MoSAIC agentic, Claude Sonnet 4.6 (revised, before F4h) | `cc_v2g_heldout.json` | `cc_v2g_mainm.json` |
| same plans rebuilt with the final builder (F4h) | `replay_f4h_cc_v2g_heldout.log` (0.890) | `replay_f4h_cc_v2g_main.log` (0.866) |

`echo_rescored_20261114.json` stores, for runs whose original reports were scored with earlier evaluator versions, the per-question scores after re-scoring with the final evaluator (mapping by value and echo-column rule); the `.../` files in `original_mistral_rescored/` are the original Mistral runs re-scored the same way. Development-set and regression-set scores were computed with the gold queries of `datasets/development_set.json` and `datasets/regression_set.json` as they are in this repository.
