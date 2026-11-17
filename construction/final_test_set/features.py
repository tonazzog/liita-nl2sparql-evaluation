"""Rule-based features of gold SPARQL queries, used to map the test sets onto the problem perimeter."""
import json, re, sys
REL = r"lexinfo:(hyponym|hypernym|partMeronym|wholeMeronym|synonym|antonym|holonym|meronym)"
def feats(q):
    s = re.sub(r"#.*", "", q)
    f = {}
    f["res"] = [r for r, p in [("LiITA", r"lila:|liita\.it/data>"), ("CompL-it", r"compl-it"), ("ELIta", r"elita:"),
               ("Sentix", r"marl:"), ("Sicil.", r"DialettoSiciliano"), ("Parm.", r"DialettoParmigiano")] if re.search(p, s)]
    ops = []
    if re.search(r"(REGEX|STRSTARTS|STRENDS|CONTAINS)\s*\(", s, re.I) and not re.search(r"definition\)?\s*,", s): ops.append("morph")
    if re.search(r"lila:has(POS|Gender|InflectionType|Degree|Person)", s): ops.append("gramm")
    rels = re.findall(REL, s)
    if rels: ops.append("rel")
    if "skos:definition" in s: ops.append("def")
    if re.search(r"ontolex:sense", s) and re.search(r"COUNT", s) and "rel" not in ops: ops.append("senses")
    if re.search(r"vartrans:translatableAs", s): ops.append("transl")
    if "elita:" in s: ops.append("emotion")
    if "marl:" in s: ops.append("polarity")
    if re.search(r"\b(COUNT|AVG|SUM|MAX|MIN)\s*\(", s, re.I): ops.append("agg")
    if re.search(r"GROUP BY", s, re.I) and re.search(r"\b(COUNT|AVG|SUM)\s*\(", s, re.I): ops.append("group")
    f["ops"] = ops
    comp = []
    sym = len(re.findall(r"\}\s*UNION\s*\{\s*\?\w+\s+lexinfo:(synonym|antonym)", s))
    nrel = len(rels) - 2 * sym + sym
    if nrel >= 2: comp.append("chain/inters")
    if re.search(r"NOT EXISTS|MINUS", s, re.I): comp.append("neg")
    if len(re.findall(r"UNION", s)) > sym: comp.append("union")
    if len(re.findall(r"SELECT", s, re.I)) > 1: comp.append("subq")
    if re.search(r"HAVING", s, re.I): comp.append("having")
    if re.search(r"FILTER\s*\(\s*(STR\()?\?\w+\)?\s*(!=|=|<|>|<=|>=)\s*(STR\()?\?\w+", s): comp.append("var-cmp")
    lits = set(re.findall(r'=\s*"([^"]+)"', s))
    if len(lits) >= 2: comp.append(f"{len(lits)}-seed")
    if "OPTIONAL" in s: comp.append("optional")
    f["comp"] = comp
    return f
if __name__ == "__main__":
    d = json.load(open(sys.argv[1], encoding="utf-8")); c = d["test_cases"] if isinstance(d, dict) else d
    for x in c:
        f = feats(x["sparql"])
        print(x["id"], x.get("structure", x["category"]), "|", ",".join(f["res"]), "|", ",".join(f["ops"]), "|", ",".join(f["comp"]), "|", x["nl_en"][:110])
