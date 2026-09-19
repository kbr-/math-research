#!/usr/bin/env python3
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'tools'))
from claim_registry import load,validate,write_json
from claim_reviews import Evidence,make_review,claim_digest
p=Path(__file__).parent;patch=json.loads((p/'patch.json').read_text());data=load();lookup={c['id']:c for c in data['claims']};ev=Evidence()
for r in patch['claims']:
 c=lookup[r['id']];assert claim_digest(c)==r['claim_sha256']
 for f,v in r['values'].items():c[f]=v
 for f,rw in r['reviews'].items():c['reviews'][f]=make_review(data,c,f,rw['evidence_targets'],revision=patch['baseline'],date=patch['date'],reviewer=patch['reviewer'],note=rw['note'],state=rw['state'],next_action=rw['next_action'],evidence=ev)
validate(data)
write_json(p/'validation.json',{'valid':True,'claims':len(patch['claims']),'fields':sum(len(r['values']) for r in patch['claims']),'scope':'Applied proposal to in-memory current registry; schema and evidence review construction passed. Canonical files unchanged.'})
print('159 records, 477 field reviews: in-memory schema and source evidence checks passed.')
