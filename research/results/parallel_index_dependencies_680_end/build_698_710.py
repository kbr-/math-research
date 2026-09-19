import json,hashlib,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'tools'))
from claim_registry import load, references
D=Path(__file__).parent;x=load();cs=x['claims'];rev='dc1d95b4cb6a463436256b830afd69029c1dc3ed';by={c['id']:c for c in cs}
packets={p['id']:p for p in json.loads((R/'research/results/parallel_index_classify_680_end/packets.json').read_text())}
rows=[];edges=[]
def evidence(i):return [p['target'] for p in packets[cs[i]['id']]['passages']]
def add(i,k,t,n):
 assert t in by,t
 edges.append({'id':cs[i]['id']+'::'+k+'::'+t,'source':{'namespace':'current','id':cs[i]['id'],'locator':None},'target':{'namespace':'current','id':t,'locator':None},'type':k,'evidence':evidence(i),'review_status':'reviewed','scope':n,'review':{'revision':rev,'date':'2026-09-19','reviewer':'Codex parallel dependencies_680_end','note':'Proof-role language and source setting checked; no edge inferred from hyperlink alone.'}})
raw='''698|depends_on|thm:binary-selector-modular-NS-source|The actual mixed OR template supplies the recurrence ports at the declared original witness cost; the semantic cube obstruction is then local.
699|refines|prop:mixed-prefix-boundary-only-obstruction|Allows polynomial old-variable dependence and quantifies the required degree between retained boundaries in the same prefix family.
699|cites|thm:comparison-component-boundary-compression|The comparison is outside the pure isolated-component hypothesis, so the prior compression theorem is not retracted.
699|cites|prop:mod-copy-original-support|Compares with the narrower unchanged-comparison support obstruction.
699|cites|thm:composed-wide-product-cost|Compares with prescribed-product degree growth; the new cube proof permits arbitrary boundary replacements.
700|rediscovers|ex:pure-disjunct-virtual-interface|The tautology-frame application was already covered; the new calculation only makes the mask explicit.
700|applies|prop:mixed-prefix-boundary-only-obstruction|Uses the genuine mixed prefix port as a masked example, outside the unweighted obstruction's conclusion.
700|cites|thm:binary-selector-modular-NS-source|Existing NS frame provides selector-valued coefficients and original degree accounting.
700|cites|cor:source-cofactor-pair-support|Proof-specific support refinement covers only its declared first mixed degree band.
700|cites|audit:PHP-relative-source-interface|PHP residual permission does not supply the missing simultaneous witnesses.
700|cites|prop:full-costed-source-coupled-marginals|Names the unresolved joint-functional equations as the next obligation, not as a proven construction.
701|depends_on|thm:all-field-matching-filtration|Only for nonvacuity: normalized old designs exist in the stated stable range.
701|depends_on|lem:all-prime-compact-bit-decoder|Only for nonvacuity: transfers the old design existence with Boolean/collision witness costs preserved.
701|cites|obs:row-quotient-proper-point-gap|The explicit correlated pullback agrees with the earlier distinction between zero mean and zero functional.
702|depends_on|thm:all-field-matching-filtration|Surjective restriction of old annihilators allows independent diagonal values before the local determinant argument.
703|applies|prop:mixed-prefix-boundary-only-obstruction|Uses its genuine mixed port and original NS ceiling as the finite projection test, not its boundary-retention conclusion.
703|cites|lem:nondegenerate-old-moment-pairing|Nonsingular pairing motivates the failed projection recipe; the finite failure does not refute the pairing lemma.
704|depends_on|thm:all-field-matching-filtration|Old stability keeps row cells independent and permits arbitrary remaining functional values.
704|depends_on|lem:nondegenerate-old-moment-pairing|Reuses the squarefree determinant argument with prescribed nonzero row masses.
704|refines|lem:nondegenerate-old-moment-pairing|Adds prescribed row masses and finitely many nonsingular predicate-ideal restrictions.
705|depends_on|lem:canonical-row-local-selector-values|Canonical row-state values and costed input replacement supply the corrected projection values.
705|depends_on|prop:row-state-first-success-profiles|The complete coefficient map uses the existing first-success row profile.
705|depends_on|lem:functional-row-state-degree-completeness|Certifies coefficient fields, companions, product agreement and the mixed-port image within the original budget.
705|depends_on|lem:prescribed-row-moment-pairing|Ensures prescribed row masses and the nonsingular projection interpretation can coexist.
705|cites|thm:row-supported-multilevel-normalization|The example does not extend the already available row-local normalization coverage.
705|cites|obs:row-local-preprocessing-order-scope|Retains the explicit unary-decoder/image scope instead of mixing incompatible degree guarantees.
706|refines|obs:pointwise-lift-inactive-regime|The elementary universal support bound quantifies why the support-only ENS union-bound guarantee is inactive.
706|cites|obs:scalar-old-component-extension-obstruction|The literal-copy success shows that the support bound is not a universal impossibility of constant coefficient assignments.
707|depends_on|lem:multi-axis-cube-residual-detector|Signed residual row cubes detect a maximal diagonal monomial, proving independence in the old matching quotient.
707|applies|audit:weighted-mixed-port-reuse|The actual tautology frame supplies the cofactor 1-P_A, making the span example a genuine source-template occurrence.
707|cites|lem:nondegenerate-old-moment-pairing|Symbolic density remains an available alternative and is not used to prove the span lower bound.
707|cites|audit:adaptive-query-fixed-distribution-gap|The large-span example does not resolve the fixed-distribution quantifier problem.
708|depends_on|thm:proper-OR-union-NS-degree-six|The prior retained-companion certificate gives the matching degree-six upper bound; preservation at degree five comes from the exact finite matrices.
709|refines|lem:affine-common-vanishing-learning|The squaring bound has the learning-ledger shape but is rank-independent for one fresh block and permits inputs at any level.
'''
for line in raw.strip().splitlines():
 i,k,t,n=line.split('|',3);add(int(i),k,t,n)
notes={698:'Mixed template is the only imported mathematical interface; separating complete-model assignments prove the boundary-only obstruction.',699:'The fixed-coefficient cube and multilinear degree argument are local; comparison compression and support/product bounds are comparisons, not premises.',700:'Reuse audit identifies an old application and separates exact masked identity from the unresolved global consistency obligation.',701:'Literal-copy equations give the obstruction locally; filtration and decoder enter only to show the old-design premise is nonvacuous.',702:'Stable filtration supplies the free functional values; determinant cancellation, finite-field specialization and density linear algebra are explicit locally.',703:'Finite matrices/models and the actual mixed port provide the failure; the valid pairing lemma is context, not refuted.',704:'Read the prescribed-mass determinant proof and its row-ideal argument; old stability and the earlier determinant construction are the imported mechanisms.',705:'Canonical row values, first-success coefficients, row-state certificates and prescribed pairing supply the concrete correction; multirow normalization is comparison.',706:'Read the full isolating-literal proof and binary refinement: self-contained beyond the NS design definition; application/comparison links do not become proof dependencies.',707:'Specialization span is elementary; the quotient independence proof explicitly invokes the signed row-cube detector, and the source frame provides the genuine cofactor.',708:'Exact saved matrices certify the finite preservation; the prior degree-six proper-union identity is the separate upper-bound input.',709:'Constant specialization, input annihilation and squaring prove the bound locally. Earlier learning ledger is a refinement comparison, not an imported proof step.'}
for i in range(698,710):
 c=cs[i];rows.append({'position':i,'id':c['id'],'state':'reviewed','evidence':evidence(i),'note':notes[i]+' Recorded direct-claim relationships inventoried; no new proof or novelty audit.','next_action':None,'source_fields_sha256':hashlib.sha256(json.dumps({k:c[k] for k in ('id','summary','assessment','record')},sort_keys=True,ensure_ascii=False).encode()).hexdigest()})
(D/'patch_698_710.json').write_text(json.dumps({'base_revision':rev,'range':[698,710],'claims':rows,'relationships':edges},indent=2)+'\n');print('closed',len(rows),'edges',len(edges))
