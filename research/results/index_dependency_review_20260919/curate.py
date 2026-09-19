#!/usr/bin/env python3
"""Close a connected dependency review from exact ambiguous proof passages."""
import argparse,importlib.util,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'tools'))
from claim_registry import load,validate,write_json,REGISTRY
from claim_reviews import make_review,Evidence
spec=importlib.util.spec_from_file_location('deps',ROOT/'tools/claim-dependencies.py');deps=importlib.util.module_from_spec(spec);spec.loader.exec_module(deps)
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);args=p.parse_args()
data=load();claims={c['id']:c for c in data['claims']};REV=subprocess.check_output(['git','rev-parse','54f2079'],cwd=ROOT,text=True).strip()
WEB='https://kbr.is-a.dev/math-research/#';GH='https://github.com/kbr-/math-research/blob/main/'
HIST=GH+'php_codex_handoff/manuscript/chapters/09_decomposition.md#'
RAZ=GH+'research/notes/SOURCE_AUDIT.md#razborov-base-and-residual-pc-lower-bound'
# namespace, label and locator keep imported mathematics separate from project claims.
rows=[
('thm:matching-affine-annihilators','current','lem:matching-annihilators',None,'depends_on','overlap-matching-rigidity','Forward inclusion and subtraction use the explicit degree-(q+1) matching annihilators.'),
('thm:matching-affine-annihilators','historical','thm:rigidity',HIST+'thm-rigidity','depends_on','overlap-matching-rigidity','Residual affine consequence belongs to the row span in the stated degree range.'),
('thm:matching-affine-annihilators','external','Razborov-1998-Theorem-3.1',RAZ,'depends_on','overlap-matching-rigidity','The exceptional matched-row restriction uses the audited bound for every rectangular board with more pigeons than holes.'),
('lem:spread-quotient-residual','current','thm:matching-affine-annihilators',None,'applies','overlap-spread-residual','Only the PHP-spread application uses MAR; the elementary quotient-dimension lemma is proved independently.'),
('lem:spread-quotient-residual','current','lem:matching-annihilators',None,'applies','overlap-spread-residual','The application uses added dimension q(n+1); not a prerequisite of the abstract linear-algebra inequality.'),
('lem:spread-quotient-residual','historical','lem:spread',HIST+'lem-spread','applies','overlap-spread-residual','Applies the dimension inequality to the historical spread data; does not assert every matching method fails.'),
('prop:matching-normalization','external','Razborov-1998-Theorem-3.1',RAZ,'depends_on','overlap-normalization','The transfer itself is explicit constant replay; its concluding residual degree lower bound uses the audited theorem.'),
('thm:one-cell-spread','current','prop:matching-normalization',None,'depends_on','overlap-removable-spread','NR supplies the concluding augmented-degree lower bound after the explicit favourable embedding.'),
('thm:one-cell-spread','historical','lem:spread',HIST+'lem-spread','cites','overlap-removable-spread','Reuses the graph-space construction but explicitly rebuilds the favourable embedding and checks disjointness.'),
('lem:normalization-affine-cut','current','prop:matching-normalization',None,'depends_on','resistant-counting','Uses the prior record dimension formula dim(J_tau/H0)=q(2n-q), before the affine slice and symmetry count.'),
('thm:spread-matching-avoidance','current','lem:normalization-affine-cut',None,'depends_on','resistant-existence','Applies RA to every matching and graph space, then sums the event probabilities.'),
('thm:spread-matching-avoidance','historical','lem:spread',HIST+'lem-spread','depends_on','resistant-existence','Starts with the historical n graph spaces and their common rank, then transports all by one invertible map.')]
added=[];incident={}
for source,namespace,target,locator,kind,anchor,scope in rows:
 key=source+'::'+kind+'::'+(namespace+':' if namespace!='current' else '')+target
 evidence=[WEB+anchor]+([RAZ] if namespace=='external' else [])
 edge={'id':key,'source':{'namespace':'current','id':source,'locator':None},'target':{'namespace':namespace,'id':target,'locator':locator},'type':kind,'scope':scope,'evidence':evidence,'review_status':'reviewed','review':{'revision':REV,'date':'2026-09-19','reviewer':'Codex GPT-6 Astra','note':'Resolved the exact local proof/application role and equation reference; reused the existing source audit, without a fresh primary-paper or kernel audit.'}}
 prior=next((e for e in data['relationships'] if e['id']==key),None)
 if prior:assert prior==edge
 else:data['relationships'].append(edge);added.append(key)
 incident.setdefault(source,[]).extend(evidence)
 if namespace=='current':incident.setdefault(target,[]).extend(evidence)
closed={
 'thm:matching-affine-annihilators':('overlap-matching-rigidity','Reviewed both inclusions and the exceptional rectangular restriction: matching products, historical affine rigidity and the audited rectangular degree bound are the direct imported inputs.'),
 'lem:spread-quotient-residual':('overlap-spread-residual','The abstract inequality has a self-contained kernel-injection proof. The subsequent PHP-spread application is recorded separately as applies edges, not prerequisites of that abstract inequality.'),
 'prop:matching-normalization':('overlap-normalization','Direct scalar substitution and proof replay are given locally. The stated degree conclusion imports the residual lower bound. Dimension/notation calculations are elementary, not hidden theorem calls.'),
 'thm:one-cell-spread':('overlap-removable-spread','Read the explicit graph embedding, coefficient assignment and disjointness check. Historical construction is cited; NR is the named input for the concluding degree bound. The static-score comparison is illustrative.'),
 'lem:normalization-affine-cut':('resistant-counting','Read the affine slice and uniform-invertible-map count. The earlier J_tau dimension is the sole indexed input; symmetry and the union bound are explicit elementary steps.'),
 'thm:spread-matching-avoidance':('resistant-existence','Read the union bound, exact matching count and asymptotic estimate. RA and the starting historical spread are the direct indexed inputs; no independence of events is assumed.')}
evidence=Evidence()
for label,targets in incident.items():
 c=claims[label];prior=c['reviews']['relationships']
 if label in closed:
  anchor,note=closed[label];targets=list(dict.fromkeys([WEB+anchor]+targets));state='reviewed';next_action=None
 else:
  targets=list(dict.fromkeys([e['target'] for e in prior['evidence']]+targets));note=prior['note']+' New incoming matching-group uses reviewed; prior outgoing disposition retained.';state=prior['state'];next_action=prior['next_action']
 c['reviews']['relationships']=make_review(data,c,'relationships',targets,revision=REV,date='2026-09-19',reviewer='Codex GPT-6 Astra',note=note,evidence=evidence,state=state,next_action=next_action)
report=json.loads((Path(__file__).parent/'candidates.json').read_text())
calibration=next(c for c in report['candidates'] if c['source']=='thm:spread-matching-avoidance' and c['method']=='equation_reference' and c['token']=='RA')
data=deps.record_decision(data,calibration,state='accepted',reason='The proof explicitly applies RA to all graph spaces and matchings; the bound is supplied by normalization-affine-cut.',reviewer='Codex GPT-6 Astra',date='2026-09-19',relation_id='thm:spread-matching-avoidance::depends_on::lem:normalization-affine-cut',evidence=evidence)
validate(data);write_json(REGISTRY,data);write_json(args.out,{'closed_reviews':list(closed),'added_edges':added,'accepted_equation_candidate':calibration['id'],'scope':'Direct source-relative dependencies and separately scoped applications; no new correctness or primary-source audit.'})
print(f'Closed {len(closed)} dependency reviews; added {len(added)} scoped edges.')
