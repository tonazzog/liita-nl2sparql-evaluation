export MISTRAL_API_KEY=$(powershell.exe -NoProfile -Command "[Environment]::GetEnvironmentVariable('MISTRAL_API_KEY','User')" | tr -d '\r\n')
export PYTHONIOENCODING=utf-8 PYTHONUNBUFFERED=1; unset NL2SPARQL_ALL_CONSTRAINTS
cd <systems>/nl2sparql && git rev-parse --short HEAD
MISTRAL_LOG=<evaluation-repo>/results/final/mi_nl2s_retry.calls.jsonl <systems>/nl2sparql_env/nl2sparql/Scripts/python.exe scripts/run_f1_evaluation.py --provider mistral --model mistral-large-4-0 --language en --strip-limit --dataset <tmp> -o <evaluation-repo>/results/final/mi_nl2s_retry.json > <evaluation-repo>/results/final/mi_nl2s_retry.log 2>&1
cd <systems>/mosaic-liita && git rev-parse --short HEAD
LLM_REASONING_MIN_TOKENS=32000 MISTRAL_LOG=<evaluation-repo>/results/final/mi_mosaic_retry.calls.jsonl MOSAIC_PLAN_LOG=<evaluation-repo>/results/final/mi_mosaic_retry.plans.jsonl <systems>/envs/prisma/Scripts/python.exe scripts/run_f1_evaluation.py --mode agentic --provider mistral --model mistral-large-4-0 --language en --dataset <evaluation-repo>/perimetro/newtest_v2_frozen.json --test-ids 4076 --delay 1.1 -o <evaluation-repo>/results/final/mi_mosaic_retry.json > <evaluation-repo>/results/final/mi_mosaic_retry.log 2>&1
python -c "
import json
for f in ['mi_nl2s_retry','mi_mosaic_retry']:
    for r in json.load(open('<evaluation-repo>/results/final/'+f+'.json',encoding='utf-8'))['results']: print(f,r['test_id'],round(r['f1'],3),str(r.get('predicted_error'))[:120])"
