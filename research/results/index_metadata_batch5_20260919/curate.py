#!/usr/bin/env python3
"""Curate source-copy and cleanup metadata from saved compact evidence."""
import argparse,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'tools'))
from claim_registry import load,validate,write_json,REGISTRY
from claim_reviews import make_review,Evidence
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);args=p.parse_args()
data=load();claims={c['id']:c for c in data['claims']};packets=json.loads((Path(__file__).parent/'packets.json').read_text())['packets']
REV=subprocess.check_output(['git','rev-parse','1f85a8a'],cwd=ROOT,text=True).strip()
# Topic groups reflect the reviewed objects, not current route membership.
groups={'C':['ens','frege-simulation','polynomial-calculus'],
        'N':['ens','frege-simulation','nullstellensatz','degree-accounting'],
        'A':['ens','affine-linear-algebra','degree-accounting'],
        'F':['ens','finite-certificates'],
        'B':['ens','method-obstructions','nullstellensatz'],
        'P':['ens','matching-php','polynomial-calculus']}
# Group, significance category, scope-sensitive rationale, in source packet order.
specs=[
('P','general_tool','Affine occupancy freezing preserves the weak base and a residual board; it does not introduce same-row exclusions.'),
('P','route_specific','The statistic-dependent class admits full multilevel elimination without count cost, but arbitrary source inputs need not lie in that class.'),
('P','general_tool','Design pullback uses linear functionals and actual proof images, not multiplicativity.'),
('P','route_specific','Eligible dependency packages can be pruned while other blocks remain genuinely transformed; recognition is in the proper normal form.'),
('F','route_specific','Finite full-base image certificates test multilevel collapse and reject invalid copy-count controls.'),
('P','route_specific','Occupied-witness density gives a sufficient matching normalizer with explicit count and density hypotheses.'),
('P','route_specific','Empty-witness density gives a sufficient freezing normalizer under the stated copy congruence and size bounds.'),
('P','route_specific','The mixed-density bridge leaves general source coverage open despite simultaneous elimination of qualifying packages.'),
('F','route_specific','A concrete mixed-family map verifies images and missed-witness controls, not universal density coverage.'),
('P','general_tool','A Hall-profile deficit supplies original-board affine normalizers for the designated column inputs, including arbitrary extras.'),
('P','route_specific','Sparse Hall families defeat a density-only heuristic while remaining normalized by the stated criterion.'),
('F','route_specific','Exact Hall-profile certificates cover nonzero field images and missing-row/collision controls.'),
('P','general_tool','Exact occupancy-equation PC/NS degrees depend on characteristic; these added linear equations are not ENS companions.'),
('P','general_tool','The one-row feasibility equivalence concerns base-zero factors, not all possible companion-image normalizers.'),
('F','route_specific','Finite upper proofs and moment designs test the characteristic-dependent degree split.'),
('P','general_tool','The exact affine accuracy frontier uses full-base image budgets and sufficient board thresholds; broader maps are excluded.'),
('A','general_tool','Quadratic slice reconstruction supplies exact finite-field binomial identities for the stated target slices.'),
('F','route_specific','Six parameter checks cover ordinary quadratic monomials and residual thresholds, not every board.'),
('P','route_specific','A common-partition package collapses through its largest class with no level/count cost; source membership is still a condition.'),
('P','route_specific','Partition-size and degree budgets give a conditional contradiction bridge, not a source coverage theorem.'),
('A','negative_result','Bit labels force singleton common classes while remaining column-normalizable, separating partition freezing from elimination.'),
('P','negative_result','The largest-class bound limits affine statistic freezing even with degree-two constant proofs; it does not bound every normalizer.'),
('P','general_tool','Integer occupancy constraints are necessary for the freezing map but do not alone prove feasibility.'),
('C','general_tool','Completed affine row relations give a PC reuse ledger; no equally sharp flattened NS bound is asserted.'),
('P','general_tool','Column-dependent copy permutations preserve base images and enlarge the class of compatible partitions.'),
('P','route_specific','Compatible local-statistic packages collapse without extra count/level cost, leaving arbitrary source compatibility open.'),
('P','negative_result','A universal shifted-copy family has discrete common refinement despite local freezing; it lies outside the common-partition hypothesis.'),
('F','route_specific','Exact shifted-copy fixtures verify original base and complete ENS image budgets.'),
('P','route_specific','A majority profile admits a compatible layout under explicit probability and size conditions; application to all sources is unproved.'),
('A','general_tool','The recorded factorial-moment sampling tail is standard and self-contained, not a new probability inequality claim.'),
('A','general_tool','The strict-majority matching construction realizes the standard degree condition with short augmenting paths.'),
('F','route_specific','Saved large layouts and exhaustive small graphs check the matcher and union-bound hypotheses for two profiles.'),
('P','route_specific','Filtering selected local classes yields same-degree transfer under the resulting majority/copy conditions.'),
('P','route_specific','The two-thirds density threshold is sufficient with finite corrections, not claimed optimal.'),
('P','route_specific','The analytic empty-intersection family has positive filtered margin but still must satisfy the copy-size conditions.'),
('P','general_tool','Exception bounds yield a deterministic layout at the stated congruent copy count and residual size.'),
('A','general_tool','The degree-sum matching condition is standard; the record supplies an explicit equality-case construction.'),
('F','route_specific','Finite equality-case graphs and base-image certificates test the deterministic boundary.'),
('P','general_tool','A genuine matching trims both high-exception vertex sets while preserving the quantified size bound.'),
('P','route_specific','Trimming and filtering give the stated deterministic residual under explicit aggregate exception/degree budgets.'),
('P','route_specific','The aggregate-density threshold is a sufficient consequence of this trimming method, not a universal optimum.'),
('A','general_tool','Literal coefficient signatures identify coarsest local partitions; row-equivalence rewrites are excluded.'),
('P','negative_result','Separating occupied column states obstructs affine statistic freezing, not general block normalization.'),
('P','negative_result','Sharp label probes force maximal partition exceptions while their column blocks remain cheaply normalizable.'),
('A','general_tool','Freedom at common zeros controls actual normalizer output profiles within original image budgets.'),
('P','route_specific','Normalizer-output/statistic composition charges actual output profile counts and retains certified selector reduction.'),
('P','route_specific','Grouped bit outputs permit a linear residual for qualifying later packages; arbitrary later raw-bit uses are excluded.'),
('C','general_tool','Pure acyclic affine definitions preserve proof degree by existing replay; sparse proof size is not preserved automatically.'),
('N','general_tool','The conjunction selector has an explicit full-product certificate and activity cost, not a lower bound on all gate interfaces.'),
('P','context','Aggregate occupancy counting behaves differently by characteristic, and its models need not lift to PHP.'),
('A','negative_result','Exact extension-field counts require high old-variable Boolean degree on independent inputs; auxiliary-variable encodings are not excluded.'),
('A','general_tool','The maximum prime-field coordinate degree is basis-independent within the stated exact independent-input representation.'),
('P','route_specific','Selector-only later use limits occupied profile classes and supports conditional compatible-package transfer.'),
('C','route_specific','The constructor audit restricts retained input dependencies before optional packing; proof lines may still use individual coefficients.'),
('P','negative_result','Grouped and split bit blocks expose different selector partitions; this is not permission to regroup an existing proof.'),
('P','general_tool','Literal signs give an exact local column classification with explicit low-degree normalizers and original field budgets.'),
('P','negative_result','Positive-literal selectors realize arbitrary partitions at logarithmic count; no proof-essentiality or family lower bound follows.'),
('C','context','This is the open source-to-base elimination obligation, not an established theorem or evidence that the coverage gap is closed.'),
('P','general_tool','The auxiliary functional-base bridge applies the audited Razborov bound after adjoining axioms; it does not derive functionality from weak PHP.'),
('P','general_tool','A counting injection bounds the positive-request matching event without assuming edge independence.')]
assert len(specs)==len(packets)==60
conditional={227,239,265,272}
finite={224,228,231,234,237,247,251,257}
refuted=set();context={269,277};evidence=Evidence();rows=[]
for position,(packet,(group,category,rationale)) in enumerate(zip(packets,specs),220):
 c=claims[packet['id']];assert c['summary']==packet['summary'] and c['assessment']==packet['assessment']
 c['mathematical_status']='conditional' if position in conditional else 'finite_check' if position in finite else 'refutation' if position in refuted else 'context' if position in context else 'established' if position==278 else 'working_proof'
 c['topics']=list(groups[group])
 if category=='negative_result' and 'method-obstructions' not in c['topics']:c['topics'].append('method-obstructions')
 targets=list(dict.fromkeys(p['target'] for p in packet['passages']));assert targets
 c['significance']={'category':category,'rationale':rationale,'novelty':'known' if position in (249,250,256,267,278) else 'not_claimed','publication_status':'not_applicable','references':targets,'next_action':None}
 for field in ('mathematical_status','topics','significance'):
  c['reviews'][field]=make_review(data,c,field,targets,revision=REV,date='2026-09-19',reviewer='Codex GPT-6 Astra',evidence=evidence,
    note='Recorded assessment and compact source qualifications reviewed; original wording, corrections and restricted scopes retained. No new proof or novelty verification.')
 c['reviews']['relationships']=make_review(data,c,'relationships',targets,revision=REV,date='2026-09-19',reviewer='Codex GPT-6 Astra',evidence=evidence,state='pending',
    note='Source regions inventoried, but direct equation/setup dependencies, earlier repairs and optional uses still need a complete ownership review.',
    next_action='Map direct prerequisites and correction/refinement links in '+', '.join('#'+p['target'].split('#')[-1] for p in packet['passages'])+'; separate the claimed result from shared-region proofs and finite controls.')
 rows.append({'id':c['id'],'status':c['mathematical_status'],'topics':c['topics'],'significance':category})
validate(data);write_json(REGISTRY,data);write_json(args.out,{'baseline':REV,'claims':rows,'relationship_reviews':'60 pending, not complete','scope':'Compact-evidence metadata classifications; no new mathematics or canonical edges.'})
print('Curated 60 status/topic/significance records; dependency reviews explicitly pending.')
