import sys,json,hashlib,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'tools'))
from claim_registry import load, references
D=Path(__file__).parent;x=load();cs=x['claims']; by={c['id']:c for c in cs};rev='dc1d95b4cb6a463436256b830afd69029c1dc3ed'
rows=[];edges=[]
def add(i,kind,target,note):
 c=cs[i];ts=[r['target'] for r in references(c) if '.lean' in r['target'] or '#lean-' in r['target']]
 edges.append({'id':c['id']+'::'+kind+'::'+target,'source':{'namespace':'current','id':c['id'],'locator':None},'target':{'namespace':'current','id':target,'locator':None},'type':kind,'evidence':ts,'review_status':'reviewed','scope':note,'review':{'revision':rev,'date':'2026-09-19','reviewer':'Codex parallel dependencies_680_end','note':'Actual proof-use passages and owning declarations checked; import-only and colliding unqualified names are not proof dependencies.'}})
assertions='''680|depends_on|lem:functional-matching-normal-form|Occupied/unused insertion identities prove the row-boundary cancellation.
680|depends_on|third-party:finite-augmented-chain-api|Supported boundary and empty-chain identities supply the augmented cycle, including s=1.
680|depends_on|third-party:chessboard-homological-bound|The stable-range homology theorem supplies a filling of the cycle.
680|depends_on|third-party:chessboard-parameter-arithmetic|chessboardNu_stable_range converts N>=2s-1 into the exact filling range.
680|cites|audit:matching-moment-completeness|Uses MatchingMarginals as the input interface; no completeness theorem is needed for the local cycle proof.
681|cites|audit:matching-moment-completeness|Pullback preserves the explicitly defined MatchingMarginals equations.
681|cites|lem:functional-matching-normal-form|Uses IsMatching, RowUnused and ColUnused definitions; relabeling identities are proved locally.
681|cites|third-party:augmented-chain-naturality|Uses the InRange support interface; the relabeling equivalence is elementary and does not use cycle filling.
682|depends_on|lem:matching-moment-row-relabeling|Pull back row marginals, preserve matching faces and identify the row-set embedding range.
682|depends_on|lem:matching-marginal-cycle|matching_moment_filling fills each selected row set; rowUnused_iff_not_mem_image handles row boundaries.
682|depends_on|third-party:augmented-chain-naturality|push_supported and boundary_push transport the local filling to the full row set.
682|depends_on|lem:functional-matching-normal-form|Insertion identities and functionalUnaryBase decomposition control matching-supported boundary terms.
682|depends_on|audit:matching-moment-completeness|The NS extension uses annihilates_implies_marginals, momentFunctional_annihilates and agreement on matching normal form.
682|depends_on|third-party:linear-annihilator-extension|The bounded-functional corollary extends a linear functional from the degree subspace before applying matching extension.
682|cites|def:ordinary-polynomial-proof-foundations|NS spaces, degree spaces and monotonicity provide the ordinary proof-system interface.
683|cites|thm:bit-PHP-affine-clause-PC-transfer|Publication transfer motivates the helper; the field-uniform telescoping induction does not depend on that transfer.
684|depends_on|lem:affine-literal-product-prefix|The initial-value derivation explicitly calls affine_literal_product_prefix on the lifted pair literals.
684|depends_on|lem:reuse|Multiplies an old axiom and companions by polynomials through the fixed ceiling.
684|depends_on|def:affine-clause-PC-system|registry_input_degree, registry_value_degree and registry_companion_degree provide the charged bounds.
684|cites|lem:compact-bit-decoder-coordinates|Uses the bit-label/compact-base coordinate interface; the semantic initial-clause proof is local.
684|cites|def:ordinary-polynomial-proof-foundations|Uses actual ordinary PC axioms and monotonicity; a colliding mono token is not a matching-cycle dependency.
685|refines|lem:simultaneous-affine-family-removal|Adds a unit-span high-block alternative at the same ceiling, preserving the earlier literal-only theorem.
685|depends_on|lem:low-rank-ENS-specialization|lowRankENS_specialization supplies the low-rank case of the local coefficient construction.
685|depends_on|lem:binary-degree-controlled-Boolean-reduction|polynomial_boolean_ns_bound certifies substituted Boolean equations and high literal witnesses.
685|depends_on|lem:reuse|NS multiplication and NS-to-PC conversion certify weighted images at the common ceiling.
685|depends_on|lem:fresh-ENS-block-degree|Injective renaming preserves the actual old-axiom degree used in replay.
685|depends_on|lem:substitution|Derives.substitute_weighted replays the supplied refutation after all weighted axiom images are certified.
685|cites|def:affine-clause-PC-system|Tautological source clauses motivate the new unit case; the removal theorem itself applies to affine ENS families.
686|depends_on|lem:affine-clause-basis-compression|Compresses each source clause to width at most v+1 with the same truth set.
686|depends_on|lem:binary-semantic-affine-cover|Converts a general binary semantic step into one weakening or two auxiliary clauses with a complementary pivot.
686|depends_on|lem:semantic-weakening-PC-degree|registry_semantic_weakening derives actual initial and one-premise registry values.
686|depends_on|lem:affine-clause-resolution-PC-degree|registry_resolution combines auxiliary values at the shared fixed ceiling.
686|cites|def:ordinary-polynomial-proof-foundations|Uses Derives and its monotonicity; neither the resolve constructor nor mono name proves an extra dependency.
687|depends_on|lem:finite-affine-map-span-witnesses|finite_affine_unit_coefficients supplies a common zero for the proper affine family before basis completion.
687|refines|lem:affine-coordinate-completion|Generalizes coefficient-form completion to arbitrary finite coordinate and input types.
689|depends_on|lem:coordinate-restriction-ideal|coordinate_restriction_coefficients yields selected-variable factors of the inverse pullback.
689|depends_on|lem:ordinary-restriction-dimension|Uses affine substitution degree preservation and ordinary degree-space dimension bounds.
689|depends_on|lem:finite-affine-map-polynomial-bridge|Finite affine polynomial degree and evaluation identify pullback composition and literal factors.
689|cites|lem:finite-affine-coordinate-completion|Consumes supplied affine coordinates; completion is available to construct them but not a proof prerequisite of the conditional restriction identity.
691|depends_on|lem:compact-bit-decoder-coordinates|The explicit bitLabelEquiv and its bijectivity define coordinate flips on finite column labels.
692|cites|def:ordinary-polynomial-proof-foundations|Uses the NS span/generator interface; cancellation and degree-drop proofs are local, not applications of the imported substitution theorem.
693|depends_on|lem:finite-affine-map-polynomial-bridge|Injectivity and constant-one preservation identify the affine and polynomial span ranks and unit membership.
693|depends_on|lem:finite-affine-coordinate-completion|Completes a proper basis of affine inputs to rank-sized coordinates.
693|depends_on|lem:ordinary-affine-restriction-ideal|Pullback ideal witnesses are re-expanded into coefficients of the original input tuple.
694|depends_on|lem:proper-affine-block-restriction|blockRestrictionData_exists supplies the actual restriction and literal witness interface for each proper block.
694|depends_on|lem:row-linear-polynomial-space|Dimension and total-degree bounds specify the common-kernel domain.
694|depends_on|lem:ordinary-affine-restriction-ideal|affineRestriction_image_finrank_le bounds each restriction image.
694|depends_on|lem:ordinary-restriction-kernel-bound|Square-condition binomial bounds and ceil-square-root estimates give the strict dimension deficit.
694|cites|lem:affine-family-removal-with-unit-blocks|Constructed witnesses meet that theorem's unit-or-literal interface; the removal theorem is an application, not a prerequisite of the kernel count.
695|depends_on|lem:row-linear-polynomial-space|Injectivity and degree of row-monomial exponents identify and expand the maximal-row coefficient.
695|depends_on|lem:binary-cube-degree-drop|cube_sum_cancel cancels monomials missing a selected row.
695|depends_on|lem:disjoint-binary-coordinate-pairs|Uses only flipColumn_label for the chosen coordinate bit sums, not the disjoint-pair packing existence theorem.
695|cites|lem:cube-residual-dual-separation|The local coefficient isolation prepares the separate board-specific separation application.
696|depends_on|lem:binary-cube-degree-drop|cubeDifference_degree and cubeDifference_ns supply degree drop and NS transport after generator images are checked.
696|depends_on|lem:disjoint-binary-coordinate-pairs|Coordinate-pair cardinality and disjoint endpoints construct the concrete residual data and bit differences.
696|depends_on|lem:functional-matching-normal-form|functionalUnaryBase_eq splits actual generators into Boolean, exclusion and row cases.
696|cites|def:ordinary-polynomial-proof-foundations|Uses the ordinary NS space and functional-base interface.
'''
for line in assertions.strip().splitlines():
 i,k,t,n=line.split('|',3);add(int(i),k,t,n)
notes={680:'Reviewed cycle/filling calls and matching-marginal definitions; no completeness theorem is silently used for the local cycle.',681:'Read the short relabeling proof: the cycle module import is only a transitive interface carrier, and no cycle/filling theorem is called.',682:'Reviewed row-set filling and bounded-functional bridge. Exported theorem names colliding with the downstream MatchingFiltration audit are definitions here, not backward dependencies.',683:'Full short induction is self-contained beyond polynomial algebra; substitution import is unused as a theorem. Publication link is motivation.',684:'Read actual initial-value proof and semantic clause bridge. Weakening import supplies interfaces, but no weakening theorem is called in this local bridge.',685:'Reviewed all three local cases and final weighted replay, including an actual substitute_weighted call absent from automatic discovery.',686:'Reviewed plan construction and replay calls. Ambiguous resolve and mono tokens are constructors/PC methods, not extra dependency edges.',687:'Coordinate proof invokes the unit-span/common-zero theorem then elementary dual-basis completion; predecessor completion is generalized, not used.',688:'Coordinate-restriction proof is local monomial extraction and Mathlib polynomial algebra; no current claim theorem dependency is present.',689:'Reviewed pullback and literal coefficient steps and image dimension call; supplied coordinates are hypotheses, not an invocation of completion.',690:'Only Mathlib imports and local real/binomial arithmetic; no direct current or historical claim dependency.',691:'Coordinate flips use the actual bitLabelEquiv; the pair packing proof is local counting.',692:'Cube cancellation, monomial support and degree-drop arguments are local; NS interface cited separately from proof prerequisites.',693:'Actual basis completion and inverse pullback factorization calls identify the three direct interfaces.',694:'Kernel proof combines four mapped project interfaces; removal theorem is only the downstream application.',695:'Uses row-monomial geometry, cancellation and coordinate flip identity; the packing existence theorem is not assumed.',696:'Generator images are checked casewise before cube-difference transport; MatchingFiltration import is not itself a proof dependency.',697:'Parameter closure proves its explicit geometric-growth inequalities locally with Mathlib limits; RestrictionKernelBounds import is unused as a project theorem.'}
for i in range(680,698):
 c=cs[i]; ev=[r['target'] for r in references(c) if '.lean' in r['target'] or '#lean-' in r['target']]
 rows.append({'position':i,'id':c['id'],'state':'reviewed','evidence':ev,'note':notes[i]+' Inventory covers recorded direct project/historical proof dependencies and substantive comparisons; library internals are outside the claim graph.','next_action':None,'source_fields_sha256':hashlib.sha256(json.dumps({k:c[k] for k in ('id','summary','assessment','record')},sort_keys=True,ensure_ascii=False).encode()).hexdigest()})
for e in edges:assert e['target']['id'] in by,e['target']['id']
(D/'patch_680_698.json').write_text(json.dumps({'base_revision':rev,'range':[680,698],'claims':rows,'relationships':edges},indent=2)+'\n')
print('closed',len(rows),'edges',len(edges))
