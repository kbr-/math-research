import json,sys,copy
from pathlib import Path
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'tools'))
from claim_registry import load,validate,check_targets
from claim_reviews import Evidence,claim_digest
from claim_graph import audit
P=Path(__file__).parent
patches=[json.loads((P/f).read_text()) for f in ['patch.json','patch_continued.json']]
wrong='lem:strict-level-axiom-input-certificates::corrects::obs:proper-or-subgroups-share-level'
old=next(e for e in patches[0]['edges'] if e['id']==wrong)
correct=[]
for t in ['cor:negative-leaf-proper-pruning','cor:all-axiom-boundary-proper-pruning']:
 e=copy.deepcopy(old);e['target']['id']=t;e['id']=e['source']['id']+'::corrects::'+t;e['scope']='Supplies the strict-support certificates missing from the original automatic application, preserving the corrected asymptotic result; the valid same-level obstruction audit is not retracted.';e['evidence']=['https://kbr.is-a.dev/math-research/#levels-leaf-pruning','https://kbr.is-a.dev/math-research/#levels-positive-support','https://kbr.is-a.dev/math-research/#levels-negative-support'];correct.append(e)
amend={'remove_proposed_edge_ids':[wrong],'add_edges':correct,'reason':'Repair corrects the faulty automatic applications, not the valid audit that identified their gap. Supersedes only that relation in immutable patch.json.'}
(P/'patch_review_amendment.json').write_text(json.dumps(amend,indent=2)+'\n')
d=load();existing={e['id']:e for e in d['relationships']};conflicts=[];edges=[e for p in patches for e in p['edges'] if e['id']!=wrong]+correct
for e in edges:
 if e['id'] in existing:
  if existing[e['id']]['scope']!=e['scope']:conflicts.append({'id':e['id'],'existing_scope':existing[e['id']]['scope'],'proposed_scope':e['scope']})
 else:d['relationships'].append(e)
validate(d)
ref=check_targets(dict(d,claims=[],preamble='',relationships=edges));E=Evidence();cs={c['id']:c for c in d['claims']};stale=[]
for p in patches:
 for r in p['reviews']:
  if claim_digest(cs[r['id']])!=r['claim_sha256']:stale.append(r['id']+' core')
  for x in r['evidence']:
   if E.sha256(x['target'])!=x['sha256']:stale.append(r['id']+' '+x['target'])
graph=audit(d)
out={'reviews':sum(len(p['reviews']) for p in patches),'proposed_edges_after_amendment':len(edges),'reference_validation':ref,'stale_review_evidence':stale,'existing_scope_differences':conflicts,'graph_audit':graph,'scope':'In-memory additive union only; canonical files untouched; existing edge scopes preserved pending coordinator review.'}
(P/'validation.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ['existing_scope_differences','graph_audit']}));print('Existing scope differences:',len(conflicts));print(json.dumps(graph))
