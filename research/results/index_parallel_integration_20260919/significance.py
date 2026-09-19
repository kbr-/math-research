#!/usr/bin/env python3
"""Apply reviewed significance-only proposals after exact evidence checks."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'tools'))
from claim_registry import load,write_json,validate,REGISTRY
from claim_reviews import Evidence,claim_digest,digest
data=load();byid={c['id']:c for c in data['claims']};ev=Evidence()
patch=json.loads((ROOT/'research/results/parallel_index_significance_integration/patch.json').read_text())
for row in patch['claims']:
 c=byid[row['id']];assert claim_digest(c)==row['baseline_claim_sha256']
 assert set(row['fields'])=={'significance'}
 r=row['reviews']['significance']
 for item in r['evidence']:assert ev.sha256(item['target'])==item['sha256'],item['target']
 assert c['reviews']['significance']['state']=='pending'
 c['significance']=row['fields']['significance'];assert digest(c['significance'])==r['value_sha256']
 c['reviews']['significance']=r
validate(data);write_json(REGISTRY,data)
write_json(Path(__file__).with_name('significance-integration.json'),{'claims':[r['id'] for r in patch['claims']],'scope':'Only significance and its review changed; completed bounded audits preserve novelty uncertainty.'})
print('Integrated',len(patch['claims']),'significance dispositions.')
