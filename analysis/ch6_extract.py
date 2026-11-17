"""Extractions for thesis chapter 6 from the final test-v2 reports (no LLM, no endpoint).

usage: python analysis/ch6_extract.py   -> writes analysis/ch6/*.csv and analysis/ch6/summary.md
"""
import collections
import csv
import json
import os
import random

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repository root
DS = os.path.join(HERE, "datasets", "final_test_set.json")
FIN = os.path.join(HERE, "runs", "final")
OUT = os.path.join(HERE, "analysis", "ch6")
CONFIGS = {  # final reports (rescored; NL2SPARQL Mistral with the 4083 retry merged)
    "NL2S-Mistral": "mi_nl2s_rsm.json",
    "MoSAIC-Mistral": "mi_mosaic_rs.json",
    "NL2S-Claude": "cc_nl2s_rs.json",
    "MoSAIC-Claude": "cc_mosaic_rs.json",
    "NL2S-Agent-Claude": "cc_nl2s_agent_rsm.json",  # not developed in this phase
}
GROUPS = ["S"] + [f"C{i}" for i in range(1, 14)] + ["M"]
GROUP_NAMES = {
    "S": "simple", "C1": "conjunction", "C2": "disjunction", "C3": "chain", "C4": "intersection",
    "C5": "self-join", "C6": "negation", "C7": "union", "C8": "group-by/ranking", "C9": "HAVING",
    "C10": "comparison w/ reference", "C11": "comparison between variables", "C12": "nested aggregation",
    "C13": "multi-statistic", "M": "metadata",
}
B = 10000
random.seed(20261116)


def load():
    ds = {str(c["id"]): c for c in json.load(open(DS, encoding="utf-8"))["test_cases"]}
    reps = {}
    for k, f in CONFIGS.items():
        rs = json.load(open(os.path.join(FIN, f), encoding="utf-8"))["results"]
        reps[k] = {str(r["test_id"]): r for r in rs}
        assert set(reps[k]) == set(ds), (k, len(reps[k]))
    return ds, reps


def f1(r):
    return float(r.get("f1") or 0.0)


def mean(xs):
    return sum(xs) / len(xs) if xs else float("nan")


def outcome(r):
    """Failure taxonomy for one result."""
    err = str(r.get("predicted_error") or "")
    if not r.get("predicted_sparql"):
        if "520" in err or "API error" in err:
            return "no query: API error"
        if "TreePlanError" in err:
            return "no query: invalid plan"
        if "timed out" in err.lower() or "TimeoutExpired" in err or "claude.CMD" in err:
            return "no query: CLI timeout"
        if "length" in err.lower() or "trunc" in err.lower() or "JSON" in err:
            return "no query: truncated/invalid output"
        return "no query: other (" + err[:40] + ")"
    if err and err != "None":
        if "timed out" in err.lower():
            return "not executed: endpoint timeout"
        if "500" in err or "InternalError" in err:
            return "not executed: endpoint 500"
        if "BadFormed" in err or "SP0" in err:
            return "not executed: malformed / rejected"
        return "not executed: other"
    v = f1(r)
    if v == 1.0:
        return "correct (F1=1)"
    if v == 0.0:
        return "executed, wrong (F1=0)"
    return "executed, partial (0<F1<1)"


def write_csv(name, header, rows):
    with open(os.path.join(OUT, name), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)


def main():
    os.makedirs(OUT, exist_ok=True)
    ds, reps = load()
    ids = sorted(ds)
    cfgs = list(CONFIGS)
    md = ["# Chapter 6 extractions (test v2, 86 questions)", ""]

    # 1. per-question matrix (for appendix / plots)
    write_csv("per_question.csv", ["id", "group", "cell", "register"] + cfgs,
              [[i, ds[i]["group"], ds[i]["cell"], ds[i]["register"]] + [f"{f1(reps[c][i]):.3f}" for c in cfgs]
               for i in ids])

    # 2. group x config
    rows = []
    md += ["## F1 per group", "", "| group | n | " + " | ".join(cfgs) + " |", "|---" * (len(cfgs) + 2) + "|"]
    for g in GROUPS:
        gi = [i for i in ids if ds[i]["group"] == g]
        vals = [mean([f1(reps[c][i]) for i in gi]) for c in cfgs]
        rows.append([g, GROUP_NAMES[g], len(gi)] + [f"{v:.3f}" for v in vals])
        md.append(f"| {g} {GROUP_NAMES[g]} | {len(gi)} | " + " | ".join(f"{v:.2f}" for v in vals) + " |")
    write_csv("group_by_config.csv", ["group", "name", "n"] + cfgs, rows)

    # 3. register x group (composition) and register x config, within S and composite
    md += ["", "## Register", "", "Questions per group and register (studente / tecnico):", ""]
    comp = collections.Counter((ds[i]["group"], ds[i]["register"]) for i in ids)
    regs = sorted({ds[i]["register"] for i in ids})
    rows = [[g] + [comp[(g, r)] for r in regs] for g in GROUPS]
    write_csv("register_by_group.csv", ["group"] + regs, rows)
    md.append("| group | " + " | ".join(regs) + " |")
    md.append("|---" * (len(regs) + 1) + "|")
    md += ["| " + " | ".join(str(x) for x in r) + " |" for r in rows]
    md += ["", "F1 by register, overall / simple (S) / composite (C1-C13):", "",
           "| config | " + " | ".join(f"{r} all | {r} S | {r} C" for r in regs) + " |",
           "|---" * (1 + 3 * len(regs)) + "|"]
    rows = []
    for c in cfgs:
        cells = []
        for r in regs:
            for sel in (lambda g: True, lambda g: g == "S", lambda g: g.startswith("C")):
                xs = [f1(reps[c][i]) for i in ids if ds[i]["register"] == r and sel(ds[i]["group"])]
                cells.append(f"{mean(xs):.3f} (n={len(xs)})")
        rows.append([c] + cells)
        md.append(f"| {c} | " + " | ".join(cells) + " |")
    write_csv("register_by_config.csv", ["config"] + [f"{r}_{s}" for r in regs for s in ("all", "S", "C")], rows)

    # 4. bootstrap CIs and paired comparisons
    md += ["", f"## Bootstrap (percentile 95% CI, {B} resamples of questions)", "",
           "| config | mean F1 | 95% CI |", "|---|---|---|"]
    mat = {c: [f1(reps[c][i]) for i in ids] for c in cfgs}
    n = len(ids)
    boots = [[random.randrange(n) for _ in range(n)] for _ in range(B)]
    rows = []
    for c in cfgs:
        ms = sorted(mean([mat[c][j] for j in s]) for s in boots)
        lo, hi = ms[int(0.025 * B)], ms[int(0.975 * B) - 1]
        rows.append([c, f"{mean(mat[c]):.3f}", f"{lo:.3f}", f"{hi:.3f}"])
        md.append(f"| {c} | {mean(mat[c]):.3f} | [{lo:.3f}, {hi:.3f}] |")
    write_csv("bootstrap_ci.csv", ["config", "mean", "ci_lo", "ci_hi"], rows)

    md += ["", "Paired comparisons (A - B): mean difference, bootstrap 95% CI, two-sided paired permutation "
           "(sign-flip) p-value, wins/ties/losses per question:", "",
           "| A vs B | diff | 95% CI | p | W/T/L |", "|---|---|---|---|---|"]
    rows = []
    for a_i in range(len(cfgs)):
        for b_i in range(a_i + 1, len(cfgs)):
            a, b = cfgs[a_i], cfgs[b_i]
            d = [x - y for x, y in zip(mat[a], mat[b])]
            obs = mean(d)
            ms = sorted(mean([d[j] for j in s]) for s in boots)
            lo, hi = ms[int(0.025 * B)], ms[int(0.975 * B) - 1]
            ext = sum(1 for _ in range(B)
                      if abs(mean([x if random.random() < 0.5 else -x for x in d])) >= abs(obs) - 1e-12)
            p = (ext + 1) / (B + 1)
            w = sum(x > 1e-9 for x in d); l = sum(x < -1e-9 for x in d); t = n - w - l
            rows.append([a, b, f"{obs:.3f}", f"{lo:.3f}", f"{hi:.3f}", f"{p:.3f}", w, t, l])
            md.append(f"| {a} vs {b} | {obs:+.3f} | [{lo:+.3f}, {hi:+.3f}] | {p:.3f} | {w}/{t}/{l} |")
    write_csv("paired_tests.csv", ["A", "B", "diff", "ci_lo", "ci_hi", "p_perm", "wins", "ties", "losses"], rows)

    # 5. failure taxonomy
    tax = {c: collections.Counter(outcome(reps[c][i]) for i in ids) for c in cfgs}
    cats = sorted({k for t in tax.values() for k in t})
    md += ["", "## Outcome taxonomy (questions)", "", "| outcome | " + " | ".join(cfgs) + " |",
           "|---" * (len(cfgs) + 1) + "|"]
    rows = [[k] + [tax[c][k] for c in cfgs] for k in cats]
    md += ["| " + " | ".join(str(x) for x in r) + " |" for r in rows]
    write_csv("outcome_taxonomy.csv", ["outcome"] + cfgs, rows)
    detail = [[i, ds[i]["group"], c, outcome(reps[c][i]), str(reps[c][i].get("predicted_error") or "")[:120]]
              for c in cfgs for i in ids if not outcome(reps[c][i]).startswith(("correct", "executed"))]
    write_csv("failures_detail.csv", ["id", "group", "config", "outcome", "error"], detail)

    # 6. agreement between systems (complementarity)
    md += ["", "## Complementarity (same model)", ""]
    for m in ("Mistral", "Claude"):
        a, b = mat[f"NL2S-{m}"], mat[f"MoSAIC-{m}"]
        both = sum(x == 1 and y == 1 for x, y in zip(a, b))
        none = sum(x == 0 and y == 0 for x, y in zip(a, b))
        oracle = mean([max(x, y) for x, y in zip(a, b)])
        md.append(f"- {m}: both perfect {both}, both zero {none}, only NL2S perfect "
                  f"{sum(x == 1 and y < 1 for x, y in zip(a, b))}, only MoSAIC perfect "
                  f"{sum(y == 1 and x < 1 for x, y in zip(a, b))}; oracle (best of the two per question) {oracle:.3f}")
    a = mean([max(mat[c][j] for c in cfgs) for j in range(n)])
    md.append(f"- Oracle over all configurations: {a:.3f}")

    open(os.path.join(OUT, "summary.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
