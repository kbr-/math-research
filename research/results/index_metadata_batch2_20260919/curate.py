#!/usr/bin/env python3
"""Apply reviewed compact-evidence classifications; keep unresolved graph reviews pending."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'tools'))
from claim_registry import load,validate,write_json,REGISTRY
from claim_reviews import make_review,Evidence
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);args=p.parse_args()
data=load();claims={c['id']:c for c in data['claims']};WEB='https://kbr.is-a.dev/math-research/#'
REV='9d54a66';import subprocess
REV=subprocess.check_output(['git','rev-parse',REV],cwd=ROOT,text=True).strip()
packets=json.loads((Path(__file__).parent/'packets-reviewed.json').read_text())['packets']
newtopics=[('affine-linear-algebra','Affine and linear algebra','Subspace ranks, quotient geometry, duality and affine feasibility.'),('frege-simulation','Frege simulation','Translation of proof syntax, source formulas and logical axiom schemas into algebra.'),('finite-certificates','Finite certificates','Exact finite traces, separating duals and computational controls.')]
for key,title,description in newtopics:
 if not any(t['id']==key for t in data['topic_definitions']):data['topic_definitions'].append(dict(id=key,title=title,description=description))
# Each line corresponds to the saved immutable packet order (original positions 15..59).
specs=[
 ('matching-php affine-linear-algebra','general_tool','Exact affine annihilator description in the stated matching/degree window; no arbitrary-degree rigidity claimed.'),
 ('affine-linear-algebra method-obstructions','negative_result','Quotient-dimension obstruction to nesting; explicitly not a barrier to all matching normalizations.'),
 ('matching-php ens substitution','route_specific','Sufficient simultaneous normalization by a single supplied matching, not existence for every source.'),
 ('matching-php affine-linear-algebra ens','route_specific','Favorable spread embedding is removable by one cell; cautions against promoting static spread data to a universal restriction barrier.'),
 ('matching-php affine-linear-algebra','general_tool','Dimension of the normalization cut supports the counting argument under its exact quotient setup.'),
 ('matching-php affine-linear-algebra method-obstructions','negative_result','Existence of resistant embeddings obstructs universal small-matching constant normalization, not all elimination.'),
 ('matching-php finite-certificates method-obstructions','negative_result','392 exact single-cell separation certificates on seven specified spaces; finite scope retained.'),
 ('ens substitution polynomial-calculus','general_tool','Whole-layer transfer from supplied polynomial normalizers; normalizer existence and costs remain hypotheses.'),
 ('ens substitution nullstellensatz degree-accounting','general_tool','NS transfer tracks original-axiom cofactors; cheap PC consequence alone does not provide the needed NS representation.'),
 ('matching-php ens substitution','route_specific','Simultaneous degree-preserving collision-pair removal on the specified PHP base, without inserting row functionality.'),
 ('matching-php ens method-obstructions','negative_result','Matching criterion fails on collision pairs even though a different polynomial normalization removes them.'),
 ('matching-php ens substitution','route_specific','Extra old inputs preserve the known pair normalizer when their coefficient assignments are zero.'),
 ('affine-linear-algebra finite-certificates method-obstructions','negative_result','Seven exact duals exclude the specified affine-normalizer/degree-two certificate search, not higher-degree methods.'),
 ('ens substitution polynomial-calculus','general_tool','Companion-product certificates suffice without requiring the product factor itself to be a cheap consequence.'),
 ('affine-linear-algebra ens','general_tool','Linear feasibility and separating tuple criterion for the stated companion images; a reusable algebraic interface.'),
 ('matching-php finite-certificates polynomial-calculus','route_specific','Exact closure/ideal comparison for the binary seven-hole instance, not a general PC/NS equality.'),
 ('affine-linear-algebra finite-certificates method-obstructions','negative_result','Finite rank certificates rule out quadratic common annihilators for the saved triples only.'),
 ('ens finite-certificates method-obstructions','negative_result','Exact dual tuples exclude the stated one-factor affine substitution through degree three on seven saved examples.'),
 ('frege-simulation matching-php','general_tool','MOD-one implies nonempty row with bounded-depth polynomial proof; does not imply row functionality.'),
 ('frege-simulation ens matching-php','route_specific','Ordinary-PHP simulation bridge over the exact weak base, relying on the recorded source audit.'),
 ('frege-simulation matching-php nullstellensatz','route_specific','Explicit original-base certificates for the actual clause approximations, preserving the true-is-zero convention.'),
 ('frege-simulation ens substitution','route_specific','Removes clause blocks and globally specializes later inputs; it does not leave dependent later companions unchanged.'),
 ('frege-simulation ens substitution','general_tool','Complementary-disjunction unit witness survives flattening and additional inputs with aligned source coordinates.'),
 ('frege-simulation ens nullstellensatz degree-accounting','general_tool','Sharp twice-degree source Booleanity certificate uses earlier subformula companions where needed.'),
 ('frege-simulation ens substitution','general_tool','Distribution normalizer uses argument companions or Booleanity; retain the later accuracy/degree refinement.'),
 ('ens substitution nullstellensatz degree-accounting','general_tool','Hierarchical image-certificate composition with explicit BD cost; compatibility and earlier-level hypotheses remain essential.'),
 ('frege-simulation ens substitution','route_specific','Selected source templates admit LD transfer with aligned source coordinates; later refinement lowers sufficient accuracy to two.'),
 ('ens substitution','general_tool','Constant field selectors remove rank-r blocks when accuracy pays the stated (p-1)r threshold.'),
 ('ens substitution nullstellensatz','general_tool','Earlier Booleanity permits simultaneous one-factor-per-input packing without degree loss; certificates remain supplied premises.'),
 ('frege-simulation ens substitution','route_specific','Six explicitly expanded MOD schema blocks have constant pruning assignments; preserve the accuracy-two refinement and syntax choice.'),
 ('frege-simulation nullstellensatz degree-accounting','route_specific','Two distinct specializations have different certified degree ledgers, 6p-2 and 4p-2; neither silently replaces the other.'),
 ('frege-simulation degree-accounting','general_tool','Isolated interpolation identity and joint degree bound are formally verified; surrounding MOD certificates are outside that coverage.'),
 ('frege-simulation ens substitution','route_specific','Compatible template and Boolean-packing substitutions compose at the stated LD bound, not arbitrary argument removal.'),
 ('frege-simulation ens nullstellensatz','general_tool','Theorem-approximation induction removes assumption leaves but retains logical-axiom and MP costs.'),
 ('nullstellensatz substitution degree-accounting','general_tool','Image-certificate transfer keeps arbitrary substituted targets explicit and charges original axiom degrees.'),
 ('frege-simulation matching-php substitution','route_specific','Final PHP boundary and clause blocks share one affine substitution; later-family changes remain explicit.'),
 ('frege-simulation matching-php ens','route_specific','Direct ordinary-PHP translation avoids the optional MOD-row prelude without changing the general elimination gap.'),
 ('ens substitution degree-accounting','general_tool','Local implication images relative to a retained core have quantified overhead; no global degree-preserving composition follows.'),
 ('ens substitution polynomial-calculus','general_tool','Retained core factors and residual tests permit simultaneous removal under literal input inclusion and accuracy budgets.'),
 ('matching-php ens substitution','route_specific','Clause-containing tuples retain base witnesses even with arbitrary additional earlier inputs.'),
 ('frege-simulation ens substitution','route_specific','Core-sharing and clause-containing rules compose only with one rule per block and unremoved designated cores.'),
 ('ens degree-accounting affine-linear-algebra','general_tool','Exact packing optimum for prescribed independent linear factors, not all possible elimination witnesses.'),
 ('ens frege-simulation method-obstructions','negative_result','Constant proof height does not control raw core-inclusion-chain length; essential support and other eliminations remain separate.'),
 ('ens polynomial-calculus nullstellensatz degree-accounting','general_tool','Matched-input block agreement separates NS certificate costs from PC final-line reuse.'),
 ('ens frege-simulation degree-accounting','general_tool','Coherent source-line copies have a uniform agreement bound, not a bound proportional to each individual polynomial degree.')]
assert len(specs)==len(packets)==45
finite={21,27,30,31,32};evidence=Evidence();report=[]
for position,(packet,spec) in enumerate(zip(packets,specs),15):
 c=claims[packet['id']];assert c['summary']==packet['summary'] and c['assessment']==packet['assessment']
 topics,category,rationale=spec
 targets=[p['target'] for p in packet['passages']];assert targets
 c['mathematical_status']='finite_check' if position in finite else 'refutation' if position==57 else 'established' if position==46 else 'working_proof'
 c['topics']=topics.split()
 c['significance']={'category':category,'rationale':rationale,'novelty':'not_claimed','publication_status':'not_applicable','references':targets,'next_action':None}
 for field in ('mathematical_status','topics','significance'):
  c['reviews'][field]=make_review(data,c,field,targets,revision=REV,date='2026-09-19',reviewer='Codex GPT-6 Astra',evidence=evidence,
    note='Reviewed verbatim indexed assessment and compact statement/qualification evidence. Preserve all original scope limits; classification is not a new proof audit or novelty finding.')
 report.append({'id':c['id'],'fields':['mathematical_status','topics','significance']})
# Specific relationships supported by extracted proof contexts; the full inventory is still pending.
edge_specs=[
 ('prop:collision-pair-matching-obstruction','prop:matching-normalization','obstructs','polynorm-matching-obstruction','Refutes universal availability of the matching-normalization criterion, not the proposition with its premise.'),
 ('prop:php-clause-block-pruning','ex:later-block-dependency','cites','php-clause-pruning','Explains why retained later inputs are specialized; the example is not a proof prerequisite.'),
 ('lem:covered-disjunction-normalizer','lem:mp-telescoping','depends_on','axiom-covered-disjunction','Uses the explicit telescoping coefficients of the earlier argument block.'),
 ('thm:earlier-boolean-packing','thm:hierarchical-ns-normalization','depends_on','mod-boolean-packing','Applies the hierarchical theorem with B=1 for simultaneous replacement.'),
 ('thm:earlier-boolean-packing','lem:approximation-booleanity-degree','applies','mod-boolean-packing','Supplies Booleanity for the source-block consequence; the abstract theorem also accepts other supplied certificates.'),
 ('lem:theorem-approximation-simulation','lem:mp-composition','depends_on','direct-theorem-approximation','Uses the NS MP recurrence in the balanced theorem induction.'),
 ('lem:ns-target-image-transfer','thm:hierarchical-ns-normalization','refines','direct-target-transfer','Reuses the final-cofactor argument while keeping the substituted target explicit; not a new independent mechanism.'),
 ('prop:php-final-boundary-pruning','lem:php-clause-certificates','depends_on','direct-php-boundary','Uses the exact earlier certificates for the boundary-only removal.'),
 ('prop:php-final-boundary-pruning','prop:php-clause-block-pruning','depends_on','direct-php-boundary','Uses the ordinary clause substitution in simultaneous removal.'),
 ('cor:php-clause-containing-pruning','prop:php-clause-block-pruning','refines','relative-php-superclauses','Extends the same ordinary clause coefficients to tuples with additional inputs.'),
 ('cor:core-cover-source-preprocessing','thm:direct-ordinary-php-transfer','applies','relative-combined-source','Applies the compatible preprocessing to the direct source; does not reprove the underlying simulation.'),
 ('lem:mod-interpolation','lem:pruned-mod-axiom-certificate','cites','entry-2026-09-14-lean-mod-interpolation','Records provenance in the earlier MOD calculation; not a dependency of the isolated formal identity.')]
added=[];incident={}
for source,target,kind,anchor,scope in edge_specs:
 key=source+'::'+kind+'::'+target
 edge={'id':key,'source':{'namespace':'current','id':source,'locator':None},'target':{'namespace':'current','id':target,'locator':None},'type':kind,'scope':scope,'evidence':[WEB+anchor],'review_status':'reviewed','review':{'revision':REV,'date':'2026-09-19','reviewer':'Codex GPT-6 Astra','note':'Reviewed extracted local proof/citation context; complete direct-dependency inventory remains a separate claim-level question.'}}
 prior=next((e for e in data['relationships'] if e['id']==key),None)
 if prior:assert prior==edge
 else:data['relationships'].append(edge);added.append(key)
 for label in (source,target):incident.setdefault(label,[]).append(WEB+anchor)
for packet in packets:
 c=claims[packet['id']];targets=list(dict.fromkeys([p['target'] for p in packet['passages']]+incident.get(c['id'],[])))
 anchor=packet['passages'][0]['target'].split('#')[-1]
 c['reviews']['relationships']=make_review(data,c,'relationships',targets,revision=REV,date='2026-09-19',reviewer='Codex GPT-6 Astra',evidence=evidence,state='pending',
  note='Candidate and compact-source review supplied the recorded scoped edges, but unlinked local equations/setup and optional applications have not been exhaustively mapped.',
  next_action='Resolve direct named/equation-label prerequisites in #'+anchor+' against neighboring indexed results; distinguish proof uses from illustrative controls and shared-region citations, then close the claim-level relationship review.')
for label,targets in incident.items():
 if label in {p['id'] for p in packets}:continue
 c=claims[label];prior=c['reviews']['relationships'];targets=list(dict.fromkeys([e['target'] for e in prior['evidence']]+targets))
 c['reviews']['relationships']=make_review(data,c,'relationships',targets,revision=REV,date='2026-09-19',reviewer='Codex GPT-6 Astra',evidence=evidence,
  note=prior['note']+' Incoming usage/citation from this batch reviewed; prior outgoing inventory retained.',state=prior['state'],next_action=prior['next_action'])
validate(data);write_json(REGISTRY,data);write_json(args.out,{'baseline':REV,'claims':report,'relationships_added':added,'pending_relationship_reviews':len(packets),'scope':'Compact-evidence classification; full dependency review remains explicitly pending.'})
print(f'Curated {len(packets)} status/topic/significance records; added {len(added)} scoped edges; {len(packets)} relationship reviews pending.')
