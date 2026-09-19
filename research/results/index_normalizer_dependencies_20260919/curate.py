#!/usr/bin/env python3
import argparse,importlib.util,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'tools'))
from claim_registry import load,validate,write_json,REGISTRY
from claim_reviews import make_review,Evidence
spec=importlib.util.spec_from_file_location('deps',ROOT/'tools/claim-dependencies.py');deps=importlib.util.module_from_spec(spec);spec.loader.exec_module(deps)
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);args=p.parse_args()
data=load();claims={c['id']:c for c in data['claims']};REV=subprocess.check_output(['git','rev-parse','9f9b33c'],cwd=ROOT,text=True).strip()
WEB='https://kbr.is-a.dev/math-research/#';GH='https://github.com/kbr-/math-research/blob/main/'
RAZ=GH+'research/notes/SOURCE_AUDIT.md#razborov-base-and-residual-pc-lower-bound'
rows=[
('ex:certified-resistant-spread','thm:spread-matching-avoidance','cites','resistant-finite-certificate','The existence probability is contextual; the saved matrix and separating vectors certify the finite example independently.'),
('ex:certified-resistant-spread','prop:matching-normalization','applies','resistant-finite-certificate','The affine functionals negate the stated scalar-span normalization criterion, not all possible normalizers.'),
('cor:normalization-ns','thm:polynomial-normalization','cites','polynorm-ns','Uses the same substitution and original companion-degree setup; its cofactor proof does not invoke the PC transfer conclusion.'),
('thm:collision-pair-elimination','thm:polynomial-normalization','depends_on','polynorm-collision-pairs','PN supplies the PC transfer using the explicit degree-two error certificate.'),
('thm:collision-pair-elimination','cor:normalization-ns','depends_on','polynorm-collision-pairs','PN-NS supplies the NS transfer with original-degree cofactor charges.'),
('prop:collision-pair-matching-obstruction','thm:collision-pair-elimination','cites','polynorm-matching-obstruction','Uses the row-difference tuple definition and contrasts methods; the near-matching countermodel is proved directly.'),
('cor:normalization-extra-inputs','thm:collision-pair-elimination','depends_on','polynorm-extra-inputs','Reuses the exact H_ab base identity, coefficient assignment and original-degree transfer.'),
('cor:normalization-extra-inputs','prop:collision-pair-matching-obstruction','applies','polynorm-extra-inputs','The supplemental enriched family reuses the near-matching assignment to preserve failure of constant normalization.'),
('ex:spread-affine-normalizer-obstruction','ex:certified-resistant-spread','cites','polynorm-spread-checks','Input dataset provenance: the same seven stored rank-24 spaces, not reliance on their single-cell obstruction conclusion.'),
('ex:spread-affine-normalizer-obstruction','thm:collision-pair-elimination','applies','polynorm-spread-checks','The supplemental positive controls test CP-H and its pair spaces; they are separate from the seven negative dual certificates.'),
('ex:spread-affine-normalizer-obstruction','cor:normalization-extra-inputs','applies','polynorm-spread-checks','Supplemental coefficient checks include the extra-column-form companion identities.'),
('prop:direct-companion-substitution','thm:polynomial-normalization','refines','annihilation-transfer','In the binary affine-input specialization, replaces a cheap factor certificate by supplied degree-three companion-product proofs; not a generalization of every PN parameter.'),
('lem:companion-linear-feasibility','prop:direct-companion-substitution','cites','annihilation-feasibility','Identifies the companion conditions whose feasibility is tested; the equivalence and dual separation are proved locally.'),
('ex:php7-degree-three-pc-space','ex:spread-affine-normalizer-obstruction','depends_on','annihilation-pc-space','The equality of the lower-degree part with C2 uses the earlier certified degree-two base space reported in that record, not its spread obstruction conclusion.'),
('ex:spread-three-input-annihilators','ex:php7-degree-three-pc-space','depends_on','annihilation-three-inputs','The certified quotient spaces and C3-intersect-P2=C2 identify the rank kernel with the stated old-consequence assertion.'),
('ex:spread-three-input-annihilators','ex:spread-affine-normalizer-obstruction','depends_on','annihilation-three-inputs','For the two-input control, the earlier normalizer obstruction proves the displayed kernel generator is nonzero modulo C2.'),
('ex:spread-three-input-annihilators','ex:certified-resistant-spread','cites','annihilation-three-inputs','The stored input order defines the seven triples and the one-/two-input controls.'),
('ex:spread-three-input-annihilators','lem:companion-linear-feasibility','applies','annihilation-three-inputs','CAF interprets injective multiplication as reducing the relaxed factor test; the ranks themselves come from exact certificates.'),
('ex:spread-companion-substitution-obstruction','ex:spread-three-input-annihilators','depends_on','annihilation-spread-obstruction','QA-7 is the first input of the stated deduction from a hypothetical companion solution.'),
('ex:spread-companion-substitution-obstruction','ex:php7-degree-three-pc-space','depends_on','annihilation-spread-obstruction','C3-7 identifies the derived quadratic factor class with the degree-two base space.'),
('ex:spread-companion-substitution-obstruction','ex:spread-affine-normalizer-obstruction','depends_on','annihilation-spread-obstruction','The prior degree-two normalizer obstruction contradicts that factor certificate.'),
('ex:spread-companion-substitution-obstruction','lem:companion-linear-feasibility','depends_on','annihilation-spread-obstruction','CAD explains why the separately saved and directly checked functional tuples certify inconsistency.')]
added=[];incident={}
def put(source,namespace,target,locator,kind,anchor,scope):
 key=source+'::'+kind+'::'+(namespace+':' if namespace!='current' else '')+target
 edge={'id':key,'source':{'namespace':'current','id':source,'locator':None},'target':{'namespace':namespace,'id':target,'locator':locator},'type':kind,'scope':scope,'evidence':[WEB+anchor],'review_status':'reviewed','review':{'revision':REV,'date':'2026-09-19','reviewer':'Codex GPT-6 Astra','note':'Resolved local proof role and recorded certificate provenance; no new numerical run, kernel replay or primary-source audit.'}}
 prior=next((e for e in data['relationships'] if e['id']==key),None)
 if prior:assert prior==edge
 else:data['relationships'].append(edge);added.append(key)
 incident.setdefault(source,[]).append(WEB+anchor)
 if namespace=='current':incident.setdefault(target,[]).append(WEB+anchor)
for source,target,kind,anchor,scope in rows:put(source,'current',target,None,kind,anchor,scope)
for target,slug,scope in [
 ('lem:reuse','lem-reuse','Multiplies the completed H_a polynomial without multiplying its entire derivation.'),
 ('lem:fieldreduction','lem-fieldreduction','Supplies an ordinary old-domain certificate for beta^p-beta within pT.'),
 ('lem:substitution','lem-substitution','Replays each source PC inference under the degree-T polynomial substitution.')]:
 put('thm:polynomial-normalization','historical',target,GH+'php_codex_handoff/manuscript/chapters/01_foundations.md#'+slug,'depends_on','polynorm-transfer',scope)
put('cor:normalization-ns','historical','lem:fieldreduction',GH+'php_codex_handoff/manuscript/chapters/01_foundations.md#lem-fieldreduction','depends_on','polynorm-ns','The used coefficient field equations require their explicit old-domain identities, charged at pT.')
put('thm:collision-pair-elimination','external','Razborov-1998-Theorem-3.1',RAZ,'depends_on','polynorm-collision-pairs','The final degree lower bound applies the already-audited weak-base PC consequence of the source theorem.')
closed={
 'ex:certified-resistant-spread':('resistant-finite-certificate','Finite evidence consists of the saved input matrix and 392 direct separating-vector checks. RU is a separate existence explanation, not necessary for that certification.'),
 'thm:polynomial-normalization':('polynorm-transfer','The proof explicitly invokes historical reuse, field reduction and substitution; supplied H_a derivations are hypotheses, not automatically extracted witnesses.'),
 'cor:normalization-ns':('polynorm-ns','Cofactor substitution is proved explicitly with original companion degrees; the historical field reduction supplies the field-axiom image. The PC transfer conclusion is not used.'),
 'thm:collision-pair-elimination':('polynorm-collision-pairs','The explicit CP-H identity satisfies PN and PN-NS; the displayed refutation lower bound imports the audited Razborov result.'),
 'prop:collision-pair-matching-obstruction':('polynorm-matching-obstruction','The near-matching assignment directly falsifies the normalization premise. Existing obstructs edge and the family-definition citation describe its role; the assignment is not a PHP model.'),
 'cor:normalization-extra-inputs':('polynorm-extra-inputs','The pair certificate and degree inequality prove transfer with extras. The additional affine example applies the earlier near-matching control.'),
 'ex:spread-affine-normalizer-obstruction':('polynorm-spread-checks','The recorded degree-two space and direct dual checks certify the core obstruction. Stored spread data is provenance; polynomial-normalizer identities provide supplemental positive controls.'),
 'prop:direct-companion-substitution':('annihilation-transfer','The binary affine substitution and all image-degree checks are given locally. Its relation to PN is a scoped refinement, not reliance on a cheap H proof.'),
 'lem:companion-linear-feasibility':('annihilation-feasibility','The affine image-space equivalence and finite-dimensional separation are self-contained. The direct companion criterion specifies the conditions being tested, not a logical prerequisite.'),
 'ex:php7-degree-three-pc-space':('annihilation-pc-space','Saved derivation replay and all closure products certify C3; the earlier degree-two base calculation identifies its lower-degree slice. No new replay was performed.'),
 'ex:spread-three-input-annihilators':('annihilation-three-inputs','Read the quotient/rank certificate interpretation and the local two-input identity; the nonzero control class uses the preceding normalization obstruction.'),
 'ex:spread-companion-substitution-obstruction':('annihilation-spread-obstruction','Reviewed the QA-7/C3-7 deduction and the independent CAD dual certificate argument, with exact finite scope.')}
evidence=Evidence()
for label,targets in incident.items():
 c=claims[label];prior=c['reviews']['relationships']
 if label in closed:
  anchor,note=closed[label];targets=list(dict.fromkeys([WEB+anchor]+targets));state='reviewed';next_action=None
 else:
  targets=list(dict.fromkeys([e['target'] for e in prior['evidence']]+targets));note=prior['note']+' New incoming normalizer-cluster roles reviewed.';state=prior['state'];next_action=prior['next_action']
 if label=='ex:spread-three-input-annihilators':targets.append(WEB+'annihilation-two-input-control')
 if label in ('thm:polynomial-normalization','cor:normalization-ns'):targets.append(WEB+'entry-2026-09-14-bounded-companion-degree-audit')
 c['reviews']['relationships']=make_review(data,c,'relationships',targets,revision=REV,date='2026-09-19',reviewer='Codex GPT-6 Astra',note=note,evidence=evidence,state=state,next_action=next_action)
report=json.loads((ROOT/'research/results/index_dependency_review_20260919/candidates.json').read_text())
accepted=[]
for token,target in [('QA-7','ex:spread-three-input-annihilators'),('C3-7','ex:php7-degree-three-pc-space'),('CAD','lem:companion-linear-feasibility')]:
 candidate=next(c for c in report['candidates'] if c['source']=='ex:spread-companion-substitution-obstruction' and c['method']=='equation_reference' and c['token']==token)
 data=deps.record_decision(data,candidate,state='accepted',reason='Exact source argument uses '+token+' in the reviewed finite obstruction proof.',reviewer='Codex GPT-6 Astra',date='2026-09-19',relation_id='ex:spread-companion-substitution-obstruction::depends_on::'+target,evidence=evidence);accepted.append(candidate['id'])
validate(data);write_json(REGISTRY,data);write_json(args.out,{'closed_reviews':list(closed),'added_edges':added,'accepted_equation_candidates':accepted,'scope':'Source-relative mathematical dependencies and recorded evidence, not new certificate verification.'})
print(f'Closed {len(closed)} dependency reviews; added {len(added)} scoped edges; accepted {len(accepted)} equation candidates.')
