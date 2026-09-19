import json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'tools'))
from claim_registry import load,validate
from claim_reviews import make_review,Evidence
D=Path(__file__).parent;p=json.loads((D/'patch.json').read_text());data=load();by={c['id']:c for c in data['claims']};ev=Evidence()
for item in p['claims']:
 c=by[item['id']];c.update(item['fields'])
 for field,r in item['reviews'].items():
  c['reviews'][field]=make_review(data,c,field,r['evidence_targets'],revision=p['baseline_revision'],date='2026-09-19',note=r['note'],reviewer='Codex parallel classify_680_end',state=r['state'],next_action=r['next_action'],evidence=ev)
validate(data)
report={'patch_claims':len(p['claims']),'field_reviews':3*len(p['claims']),'schema_valid':True,'evidence_targets_resolved':len(ev.cache),'canonical_registry_written':False}
(D/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
