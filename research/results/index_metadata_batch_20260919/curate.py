#!/usr/bin/env python3
"""Apply manually reviewed source metadata for the first chronological claim batch."""
import argparse
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools'))
from claim_registry import load, validate, write_json, REGISTRY
from claim_reviews import make_review, Evidence
parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
data=load();claims={c['id']:c for c in data['claims']};WEB='https://kbr.is-a.dev/math-research/#'
REV='f9782de127b6c23ea41d0d3a0bd20b02ce0f53df'
topics=[
 ('polynomial-calculus','Polynomial calculus','PC derivations, closure spaces, proof transformations and final-line reuse.'),
 ('nullstellensatz','Nullstellensatz certificates','Ordinary polynomial ideal certificates, cofactors and certificate degree.'),
 ('substitution','Substitution and elimination','Variable interpretations, weighted replay and removal of extension blocks.'),
 ('matching-php','Matching structure in PHP','Partial matchings, matching weights and the unary PHP base.'),
 ('method-obstructions','Method obstructions','Counterexamples and limitations with the affected hypothesis or method identified.')]
for key,title,description in topics:
 if not any(t['id']==key for t in data['topic_definitions']):data['topic_definitions'].append(dict(id=key,title=title,description=description))
# id, source region, status, topics, significance category, scope-sensitive rationale.
rows=[
 ('local:zero-cofactor-pruning','local-zero-cofactor-pruning','working_proof',['ens','nullstellensatz','substitution'],'general_tool','Certificate-aware removal of unused companion blocks; explicitly an elementary clarification of the historical unused-block observation, with no novelty claim or affordable-support bound.'),
 ('lem:mp-identities','mp-two-cases','working_proof',['ens','polynomial-calculus'],'general_tool','Explicit polynomial identities for both MP conclusion cases; reusable local algebra, not extension elimination.'),
 ('lem:mp-booleanity','mp-booleanity','working_proof',['ens','nullstellensatz','degree-accounting'],'general_tool','Structural Booleanity certificates retain all used domain and extension axioms; useful for local inference simulation without pretending approximate values are literally Boolean.'),
 ('lem:mp-composition','mp-certificates','working_proof',['ens','polynomial-calculus','nullstellensatz','degree-accounting'],'general_tool','Separates height-accumulating flattened NS cofactors from augmented-PC final-line reuse. The later bounded audit confirms these estimates use companion upper bounds, not the refuted loose-ceiling equality.'),
 ('prop:mp-substitution-interface','mp-elimination-gap','conditional',['ens','substitution','polynomial-calculus'],'route_specific','Sufficient global substitution interface with supplied leaf and local-correction derivations; neither their existence nor the degree budget for PHP is established.'),
 ('ex:mp-zero-specialization','mp-elimination-gap','refutation',['ens','substitution','method-obstructions'],'negative_result','Explicit Boolean control rules out blanket zero specialization of corrections; it does not exclude other substitutions or prove a PHP lower bound.'),
 ('lem:old-consequence-transfer','boundary-old-consequence','working_proof',['ens','substitution','polynomial-calculus','degree-accounting'],'general_tool','Extends one-block elimination from refutations to arbitrary old targets, with explicit target-degree charges and domain hypotheses.'),
 ('lem:weighted-replay','boundary-weighted-replay','working_proof',['ens','substitution','polynomial-calculus'],'general_tool','Replays a full premise using supplied input-weight products and reuses their final polynomials; the product derivations are genuine premises.'),
 ('thm:mp-boundary','boundary-mp-elimination','working_proof',['ens','substitution','polynomial-calculus'],'route_specific','Eliminates one implication block through both full premise proofs while preserving old boundary polynomials; retained axioms must be independent of that block.'),
 ('ex:missing-annihilator','boundary-controls','refutation',['ens','substitution','method-obstructions'],'negative_result','Satisfiable control shows the implication proof alone cannot supply the required weighted input products; it does not refute weighted replay with its hypotheses.'),
 ('ex:later-block-dependency','boundary-controls','refutation',['ens','substitution','method-obstructions'],'negative_result','A later companion changes under zero replay, defeating the unchanged-old-axiom premise. This limits the given replay method, not all multilevel elimination.'),
 ('ex:prime-dependent-loss','boundary-controls','working_proof',['ens','polynomial-calculus','degree-accounting','method-obstructions'],'negative_result','Exact field-domain example separates augmented degree three from old degree p for p at least five; not Boolean PHP or an asymptotic fixed-prime obstruction.'),
 ('thm:target-annihilator-batch','overlap-target-batch','working_proof',['ens','polynomial-calculus','substitution'],'general_tool','Batches input spans modulo a supplied target-annihilator space, generalizing nested quotient replay without assuming its elements are old consequences.'),
 ('lem:matching-annihilators','overlap-matching-annihilators','working_proof',['matching-php','nullstellensatz'],'route_specific','Explicit partial-matching annihilator certificates and dimension count on weak linear-row PHP; does not insert same-row exclusions.')]
# scope records the actual role, including countercontrols and alternative self-contained proofs.
edges=[
 ('lem:mp-identities','lem:mp-telescoping','depends_on','mp-two-cases','Uses the telescoping coefficient identities in both conclusion cases.'),
 ('lem:mp-booleanity','lem:mp-telescoping','depends_on','mp-booleanity','Disjunction Booleanity uses the telescoping identity and coefficient upper bounds.'),
 ('lem:mp-composition','lem:mp-identities','depends_on','mp-certificates','Uses the exact MP-A/B identities for coefficient collection and PC reuse.'),
 ('lem:mp-composition','lem:mp-booleanity','depends_on','mp-certificates','The non-disjunction case includes the explicit Booleanity certificate.'),
 ('lem:mp-composition','lem:mp-telescoping','depends_on','entry-2026-09-14-bounded-companion-degree-audit','Needs coefficient and companion upper bounds only; the later audit found no equality-dependent inference here.'),
 ('prop:mp-substitution-interface','lem:mp-identities','depends_on','mp-elimination-gap','Substitutes the MP identity at every node with supplied correction proofs.'),
 ('prop:mp-substitution-interface','lem:mp-composition','depends_on','mp-elimination-gap','Uses the local multiplier degree bound and final-line composition.'),
 ('ex:mp-zero-specialization','prop:mp-substitution-interface','obstructs','mp-elimination-gap','Refutes blanket zero substitution as a way to supply the interface premises; not the conditional theorem.'),
 ('thm:mp-boundary','lem:old-consequence-transfer','depends_on','boundary-mp-elimination','Transfers the antecedent proof first, with the antecedent among the inputs.'),
 ('thm:mp-boundary','lem:weighted-replay','depends_on','boundary-mp-elimination','Replays the implication proof with the conclusion polynomial as weight.'),
 ('thm:mp-boundary','lem:mp-booleanity','applies','boundary-mp-elimination','Optional supplier of the required Booleanity derivation when its axioms remain old; arbitrary supplied derivations also suffice.'),
 ('ex:missing-annihilator','lem:weighted-replay','obstructs','boundary-controls','Shows why the supplied product premise cannot be removed; not a refutation of the lemma.'),
 ('ex:missing-annihilator','thm:mp-boundary','obstructs','boundary-controls','Shows why the implication derivation without the antecedent is insufficient.'),
 ('ex:later-block-dependency','thm:mp-boundary','obstructs','boundary-controls','Blocks applying the theorem when retained later axioms depend on the removed coefficients.'),
 ('ex:prime-dependent-loss','lem:old-consequence-transfer','obstructs','boundary-controls','Refutes a degree-preserving strengthening on general field-domain bases; consistent with the stated charged bound.')]
added=[]
for source,target,kind,anchor,scope in edges:
 key=source+'::'+kind+'::'+target
 edge={'id':key,'source':{'namespace':'current','id':source,'locator':None},'target':{'namespace':'current','id':target,'locator':None},'type':kind,'evidence':[WEB+anchor],'review_status':'reviewed','scope':scope,'review':{'revision':REV,'date':'2026-09-19','reviewer':'Codex GPT-6 Astra','note':'Read the exact local argument and scope; no fresh mathematical or Lean verification.'}}
 prior=next((e for e in data['relationships'] if e['id']==key),None)
 if prior:assert prior==edge
 else:data['relationships'].append(edge);added.append(key)
historical=[
 ('local:zero-cofactor-pruning','thm:nested','08_batching.md#thm-nested','local-zero-cofactor-pruning','Identifies the earlier unused-block observation and gives a nested-span control.'),
 ('local:zero-cofactor-pruning','thm:additive','07_elimination.md#thm-additive','local-zero-cofactor-pruning','Cited application giving the post-pruning additive support bound, not needed for the pruning substitution identity.'),
 ('local:zero-cofactor-pruning','lem:subsetdp','09_decomposition.md#lem-subsetdp','local-zero-cofactor-pruning','Optional exact subset recurrence on the pruned affine family; not a uniform affordable bound.'),
 ('prop:mp-substitution-interface','thm:one-elimination','07_elimination.md#thm-one-elimination','mp-elimination-gap','Cited as an inapplicable shortcut when freshness fails, not a proof dependency.'),
 ('prop:mp-substitution-interface','lem:prefixcertificate','07_elimination.md#lem-prefixcertificate','mp-elimination-gap','Historical control distinguishing NS flattening from PC reuse.'),
 ('lem:old-consequence-transfer','thm:one-elimination','07_elimination.md#thm-one-elimination','boundary-old-consequence','The source identifies t=1 with the historical refutation bound; local proof is self-contained.'),
 ('thm:target-annihilator-batch','lem:nestedquotient','08_batching.md#lem-nestedquotient','overlap-target-batch','The source identifies t=1 with the nested quotient bound; does not assert a separately reread historical dependency.')]
for source,target,path,anchor,scope in historical:
 key=source+'::cites::historical:'+target
 edge={'id':key,'source':{'namespace':'current','id':source,'locator':None},'target':{'namespace':'historical','id':target,'locator':'https://github.com/kbr-/math-research/blob/main/php_codex_handoff/manuscript/chapters/'+path},'type':'cites','evidence':[WEB+anchor],'review_status':'reviewed','scope':scope,'review':{'revision':REV,'date':'2026-09-19','reviewer':'Codex GPT-6 Astra','note':'Citation role verified in the local source passage; no new audit of the historical theorem.'}}
 prior=next((e for e in data['relationships'] if e['id']==key),None)
 if prior:assert prior==edge
 else:data['relationships'].append(edge);added.append(key)
evidence=Evidence()
for label,anchor,status,topics,category,rationale in rows:
 c=claims[label];targets=[WEB+anchor]
 if label=='lem:mp-composition':targets.append(WEB+'entry-2026-09-14-bounded-companion-degree-audit')
 c['mathematical_status']=status;c['topics']=topics
 c['significance']={'category':category,'rationale':rationale,'novelty':'not_claimed','publication_status':'not_applicable','references':targets,'next_action':None}
 for field in ('mathematical_status','topics','significance','relationships'):
  note='Reviewed exact indexed source passage and original qualifications. Classification records its stated scope; no new theorem, proof certification or novelty claim.'
  if field=='relationships':note='Reviewed direct named claim-level uses and scoped obstructions in the source. Self-contained algebra and elementary PC/domain rules are not artificial claim nodes; historical links remain citations. Incoming edges also included in fingerprint.'
  c['reviews'][field]=make_review(data,c,field,targets,revision=REV,date='2026-09-19',note=note,reviewer='Codex GPT-6 Astra',evidence=evidence)
# New incoming uses affect the seed's relationship fingerprint, not its proof.
c=claims['lem:mp-telescoping'];targets=[WEB+'mp-two-cases',WEB+'mp-booleanity',WEB+'entry-2026-09-14-bounded-companion-degree-audit']
c['reviews']['relationships']=make_review(data,c,'relationships',targets,revision=REV,date='2026-09-19',note='Retain the previously reviewed absence of claim-level prerequisites; review the newly recorded incoming MP uses with upper-bound scope.',reviewer='Codex GPT-6 Astra',evidence=evidence)
validate(data);write_json(REGISTRY,data)
write_json(args.out,{'baseline':REV,'claims_curated':[r[0] for r in rows],'added_relationships':added,'scope':'Metadata curation of exact indexed passages, no new proof or kernel run. Original claim text retained.'})
print(f'Curated {len(rows)} claims; added {len(added)} scoped relationships.')
