#!/usr/bin/env python3
"""Emit reviewed metadata proposals without modifying the canonical registry."""
import argparse,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'tools'))
from claim_registry import load,write_json
from claim_reviews import claim_digest
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);args=p.parse_args()
data=load();packets=json.loads((Path(__file__).parent/'packets.json').read_text())['packets']
revision=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
# Position selections are explicit editorial decisions after assessment/packet review.
context={538,547,551,554,557,585,596,615,624,630,650,653,640,659}
finite={521,527,532,537,542,546,550,561,564,569,574,579,584,589,594,598,602,607,612,613,622}
established={552,559,616,629}|set(range(634,648))|set(range(659,680))
established-=context
negative={526,580,595,618,619,620,628,631,633,651,654,655}
known={552,558,559,616,629,631,635,638,639,641,643,645,646,647,660,663,665,666}
conditional={597}
# Narrow annotations distinguish historical audits from theorem novelty claims.
notes={
 551:'Historical internal publication-scope audit supporting the unrestricted bit-PHP candidate; it is not a fresh search or independent expert review.',
 554:'Historical primary-source supplement on regularity and depth restrictions; preserve its provisional verdict without claiming a fresh literature audit.',
 557:'Historical whitepaper-production record, not a new theorem or current page-count assertion; current publication status belongs to the theorem and latest revision records.',
 558:'Exposition of the classical chessboard connectivity consequence, not an independently new connectivity theorem.',
 580:'Counterexample to closure under sums of flat indicators; it does not imply proof hardness.',
 595:'An ideal-level obstruction to universal affine-pair extraction, with a separate covered reduction example; not a failure of all source elimination.',
 596:'Scope control: the obstructing pair-consequence family remains covered by leading-pair reduction.',
 597:'A sufficient compression endpoint restated with its missing arbitrary-tuple hypothesis; no general compression theorem is supplied.',
 612:'Finite exact NS-versus-PC degree separation in the specified normalized quadratic system, not the PHP base or complete ENS filtration.',
 615:'Historical route audit requiring a quantitative depth-uniform invariant; a list of restricted depths is not closure.',
 617:'Explicit standard approximate-majority circuit construction and its ENS evaluation source; neither finite-check-only nor proof-essential occurrence.',
 618:'General Boolean-domain obstruction to universal sublinear complete old-only normalization, leaving PHP-relative and proof-specific routes open.',
 619:'Quantitative Boolean-domain affine-profile obstruction; no PHP-relative impossibility follows.',
 620:'Free-parameter profile barrier does not automatically apply to legitimate selector-valued source children.',
 624:'Historical interface/reuse audit; no new full-source compression.',
 628:'Refutes the particular Boolean-domain rank-cutoff moment assignment, not the existence of PHP designs.',
 630:'Quantifier audit: full old-moment preservation alone is insufficient for joint selector feasibility.',
 631:'Application of an attributed functional-method limitation; constant-width semantic inversion does not provide a joint residual certificate.',
 633:'Obstruction to conditioning-natural simultaneous sections; individual extensions and source-specific corrections remain available.',
 640:'Definitions and project API for finite augmented covers/nerve, without an independent theorem novelty claim.',
 650:'Historical failed causal-gluing attempt identifies a quantifier mismatch; no required fixed-distribution survival theorem.',
 651:'Cover-degree obstruction from the known certifier lemma, not a general impossibility of pseudorandom generators.',
 653:'Reuse audit of existing pruning interfaces rather than expanded pruning coverage.',
 654:'Necessary Boolean-domain matrix-normalization costs; no PHP-relative or arbitrary matrix-weight impossibility.',
 655:'Cyclic coefficient dependencies block the proposed triangular aggregate replacement, not every source transformation.',
 659:'Verified proof-system definitions and elementary interfaces; no bounded-degree PC=NS assertion.'}
rows=[];skipped=[]
for i,(c,packet) in enumerate(zip(data['claims'][520:680],packets),520):
 assert c['id']==packet['id'] and c['summary']==packet['summary'] and c['assessment']==packet['assessment']
 if all(c['reviews'].get(f,{}).get('state')=='reviewed' for f in ['mathematical_status','topics','significance']):
  skipped.append(c['id']);continue
 status='context' if i in context else 'finite_check' if i in finite else 'established' if i in established else 'conditional' if i in conditional else 'working_proof'
 if 522<=i<=534 or 625<=i<=630 or i in {648,649,632,633}:topics=['moment-designs','matching-php','polynomial-calculus']
 elif 634<=i<=647 or i in {558,559,629}:topics=['topological-methods','matching-php']
 elif 551<=i<=554 or i==557:topics=['bit-php','resolution-parities','publication']
 elif 659<=i<=667:topics=['polynomial-calculus','nullstellensatz','degree-accounting']
 elif i in {668,669,670,676,678}:topics=['affine-linear-algebra','polynomial-calculus']
 elif 671<=i<=673:topics=['bit-php','matching-php','polynomial-calculus']
 elif i>=674:topics=['ens','affine-linear-algebra','degree-accounting']
 else:topics=['ens','frege-simulation','degree-accounting']
 if i==552:topics=['bit-php','frege-simulation']
 if i in {555,556,570,571,577,581,586,590,591,592,599,600,603,604,605,608,609,610}:topics=['ens','affine-linear-algebra','degree-accounting']
 if i in {616,618,619,620,651,654}:topics=['ens','method-obstructions','degree-accounting']
 if i in finite:topics=list(dict.fromkeys(topics+['finite-certificates']))
 if i in negative:topics=list(dict.fromkeys(topics+['method-obstructions']))
 category='context' if i in context else 'negative_result' if i in negative else 'route_specific' if i in finite or c['id'].startswith(('thm:','cor:','ex:')) else 'general_tool'
 if i in {524,525,528,530,531,533,534,560,562,565,567,625,626,627,648,652,656,657,658}:category='general_tool'
 targets=list(dict.fromkeys(p['target'] for p in packet['passages']));assert targets
 rationale=notes.get(i,('Exact finite component evidence, without extrapolating its controls to the general lower-bound goal. ' if i in finite else 'Reusable scoped interface; preserve the stated field, degree and source restrictions. ' if category=='general_tool' else 'Restricted-source advance; it does not discharge the arbitrary-depth full-source obligation. ' if category=='route_specific' else 'Scoped obstruction only; do not infer impossibility of the complete research program. ')+c['assessment'])
 sig={'category':category,'rationale':rationale,'novelty':'known' if i in known else 'not_claimed','publication_status':'not_applicable','references':targets,'next_action':None}
 note='Reviewed exact indexed assessment and bounded source packet; this classifies the recorded scope, not a new proof verification or literature audit. '+c['assessment']
 values={'mathematical_status':status,'topics':topics,'significance':sig}
 reviews={f:{'state':'reviewed','note':note,'next_action':None,'evidence_targets':targets} for f in values}
 # Do not replace fields already reviewed even if others are missing.
 values={f:v for f,v in values.items() if c['reviews'].get(f,{}).get('state')!='reviewed'}
 reviews={f:v for f,v in reviews.items() if f in values}
 rows.append({'id':c['id'],'position':i,'claim_sha256':claim_digest(c),'values':values,'reviews':reviews})
write_json(args.out,{'schema_version':1,'baseline':revision,'worker':'classify_520_680','date':'2026-09-19','reviewer':'Codex GPT-6 Astra','claims':rows,'topic_definitions':[],'preserved_reviewed':skipped,'scope':'Metadata curation from compact evidence, not new proof or novelty audit; no relationship inventory completed.'})
print(f'{len(rows)} proposed records; {len(skipped)} fully reviewed records preserved; no canonical edits.')
