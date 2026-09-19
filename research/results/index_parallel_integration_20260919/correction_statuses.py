#!/usr/bin/env python3
"""Apply scoped correction-endpoint reviews; never infer blanket retraction."""
import json,sys,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'tools'))
from claim_registry import load,write_json,validate,REGISTRY
from claim_reviews import make_review,Evidence,claim_digest
data=load();claims={c['id']:c for c in data['claims']};ev=Evidence()
rev=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
URL='https://kbr.is-a.dev/math-research/#';newscope=URL+'permutation-audit-correction-impact';changed=[]
for folder in ('parallel_index_correction_endpoints','parallel_correction_scope_review'):
 filename='status-review-proposals.json' if folder.endswith('endpoints') else 'status-proposals.json'
 patch=json.loads((ROOT/'research/results'/folder/filename).read_text())
 for row in patch['status_reviews']:
  c=claims[row['id']];assert claim_digest(c)==row['source_fields_sha256']
  assert c['mathematical_status']==row['current_mathematical_status']
  for e in row['evidence']:assert ev.sha256(e['target'],e.get('normalization'))==e['sha256'],e['target']
  old=c['reviews']['mathematical_status'];targets=list(dict.fromkeys([e['target'] for e in old['evidence']]+[e['target'] for e in row['evidence']]+[newscope]))
  c['mathematical_status']=row['proposed_mathematical_status']
  c['reviews']['mathematical_status']=make_review(data,c,'mathematical_status',targets,revision=rev,date='2026-09-19',reviewer='Codex coordinator with independent correction-scope review',note=row['note'],evidence=ev)
  changed.append(c['id'])
  if folder=='parallel_correction_scope_review' and row['current_mathematical_status']!=row['proposed_mathematical_status']:
   source='audit:permutation-NA-source-error';key=source+'::corrects::'+c['id']
   assert not any(e['id']==key for e in data['relationships'])
   data['relationships'].append({'id':key,'source':{'namespace':'current','id':source,'locator':None},'target':{'namespace':'current','id':c['id'],'locator':None},'type':'corrects','evidence':[newscope]+[e['target'] for e in row['evidence']],'review_status':'reviewed','scope':row['note'],'review':{'revision':rev,'date':'2026-09-19','reviewer':'Codex coordinator','note':'Scoped direct-use or application audit; final statement not declared false.'}})
   for label in (source,c['id']):
    claim=claims[label];old=claim['reviews']['relationships'];targets=list(dict.fromkeys([e['target'] for e in old['evidence']]+[newscope]))
    claim['reviews']['relationships']=make_review(data,claim,'relationships',targets,revision=rev,date='2026-09-19',reviewer='Codex coordinator',note=old['note']+' Added source-backed scoped probability correction; conditional decoder implications remain distinct.',evidence=ev)
# The newly indexed many-out-row source uses the stable mathematical audit section,
# not its still-being-written administrative checkpoint paragraph.
c=claims['lem:many-out-rows-satisfaction']
for field,old in list(c['reviews'].items()):
 targets=[URL+'permutation-audit-scope' if e['target']==URL+'entry-2026-09-19-permutation-probability-audit' else e['target'] for e in old['evidence']]
 c['reviews'][field]=make_review(data,c,field,targets,revision=rev,date='2026-09-19',reviewer='Codex coordinator',note=old['note']+' Audit locator narrowed to its unchanged mathematical scope section.',state=old['state'],next_action=old['next_action'],evidence=ev)
validate(data);write_json(REGISTRY,data);write_json(Path(__file__).with_name('correction-status-integration.json'),{'reviewed':changed,'scope':'Historical correction scopes retained; five additional probability-dependent aggregates made conditional, no blanket retraction.'})
print('Integrated',len(changed),'correction-target status reviews.')
