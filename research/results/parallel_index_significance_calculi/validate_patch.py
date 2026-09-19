import json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'tools'))
from claim_registry import load,validate
from claim_reviews import make_review,Evidence
D=Path(__file__).parent;p=json.loads((D/'patch.json').read_text());x=load();by={c['id']:c for c in x['claims']};e=Evidence()
for a in p['claims']:
 c=by[a['id']];c['significance']=a['significance'];r=a['review'];c['reviews']['significance']=make_review(x,c,'significance',r['evidence_targets'],revision=p['base_revision'],date='2026-09-19',note=r['note'],reviewer='Codex parallel significance audit',state=r['state'],next_action=r['next_action'],evidence=e)
validate(x);report={'claims':2,'schema_valid':True,'evidence_targets_hashed':len(e.cache),'canonical_written':False};(D/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
