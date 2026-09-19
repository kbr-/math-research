#!/usr/bin/env python3
"""Register the dated permutation audit without changing historical claim text."""
import copy,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'tools'))
from claim_registry import load,validate,write_json,REGISTRY,references
from claim_reviews import make_review,Evidence,FIELDS
data=load(); claims={c['id']:c for c in data['claims']}; ev=Evidence()
revision=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
URL='https://kbr.is-a.dev/math-research/#'
audit='audit:permutation-NA-source-error'; premise='imp:permutation-matrix-negative-association'; bound='lem:matched-pair-exponential-avoidance'
scope=URL+'permutation-audit-scope'
def review(c,field,targets,note,state='reviewed',next_action=None):
 c['reviews'][field]=make_review(data,c,field,targets,revision=revision,date='2026-09-19',reviewer='Codex coordinator, independent source-audit integration',note=note,state=state,next_action=next_action,evidence=ev)
def edge(a,b,kind,scope_text,targets):
 key=a+'::'+kind+'::'+b
 assert not any(e['id']==key for e in data['relationships']),key
 data['relationships'].append({'id':key,'source':{'namespace':'current','id':a,'locator':None},'target':{'namespace':'current','id':b,'locator':None},'type':kind,'evidence':targets,'review_status':'reviewed','scope':scope_text,'review':{'revision':revision,'date':'2026-09-19','reviewer':'Codex coordinator','note':'Independent exact counterexample and bounded direct-use source review; no automatic refutation of stronger conclusions.'}})
specs=[
 (audit,'The full permutation-matrix family is not negatively associated; the generic exponential matched-pair avoidance bound fails for every positive even matched size.',
 'Exact two-coordinate covariance and derangement counterexamples; source correction only, with no novelty claim.',
 'refutation',['permutation-NA-counterexample','matched-pair-avoidance-refutation','permutation-audit-scope'],'negative_result'),
 (premise,'Historical premise as used in the notebook: arbitrary disjoint row/column events of a uniform permutation matrix obey negative-association product bounds.',
 'Retracted by the dated two-coordinate counterexample. This records the notebook interpretation, not a verified assertion of the cited Joag-Dev–Proschan paper.',
 'retracted',['dense-labels-satisfied','permutation-NA-counterexample'],'context'),
 (bound,"Historical generic bound: conditional on fixed Q,R', every matched pair set P has avoidance probability at most exp(-|P|/(n-N)).",
 'Retracted: a reference perfect matching has derangement probability greater than exp(-1) at every positive even matched size, including valid random-flat parameters.',
 'retracted',['pinned-class-reduction','matched-pair-avoidance-refutation'],'context')]
for label,summary,assessment,status,anchors,category in specs:
 assert label not in claims,label
 targets=[URL+a for a in anchors]
 c={'id':label,'summary':summary,'assessment':assessment,'record':'; '.join(f'[Source {i+1}]({t})' for i,t in enumerate(targets)),
 'mathematical_status':status,'formalization':{'status':'not_started','scope':'No formalization was attempted or claimed in this source-audit cycle.','references':[URL+'permutation-audit-scope'],'artifacts':[]},
 'topics':['matching-php','query-models','method-obstructions'],
 'significance':{'category':category,'rationale':'Prevents reliance on an invalid probability premise and distinguishes a refuted generic bound from stronger unrefuted conclusions.','novelty':'not_claimed','publication_status':'not_applicable','references':targets,'next_action':None},'reviews':{}}
 data['claims'].append(c);claims[label]=c
 for field in FIELDS[:-1]:review(c,field,targets,'Exact dated audit and historical statement reviewed; no imported source theorem or formal verification inferred.')
edge(audit,premise,'corrects','Refutes the blanket matrix-event negative-association assertion as used in the notebook.',[URL+'permutation-NA-counterexample'])
edge(audit,bound,'corrects','Refutes the exact generic conditional avoidance inequality; does not refute stronger dense-label bounds.',[URL+'matched-pair-avoidance-refutation'])
edge(bound,premise,'depends_on','Historical proof uses the invalid permutation-matrix product bound; retained as dependency of a retracted claim.',[URL+'pinned-class-reduction'])
affected={label:row['anchor'] for row in json.load(open(ROOT/'research/results/parallel_index_negative_association_audit/affected-direct-claims.json')) for label in row['claim_ids']}
affected['lem:pair-space-round-bound']='pair-space-round-bound'
# The last source uses the H1 column-event product. Its final conclusion is not refuted.
for label,anchor in affected.items():
 c=claims[label];c['mathematical_status']='conditional'
 targets=[URL+anchor,scope]
 note='Recorded proof uses an unsupported permutation/injection event product. Final statement is not refuted; it may be relied on only after supplying a valid replacement estimate with its stated hypotheses and constants. Unaffected subclaims retain their separate scope.'
 review(c,'mathematical_status',targets,note)
 edge(audit,label,'corrects',note,targets)
 edge(label,premise,'depends_on','Direct recorded probability step invokes the refuted matrix-event premise; a proof-status warning, not endorsement of that premise.',targets)
c=claims['obs:pinned-wide-mass-barrier']
review(c,'mathematical_status',[URL+'wide-mass-pinned',scope],
 'Retains its obstruction/proposal status. The proposed conditional D1 repair also needs a replacement for the false matrix-event product, in addition to the already open concentration and alive-pin obligations.')
edge(audit,c['id'],'corrects','Qualifies the proposed D1 repair only: conditioning does not automatically justify permutation-matrix negative association. The stated barrier is not retracted.',[URL+'wide-mass-pinned',scope])
edge(c['id'],premise,'cites','The proposed repair refers to the now-refuted premise; it is a proposal, not a proved dependency.',[URL+'wide-mass-pinned',scope])
changed=set(affected)|{audit,premise,bound,c['id']}
for label in changed:
 c=claims[label]
 if label in {audit,premise,bound}:
  review(c,'relationships',[URL+'permutation-NA-counterexample',URL+'matched-pair-avoidance-refutation',scope], 'Complete source-relative audit inventory; corrections are scoped and invalid premises remain explicit.')
 else:
  # Merger completes the independently reviewed original inventory afterward.
  review(c,'relationships',[scope],'Audit edges recorded; original source dependency inventory must be merged with the completed worker proposal.',state='pending',next_action='Integrate and review the completed source-relative worker dependency proposal, preserving these audit edges.')
validate(data);write_json(REGISTRY,data)
write_json(Path(__file__).with_name('audit-registration.json'),{'revision':revision,'new_claims':[audit,premise,bound],'conditional_proof_status':sorted(affected),'qualified_proposal':'obs:pinned-wide-mass-barrier','historical_text_changed':False})
print('Registered 3 audit claims; qualified',len(affected),'direct proof uses and one proposed repair.')
