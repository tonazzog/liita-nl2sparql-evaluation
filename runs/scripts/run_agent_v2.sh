#!/bin/bash
# NL2SPARQL agent (not developed in this phase), Claude Sonnet 4.6: smoke on 3 held-out q, then single run on frozen test v2.
S=<tmp>
DS=<evaluation-repo>/perimetro/newtest_v2_frozen.json
D=<evaluation-repo>/results/final
SHA=$(sha256sum $DS | cut -c1-64)
[ "$SHA" = 4e63a354d393dd425f11d28b9196831b6578b8ec0140956062c5c23c962ce7ea ] || { echo "TEST V2 SHA MISMATCH"; exit 1; }
cd <systems>/nl2sparql
[ "$(git rev-parse HEAD)" = "$(git rev-parse thesis-final-2026-11-15^{commit})" ] || { echo "not at tag"; exit 1; }
[ -z "$(git status --porcelain --untracked-files=no)" ] || { echo "dirty"; exit 1; }
export PYTHONIOENCODING=utf-8 PYTHONUNBUFFERED=1
unset NL2SPARQL_ALL_CONSTRAINTS
NPY=<systems>/nl2sparql_env/nl2sparql/Scripts/python.exe
run() { # $1 dataset $2 tag
  env CLAUDECODE_LOG="$D/$2.calls.jsonl" $NPY scripts/run_f1_evaluation.py --use-agent --provider claudecode \
    --model claude-sonnet-4-6 --language en --strip-limit --dataset $1 -o $D/$2.json > $D/$2.log 2>&1
  echo "$2: $(grep -m1 'Avg F1' $D/$2.log) | $(grep -m1 'Translation errors' $D/$2.log)"
}
run <tmp> smoke_cc_nl2s_agent
grep -q "Translation errors : 3" $D/smoke_cc_nl2s_agent.log && { echo "SMOKE FAILED"; exit 1; }
grep -q "Avg F1" $D/smoke_cc_nl2s_agent.log || { echo "SMOKE FAILED (no result)"; exit 1; }
run $DS cc_nl2s_agent
echo ALL DONE
