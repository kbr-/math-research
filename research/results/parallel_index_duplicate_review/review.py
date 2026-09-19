"""Human-authored scope judgments over generated retrieval evidence; no canonical writes."""
import json,re,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'tools'))
from claim_registry import load,references,write_json
P=Path(__file__).parent;data=load();cs={c['id']:c for c in data['claims']};rev=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();candidates=json.loads((P/'candidates.json').read_text());packets={p['id']:p for p in json.loads((P/'packets.json').read_text())['packets']}
reasons=[
 'Crowded-row exposure combines bounded crowded-row count with mass bounds and a finite size/tail ledger; few-light-rows permits arbitrary size and tail shapes when the entire light row set is small. These are different hypotheses, not duplicate theorems.',
 'The d<ell theorem extends rigidity from d=2 to every degree below ell. At d=2 it recovers the ell>=3 quadratic case; retain both original records and record a qualified refinement.',
 'The crowded-row theorem combines exposure of a small exceptional row set with the multirow mass argument. The mass theorem has separate large-union and no-crowded-row alternatives. Neither pair of full statements is an exact duplicate.',
 'The two-role version allows overlap of pinned/light row sets on the complete-term tree with extra exposed-set/mass handling; the earlier theorem is role-separated on the both-endpoints tree. Switching qualifications and constants differ.',
 'The two-role few-row theorem extends the heavy-round mechanism to overlapping roles and complete-term processing. Switching still needs sparse pinning and later composition repair; not identical to the role-separated theorem.',
 'Two-tier permits dense classes plus sparse classes and proves a smaller heavy-round count on another tree; full-column is its all-dense special case after the recorded tree transfer and larger constants. Both retain rank-step corrections and a conditional original switching clause.',
 'Crowded-size bound reaches c<3-2eps only with bounded-row/width J0 conditions; multirow-size has c<2-eps with arbitrary tails. Higher size exponent does not imply all hypotheses of the other result.',
 'Arbitrary cyclic lengths allow repeated factors and independent affine operands; earlier result uses special lengths2^s-1 and small field components. Same qualitative square-root degree scale does not erase different finite conditions and mechanisms.',
 'First-boundary result has D=3h+1 and n>=6h+1 with no h+2<ell restriction. Coherent-band result permits u through h at D=3h+u but needs h+u+1<ell. Their overlap at u=1 does not make their parameter ranges equivalent.',
 'Two-role size corollaries alter source role structure, tree and sparse-pinning assumptions; crowded-size has stronger exponent under bounded-tail hypotheses for role-separated readers. Retain distinct scopes and later correction/restoration evidence.',
 'Wide-round composition explicitly supersedes the failed wide-move interface: it changes the tree and charges a matching-number bound instead of an unavailable wide-move bound. It remains conditional on its own two bounds and is not the same theorem.',
 'Two-role few-row result controls all light rows and permits arbitrary tail shapes/size. Exposed version permits many unexposed rows under mass, t, W and size hypotheses. Neither is a duplicate of the other.',
 'One is a size corollary with arbitrary tail row support below n^(2-eps); the other has any size with few total light rows. Source class and sufficient parameters differ.',
 'The conjecture allows arbitrary fresh rank but requires a level-one base; rank-two theorem allows any Boolean base but fixes helper rank2. One remains conjectural, the other rediscovered proof. Their intersection is only a special case.',
 'Full-stack construction requires joint independence of all r^2 inputs; multiscale construction gives many pairwise-disjoint rank-r subspaces on each residual. Joint independence is stronger than pairwise separation and uses a different inventory.',
 'Two-role corollaries generalize role handling with sparse pinning and other restrictions. The role-separated size corollary does not impose those tree/role hypotheses; original switching and later restoration scopes must remain visible.',
 'Row-spread bounds labels per light row and needs no dense/sparse class partition; two-tier controls classes by pinned-row density at each label. The original source explicitly calls these incomparable.',
 'Few-light-rows imposes a global small row set but no size/mass/shape bound; multirow mass permits many rows subject to large-union or per-row mass criteria. Distinct sufficient mechanisms.',
 'Two matching-satisfaction lemmas share negative association, but host sets differ: full pinned-column classes versus dense classes of at least n/4 rows, with different thresholds12 versus20 times2^w(c+1)ln n. Not interchangeable constants/domains.',
 'Shared-probe positive-MOD exclusion concerns transformed nonlinear source inputs at logarithmic accuracy. Accuracy-one affine theorem concerns actual old-affine tuples and a stronger inventory range; a complete source transfer is needed between them.',
 'Earlier shared-bit transfer covers accuracyh>=2 using scalar bottom maps. Accuracy-one transfer supplies a different affine coefficient map for the missingh=1 case. Same D-to-D endpoint, complementary hypotheses and different original image ledgers.',
 'Size corollary derives a sufficient crowded-row bound from total light mass and term count. The parent theorem assumes crowded-row structure directly and covers other readers; theorem versus application, not duplicate metadata.'
]
assert len(reasons)==len(candidates['candidates'])==22
out=[]
for number,(candidate,reason) in enumerate(zip(candidates['candidates'],reasons)):
 left,right=candidate['left'],candidate['right'];out.append({**candidate,'candidate_number':number,'disposition':'distinct_scopes_preserve_both','rationale':reason,'evidence':[{'id':id,'summary':packets[id]['summary'],'assessment':packets[id]['assessment'],'sources':[{'target':p['target'],'sha256':p['source_sha256']} for p in packets[id]['passages']]} for id in (left,right)],'merged':False})
write_json(P/'candidate-decisions.json',{'schema_version':1,'candidate_report_sha256':candidates['derived_from_sha256'],'method':candidates['method'],'threshold':candidates['threshold'],'reviewed_pairs':22,'remaining_pairs':0,'decisions':out,'scope':'Metadata equivalence/scope review from exact recorded summaries, qualifications and targeted source packets; not independent theorem verification. All original IDs remain.'})
edges=[]
def edge(source,kind,target,scope,evidence=None):
 assert source in cs and target in cs,(source,target)
 targets=evidence or [p['target'] for p in references(cs[source]) if 'math-research/#' in p['target']]
 edges.append({'id':source+'::'+kind+'::'+target,'source':{'namespace':'current','id':source,'locator':None},'target':{'namespace':'current','id':target,'locator':None},'type':kind,'scope':scope,'evidence':targets,'review_status':'reviewed','review':{'revision':rev,'date':'2026-09-19','reviewer':'Codex duplicate/rediscovery reviewer','note':'Exact recorded hypothesis and cost distinctions reviewed; no mathematical equivalence inferred from lexical score.'}})
edge('thm:transported-bit-low-degree-rigidity','refines','thm:transported-bit-quadratic-rigidity','Extends J2 Boolean rigidity at ell>=3 to every d<ell; original quadratic proof remains its historical record.')
edge('thm:two-tier-column-switching','refines','thm:bipartite-full-column-switching','Heavy-round class coverage extends the all-dense bipartite case to dense-plus-sparse classes, with changed tree/constants and later rank-step correction. Original switching conclusion remains conditional.')
edge('thm:arbitrary-cyclic-complete-source-exclusion','refines','thm:binary-cyclic-sum-complete-source-exclusion','Extends source coverage from lengths2^s-1 to arbitrary lengths with repeated factors and independent affine operands; finite quantitative ledgers differ.')
edge('thm:wide-round-composition','supersedes','thm:wide-move-composition','Replaces the unavailable wide-move bound by wide-round-tree matching-number control. New composition retains its own explicit probability hypotheses.')
edge('thm:uniform-joint-residual-affine-family','refines','thm:multiscale-affine-rank-family','Strengthens pairwise residual independence to full-stack joint independence; does not assert essential proof occurrence.')
edge('thm:unit-accuracy-shared-bit-complete-transfer','refines','thm:dense-shared-bit-complete-transfer','Fills the missing accuracy-one case with a distinct complete affine bottom map; earlier h>=2 scalar-map theorem is retained.')
# Explicit assessment corpus: values below are editorially assigned, not guessed by similarity.
map_specs={
 'lem:sharper-ns-formula-copy':('refines','lem:block-copy-agreement','Tightens the same NS copy recurrence using actual OR product degrees.'),
 'lem:directional-distribution-unit':('rediscovers','lem:distribution-normalizer','Rediscovered DIST-H identity with sharper prefix/degree accounting; not a separately new polynomial identity.'),
 'lem:portfolio-level-support-Booleanity':('refines','thm:goal-normalized-sharp-Booleanity','Adds support-locality within the recorded portfolio; does not cover arbitrary earlier-zero witnesses.'),
 'thm:small-probe-normalization':('refines','lem:weighted-refutation-replay','Conditional small-probe image certificates refine the existing weighted replay mechanism.'),
 'lem:separate-interface-gate-budgets':('refines','lem:unit-annihilator-OR-interface','Separates the unit and annihilator ceilings in the three-term OR proof.'),
 'thm:level-confined-strict-PC-leaves':('refines','lem:strict-level-axiom-input-certificates','Replaces strict source-leaf NS/prefix steps by supplied PC interfaces and reuse; no same-degree NS conclusion.'),
 'cor:binary-full-affine-span-packing':('refines','cor:affine-basis-row-count','Uses full affine intersection before degree-ordered basis extension, preserving original input budgets.'),
 'lem:nonsharp-Boolean-packing-ledgers':('refines','cor:affine-basis-row-count','Retains nonsharp supplied Booleanity costs; NS and PC transfer conditions differ.'),
 'cor:uniform-PC-ideal-cover-ledger':('refines','thm:Boolean-ideal-generator-cover','Keeps uniform PC Booleanity ceiling in the earlier ideal-cover certificate; decompositions still required.'),
 'lem:stable-ideal-affine-feasibility':('refines','lem:companion-linear-feasibility','Tests companion images relative to the stable old ideal rather than only zero images.'),
 'thm:dense-occupied-column-elimination':('refines','prop:matching-normalization','Quantifies matching restrictions that normalize designated column-local input packages.'),
 'ex:sharp-label-inventory-freezing-gap':('refines','obs:binary-label-common-partition','Sharp Boolean bit-probe inventory gives explicit maximal freezing gap while whole-block normalization still works.'),
 'thm:uniform-residual-affine-rank-families':('refines','thm:spread-matching-avoidance','Refines resistant-family construction in the stated previously uncovered residual-rank regime.'),
 'thm:compact-direct-NS-source-circuits':('refines','lem:theorem-approximation-simulation','Supplies polynomial shared-circuit representation for the recorded direct source, without monomial sparsity or constant arithmetic depth.'),
 'thm:shallow-source-cofactor-formulas':('refines','thm:compact-direct-NS-source-circuits','Refines source cofactor representation to bounded arithmetic-depth formulas with the stated ordinary-degree ledger.'),
 'thm:multiscale-affine-rank-family':('refines','thm:uniform-residual-affine-rank-families','Makes the resistance inventory uniform across dyadic residual scales.'),
 'thm:uniform-joint-residual-affine-family':('refines','thm:multiscale-affine-rank-family','Strengthens pairwise residual independence to full-stack joint independence; does not assert essential proof occurrence.'),
 'cor:source-cofactor-pair-support':('refines','thm:pair-separated-NS-PC-transfer','Requires separation only on pairs present in the given source certificate, retaining actual cofactor costs.'),
 'prop:proper-OR-union-complete-support':('refines','thm:shallow-source-cofactor-formulas','Extracts exact collected companion support in the supplied proper OR witness; no global-support necessity.'),
 'lem:binary-affine-selector-source-profile':('refines','lem:constructor-selector-only-dependencies','Specializes the actual binary source grammar to old-affine plus earlier-selector inputs before optional packing.'),
 'thm:matching-tree-weighted-module-refutation':('refines','thm:assignment-tree-ens-refutation','Branches on one hole per pigeon and expresses the exhaustive control using current weighted modules; still nonpolynomial inventory.'),
 'cor:compact-bit-pruned-assignment-tree':('refines','thm:assignment-tree-ens-refutation','Prunes repeated-label branches and uses compact pair-leaf witnesses; no small Frege proof follows.'),
 'lem:label-decoder-interpolation-certificate':('refines','lem:two-functional-row-state-interpolation','Explicit telescoping gives the decoder image certificate in the functional-row setting, excluding weak rows.'),
 'prop:compact-source-affine-old-part':('refines','lem:compact-source-bottom-selector-profile','Identifies old-affine forms after the chosen source/boundary construction, not arbitrary degree-ell old polynomials.'),
 'obs:label-substitution-selector-count-failure':('refines','prop:retained-label-parent-source','Counts actual nonlinear selector directions under literal substitution; does not construct a short PHP proof.'),
 'thm:dependent-rank-source-collapse':('refines','thm:sparse-selector-source-collapse','Replaces number of dependent positions by independent selector rank using adapted basis and original cost profiles.'),
 'lem:accuracy-dependent-affine-exclusion':('refines','audit:ordinary-restriction-affine-family','Makes accuracy/rank tradeoff explicit in the ordinary restriction argument.'),
 'thm:unit-accuracy-affine-family-exclusion':('refines','thm:constant-accuracy-affine-family-exclusion','Lowers accuracy to one with separate coefficient/weight degrees; only refutation exclusion is asserted.'),
 'obs:disjoint-sums-quadratic-vanishing-ideal':('refines','obs:quadratic-sum-flat-span-obstruction','Upgrades the same disjoint-sum obstruction from constant span to degree-two consequences of the full Boolean ideal.'),
 'lem:prescribed-row-moment-pairing':('refines','lem:nondegenerate-old-moment-pairing','Adds prescribed first moments under finite extension while retaining the determinant nondegeneracy mechanism.'),
 'thm:fresh-block-conservativity-loss-bound':('refines','lem:affine-common-vanishing-learning','Refines weighted-specialization learning loss for a fresh block; does not supply affordable arbitrary composition.'),
 'cor:affine-rank-two-same-degree-conservativity':('rediscovers','lem:rank-two-bottom-quadratic-transfer','Top-level accuracy-one affine rank-two conservativity is the earlier complete normalization special case; a second proof is recorded, not a new mathematical result.')}
for source,(kind,target,scope) in map_specs.items():
 if not any(e['source']['id']==source and e['target']['id']==target and e['type']==kind for e in edges):edge(source,kind,target,scope)
explicit=json.loads((P/'explicit-refinement-inventory.json').read_text());decisions=[]
for c in explicit['records']:
 id=c['id'];hits=[e for e in edges if e['source']['id']==id]
 existing=[e for e in data['relationships'] if e['source']['id']==id or e['target']['id']==id]
 if id in map_specs:disposition='scoped_relationship_proposed';note=map_specs[id][2]
 elif id in {'ex:column-dependent-image-certificates','lem:switched-reader-old-image'}:disposition='keyword_not_claim_rediscovery';note='Refinement refers to a partition/proof operation, not an assertion that this claim duplicates another.'
 elif id in {'thm:source-template-normalization','prop:mod-schema-block-pruning'}:disposition='incoming_refinement_already_recorded';note='Assessment describes a later accuracy refinement; keep original identity and the existing incoming refinement rather than invent a reverse edge.'
 elif id in {'lem:distribution-refined-degree','lem:mod-two-axiom-certificate'}:disposition='existing_explicit_refinement';note='Canonical outgoing refinement already identifies the earlier precise certificate.'
 elif id=='lem:one-collision-linear-query-attack':disposition='external_rediscovery_worker_patch';note='Existing worker patch records attributed Byramji–Impagliazzo RemarkA.4 pointwise mechanism; design extension/height improvement remains scoped, not independent invention.'
 elif id=='cor:affine-basis-row-count':disposition='worker_scoped_refinement';note='Worker dependency patch identifies the earlier generator-cover/bin construction; not mathematical duplication.'
 elif id=='cor:four-h-rank-source-module-designs':disposition='method_parameter_refinement';note='Source says this rank scale was already covered by factor-bin packing; new statement preserves same degree in a restricted module band. It is not equivalent to the full packing theorem.'
 elif id=='thm:source-outer-linear-factor-normal-form':disposition='representation_refinement';note='Refines proof-path/cofactor representation after preprocessing; existing source dependency chain identifies path machinery. Not an equivalent restatement of a lower-bound theorem.'
 elif id=='lem:uniform-degree-two-affine-rigidity':disposition='finite_to_uniform_extension';note='Uniform all-field theorem strengthens earlier finite checks; finite evidence cannot be mathematically equivalent to the universal claim.'
 elif id=='thm:source-highest-or-level-unused':disposition='support_refinement';note='One-time source-support consequence using strict leaf certificates; not iterative elimination or a duplicate of its local leaf lemma.'
 else:raise AssertionError(id)
 decisions.append({'id':id,'assessment':c['assessment'],'disposition':disposition,'rationale':note,'proposed_edge_ids':[e['id'] for e in hits],'existing_related_edges':[e['id'] for e in existing],'source_targets':[p['target'] for p in c['source_evidence']]})
write_json(P/'explicit-decisions.json',{'schema_version':1,'reviewed_records':len(decisions),'remaining_records':0,'decisions':decisions,'scope':'Complete regex assessment census. A refinement is not automatically mathematical equivalence; all labels and original records are preserved.'})
write_json(P/'relationship-proposals.json',{'schema_version':1,'base_revision':rev,'relationships':edges,'scope':'Deduplicate against concurrently produced worker proposals before canonical integration. No claim metadata or record deletions.'})
print('Reviewed22 candidate pairs and44 explicit assessment matches;',len(edges),'scoped relation proposals.')
