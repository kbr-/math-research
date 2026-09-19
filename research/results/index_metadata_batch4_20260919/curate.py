#!/usr/bin/env python3
"""Curate replay, ideal-cover and column-profile metadata from compact evidence."""
import argparse,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'tools'))
from claim_registry import load,validate,write_json,REGISTRY
from claim_reviews import make_review,Evidence
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);args=p.parse_args()
data=load();claims={c['id']:c for c in data['claims']};packets=json.loads((Path(__file__).parent/'packets.json').read_text())['packets']
REV=subprocess.check_output(['git','rev-parse','2eed4da'],cwd=ROOT,text=True).strip()
# Topic groups reflect the reviewed objects, not current route membership.
groups={'C':['ens','frege-simulation','polynomial-calculus'],
        'N':['ens','frege-simulation','nullstellensatz','degree-accounting'],
        'A':['ens','affine-linear-algebra','degree-accounting'],
        'F':['ens','finite-certificates'],
        'B':['ens','method-obstructions','nullstellensatz'],
        'P':['ens','matching-php','polynomial-calculus']}
# Group, significance category, scope-sensitive rationale, in source packet order.
specs=[
('C','route_specific','Private constant propagation composes known modes without closing residual source coverage.'),
('F','route_specific','Exact alternating cascades test goal-relative cuts and their inverse controls on twelve chains.'),
('C','general_tool','A proved nonzero input permits coefficient removal with its exact polynomial image retained, not collapsed semantically.'),
('C','route_specific','Opposite-signed goal matches supply a bounded witness within the private-ancestor schedule.'),
('F','negative_result','Finite traces and models show that a product vanishing under a goal may still have a nonconstant polynomial image.'),
('C','route_specific','Only the specified MOD residue/sign cases yield the stated aggregate normalizers and accuracy budget.'),
('N','general_tool','Selector Booleanity is domain-only, while the alternative linear normalizer need not be Boolean away from the goal.'),
('C','negative_result','All-accuracy controls exclude the aggregate-only rule for the other residue/sign cases.'),
('A','negative_result','The constant-coefficient accuracy bound uses a free Boolean base; extra constraints and polynomial coefficients are excluded.'),
('N','general_tool','A compatible choice of exact polynomial images preserves sharp Booleanity without retaining discarded goals.'),
('N','general_tool','Level-support refinement applies within the specified portfolio, not arbitrary earlier-zero witnesses.'),
('C','route_specific','Existing rank and equal-span passes give a post-goal normal form; they do not establish that all remaining spans are cheap.'),
('B','negative_result','A pebbling-based image separates PC and NS witness cost on a consistent generic base, not PHP.'),
('C','general_tool','Small-probe normalization extracts and realizes a selector only under supplied refutation and image-witness conditions.'),
('A','general_tool','Affine pairing gives a sufficient row count and retains nonzero field-image costs.'),
('B','negative_result','The antichain violation cube obstructs constant rows and probe factors, not arbitrary affine rows or PHP-specific methods.'),
('F','route_specific','Exact replay exercises sharp row counts and an actually nonzero coefficient field image.'),
('C','general_tool','Unit/annihilator OR relations require literal coordinate alignment and one common retained system.'),
('C','general_tool','A supplied input refutation gives a virtual zero parent through weighted replay; source recompilation is separate.'),
('F','route_specific','Finite pebbling interface traces contrast virtual witnesses with the constrained normalizer row count.'),
('C','general_tool','Copy agreement uses completed equality and unit/annihilator witnesses rather than multiplying whole derivations.'),
('C','general_tool','Depth-independent copy induction is conditional on aligned values and a single retained-system interface.'),
('F','route_specific','Finite copy traces demonstrate final-line reuse and include missing-witness controls.'),
('C','general_tool','The virtual interface yields PC Booleanity; it does not assert a sharp NS certificate.'),
('C','general_tool','Sharper gate accounting includes singleton non-OR children with their actual input degrees.'),
('C','general_tool','Fixed Boolean frame compilation uses supplied PC interfaces; MOD-specific schemas require a separate argument.'),
('C','general_tool','MP shares a common ceiling while retained interfaces are supplied; no new elimination mechanism is asserted.'),
('C','general_tool','MOD interpolation after copy alignment accounts for changed representatives without a prefix-arity factor.'),
('C','general_tool','The ten-leaf recursion compiler is conditional on supplied interfaces, not a constructed packing assignment.'),
('C','route_specific','The combined schema-value compiler still leaves strict support and retained-family selection open.'),
('C','general_tool','Strict leaf witnesses require level-confined interfaces and the prescribed unsimplified axiom expansion.'),
('C','route_specific','The pure-disjunct application uses the earlier unit witness without requesting an unrelated same-level root.'),
('C','negative_result','Freshness alone cannot delete all same-level peers; the control uses exponential inventory outside polynomial source claims.'),
('C','route_specific','Level-ordered virtual axiom values preserve original structural bounds and rebuild the remaining genuine inputs.'),
('C','route_specific','The recurrence quantifies the recorded interface construction; its endpoint is supplied separately.'),
('N','general_tool','Sharp NS Booleanity follows for the stated constant/genuine values even though unit witnesses remain PC.'),
('P','route_specific','The rebuilt source reaches the exact weak-PHP endpoint with specialized retained inputs, not a general elimination bound.'),
('P','route_specific','Existing span and rank normal forms apply to the new endpoint but leave wide residual inputs.'),
('C','context','Two degree/level advantages belong to different source families and cannot be combined without proof.'),
('A','general_tool','The affine-bin refinement counts actual affine basis members while preserving original image budgets.'),
('A','route_specific','Merging equal spans before packing can expose additional affine directions; survivors still require coverage.'),
('A','negative_result','Boolean-degree controls delimit specific affine normalizers, not a universal optimality frontier.'),
('F','route_specific','Exact mixed-bin certificates include full lifted models and non-Boolean failure controls.'),
('P','general_tool','One-cell-per-row projection preserves complete refutations only when every retained input and base image is transformed.'),
('A','general_tool','Pivot invariance concerns the row quotient, not reduction modulo the full inconsistent PHP ideal.'),
('A','route_specific','Balanced pivots optimize the stated collision-generator term count, not arbitrary ENS-input sparsity.'),
('F','negative_result','Finite row-subsystem evidence distinguishes old consequence degree from the degree of a newly projected axiom.'),
('P','general_tool','Column state interpolation normalizes arbitrary polynomial inputs with original-degree certificates, without a rank or Boolean-input assumption.'),
('P','route_specific','Column subsets and groups give sufficient coverage rules; general mixed-support coverage remains open.'),
('P','general_tool','A degree-preserving column algebra section keeps the normalizers compatible with row coordinates.'),
('F','route_specific','Exact column-state certificates cover nonlinear/non-Boolean inputs and omitted-collision controls.'),
('P','general_tool','Uniform degree-two affine rigidity extends earlier finite checks with the explicit board and free-variable hypotheses.'),
('P','independent_result','Potentially independently useful classification of affine degree-two Boolean values modulo rows in odd characteristic; source and novelty need targeted review.'),
('A','general_tool','The full affine intersection strengthens the binary basis pass without changing its proof degree.'),
('F','route_specific','Exhaustive slices support the classification but are explicitly not a complete board-wide enumeration.'),
('C','general_tool','Stable-ideal input replacement preserves original targets and coefficient variables through certified old companion images.'),
('N','general_tool','Sharp reduced-input Booleanity is characteristic-dependent; the binary argument does not extend automatically to odd primes.'),
('B','independent_result','Potentially independent exact PC-versus-NS Booleanity-degree gap for one monomial block over an odd-field domain base; full PHP excluded here.'),
('F','route_specific','Exact replacement and gap fixtures preserve nonzero targets and provide lower-bound controls.'),
('P','independent_result','Potentially independent full-weak-PHP lift of an exact one-block Booleanity-degree gap under a sufficient board bound; arbitrary added families excluded.'),
('P','route_specific','The logarithmic-accuracy parameter corollary has a sufficient, not necessary, board threshold.'),
('N','general_tool','Nonsharp witness ledgers keep NS cofactor costs distinct from PC final-line reuse under the same map.'),
('N','general_tool','Surplus ordering minimizes the displayed telescoping ledger, not every possible certificate.'),
('C','general_tool','A common PC Booleanity ceiling supports reduction, packing and sharing without assuming sharp NS Booleanity.'),
('P','route_specific','The reduced source endpoint retains degree and family bounds but leaves wide residual coverage uncontrolled.'),
('N','route_specific','Exact upper-block thresholds apply to the specified assignment and distinguish NS from PC image budgets.'),
('C','general_tool','Uniform-PC ideal cover still requires supplied degree-controlled decompositions and witnesses.'),
('N','general_tool','Vanishing stable normal forms certify the specified affine companion images; the proper ideal and original budgets matter.'),
('A','general_tool','Shared linear feasibility generalizes the earlier companion criterion to arbitrary input degree and prime fields.'),
('N','general_tool','A high-rank quadratic cover with no common factor improves a particular coarse ledger, not every normalizer cost.'),
('A','negative_result','Proper-ideal factor bounds differ from full PHP, where row equations can allow accuracy one.'),
('F','route_specific','Exact primal/dual examples distinguish one-row feasibility from multirow and row-equation methods.'),
('A','general_tool','An integer two-row normalizer for three independent differences has original-degree certificates in every characteristic.'),
('A','independent_result','Potentially independent exact coefficient-degree/row-count frontier over a proper column ideal; additional PHP equations are excluded.'),
('F','route_specific','Finite rational search and modular certificates support the explicit triple construction; search attempts alone are not proof.'),
('A','independent_result','Potentially independent exact heterogeneous-alphabet frontier with matching lower and upper bounds in the encoded independent-profile model.'),
('A','general_tool','Encoding-cost comparison separates categorical state indicators from native scalar coordinates with explicit alphabet assumptions.'),
('A','negative_result','The vector-profile counterexample shows that selector degree cannot replace scalar alphabet cost in the stated factor rule.'),
('P','route_specific','A fully covered pigeon row defeats proper-profile lower bounds via an actual PHP row equation; partial cover remains separate.'),
('F','route_specific','Finite higher-alphabet image certificates verify budgets and complete states for the specified F5 cases.')]
assert len(specs)==len(packets)==80
conditional={153,161,165,168,169,170}
finite={141,144,156,159,162,182,186,190,194,198,211,214,219}
refuted={147,217};context={178};evidence=Evidence();rows=[]
for position,(packet,(group,category,rationale)) in enumerate(zip(packets,specs),140):
 c=claims[packet['id']];assert c['summary']==packet['summary'] and c['assessment']==packet['assessment']
 c['mathematical_status']='conditional' if position in conditional else 'finite_check' if position in finite else 'refutation' if position in refuted else 'context' if position in context else 'working_proof'
 c['topics']=list(groups[group])
 if category=='negative_result' and 'method-obstructions' not in c['topics']:c['topics'].append('method-obstructions')
 targets=list(dict.fromkeys(p['target'] for p in packet['passages']));assert targets
 c['significance']={'category':category,'rationale':rationale,'novelty':'not_claimed','publication_status':'not_applicable','references':targets,'next_action':None}
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
validate(data);write_json(REGISTRY,data);write_json(args.out,{'baseline':REV,'claims':rows,'relationship_reviews':'80 pending, not complete','scope':'Compact-evidence metadata classifications; no new mathematics or canonical edges.'})
print('Curated 80 status/topic records and 75 significance dispositions; five novelty audits and 80 dependency inventories remain pending.')
