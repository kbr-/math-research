#!/usr/bin/env python3
"""Curate source-copy and cleanup metadata from saved compact evidence."""
import argparse,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'tools'))
from claim_registry import load,validate,write_json,REGISTRY
from claim_reviews import make_review,Evidence
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);args=p.parse_args()
data=load();claims={c['id']:c for c in data['claims']};packets=json.loads((Path(__file__).parent/'packets.json').read_text())['packets']
REV=subprocess.check_output(['git','rev-parse','c838d05'],cwd=ROOT,text=True).strip()
# Topic groups reflect the reviewed objects, not current route membership.
groups={'C':['ens','frege-simulation','polynomial-calculus'],
        'N':['ens','frege-simulation','nullstellensatz','degree-accounting'],
        'A':['ens','affine-linear-algebra','degree-accounting'],
        'F':['ens','finite-certificates'],
        'B':['ens','method-obstructions','nullstellensatz'],
        'P':['ens','matching-php','polynomial-calculus']}
# Group, significance category, scope-sensitive rationale, in source packet order.
specs=[
('C','route_specific','Independent line scopes retain the audited simulation scale using explicit copy agreement; no unrestricted source elimination follows.'),
('N','general_tool','Matched-core NS cover has an explicit image budget and supplied earlier differences; existence of cheap matching witnesses is not asserted.'),
('C','route_specific','Proof-line core chains are height-controlled only at line occurrences; proper-subformula chains are excluded.'),
('C','general_tool','PC final-line reuse avoids the NS matching surcharge under the common supplied ceiling and coordinate hypotheses.'),
('C','general_tool','Weighted refutation replay derives the chosen weight from supplied weighted assumptions; those assumptions cannot be omitted.'),
('C','route_specific','Signed proof boundaries are removed in independent line scopes using the audited leaf input; proper families remain.'),
('C','route_specific','Canonical sharing removes one input-agreement cost while preserving private boundaries; proper copies may still survive.'),
('P','route_specific','Ordinary PHP reaches a nonboundary ENS family at polylogarithmic PC degree; that family remains the elimination target.'),
('A','context','Elementary Boolean-domain padding separates polynomial degree from domain values; full source integration is explicitly unused.'),
('F','route_specific','Exact nine-variable separation of PC degree four and NS degree six is a finite control, not a universal separation theorem.'),
('F','route_specific','A derived finite control shows why ordinary design degree is not interchangeable with PC degree.'),
('F','route_specific','Exact signed MOD traces expose proper support under the recorded two fields; no general support bound is inferred.'),
('C','general_tool','Simultaneous zero pruning needs supplied strictly earlier input proofs at a common ceiling.'),
('C','route_specific','Negative axiom-root pruning uses the corrected strict-level support and ceiling, not the earlier unsupported inference.'),
('N','general_tool','Positive leaf NS cofactors provide polynomial witnesses and image certificates; a low-degree PC refutation alone does not supply them.'),
('C','general_tool','Triangular polynomial substitution quantifies level-composition cost from supplied local image proofs.'),
('C','route_specific','Both-sign axiom-root pruning retains the later repaired support argument and revised uniform bound.'),
('F','negative_result','Degree growth for prescribed witnesses is a finite control against optimistic composition, not a lower bound for all normalizers.'),
('C','context','Syntax clarification prevents applying an unflattened OR fixture to the wrong source formula; its algebra is unchanged.'),
('N','general_tool','Correct flattened projection coefficients expose argument Booleanity as the remaining requests.'),
('N','general_tool','Sharp source Booleanity survives the specified Boolean-constant substitutions; original typed domains remain part of the setup.'),
('C','general_tool','Isolated Booleanity ports permit conditional proof transfer under the declared constant substitution; arbitrary uses of companions are not covered.'),
('B','negative_result','A satisfiable countermodel separates product Booleanity from the companion information needed for positive antecedents.'),
('B','negative_result','All-companion normalizers over a Boolean-domain base face an NS-degree constraint; this is a restriction on that normalization method.'),
('B','negative_result','The audited pebbling input gives a coefficient-degree obstruction despite cheap PC proofs; it is not a PHP conclusion.'),
('F','route_specific','Exact four-vertex path certificates and controls exhibit the stated PC/NS/normalizer tradeoff only.'),
('C','negative_result','Flattened OR subgroups can share the parent level, correcting the support inference that all proper pieces are strictly earlier.'),
('N','general_tool','Constructive source-frame repair supplies strict-level axiom input certificates at the stated scale.'),
('C','route_specific','Separated formula occurrences retain agreement and leaf simulation without silently identifying repeated syntax nodes.'),
('C','route_specific','The occurrence convention supplies the freshness needed at proper signed MP interfaces, including repeated-antecedent controls.'),
('C','route_specific','Subtree-local interface replay preserves the stated height-dependent invariant; it does not eliminate the remaining source.'),
('P','route_specific','The ordinary-PHP reduction incorporates private-boundary, interface and clause pruning while leaving the proper family uncontrolled.'),
('C','route_specific','Inherited representatives preserve intact descendants and fresh interfaces through the declared occurrence forest.'),
('C','general_tool','Positive-boundary zero replay uses available conclusion inputs and a fresh block; those supplied assumptions are essential.'),
('C','route_specific','Inherited consequent representatives remove copy cost in the recorded simulation, with argument and MOD families still open.'),
('N','general_tool','MOD-first output Booleanity admits a domain-only certificate after substitution through twice the substituted degree.'),
('C','general_tool','Formula-copy PC agreement costs at most 2L by final-line reuse; the NS bound remains a separate assertion.'),
('C','negative_result','Original-frontier support can be large at constant proof depth even when the family is cheaply normalizable.'),
('C','general_tool','Signed MOD scalar conversions quantify finite-domain costs and require the declared domains.'),
('C','route_specific','Scalar MOD interfaces fit the inherited MP recurrence with a pre-power weight at positive conclusions.'),
('C','negative_result','Scalar derivation/refutation can require many original frontier families; this does not rule out normalization.'),
('A','general_tool','Literal variable identification gives a degree-preserving quotient for intact surviving occurrence trees.'),
('C','route_specific','Sharing only eventual survivors preserves private-cut freshness and makes the relevant comparisons literal.'),
('C','general_tool','Canonical signed multiplicities cancel in pre-power sums without argument Booleanity; global support remains open.'),
('N','general_tool','Compatible constant modes preserve sharp specialized Booleanity with retained inputs explicitly specialized.'),
('C','general_tool','Mixed-mode transfer is conditional on the audited mode and port hypotheses; it does not license arbitrary role sharing.'),
('P','route_specific','Ordinary row/collision/final-PHP assignments fit the mixed modes with explicit old-base discharge; other wide blocks remain.'),
('A','general_tool','Optimal coefficients for a prescribed two-child product give a local bound, not a resolved same-level global composition.'),
('A','general_tool','Terminal-degree cost improves the prescribed-product ledger; alternate normalizations are not ruled out.'),
('A','general_tool','Anchored factor partition solves the stated disjoint-monomial packing optimum, not arbitrary inputs or targets.'),
('A','general_tool','Degree-adapted actual Boolean generators support the same-span quotient; arbitrary bases have countercontrols.'),
('N','general_tool','Boolean ideal-generator cover uses certified generators and NS input witnesses within original companion budgets.'),
('N','general_tool','Retained-core ideal absorption needs explicit residual NS witnesses and its stated cost inequality.'),
('N','general_tool','Sharper actual-product accounting refines the earlier NS copy recurrence while preserving the separate 2L PC result.'),
('N','general_tool','The directional unit identity is a recorded rediscovery of the distribution error, with improved accounting rather than independent novelty.'),
('N','general_tool','A refined distribution certificate lowers sufficient outer accuracy to two; admissible and inadmissible controls delimit the ledger.'),
('N','general_tool','Coordinate-weighted prefixes preserve B at most L for the specified aligned source normalizers at accuracy at least two.'),
('C','route_specific','Highest-OR-level omission is a one-time support refinement of the repaired simulation, not iterative level elimination.'),
('N','general_tool','Earlier-zero extends the constant-mode argument using a retained-system NS certificate through product degree.'),
('C','route_specific','The coherent six-gate MOD expansion admits accuracy-two pruning by one earlier-zero and five packed assignments.'),
('N','general_tool','A different complete MOD-axiom image improves the formal two-variable certificate to 4p-2, with a sharper binary value.'),
('C','general_tool','Matched MOD scalar interfaces remove fresh OR frontiers under combined goal-input assumptions; global occurrence integration is separate.'),
('F','route_specific','Ninety-four exact traces verify the recorded frontier replay cases; a storage-limited expanded baseline is not successful evidence.'),
('C','route_specific','The expanded private-cut plan preserves survivor closure and removal-time freshness for the specified matched arguments.'),
('C','route_specific','Hybrid frontier cuts preserve the PC invariant while leaving canonical-copy and coverage gaps visible.'),
('F','negative_result','Conditional schedule witnesses show that future private cuts can make current goal-input comparisons nonliteral.'),
('C','route_specific','Partial frontier cuts retain a nonconstant residual scalar and preserve the existing invariant under the recorded matching rules.'),
('F','negative_result','Satisfiable controls isolate a selected companion request from the other goal assumptions in the recorded fixtures.'),
('C','route_specific','Maximal-root scheduling protects representatives and supplies the stated closure/freshness properties.'),
('C','route_specific','Saturated cleanup preserves the invariant with general copy comparisons; universal coverage is explicitly not claimed.'),
('C','negative_result','A fixed-depth structural family escapes the maximal-root rule; it is not an essential-support lower bound.'),
('C','general_tool','Weighted virtual copies extend the existing identity only with supplied virtual-companion proofs.'),
('B','context','The pointwise union-bound route asks for accuracy beyond its useful active regime; it is not a universal design-lift obstruction.'),
('N','general_tool','An exhaustive assignment tree gives low-degree ENS certificates with exponential inventory, distinguishing degree from family-count cost.'),
('P','negative_result','The PHP exponential-family control excludes elimination bounds independent of family count, leaving polynomial-family regimes open.'),
('C','general_tool','Goal-relative constant cleanup can retain specialized ancestors when input-image proofs are supplied; global scheduling is separate.'),
('F','route_specific','Finite complete traces and models verify that an inner block can disappear while a nonconstant modified ancestor remains.'),
('C','route_specific','Private ancestor closure integrates nonmaximal cleanup into the PC invariant; the modified family still lacks a general bound.'),
('P','route_specific','The protected final clause family preserves the PHP endpoint despite other modified blocks; further pruning requires current witnesses.'),
('F','route_specific','Finite conditional forest controls validate recorded cuts and expose failure of premature canonical sharing.')]
assert len(specs)==len(packets)==80
conditional={61,63,72,75,81,105,111,112,131}
finite={69,70,71,77,85,122,125,127,136,139}
refuted={82,86,130};context={78,132};evidence=Evidence();rows=[]
for position,(packet,(group,category,rationale)) in enumerate(zip(packets,specs),60):
 c=claims[packet['id']];assert c['summary']==packet['summary'] and c['assessment']==packet['assessment']
 c['mathematical_status']='conditional' if position in conditional else 'finite_check' if position in finite else 'refutation' if position in refuted else 'context' if position in context else 'working_proof'
 c['topics']=list(groups[group])
 if category=='negative_result' and 'method-obstructions' not in c['topics']:c['topics'].append('method-obstructions')
 targets=list(dict.fromkeys(p['target'] for p in packet['passages']));assert targets
 c['significance']={'category':category,'rationale':rationale,'novelty':'not_claimed','publication_status':'not_applicable','references':targets,'next_action':None}
 for field in ('mathematical_status','topics','significance'):
  c['reviews'][field]=make_review(data,c,field,targets,revision=REV,date='2026-09-19',reviewer='Codex GPT-6 Astra',evidence=evidence,
    note='Recorded assessment and compact source qualifications reviewed; original wording, corrections and restricted scopes retained. No new proof or novelty verification.')
 c['reviews']['relationships']=make_review(data,c,'relationships',targets,revision=REV,date='2026-09-19',reviewer='Codex GPT-6 Astra',evidence=evidence,state='pending',
    note='Source regions inventoried, but direct equation/setup dependencies, earlier repairs and optional uses still need a complete ownership review.',
    next_action='Map direct prerequisites and correction/refinement links in '+', '.join('#'+p['target'].split('#')[-1] for p in packet['passages'])+'; separate the claimed result from shared-region proofs and finite controls.')
 rows.append({'id':c['id'],'status':c['mathematical_status'],'topics':c['topics'],'significance':category})
validate(data);write_json(REGISTRY,data);write_json(args.out,{'baseline':REV,'claims':rows,'relationship_reviews':'80 pending, not complete','scope':'Compact-evidence metadata classifications; no new mathematics or canonical edges.'})
print('Curated 80 status/topic/significance records; dependency reviews explicitly pending.')
