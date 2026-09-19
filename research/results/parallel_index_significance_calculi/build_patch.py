import json,sys,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'tools'))
from claim_registry import load
from claim_reviews import claim_digest
D=Path(__file__).parent;data=load();by={c['id']:c for c in data['claims']};base=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();W='https://kbr.is-a.dev/math-research/#'
report='results/parallel_index_significance_calculi/report.md'
specs=[('thm:working-Res-parity-bit-PHP-size-lower-bound','candidate','preprint','Earlier formulation of the same unrestricted DAG-like usual-CNF bit-PHP theorem consolidated in thm:publication-Res-parity-bit-PHP; inherits that publication candidate assessment and is not counted as a separate result.','Use the publication theorem\'s independent expert and exact-scope novelty review; do not duplicate this predecessor as a separate publication claim.',['working-Res-parity-bit-PHP-size-lower-bound','publication-bit-PHP-and-Res-parity','publication-Res-parity-bit-PHP-theorem','bit-PHP-publication-audit-verdict']),('thm:prime-disequality-bit-PHP-size-bound','unknown','candidate','Working all-prime size bound for the explicitly defined full-field affine-disequality calculus. Potential independent side result; targeted comparison distinguishes equation-clause Res(lin_Fp), Boolean semantic variants and tree-like unary-PHP literature. No novelty or stronger-system identification is certified.','Before separate publication, obtain expert comparison with affine-subspace-cover calculi and possible Boolean-domain-aware simulations; retain the full-field disequality and explicit-domain scope.',['prime-affine-disequality-calculus','full-field-equation-clause-encoding-cost','prime-disequality-bit-PHP-size-bound'])]
claims=[]
for cid,nov,pub,why,nxt,anchors in specs:
 refs=[W+a for a in anchors]+[report]
 claims.append({'id':cid,'source_fields_sha256':claim_digest(by[cid]),'significance':{'category':'independent_result','rationale':why,'novelty':nov,'publication_status':pub,'references':refs,'next_action':nxt},'review':{'state':'reviewed','evidence_targets':refs,'note':'Exact statement, encoding and rule comparison performed against local publication audit and targeted primary sources; uncertainty retained explicitly. This is significance metadata, not new proof validation.','next_action':None}})
(D/'patch.json').write_text(json.dumps({'base_revision':base,'claims':claims,'scope':'Significance only; canonical state unchanged.'},indent=2)+'\n')
print('Prepared two source-backed significance proposals.')
