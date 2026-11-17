cd <evaluation-repo>
O=results/dev/baseline_rescored
HO=heldout_dataset_draft.json
MA=<systems>/nl2sparql/nl2sparql/data/test_dataset.json
P=<systems>/prisma-per-liita/python.exe
python rescore.py $HO results/prisma_mistral.json $O/prisma_ho.json > $O/prisma_ho.log 2>&1
python rescore.py $MA <systems>/prisma-per-liita/reports/f1_report_prisma_mistral_mistral-large-4-0.json $O/prisma_ma.json > $O/prisma_ma.log 2>&1
python rescore.py $HO results/mosaic_deterministic.json $O/mdet_ho.json > $O/mdet_ho.log 2>&1
python rescore.py $MA <systems>/mosaic-liita/reports/f1_report_mosaic_deterministic_canonical.json $O/mdet_ma.json > $O/mdet_ma.log 2>&1
python rescore.py $HO results/nl2sparql_agent_mistral.json $O/nl2s_agent_ho.json > $O/nl2s_agent_ho.log 2>&1
python rescore.py $MA <systems>/nl2sparql/reports/f1_report_agent_v2_mistral_mistral-large-4-0.json $O/nl2s_agent_ma.json > $O/nl2s_agent_ma.log 2>&1
for f in $O/*.json; do python -c "import json,sys;r=json.load(open(sys.argv[1],encoding='utf-8'))['results'];print(sys.argv[1],len(r),round(sum(float(x['f1'] or 0) for x in r)/len(r),3))" $f; done
