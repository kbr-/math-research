import json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'tools'))
from claim_registry import load,validate
from claim_reviews import Evidence
D=Path(__file__).parent;x=load();ev=Evidence();edges={e['id']:e for e in x['relationships']};n=0;count=0
for p in sorted(D.glob('patch_*.json')):
 b=json.loads(p.read_text());n+=len(b['claims']);count+=len(b['relationships'])
 for c in b['claims']:
  for t in c['evidence']:ev.sha256(t)
 for e in b['relationships']:
  for t in e['evidence']:ev.sha256(t)
  edges[e['id']]=e
x['relationships']=list(edges.values());validate(x)
a={'inventories':n,'proposed_relationships':count,'schema_valid':True,'distinct_evidence_targets_hashed':len(ev.cache),'canonical_written':False}
(D/'validation.json').write_text(json.dumps(a,indent=2)+'\n');print(a)
