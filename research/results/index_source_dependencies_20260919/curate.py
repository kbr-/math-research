#!/usr/bin/env python3
import argparse,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'tools'))
from claim_registry import load,validate,write_json,REGISTRY
from claim_reviews import make_review,Evidence
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);args=p.parse_args()
data=load();claims={c['id']:c for c in data['claims']};REV=subprocess.check_output(['git','rev-parse','dc1d95b'],cwd=ROOT,text=True).strip()
WEB='https://kbr.is-a.dev/math-research/#';GH='https://github.com/kbr-/math-research/blob/main/'
BIK=GH+'research/notes/SOURCE_AUDIT.md#bikprs-actual-simulation-structure'
added=[];reused=[];incident={}
def put(source,target,kind,anchor,scope,namespace='current',locator=None):
 key=source+'::'+kind+'::'+(namespace+':' if namespace!='current' else '')+target
 edge={'id':key,'source':{'namespace':'current','id':source,'locator':None},'target':{'namespace':namespace,'id':target,'locator':locator},'type':kind,'scope':scope,'evidence':[WEB+anchor],'review_status':'reviewed','review':{'revision':REV,'date':'2026-09-19','reviewer':'Codex GPT-6 Astra','note':'Exact proof/application and refinement role reviewed; source audit reused, no new paper or kernel verification.'}}
 prior=next((e for e in data['relationships'] if e['id']==key),None)
 if prior:
  assert prior['source']==edge['source'] and prior['target']==edge['target'] and prior['type']==kind
  reused.append(key)
 else:data['relationships'].append(edge);added.append(key)
 incident.setdefault(source,[]).append(WEB+anchor)
 if namespace=='current':incident.setdefault(target,[]).append(WEB+anchor)
rows=[
('thm:ordinary-php-ens-transfer','lem:modular-row-implies-clause','depends_on','php-transfer-theorem','The modular-row prelude supplies the ordinary clauses before applying the imported simulation.'),
('prop:php-clause-block-pruning','ex:later-block-dependency','cites','php-clause-pruning','Explains why later inputs must be globally specialized; the local affine image proof is explicit.'),
('lem:covered-disjunction-normalizer','lem:mp-telescoping','depends_on','axiom-covered-disjunction','Uses the earlier argument-block telescoping coefficients for the flattened complementary pattern.'),
('lem:approximation-booleanity-degree','lem:mp-telescoping','depends_on','axiom-booleanity','Disjunction case uses the exact prefix identity and coefficient degree accounting.'),
('lem:approximation-booleanity-degree','lem:mp-booleanity','refines','axiom-booleanity','Sharpens the earlier sufficient uniform Booleanity ceiling to the stated actual-degree source bound.'),
('lem:distribution-normalizer','lem:mp-telescoping','depends_on','axiom-distribution','Expands both earlier products and collects DIST-H coefficients.'),
('lem:distribution-normalizer','lem:approximation-booleanity-degree','depends_on','axiom-distribution','The non-OR argument case uses the sharp earlier Booleanity certificate.'),
('thm:source-template-normalization','thm:hierarchical-ns-normalization','depends_on','axiom-global-source','Converts original-degree local image certificates and the structural substitution bound into global LD transfer.'),
('thm:source-template-normalization','prop:php-clause-block-pruning','depends_on','axiom-global-source','Uses the ordinary clause assignments in the structural product/prefix induction.'),
('thm:source-template-normalization','lem:covered-disjunction-normalizer','depends_on','axiom-global-source','Uses CD assignments and their earlier prefix coordinates.'),
('thm:source-template-normalization','lem:distribution-normalizer','depends_on','axiom-global-source','Uses the original distribution assignment and error ledger; later accuracy-two refinement is a separate edge.'),
('thm:source-template-normalization','thm:ordinary-php-ens-transfer','applies','axiom-global-source','Only the stated simulation consequence combines LD with the earlier PHP-ENS degree bound.'),
('thm:earlier-boolean-packing','thm:hierarchical-ns-normalization','depends_on','mod-boolean-packing','Applies the hierarchical image theorem at B=1 for simultaneous constant assignments.'),
('thm:earlier-boolean-packing','lem:approximation-booleanity-degree','applies','mod-boolean-packing','Supplies the Booleanity premises for actual source inputs; the abstract packing theorem accepts supplied certificates.'),
('prop:mod-schema-block-pruning','thm:earlier-boolean-packing','depends_on','mod-schema-blocks','The original arity-at-most-three expansion is removed by Boolean packing at accuracy at least three.'),
('lem:pruned-mod-axiom-certificate','prop:mod-schema-block-pruning','depends_on','mod-pruned-polynomial','Uses the exact six-block expansion and fully packed images for the original 6p-2 certificate.'),
('lem:pruned-mod-axiom-certificate','lem:approximation-booleanity-degree','applies','mod-pruned-polynomial','The source-argument substitution uses the sharp certificate for the last argument, separately from the formal two-variable proof.'),
('lem:pruned-mod-axiom-certificate','lem:mod-interpolation','cites','mod-pruned-polynomial','An alternative route considered in the same record; the selected 6p-2 vanishing/domain-division proof does not require it.'),
('cor:combined-schema-preprocessing','thm:hierarchical-ns-normalization','depends_on','mod-combined-preprocessing','Local original-degree images are assembled by the hierarchical theorem.'),
('cor:combined-schema-preprocessing','thm:source-template-normalization','depends_on','mod-combined-preprocessing','Extends the structural product/prefix induction establishing B at most L.'),
('cor:combined-schema-preprocessing','thm:earlier-boolean-packing','depends_on','mod-combined-preprocessing','Adds the constant packing mode while preserving structural bounds.'),
('cor:combined-schema-preprocessing','prop:mod-schema-block-pruning','applies','mod-combined-preprocessing','The six explicit schema blocks are a particular eligible collection; arbitrary argument blocks are excluded.'),
('lem:distribution-refined-degree','lem:distribution-normalizer','refines','dist-refined-local','Same assignment and identity, tighter certificate ledger and sufficient accuracy two.'),
('thm:coordinate-weighted-prefix-normalization','thm:source-template-normalization','refines','dist-weighted-prefix','Keeps coordinate weights in the structural induction and lowers sufficient accuracy for the same stated portfolio.'),
('thm:mod-schema-accuracy-two','prop:mod-schema-block-pruning','refines','mod-two-six-gates','Replaces the forward gate assignment by earlier-zero while packing five gates; retains coherent syntax and source assumptions.'),
('lem:mod-two-axiom-certificate','lem:pruned-mod-axiom-certificate','refines','mod-two-axiom-certificate','Improves the method ledger to 4p-2 for a different forward image; does not replace the 6p-2 statement for the fully packed polynomial.')]
for row in rows:put(*row)
for source,anchor,scope in [
 ('lem:approximation-booleanity-degree','axiom-booleanity','The MOD case uses degree-nonincreasing domain reduction.'),
 ('thm:hierarchical-ns-normalization','axiom-hierarchical','Selected field images have remaining-domain certificates through pB; the cofactor induction is explicit.'),
 ('cor:constant-field-selector-pruning','mod-field-packing','Domain-vanishing companion images receive certificates within their original ordinary degrees.'),
 ('lem:pruned-mod-axiom-certificate','mod-pruned-polynomial','Division by the two monic domain equations certifies the formal polynomial through its degree, then field images are substituted.')]:
 put(source,'lem:fieldreduction','depends_on',anchor,scope,'historical',GH+'php_codex_handoff/manuscript/chapters/01_foundations.md#lem-fieldreduction')
put('thm:ordinary-php-ens-transfer','BIKPRS-Theorem-6.7(1)','depends_on','php-transfer-theorem','Imports the audited balanced ENS simulation with its source-degree, inventory and level accounting.','external',BIK)
put('lem:php-clause-certificates','BIKPRS-Definition-6.8','cites','php-clause-identities','Identifies these elementary identities with the actual translated clause approximations; the polynomial identities are proved locally.','external',BIK)
put('thm:source-template-normalization','BIKPRS-Lemma-6.10','applies','axiom-global-source','The simulation consequence uses the imported structural approximation-degree bound, not a new residual-rank bound.','external',BIK)
closed={
 'lem:modular-row-implies-clause':(['php-modular-row-bridge'],'Self-contained prefix induction in the stipulated MOD/Frege axiom system. Fixed Boolean proof templates are calculus primitives; no earlier indexed mathematical lemma is used.'),
 'thm:ordinary-php-ens-transfer':(['php-transfer-theorem'],'Uses the modular-row bridge and audited BIKPRS simulation; affine truth-convention change and row-power replacement are given explicitly.'),
 'lem:php-clause-certificates':(['php-clause-identities'],'Row and collision identities are explicit local polynomial algebra. Definition 6.8 is encoding provenance, not an additional proof of the identities.'),
 'prop:php-clause-block-pruning':(['php-clause-pruning'],'All affine images, Boolean field identities and NS/PC degree replay are given locally. The later-block example is an explanatory citation.'),
 'lem:covered-disjunction-normalizer':(['axiom-covered-disjunction'],'The only named mathematical input is telescoping for the earlier OR argument; non-OR complements are handled directly.'),
 'lem:approximation-booleanity-degree':(['axiom-booleanity'],'Source grammar induction uses telescoping and domain reduction; it refines the earlier uniform estimate. Degree hypotheses are retained, not newly correctness-certified.'),
 'lem:distribution-normalizer':(['axiom-distribution','dist-refined-local'],'Original identity uses telescoping and the argument Booleanity certificate. Its later accuracy-two result is tracked by the incoming refinement edge, not a circular premise of the original proof.'),
 'thm:hierarchical-ns-normalization':(['axiom-hierarchical'],'The original-degree cofactor induction is self-contained; domain reduction certifies field images. Supplied earlier NS identities remain actual hypotheses.'),
 'thm:source-template-normalization':(['axiom-global-source','dist-weighted-prefix'],'The original structural induction combines the clause/CD/distribution witnesses and hierarchical theorem. The lower-accuracy induction is a separate refinement; imported approximation and PHP bounds support the explicit simulation consequence.'),
 'cor:constant-field-selector-pruning':(['mod-field-packing'],'The complete selector product is explicitly constructed and its domain vanishing is checked in the source; field reduction and constant replay supply the transfer.'),
 'thm:earlier-boolean-packing':(['mod-boolean-packing'],'The BP identity is explicit, hierarchical substitution handles simultaneity, and source Booleanity is an optional supplier of the premises.'),
 'prop:mod-schema-block-pruning':(['mod-schema-blocks','mod-two-six-gates'],'The original arity argument uses Boolean packing; source syntax and coherence are fixed. Accuracy two is recorded as a later indexed refinement with a changed forward assignment.'),
 'lem:pruned-mod-axiom-certificate':(['mod-pruned-polynomial','mod-two-axiom-certificate'],'The original certificate uses the fully packed images and domain division; interpolation was an alternative idea. The 4p-2 certificate has a different image, tracked by a qualified refinement.'),
 'lem:mod-interpolation':(['mod-pruned-polynomial','entry-2026-09-14-lean-mod-interpolation'],'The isolated identity uses explicit vanishing at a=0,1 and monic division. Its Lean imports are library algebra/tactics, with no project-claim theorem prerequisite; the surrounding MOD certificate is provenance only.'),
 'cor:combined-schema-preprocessing':(['mod-combined-preprocessing'],'Combines hierarchical image certificates, the source-template structural induction and Boolean packing. The MOD expansion is a stated application, not coverage of arbitrary arguments.')}
evidence=Evidence()
for label in set(incident)|set(closed):
 c=claims[label];prior=c['reviews']['relationships'];targets=incident.get(label,[])
 if label in closed:
  anchors,note=closed[label];targets=list(dict.fromkeys([WEB+a for a in anchors]+targets));state='reviewed';next_action=None
 else:
  targets=list(dict.fromkeys([e['target'] for e in prior['evidence']]+targets));note=prior['note']+' The outgoing refinement recorded in this cluster was reviewed; full inventory status retained.';state=prior['state'];next_action=prior['next_action']
 if label=='lem:mod-interpolation':targets.append('../formalization/claims/ModInterpolation.lean')
 c['reviews']['relationships']=make_review(data,c,'relationships',targets,revision=REV,date='2026-09-19',reviewer='Codex GPT-6 Astra',note=note,evidence=evidence,state=state,next_action=next_action)
validate(data);write_json(REGISTRY,data);write_json(args.out,{'closed_reviews':list(closed),'added_edges':added,'retained_existing_edges':reused,'scope':'Source-relative dependencies and later refinements; no fresh primary-source, kernel or numerical audit.'})
print(f'Closed {len(closed)} inventories; added {len(added)} edges; retained {len(reused)} previously reviewed edges.')
