#!/usr/bin/env python3
"""Curate replay, ideal-cover and column-profile metadata from compact evidence."""
import argparse,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'tools'))
from claim_registry import load,validate,write_json,REGISTRY
from claim_reviews import make_review,Evidence
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);args=p.parse_args()
data=load();claims={c['id']:c for c in data['claims']};packets=json.loads((Path(__file__).parent/'packets.json').read_text())['packets']
REV=subprocess.check_output(['git','rev-parse','b1948e9'],cwd=ROOT,text=True).strip()
for key,title,description in [
 ('moment-designs','Moment designs','Truncated moments, annihilating functionals, covariance and design extension.'),
 ('query-models','Query models','Conflict/query trees, query description bounds and survival probabilities.'),
 ('pseudorandomness','Pseudorandomness','Small-bias generators, polynomial sampling and character bounds.'),
 ('topological-methods','Topological methods','Matching/chessboard complexes and homological extension inputs.')]:
 if not any(t['id']==key for t in data['topic_definitions']):data['topic_definitions'].append(dict(id=key,title=title,description=description))
# Topic groups reflect the reviewed objects, not current route membership.
groups={'C':['ens','frege-simulation','polynomial-calculus'],
        'N':['ens','frege-simulation','nullstellensatz','degree-accounting'],
        'A':['ens','affine-linear-algebra','degree-accounting'],
        'F':['ens','finite-certificates'],
        'B':['ens','method-obstructions','nullstellensatz'],
        'P':['ens','matching-php','polynomial-calculus'],
        'D':['moment-designs','matching-php','polynomial-calculus'],
        'Q':['ens','moment-designs','query-models'],
        'R':['query-models','pseudorandomness','degree-accounting'],
        'H':['moment-designs','matching-php','topological-methods']}
# Group, significance category, scope-sensitive rationale, in source packet order.
specs=[
('P','general_tool','Exact negative-literal matching survival count includes dependence between cells; finite equalities are controls.'),
('P','route_specific','Polynomial literal collections admit global restriction coverage, but arbitrary MOD inputs and multilevel iteration remain open.'),
('P','general_tool','Functional-base affine rigidity extends the historical result using the stronger-base residual bound.'),
('A','general_tool','Residual rank resistance refines the earlier template and preserves pairwise conditions on all specified matchings.'),
('A','negative_result','The affine core criterion can be expensive on every square-root residual; no proof-essentiality or augmented refutation is asserted.'),
('Q','general_tool','Weighted ENS conflict extraction preserves active degrees and fallback inputs while sharpening the sufficient rate.'),
('Q','negative_result','The diagonal source parameters do not directly meet the extracted sufficient inequality; the source open problem is not refuted.'),
('Q','general_tool','Imported conflict-to-live-cell conversion retains the source-degree and residual-design conditions.'),
('Q','general_tool','Row-sum queries locate a free column only, not a free row or a live cell.'),
('Q','general_tool','The binary covariance probe gives a necessary survival test without positivity assumptions.'),
('D','general_tool','The uniform quadratic design law is a full affine-space statement, not an expectation inferred from samples.'),
('D','general_tool','Distinct-map counting is valid with the stated small exceptional mass and full quadratic marginal.'),
('H','general_tool','Homological vanishing is a sufficient design-extension input; its source-range audit is recorded separately.'),
('F','route_specific','Exact finite marginal dimensions and sample ranks are distinct kinds of evidence.'),
('H','general_tool','Audited chessboard connectivity supplies the stated quadratic-design extension range.'),
('Q','negative_result','The uniform residual candidate fails the specified sufficient rate; nonuniform designs and weaker questions are not excluded.'),
('D','general_tool','The explicit low-covariance design extends in the stated range but provides no query-survival guarantee.'),
('Q','general_tool','The design-valued attack refines an attributed earlier pointwise near-permutation search; no claim of independent invention of that mechanism.'),
('D','general_tool','Moment-rank growth uses an explicitly attributed flat-extension technique and concerns polynomial covariance, not just variables.'),
('Q','general_tool','Full-polynomial probes require degree 2t within the design budget and permit arbitrary query descriptions.'),
('Q','independent_result','Potential independent obstruction to the unrestricted ENS sufficient probability rate; not an ENS upper bound or Frege separation.'),
('F','route_specific','Complete finite moment extensions and rank traces test the prototype and satisfiable flatness controls.'),
('Q','general_tool','The exact source query inventory does not by itself rule out a covariance attack.'),
('C','general_tool','Compact cofactor circuits refine the simulation representation without promising monomial sparsity or constant arithmetic depth.'),
('Q','route_specific','The conditional circuit criterion is valid, but its coarse-budget survival premise is defeated by the later compact attack.'),
('R','general_tool','Finite-field trace coefficients give bounded bias with an explicit degree-preserving circuit recurrence.'),
('R','general_tool','Small coefficient bias yields a weighted covariance probe with explicit errors and ordinary-degree accounting.'),
('Q','negative_result','The compact attack defeats the recorded coarse circuit budget; no arithmetic-depth or Frege upper bound follows.'),
('F','route_specific','Exact small-field character and evaluation checks include a failed fixed-trace control, not PHP design samples.'),
('C','general_tool','Shallow cofactor formulas refine the same source certificate with unbounded fan-in and polylogarithmic ordinary degree.'),
('R','general_tool','Least-degree contraction uses Boolean reduction essentially; its bias statement is not a raw-power identity.'),
('R','general_tool','Degree mixture gives shallow biased polynomial generators while actual query formulas retain ordinary degree bounds.'),
('Q','independent_result','Potential independent shallow-query obstruction strengthens the rate attack to depth four; it is not a Frege upper or lower bound.'),
('F','route_specific','Exact degree-mixture tests include fixed-degree and non-Boolean controls, not design sampling.'),
('H','general_tool','Functional-PHP filtration stability follows in the audited board range; it does not assert stability of augmented ENS systems.'),
('C','general_tool','Common-vanishing learning is simultaneous but pays the stated target degree/working degree ledger over the binary base.'),
('P','general_tool','Dimension exclusion is a finite-parameter sufficient criterion with explicit consequence-space and board bounds.'),
('P','route_specific','High-rank affine families are covered in the stated regime; intermediate ranks and multilevel sources remain open.'),
('F','route_specific','Exact parameter counts separate dimension and board failures without constructing large affine families.'),
('A','general_tool','A multiscale inventory refines rank resistance across all usable residual sizes, with no actual source occurrence claim.'),
('A','negative_result','Choosing a residual size cannot repair the two recorded numerical criteria; richer transformations are not excluded.'),
('F','route_specific','Exact board/degree audits verify a criterion gap and failed-range control, not concrete matrix certificates.'),
('A','general_tool','Common-kernel bases require joint independence; pairwise independence alone is insufficient.'),
('A','general_tool','The full-stack resistant construction preserves joint independence on residual boards without proving essential proof occurrence.'),
('A','negative_result','The Boolean/row common-vanishing interface has a degree gap; full quadratic PHP membership remains separate.'),
('F','route_specific','Exact kernels, bases and union-bound checks include a pairwise-only countercontrol.'),
('C','general_tool','Full-base relative learning keeps certificate degree c separate from actual target degree s.'),
('P','route_specific','The relative quadratic interface requires a nonzero shared class outside the base ideal; no rank condition supplies it automatically.'),
('F','negative_result','The zero relative kernel in one random fixture is a finite method obstruction with a positive clause-span control.'),
('D','general_tool','First-band pair duality specializes a sufficient mixed system; it does not characterize every joint design.'),
('D','general_tool','Pair-separated transfer covers the stated binary degree band and NS inputs, not arbitrary augmented PC proofs.'),
('N','general_tool','Certificate-specific surviving pair support can suffice without universal pair separation, retaining original cofactor budgets.'),
('F','route_specific','Finite pair-separated applications verify hypotheses while clause controls violate separation.'),
('A','general_tool','Faithful affine pair kernels classify distinct/equal spans under explicit base faithfulness, including redundancy.'),
('D','general_tool','Equal-span singleton coordinates can be chosen coherently; arbitrary independent choices need not match.'),
('D','general_tool','Faithful-pair transfer has no count charge at the first boundary and may mix separated pairs.'),
('N','route_specific','The source-cofactor corollary still needs actual affine reduction of extracted arrays beyond the first boundary.'),
('F','route_specific','A finite translated family defeats simple common-kernel methods but satisfies the faithful-pair NS criterion; no augmented PC claim.'),
('F','route_specific','Exact pair/coherence controls distinguish redundant representation from old relations and mismatched scalar choices.'),
('A','general_tool','The rectangle kernel provides a sufficient quadratic faithfulness test, without a converse.'),
('A','general_tool','Localization controls the quadratic relation Hessian only, with the stated deletion-rank consequence.'),
('A','route_specific','The algebraic antecedent theorem remains valid, but its proposed original level-one theorem-boundary application is vacuous.'),
('F','route_specific','Deletion and rectangle checks certify coefficient geometry, not a new full moment array or NS quotient.'),
('C','general_tool','Affine row-input replacement is a special certified bridge, not general reduction modulo all PHP consequences.'),
('P','route_specific','Common-star restriction gives family-wide NS exclusion under shared-support and residual-faithfulness hypotheses.'),
('F','route_specific','A mixed-column finite family verifies the covering restriction and wrong-column control; no augmented PC claim.'),
('N','general_tool','Exact MP diagonal extraction remains valid for formal inputs; its nonzero controls are not original theorem boundaries.'),
('N','negative_result','The supplied MP construction has higher-degree/support terms; this is not an optimality bound on all certificates.'),
('F','route_specific','Finite polynomial fixtures verify extraction and omission controls without forming a completed PHP/Frege certificate.'),
('C','route_specific','Binary affine exactness and scalar cleanup remove semantically constant original boundaries, including proper constant copies.'),
('C','context','The dated scope audit corrects the proposed source application while retaining the conditional algebra and finite checks.'),
('C','context','Proper affine-subspace indicators remain after theorem-boundary cleanup; this does not prove essential support.'),
('C','route_specific','Existing binary domain/span identities simplify source companions while leaving residual ranks above packing.'),
('N','general_tool','Collected proper-OR cofactor extraction concerns the specified certificate, not every global representation.'),
('N','general_tool','The restricted degree-six theorem combines an explicit upper certificate, certified finite separation and a restriction argument; no PHP-base conclusion.'),
('F','route_specific','Finite support and separation certificates retain the distinction between the sharp h=1 case and h=2 upper bound.'),
('C','route_specific','A shallow parity theorem realizes a large proper comparison registry after specified cleanup, with a selector-valued target.'),
('N','general_tool','The collected grid formula isolates nonzero coefficients in this certificate, not all alternatives.'),
('A','general_tool','The elementary separator bound is for the specified weighted graph; source height does not force a small separator there.'),
('C','negative_result','Every block is necessary for the displayed fixed target, but extra axioms and target-changing transformations are outside scope.')]
assert len(specs)==len(packets)==80
conditional={292,304,327}
finite={293,301,308,313,318,321,325,328,332,337,338,342,345,348,355}
refuted=set();context={286,350,351};evidence=Evidence();rows=[]
edge_specs=[
 ('audit:recent-MP-retained-source-scope','thm:one-affine-antecedent-faithfulness','corrects','recent-MP-source-application-scope','Corrects only the proposed original level-one theorem-boundary application; the conditional algebraic theorem remains valid.'),
 ('audit:recent-MP-retained-source-scope','prop:source-MP-mixed-antecedent','corrects','recent-MP-source-application-scope','Nonzero affine controls do not represent original level-one theorem boundaries; the formal extraction identity is retained.'),
 ('thm:succinct-ENS-rate-obstruction','cor:circuit-restricted-source-query-criterion','obstructs','succinct-ENS-rate-obstruction','Defeats the required survival premise at its coarse circuit budget, not the valid conditional implication.'),
 ('thm:depth-four-ENS-query-obstruction','thm:succinct-ENS-rate-obstruction','refines','shallow-ENS-query-obstruction','Strengthens the same rate obstruction to the stated shallow formula description class.')]
for source,target,kind,anchor,scope in edge_specs:
 key=source+'::'+kind+'::'+target
 edge={'id':key,'source':{'namespace':'current','id':source,'locator':None},'target':{'namespace':'current','id':target,'locator':None},'type':kind,'scope':scope,'evidence':['https://kbr.is-a.dev/math-research/#'+anchor],'review_status':'reviewed','review':{'revision':REV,'date':'2026-09-19','reviewer':'Codex GPT-6 Astra','note':'Recorded source scope and later correction/refinement reviewed; no new correctness audit.'}}
 prior=next((e for e in data['relationships'] if e['id']==key),None)
 if prior:assert prior==edge
 else:data['relationships'].append(edge)
for position,(packet,(group,category,rationale)) in enumerate(zip(packets,specs),280):
 c=claims[packet['id']];assert c['summary']==packet['summary'] and c['assessment']==packet['assessment']
 c['mathematical_status']='conditional' if position in conditional else 'finite_check' if position in finite else 'refutation' if position in refuted else 'context' if position in context else 'established' if position==287 else 'working_proof'
 c['topics']=list(groups[group])
 if category=='negative_result' and 'method-obstructions' not in c['topics']:c['topics'].append('method-obstructions')
 targets=list(dict.fromkeys(p['target'] for p in packet['passages']));assert targets
 c['significance']={'category':category,'rationale':rationale,'novelty':'known' if position==287 else 'not_claimed','publication_status':'not_applicable','references':targets,'next_action':None}
 if category=='independent_result':
  c['significance']['novelty']='unknown'
  c['significance']['publication_status']='candidate'
  c['significance']['next_action']='Audit the exact statement and compare the model, field and degree convention against primary literature before claiming independent novelty or publication readiness.'
 for field in ('mathematical_status','topics','significance'):
  c['reviews'][field]=make_review(data,c,field,targets,revision=REV,date='2026-09-19',reviewer='Codex GPT-6 Astra',evidence=evidence,
    note='Recorded assessment and compact source qualifications reviewed; original wording, corrections and restricted scopes retained. No new proof or novelty verification.',
    state='pending' if field=='significance' and category=='independent_result' else 'reviewed',
    next_action=c['significance']['next_action'] if field=='significance' and category=='independent_result' else None)
 c['reviews']['relationships']=make_review(data,c,'relationships',targets,revision=REV,date='2026-09-19',reviewer='Codex GPT-6 Astra',evidence=evidence,state='pending',
    note='Source regions inventoried, but direct equation/setup dependencies, earlier repairs and optional uses still need a complete ownership review.',
    next_action='Map direct prerequisites and correction/refinement links in '+', '.join('#'+p['target'].split('#')[-1] for p in packet['passages'])+'; separate the claimed result from shared-region proofs and finite controls.')
 rows.append({'id':c['id'],'status':c['mathematical_status'],'topics':c['topics'],'significance':category})
validate(data);write_json(REGISTRY,data);write_json(args.out,{'baseline':REV,'claims':rows,'relationship_reviews':'80 pending, not complete','scope':'Compact-evidence classifications with four explicit scoped correction/refinement edges; no new mathematics.'})
print('Curated 80 status/topic records and 78 significance dispositions; two novelty audits, four scoped edges, 80 pending dependency inventories.')
