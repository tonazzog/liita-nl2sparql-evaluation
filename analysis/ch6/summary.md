# Chapter 6 extractions (test v2, 86 questions)

## F1 per group

| group | n | NL2S-Mistral | MoSAIC-Mistral | NL2S-Claude | MoSAIC-Claude | NL2S-Agent-Claude |
|---|---|---|---|---|---|---|
| S simple | 20 | 0.77 | 0.99 | 0.81 | 0.99 | 0.87 |
| C1 conjunction | 8 | 0.81 | 0.93 | 0.81 | 0.95 | 0.81 |
| C2 disjunction | 3 | 0.67 | 1.00 | 0.89 | 1.00 | 0.89 |
| C3 chain | 5 | 0.99 | 0.80 | 0.77 | 0.73 | 0.97 |
| C4 intersection | 6 | 0.90 | 0.98 | 0.90 | 0.98 | 0.90 |
| C5 self-join | 5 | 0.70 | 0.97 | 0.87 | 0.87 | 0.87 |
| C6 negation | 7 | 0.71 | 0.70 | 0.85 | 0.71 | 0.79 |
| C7 union | 4 | 0.73 | 1.00 | 0.69 | 0.96 | 0.94 |
| C8 group-by/ranking | 6 | 0.76 | 0.50 | 0.67 | 0.50 | 0.58 |
| C9 HAVING | 4 | 0.42 | 0.75 | 0.67 | 0.75 | 0.67 |
| C10 comparison w/ reference | 3 | 1.00 | 0.67 | 0.67 | 1.00 | 0.67 |
| C11 comparison between variables | 5 | 0.86 | 0.60 | 0.86 | 0.60 | 0.94 |
| C12 nested aggregation | 3 | 0.67 | 0.33 | 1.00 | 0.33 | 1.00 |
| C13 multi-statistic | 4 | 0.96 | 0.00 | 0.46 | 0.48 | 0.30 |
| M metadata | 3 | 0.67 | 0.67 | 0.67 | 0.67 | 0.83 |

## Register

Questions per group and register (studente / tecnico):

| group | studente | tecnico |
|---|---|---|
| S | 7 | 13 |
| C1 | 3 | 5 |
| C2 | 0 | 3 |
| C3 | 2 | 3 |
| C4 | 3 | 3 |
| C5 | 1 | 4 |
| C6 | 3 | 4 |
| C7 | 2 | 2 |
| C8 | 1 | 5 |
| C9 | 2 | 2 |
| C10 | 1 | 2 |
| C11 | 2 | 3 |
| C12 | 0 | 3 |
| C13 | 0 | 4 |
| M | 2 | 1 |

F1 by register, overall / simple (S) / composite (C1-C13):

| config | studente all | studente S | studente C | tecnico all | tecnico S | tecnico C |
|---|---|---|---|---|---|---|
| NL2S-Mistral | 0.795 (n=29) | 0.714 (n=7) | 0.827 (n=20) | 0.770 (n=57) | 0.796 (n=13) | 0.769 (n=43) |
| MoSAIC-Mistral | 0.905 (n=29) | 1.000 (n=7) | 0.862 (n=20) | 0.730 (n=57) | 0.983 (n=13) | 0.671 (n=43) |
| NL2S-Claude | 0.822 (n=29) | 0.952 (n=7) | 0.784 (n=20) | 0.765 (n=57) | 0.731 (n=13) | 0.781 (n=43) |
| MoSAIC-Claude | 0.899 (n=29) | 1.000 (n=7) | 0.854 (n=20) | 0.771 (n=57) | 0.983 (n=13) | 0.725 (n=43) |
| NL2S-Agent-Claude | 0.836 (n=29) | 0.857 (n=7) | 0.812 (n=20) | 0.804 (n=57) | 0.881 (n=13) | 0.787 (n=43) |

## Bootstrap (percentile 95% CI, 10000 resamples of questions)

| config | mean F1 | 95% CI |
|---|---|---|
| NL2S-Mistral | 0.778 | [0.698, 0.852] |
| MoSAIC-Mistral | 0.789 | [0.700, 0.869] |
| NL2S-Claude | 0.784 | [0.704, 0.858] |
| MoSAIC-Claude | 0.814 | [0.731, 0.887] |
| NL2S-Agent-Claude | 0.815 | [0.740, 0.883] |

Paired comparisons (A - B): mean difference, bootstrap 95% CI, two-sided paired permutation (sign-flip) p-value, wins/ties/losses per question:

| A vs B | diff | 95% CI | p | W/T/L |
|---|---|---|---|---|
| NL2S-Mistral vs MoSAIC-Mistral | -0.011 | [-0.122, +0.099] | 0.851 | 15/48/23 |
| NL2S-Mistral vs NL2S-Claude | -0.006 | [-0.089, +0.079] | 0.900 | 11/64/11 |
| NL2S-Mistral vs MoSAIC-Claude | -0.036 | [-0.139, +0.068] | 0.495 | 16/46/24 |
| NL2S-Mistral vs NL2S-Agent-Claude | -0.036 | [-0.122, +0.050] | 0.412 | 13/60/13 |
| MoSAIC-Mistral vs NL2S-Claude | +0.005 | [-0.089, +0.098] | 0.922 | 18/55/13 |
| MoSAIC-Mistral vs MoSAIC-Claude | -0.025 | [-0.069, +0.012] | 0.249 | 5/76/5 |
| MoSAIC-Mistral vs NL2S-Agent-Claude | -0.026 | [-0.115, +0.062] | 0.581 | 17/56/13 |
| NL2S-Claude vs MoSAIC-Claude | -0.030 | [-0.120, +0.063] | 0.524 | 12/55/19 |
| NL2S-Claude vs NL2S-Agent-Claude | -0.030 | [-0.087, +0.021] | 0.292 | 6/74/6 |
| MoSAIC-Claude vs NL2S-Agent-Claude | -0.000 | [-0.090, +0.087] | 0.992 | 18/55/13 |

## Outcome taxonomy (questions)

| outcome | NL2S-Mistral | MoSAIC-Mistral | NL2S-Claude | MoSAIC-Claude | NL2S-Agent-Claude |
|---|---|---|---|---|---|
| correct (F1=1) | 52 | 62 | 53 | 62 | 56 |
| executed, partial (0<F1<1) | 21 | 7 | 20 | 10 | 20 |
| executed, wrong (F1=0) | 10 | 10 | 12 | 9 | 9 |
| no query: API error | 1 | 1 | 0 | 0 | 0 |
| no query: CLI timeout | 0 | 0 | 0 | 1 | 1 |
| no query: invalid plan | 0 | 2 | 0 | 0 | 0 |
| no query: truncated/invalid output | 1 | 0 | 0 | 0 | 0 |
| not executed: endpoint 500 | 1 | 2 | 1 | 0 | 0 |
| not executed: endpoint timeout | 0 | 1 | 0 | 2 | 0 |
| not executed: malformed / rejected | 0 | 1 | 0 | 2 | 0 |

## Complementarity (same model)

- Mistral: both perfect 42, both zero 3, only NL2S perfect 10, only MoSAIC perfect 20; oracle (best of the two per question) 0.938
- Claude: both perfect 46, both zero 5, only NL2S perfect 7, only MoSAIC perfect 16; oracle (best of the two per question) 0.912
- Oracle over all configurations: 0.955
