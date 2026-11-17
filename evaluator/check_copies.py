"""Check that the evaluator copies in the three systems are identical to evaluator/f1_evaluator.py.

usage: python evaluator/check_copies.py PATH_TO_NL2SPARQL PATH_TO_MOSAIC PATH_TO_PRISMA
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
COPIES = {
    "nl2sparql": os.path.join("nl2sparql", "evaluation", "f1_evaluator.py"),
    "mosaic-liita": os.path.join("evaluation", "f1_evaluator.py"),
    "prisma-per-liita": os.path.join("evaluation", "f1_evaluator.py"),
}


def digest(path):
    return hashlib.sha256(open(path, "rb").read().replace(b"\r\n", b"\n")).hexdigest()


ref = digest(os.path.join(HERE, "f1_evaluator.py"))
if len(sys.argv) != 4:
    sys.exit(__doc__)
ok = True
for (name, rel), root in zip(COPIES.items(), sys.argv[1:]):
    d = digest(os.path.join(root, rel))
    same = d == ref
    ok &= same
    print(f"{name:18} {'identical' if same else 'DIFFERENT'}  {d[:16]}")
print("reference         ", ref[:16])
sys.exit(0 if ok else 1)
