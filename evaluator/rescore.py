"""Re-score stored predictions against a dataset, without calling any language model.

usage: python evaluator/rescore.py DATASET.json REPORT.json OUT.json [id,id,...]

Every question listed (all questions if no list is given) is evaluated again with the evaluator of this
repository: the stored predicted query and the gold query are executed on the LiITA endpoint and compared.
Questions without a predicted query are copied unchanged (F1 = 0). The summary (mean precision, recall
and F1) is recomputed over all results.

Gold queries run against the live endpoint, so results can drift if the data of LiITA change.
Run one rescoring at a time: parallel runs overload the endpoint and cause gold-query timeouts.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from f1_evaluator import F1Evaluator  # noqa: E402

FIELDS = ("f1", "precision", "recall", "gold_count", "predicted_count", "true_positives", "aggregate_score",
          "aggregate_details", "variable_mapping", "gold_error", "predicted_error")


def main():
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    ds = {str(c["id"]): c for c in json.load(open(sys.argv[1], encoding="utf-8"))["test_cases"]}
    rep = json.load(open(sys.argv[2], encoding="utf-8"))
    ids = set(sys.argv[4].split(",")) if len(sys.argv) > 4 else set(ds)
    ev = F1Evaluator(strip_limit=True)
    for r in rep["results"]:
        k = str(r["test_id"])
        if k not in ids:
            continue
        if not r.get("predicted_sparql"):
            print(k, "no prediction, kept", r["f1"])
            continue
        c = ds[k]
        old = r["f1"]
        res = ev.evaluate_single(c["sparql"], r["predicted_sparql"], c.get("answer_variables") or {}, test_id=int(k))
        d = res.__dict__
        for f in FIELDS:
            if f in d:
                r[f] = d[f]
        print(k, f"{float(old or 0):.3f} -> {float(r['f1'] or 0):.3f}")
    res = rep["results"]
    n = len(res)
    rep.setdefault("summary", {})
    rep["summary"].update({
        "total_evaluated": n,
        "avg_f1": sum(float(x["f1"] or 0) for x in res) / n,
        "avg_precision": sum(float(x["precision"] or 0) for x in res) / n,
        "avg_recall": sum(float(x["recall"] or 0) for x in res) / n,
    })
    json.dump(rep, open(sys.argv[3], "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print(f"mean F1 over {n} questions: {rep['summary']['avg_f1']:.4f} -> {sys.argv[3]}")


if __name__ == "__main__":
    main()
