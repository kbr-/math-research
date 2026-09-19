import json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'tools'))
from claim_registry import load
from claim_reviews import claim_digest
D=Path(__file__).parent;old=R/'research/results/parallel_index_dependencies_680_end';x=load();by={c['id']:c for c in x['claims']};rows=[]
for name in ['patch_721_741.json','patch_741_780.json']:
 p=json.loads((old/name).read_text())
 for r in p['claims']:
  if r['state']!='pending':continue
  r=dict(r);r['state']='reviewed';r['next_action']=None
  if r['id']=='obs:literal-window-structure':r['note']='Inventory resolved: original window statement concerns slack-tree encodings moving arbitrary residual rows; later pair-space decoder moves compact residual rows only. Pigeon-only refutation corrects the row-only obligation; pair-space text is later repair scope, not a prerequisite of the original observation. No unresolved relationship ownership remains.'
  elif r['id']=='obs:window-height-budget':r['note']='Inventory resolved: degree budget uses the compact weight ledger; original mixed compact/slack composition and blanket O(N) height are withdrawn by the composition-gap record. Later current-term theorem is a different conditional decoder statement on Phi0 with explicit p_R. These are correction/repair relations, not an unproved dependency hidden in the original observation.'
  else:r['note']+=' Relationship inventory now resolved: the disputed permutation-event inference or precise inherited proof step is explicitly recorded. The independent audit and dated coordinator record identify the false premise; no missing dependency ownership remains. This marks provenance completeness only, not proof validity or repair, and changes no mathematical status.'
  assert claim_digest(by[r['id']]) in {r.get('source_fields_sha256'),r.get('claim_sha256')},r['id']
  rows.append(r)
(D/'inventory-resolutions.json').write_text(json.dumps({'base_revision':'dc1d95b4cb6a463436256b830afd69029c1dc3ed','claims':rows,'relationships':[],'scope':'Close explicit dependency-role inventory questions only; all NA mathematical status and repair decisions remain coordinator-owned.'},indent=2)+'\n');print('Resolved inventory role dispositions:',len(rows))
