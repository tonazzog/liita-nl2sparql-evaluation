#!/bin/bash
# Final single run on the frozen test v2 (English questions): NL2SPARQL base R3b and MoSAIC v2 F4h,
# Mistral Large 4 and Claude Sonnet 4.6. Systems at tag thesis-final-2026-11-15.
DS=<evaluation-repo>/perimetro/newtest_v2_frozen.json
D=<evaluation-repo>/results/final
mkdir -p $D
SHA=$(sha256sum $DS | cut -c1-64)
[ "$SHA" = 4e63a354d393dd425f11d28b9196831b6578b8ec0140956062c5c23c962ce7ea ] || { echo "TEST V2 SHA MISMATCH $SHA"; exit 1; }
for r in nl2sparql mosaic-liita; do
  cd <systems>/$r
  [ "$(git rev-parse HEAD)" = "$(git rev-parse thesis-final-2026-11-15^{commit})" ] || { echo "$r not at tag"; exit 1; }
  [ -z "$(git status --porcelain --untracked-files=no)" ] || { echo "$r dirty"; exit 1; }
done
echo "test v2 sha ok; repos at tag thesis-final-2026-11-15" | tee $D/run_info.txt
export MISTRAL_API_KEY=$(powershell.exe -NoProfile -Command "[Environment]::GetEnvironmentVariable('MISTRAL_API_KEY','User')" | tr -d '\r\n')
export PYTHONIOENCODING=utf-8 PYTHONUNBUFFERED=1
unset NL2SPARQL_ALL_CONSTRAINTS
NPY=<systems>/nl2sparql_env/nl2sparql/Scripts/python.exe
MPY=<systems>/envs/prisma/Scripts/python.exe

nl2s() {  # $1 provider $2 model $3 tag $4 logvar
  cd <systems>/nl2sparql
  env $4="$D/$3.calls.jsonl" $NPY scripts/run_f1_evaluation.py --provider $1 --model $2 --language en --strip-limit \
    --dataset $DS -o $D/$3.json > $D/$3.log 2>&1
  echo "$3: $(grep -m1 'Avg F1' $D/$3.log)"
}
mosaic() {  # $1 provider $2 model $3 tag $4 logvar
  cd <systems>/mosaic-liita
  env LLM_REASONING_MIN_TOKENS=32000 $4="$D/$3.calls.jsonl" MOSAIC_PLAN_LOG="$D/$3.plans.jsonl" \
    $MPY scripts/run_f1_evaluation.py --mode agentic --provider $1 --model $2 --language en \
    --dataset $DS --delay 1.1 -o $D/$3.json > $D/$3.log 2>&1
  echo "$3: $(grep -m1 'Avg F1' $D/$3.log)"
}
budget() { grep -qiE "budget_exhausted|budget exhausted|status code 402|error code: 402|HTTP 402" "$D/$1.log" && echo "BUDGET EXHAUSTED in $1"; }

nl2s mistral mistral-large-4-0 mi_nl2s MISTRAL_LOG; budget mi_nl2s
mosaic mistral mistral-large-4-0 mi_mosaic MISTRAL_LOG; budget mi_mosaic
nl2s claudecode claude-sonnet-4-6 cc_nl2s CLAUDECODE_LOG
mosaic claudecode claude-sonnet-4-6 cc_mosaic CLAUDECODE_LOG
echo ALL DONE
