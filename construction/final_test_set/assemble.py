"""Assemble the four blocks into newtest_draft.json (held-out-like format) and a review sheet newtest_revisione.md.
Not frozen: freezing (hash) happens only after the user's review.
"""
import collections, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from features import feats

HERE = os.path.dirname(os.path.abspath(__file__))
BLOCKS = ["newtest_s.json", "newtest_c123.json", "newtest_c456.json", "newtest_rest.json"]

qs = [q for b in BLOCKS for q in json.load(open(os.path.join(HERE, b), encoding="utf-8"))]
assert len(qs) == 86 and len({q["id"] for q in qs}) == 86, len(qs)
assert all(q["gold_rows"] for q in qs), [q["id"] for q in qs if not q["gold_rows"]]

cases = [{"id": q["id"], "cell": q["cell"], "group": q["group"], "resources": q["resources"], "ops": q["ops"],
          "register": q["register"], "nl_it": q["nl_it"], "nl_en": q["nl_en"], "sparql": q["sparql"],
          "answer_variables": q["answer_variables"], "gold_rows": q["gold_rows"], "seed": q.get("seed"),
          "params": q.get("params")} for q in qs]
json.dump({"name": "LiITA NL2SPARQL test v2 (draft, not frozen)", "created": "2026-11-10", "test_cases": cases},
          open(os.path.join(HERE, "newtest_draft.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

res = collections.Counter(r for q in cases for r in q["resources"])
reg = collections.Counter(q["register"] for q in cases)
sig = collections.Counter()
for q in cases:
    f = feats(re.sub(r"(?m)^PREFIX.*$", "", q["sparql"]))
    sig[(q["group"], tuple(f["res"]), tuple(f["ops"]), tuple(k for k in f["comp"] if k != "optional"))] += 1
lines = ["# Nuovo test set — foglio di revisione (bozza, non congelata)", "",
         f"86 domande; registro: {dict(reg)}; risorse: {dict(res)}; "
         f"firme strutturali distinte: {len(sig)} (max ripetizioni: {max(sig.values())}).", "",
         "| ID | Cella | Reg. | Domanda (it) | Domanda (en) | Righe gold |", "|---|---|---|---|---|---|"]
for q in cases:
    lines.append(f"| {q['id']} | {q['cell']} | {q['register'][:4]} | {q['nl_it']} | {q['nl_en']} | {q['gold_rows']} |")
open(os.path.join(HERE, "newtest_revisione.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
print(dict(reg), dict(res), "signatures", len(sig), "max rep", max(sig.values()))
print([k for k, v in sig.items() if v > 2])
