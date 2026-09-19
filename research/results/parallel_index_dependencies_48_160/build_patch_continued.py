#!/usr/bin/env python3
"""Build an additive proposal only; coordinator owns canonical registry updates."""
import json,re,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'tools'))
from claim_reviews import Evidence,claim_digest
D=json.loads((R/'research/claims/index.json').read_text()); C=D['claims']; REV=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
WEB='https://kbr.is-a.dev/math-research/#';GH='https://github.com/kbr-/math-research/blob/main/'
rows=[]
def add(s,t,k,scope,a=None,namespace='current',locator=None):
 source=C[s]['id'];target=C[t]['id'] if isinstance(t,int) else t
 anchor=a or re.search(r'/#([^ )]+)',C[s]['record'])[1]
 rows.append({'id':source+'::'+k+'::'+('' if namespace=='current' else namespace+':')+target,'source':{'namespace':'current','id':source,'locator':None},'target':{'namespace':namespace,'id':target,'locator':locator},'type':k,'scope':scope,'evidence':[WEB+anchor],'review_status':'reviewed','review':{'revision':REV,'date':'2026-09-19','reviewer':'Codex GPT-6 Astra parallel dependency worker','note':'Read source-relative proof and scope, including relevant correction; no new paper audit, computation replay or Lean verification.'}})
for s,t,k,n in [
(88,58,'depends_on','Occurrence OR comparison applies COPY to paired physical maximal non-OR children.'),
(88,59,'refines','Extends the NS copy bound to fully separated repeated occurrences rather than internally coherent line scopes.'),
(88,87,'depends_on','Repeats the repaired strict-support leaf construction, adding actual occurrence-copy witnesses.'),
(88,38,'depends_on','Earlier reference argument values use their sharp Booleanity certificates in schematic substitution.'),
(88,86,'cites','Uses flattened OR depth; bypassed subgroups may share the parent level.'),
(89,88,'cites','The separate physical occurrence convention supplies the definition of the two disjoint MP branches; freshness is proved directly.'),
(90,88,'depends_on','Occurrence-copy and strict leaf certificates supply the initial invariant and comparison costs.'),
(90,89,'depends_on','The selected proper interface roots are fresh for every retained axiom and conclusion input/target.'),
(90,64,'depends_on','Weighted input-system replay converts signed antecedents and negative/value conclusions.'),
(90,65,'depends_on','Uses the signed MP argument before deleting the additional occurrence-local interfaces.'),
(90,7,'depends_on','Fresh old-target elimination removes at most two interfaces with the stated per-node degree charge.'),
(91,90,'depends_on','The occurrence interface invariant supplies the final positive PHP input refutation.'),
(91,67,'depends_on','Ordinary affine clause/final-PHP images supply the weak-base endpoint.'),
(91,76,'applies','Optional recognized-root pruning uses the repaired theorem with the occurrence leaf ceiling.'),
(91,75,'applies','Optional simultaneous root/clause pruning uses the separate triangular polynomial bound.'),
(92,88,'cites','Allocates the fully separated occurrence trees only at actual proof leaves; the consequent-history structural induction is local.'),
(94,88,'depends_on','Occurrence-local leaf certificates and antecedent copy bounds start the inherited simulation.'),
(94,90,'depends_on','Reuses the preceding antecedent conversions, now with inherited rather than copied conclusions.'),
(94,92,'depends_on','Intact descendants and absent ancestors guarantee all witness availability and local freshness.'),
(94,93,'depends_on','Positive conclusions use their actual inherited inputs for degree-preserving zero replay.'),
(94,7,'depends_on','Negative/right and optional left OR interface removal uses fresh old-target transfer.'),
(94,64,'depends_on','Negative/value conclusions weight the actual input refutations and reuse completed companion proofs.'),
(94,91,'applies','The supplementary PHP endpoint and optional recognized-root consequences reuse the intact occurrence family transfer.'),
(95,80,'refines','MOD-first Booleanity extends from Boolean-constant coefficient modes to arbitrary polynomial substitutions into the typed domain.'),
(96,58,'depends_on','Uses the PC form of COPY with completed input differences at each OR node.'),
(96,88,'refines','Sharpens only the PC occurrence-copy ceiling to 2L; the NS leaf witness bound is not replaced.'),
(97,96,'applies','The bounded-degree upper proof uses final-line MOD-difference multiplication; the support lower bound is a direct missing-family countermodel.'),
(98,64,'depends_on','The scalar-refutation to nonzero-value direction weights by 1-u^(p-1) using finite-domain weighted input proofs.'),
(99,92,'depends_on','Uses inherited representatives and the established fresh-interface physical forest.'),
(99,94,'depends_on','Keeps the inherited OR conversions and source-height recurrence while refining MOD interfaces.'),
(99,98,'depends_on','Finite-domain conversions initialize MOD leaves and produce signed scalar MP transitions.'),
(99,96,'depends_on','Transfers child pre-power sums through the common 2L PC copy ceiling.'),
(99,88,'depends_on','Occurrence strict leaf certificates retain their genuine NS ceiling.'),
(100,97,'depends_on','Reuses the original frontier family and omitted-family countermodel for zero/nonzero scalar targets.'),
(101,92,'depends_on','The quotient requires descendant closure of the surviving forest and a live witness for every shared class.'),
(102,101,'depends_on','Shares only eventual survivors using the degree-preserving full-syntax affine quotient.'),
(102,92,'depends_on','Inherited-path ancestor removal preserves private-root freshness and immediate representative availability.'),
(102,99,'depends_on','The signed scalar recurrence applies after its MP comparisons become literal.'),
(102,88,'depends_on','Leaf certificates still allow private future cuts and keep their NS occurrence-copy bound.'),
(103,101,'depends_on','Coherent canonical argument values make signed multiplicities literal polynomial cancellations.'),
(103,97,'cites','Explains why changing the comparison polynomial via sharing escapes the unchanged-target support obstruction.'),
(104,102,'cites','The intended source application starts after the hybrid private cuts; the abstract Booleanity induction assumes the stated current modes.'),
(104,81,'cites','Direct-use restrictions for unit mode inherit the isolated Booleanity-port access contract.'),
(104,95,'depends_on','MOD nodes use domain-only Booleanity after the current substitution.'),
(104,80,'refines','Extends Boolean-constant products to nonconstant packed/base-zero images using sharp current certificates.'),
(105,104,'depends_on','Specialized sharp Booleanity certifies packed companion and isolated macro images within original degrees.'),
(105,81,'refines','Extends the outer port transfer to the compatible mixed modes and explicit direct-use image witnesses.'),
(106,105,'depends_on','The mixed-mode transfer preserves the incoming proof when named extra assumptions are explicitly discharged.'),
(106,50,'applies','Known weak-PHP row/collision/final-product image witnesses specify compatible endpoint modes.'),
(108,107,'depends_on','Composes the exact paired-factor normalization along one OR level; telescoping yields terminal-degree cost.'),
(109,56,'cites','The earlier core/linear-residual optimum has different hypotheses; the independent weighted-bin examples do not contradict it.'),
(110,101,'refines','Shares equal literal input spans using a degree-ordered basis of actual Boolean generators, rather than only identical syntax.'),
(110,102,'applies','The source application preserves planned private cuts and canonical survivor closure required by hybrid freshness.'),
(111,104,'depends_on','The PRODUCT-Bool identity preserves sharp Booleanity of the Boolean generator product.'),
(111,105,'depends_on','Uses the mixed-mode level induction and original-degree outer transfer with supplied retained NS witnesses.'),
(111,110,'applies','Its rank corollary chooses the degree-ordered actual Boolean basis so every input representation fits its own degree.'),
(112,53,'refines','Replaces extra residual factors by supplied ideal-membership witnesses with explicit C_i+s_F budgets while retaining the core.'),
(112,111,'cites','Uses the same supplied NS input-witness format; retained core companions replace the Boolean generator product in the direct proof.'),
(112,1,'applies','The absorption example uses the core prefix identity to express residuals in the core input ideal.'),
(113,58,'depends_on','COPY-NS with actual product degree supplies each OR increment in the sharper NS depth bound.'),
(113,59,'refines','Tightens the conservative NS formula-copy ceiling to 2(ell+1)L without claiming the depth-independent PC bound for NS.'),
(114,39,'refines','Rearranges the same distribution error into a directional unit certificate with a precise request set.'),
(114,1,'depends_on','Two matched prefix identities yield the displayed unit identity.'),
(114,38,'applies','The non-OR child variant needs the supplied sharp Booleanity port instead of actual child companions.'),
(115,39,'refines','Keeps the original normalizer assignment and sharpens its sufficient accuracy from four to two.'),
(115,114,'depends_on','Uses the actual-degree prefix accounting of the directional distribution identity.'),
(115,38,'applies','The non-OR case uses sharp Booleanity through twice the child degree.'),
(116,41,'refines','Strengthens the source-coordinate portfolio induction with each prefix coordinate weighted by its own input bound.'),
(116,115,'depends_on','Refined distribution error cost closes the structural induction already at h>=2.'),
(116,40,'depends_on','Original-degree local image certificates give LD transfer through hierarchical normalization.'),
(117,87,'depends_on','Strict signed leaf certificates omit the highest source OR level.'),
(117,99,'depends_on','The inherited signed scalar induction classifies positive OR and value/MOD conclusion support.'),
(117,102,'depends_on','Literal hybrid MP comparisons introduce no new highest-level companion requirements.'),
(117,50,'applies','The ordinary clause/final-PHP endpoint and level-preserving preprocessing retain the one-time support omission.'),
(118,104,'refines','Extends sharp mixed-mode Booleanity from old-base zero to supplied sharp zero proofs over retained earlier levels.'),
(118,105,'depends_on','Applies the same constant substitution and original-degree outer transfer once the new images are supplied.'),
(119,44,'cites','Uses the previously recorded unsimplified six-gate schema and literal coherent arguments.'),
(119,46,'depends_on','The interpolation error m-ab-(1-a)c=(a²-a)R_p certifies the new forward gate.'),
(119,118,'depends_on','The forward product is earlier-zero with an NS certificate through its actual degree.'),
(119,104,'depends_on','Rebuilt sharp child Booleanity and ordinary packing handle the five other gates simultaneously.'),
(120,119,'depends_on','The complete axiom certificate uses the new forward epsilon and the five packed gate images.'),
(120,46,'depends_on','The interpolation identity gives q=m-H_a S and the displayed error decomposition.'),
(120,95,'depends_on','MOD-value Booleanity of m has its degree-nonincreasing domain certificate.'),
(120,104,'applies','Source argument substitution uses the last argument sharp Booleanity under compatible preceding constant modes.'),
(121,98,'applies','Only the comparison full-MP route uses scalar conversion; direct fresh frontier zero replay is proved by constant specialization.'),
(122,121,'applies','Saved direct and full-join traces instantiate the matched MOD-to-OR replay, with specified uncomputed oversized baseline.'),
(122,98,'applies','The recorded full signed joins include scalar conversions and finite-domain weighted assumptions.'),
(123,102,'refines','Expands the private cut plan by the consumed MOD antecedent argument roots while preserving survivor descendant closure.'),
(123,92,'depends_on','Origin-leaf consequent histories supply absent ancestors and intact right representatives.'),
(124,123,'depends_on','The expanded cut plan supplies freshness for current frontier roots after sharing.'),
(124,96,'depends_on','Nonliteral goal-input pairs use intact subtree copy proofs through 2L.'),
(124,121,'depends_on','Uses the PC input-witness variant of direct frontier zero replay.'),
(124,99,'depends_on','Unchosen nodes retain the ordinary signed scalar recurrence.'),
(124,117,'applies','New frontier/input witnesses stay below the relevant OR level and preserve highest-layer omission.'),
(124,91,'applies','Intact final clause subtrees preserve the prior occurrence PHP endpoint and eligible later root pruning.'),
(125,123,'applies','Finite structural fixtures exercise the expanded cut plan and bad-merge freshness control.'),
(125,124,'applies','Nonidentity witnesses show why the goal-input copy repair is needed; they are not companion models disproving agreement.'),
(126,72,'refines','Common-ceiling zero replay is used after the MP join with explicit retained goal inputs, not unconditional input proofs.'),
(126,93,'depends_on','Even-negated positive conclusions first replace 1-P_B by the actual input assumptions.'),
(126,124,'depends_on','Uses the intact goal-input comparison argument and its nonliteral-pair 2L witnesses.'),
(126,123,'depends_on','Extends the existing ancestor-closure cut schedule to both selected antecedent copies.'),
(126,96,'depends_on','Selected-pair and aggregate input-copy proofs fit the shared PC ceiling.'),
(126,99,'depends_on','Keeps the complete signed MP join and scalar-domain obligations before partial cleanup.'),
(126,117,'applies','Selected roots remain below implication OR level, preserving the support refinement.'),
(126,91,'applies','The intact final clause family preserves the ordinary-PHP and eligible root-pruning consequences.'),
(127,126,'applies','Finite two-copy traces and missing-goal models test partial-cut replay; they do not certify a generic source compiler.'),
(128,92,'depends_on','The live-forest history supplies absent ancestors above active representatives.'),
(128,101,'depends_on','Precomputed ancestor-closed cuts allow canonical quotienting only on descendant-closed survivors.'),
(128,99,'cites','The schedule is placed after positive outputs of the existing signed scalar invariant.'),
(128,96,'depends_on','Intact matched non-OR source/goal children supply all cleanup inputs through 2L.'),
(129,128,'depends_on','Saturated maximal cleanup has degree max(D,2L) and preserves protected representatives.'),
(129,99,'depends_on','Uses the full signed recurrence with general copy witnesses at ordinary nodes.'),
(129,96,'depends_on','Future cuts make ordinary antecedent comparisons nonliteral; the general PC copy ceiling supplies them.'),
(129,102,'cites','The earlier narrower cut plan had literal comparisons; that assertion is not inherited by the enlarged plan.'),
(129,117,'applies','All newly requested copy blocks remain below the original maximum OR level.'),
(129,91,'applies','Protected intact clause families retain the ordinary-PHP endpoint.'),
(129,126,'refines','Includes covered-root removals of the partial MOD rule, while matched shortcut proof omission remains separate.'),
(130,128,'applies','The structural fixture implements maximal cleanup and exposes roots not syntactically covered by its goal frontier.'),
(131,58,'depends_on','Reuses the exact COPY identity with supplied virtual companion derivations and weighted prefixes.'),
(131,96,'refines','Extends the 2L PC copy ceiling to the stated virtual-prefix/companion interface, conditional on all supplied witnesses.'),
(131,116,'applies','The source-coordinate clause/CD/distribution portfolio supplies the required weighted prefix and structural companion premises.'),
(133,1,'depends_on','Assignment-tree splitting uses parent/child prefix identities with the split Boolean equation.'),
(134,133,'depends_on','Specializes the exhaustive assignment-tree certificate to the exact weak PHP base.'),
(135,72,'refines','Constant replay allows specialized retained ancestors with supplied input witnesses in the resulting goal-relative system.'),
(135,96,'applies','The intact-subtree sufficient case supplies selected input witnesses via 2L copy agreement.'),
(136,135,'applies','Nested satisfiable target fixtures retain the exact nonconstant ancestor and actual goal-dependent selected images.'),
(137,101,'depends_on','Affine canonical quotient is applied only to the complement of the ancestor-private set.'),
(137,92,'depends_on','Inherited representative history preserves intact immediate proof interfaces and origin-leaf locality.'),
(137,135,'depends_on','Each cleanup cut keeps all affected retained ancestor axioms with specialized inputs.'),
(137,96,'depends_on','Only intact source/goal subtrees supply automatic cleanup and ordinary comparison witnesses through 2L.'),
(137,99,'depends_on','General nonliteral comparisons fit the original signed scalar height recurrence.'),
(137,117,'applies','New witness support lies below the original maximum source OR level; substitutions add no variables.'),
(137,128,'refines','Separates private ancestor closure from the actual cut set, allowing eligible nonmaximal roots and modified retained auxiliaries.'),
(138,137,'depends_on','The final representative and designated clause subtrees stay protected despite modifications elsewhere.'),
(138,36,'depends_on','Designated row/collision affine assignments and original-degree images discharge the final clause assumptions.'),
(139,137,'applies','Conditional finite forests test private modified ancestors, nonmaximal cuts and copy-subtree availability.'),
(139,136,'cites','The prior 24 local replay traces provide the saved algebraic control; this new check is structural, not a fresh replay.'),
(140,104,'refines','Literal nonzero-coordinate and all-zero-input modes are zero-image special cases of the mixed assignments.'),
(140,137,'depends_on','The full interleaved source schedule uses the same ancestor-private compatibility and protected-representative induction.'),
(140,138,'depends_on','Protected-clause endpoint remains the stated PHP transfer after constant propagation.'),
(140,139,'applies','Saved modified U_j tuples have literal constant-one inputs, so the new zero-product mode applies analytically.'),
(141,140,'applies','Exact alternating-chain fixtures test the literal zero/product-one propagation and all image certificates.'),
(142,140,'refines','Replaces literal nonzero input detection by one supplied current-system PC proof of g_j-c; exact product image need not vanish identically.'),
(143,142,'depends_on','The nonzero-input local rule uses the copy-plus-opposite-goal witness for g_j-1.'),
(143,96,'depends_on','Intact opposite-signed source/goal children give the required copy difference through 2L.'),
(143,137,'depends_on','Ancestor-private scheduling permits nonconstant exact images while protecting witness subtrees and representatives.'),
(143,138,'applies','Retains the protected-clause endpoint; other preprocessing still needs current witnesses.'),
(144,142,'applies','Literal and copied finite witnesses instantiate exact-image nonzero-input replay.'),
(144,143,'applies','The independent-copy cases realize the opposite-goal match, with missing-goal and false-zero-collapse controls.'),
(145,42,'depends_on','Constant field-selector factorization realizes 1-s^(p-1) from homogeneous tuple combinations.'),
(145,142,'depends_on','Completed witness reuse gives the same max(D,C) all-companion replay bound.'),
(145,98,'depends_on','Negative MOD nonzero residue uses finite-domain power-to-scalar conversion.'),
(145,96,'depends_on','Actual matched argument aggregates require intact source/goal copy agreement through 2L.'),
(145,137,'applies','The source consequence requires ancestor-private scheduling and exact retained images.'),
(145,138,'applies','The protected clause endpoint keeps its earlier limited scope.'),
(146,95,'applies','Selector Booleanity uses the same domain-only power mechanism as substituted MOD values; the goal is not used.'),
(147,145,'obstructs','Zero-sum input vectors invalidate extension of the aggregate-only rule to the excluded residues; they do not refute the valid two criteria.'),
(148,145,'refines','Shows selector accuracy p-1 is necessary for constant assignments in the explicit free Boolean-input case, not in an arbitrary PHP-constrained base.'),
(149,145,'depends_on','Portfolio selection uses the goal aggregate witnesses to choose Boolean-preserving selectors at the permitted accuracy.'),
(149,104,'refines','Extends rebuilt sharp Booleanity to projection and selector images without relying on discarded goals.'),
(149,146,'depends_on','Field selectors retain sharp goal-free NS Booleanity.'),
(149,138,'applies','The stated post-source construction starts from the protected weak-PHP clause endpoint.'),
(150,149,'refines','Within the stated portfolio, rebuilds the sharp certificate using the actual current ENS-level support.'),
(151,149,'depends_on','Current modified input values have the sharp goal-free Booleanity certificates needed for packing.'),
(151,150,'depends_on','Those certificates can be taken in strictly earlier current levels despite higher-level original syntax.'),
(151,110,'depends_on','Uses the degree-ordered basis of actual Boolean inputs and same-span affine quotient.'),
(151,111,'depends_on','The rank corollary supplies original-degree companion images for rank-at-most-accuracy removal.'),
(151,138,'depends_on','Post-simulation refutation starts after the protected-clause endpoint with no remaining goal assumptions.'),
(152,83,'cites','Explains why a positive-pebbling old base differs from the domain-only hypothesis of the older normalizer obstruction.'),
(152,151,'cites','The added independent y coordinate keeps rank above accuracy, so the example does not contradict rank packing.'),
(153,64,'depends_on','Weights the supplied probe-zero refutation by the selector product and inserts actual weighted-probe witnesses.'),
(153,149,'depends_on','The compatible Boolean product identity gives unconditional sharp Booleanity of the selector product.'),
(153,42,'depends_on','Field-selector factorization realizes each probe factor using p-1 constant rows.'),
(154,153,'depends_on','Realizes the same extracted selector H with affine paired rows and retains its supplied witness cost.'),
(154,56,'applies','Uses the existing telescoping factor-packing mechanism in the sufficient affine-pair special case; no general optimum is claimed.'),
(154,137,'applies','The stated source consequence additionally requires the existing ancestor-private and surviving-witness hypotheses.'),
(155,153,'obstructs','Punctured antichain violation cubes force many sufficient probe factors despite PC-three input refutations; this is not a PHP source occurrence claim.'),
(156,153,'applies','The saved F3 fixture checks weighted selector extraction even though the goal already supplies H more cheaply.'),
(156,154,'applies','Its affine realization uses a nonzero coefficient-field image; the row-count optimality is a direct Boolean-cube degree argument.'),
(157,64,'depends_on','Weighted replay of complete conditional unit proofs derives the three-term OR relation.'),
(157,149,'cites','Compatible genuine/value portfolios retain separate Booleanity facts; the abstract interface theorem does not promise sharp NS Booleanity.'),
(158,64,'depends_on','Weights the supplied parent input refutation by ab, using only child annihilator proofs.'),
(158,157,'refines','Sharpens the zero-parent specialization and removes the need for child conditional unit proofs.'),
(159,158,'depends_on','The strictly earlier PC-three parent-input witness and child annihilators yield the degree-nine virtual OR relation.'),
(159,155,'depends_on','The same seven-vertex antichain cube gives the constant-row lower bound while all old assignments extend to the retained child system.'),
]:add(s,t,k,n)
# Explicit historical/source imported components.
for i,n in [(95,'Polynomial MOD-value Booleanity uses degree-nonincreasing mixed-domain division.'),(98,'The scalar conversions need the degree-p deg(u) domain proof of u^p-u.'),(109,'Polynomial coefficient field images use typed-domain reduction through pT_*.'),(154,'Affine coefficient field images have degree-p domain certificates and must not be discarded.')]:
 add(i,'lem:fieldreduction','depends_on',n,namespace='historical',locator=GH+'php_codex_handoff/manuscript/chapters/01_foundations.md#lem-fieldreduction')
add(117,'BIKPRS-1996-simulation','depends_on','The highest-layer claim uses the audited specific axiom presentation: Boolean frames and the unsimplified MOD empty/recursion schemas.',namespace='external',locator=GH+'research/notes/SOURCE_AUDIT.md#bikprs-actual-simulation-structure')
add(133,'lem:prefixcertificate','cites','Contrasts the historical one-chain pebbling construction with the exhaustive Boolean assignment tree; the new split identity is explicit.',namespace='historical',locator=GH+'php_codex_handoff/manuscript/chapters/07_elimination.md#lem-prefixcertificate')
add(134,'Razborov-1998-Theorem-3.1','depends_on','The family-count-independent elimination obstruction contrasts the augmented certificate with the already-audited weak-base PC lower bound.',namespace='external',locator=GH+'research/notes/SOURCE_AUDIT.md#razborov-base-and-residual-pc-lower-bound')
for i in [152,155]:
 add(i,'lem:pebblingpc','depends_on' if i==152 else 'cites','Uses the topological PC-three pebbling mechanism; '+('omits the sink equation to derive 1-x_N in the consistent positive base.' if i==152 else 'the proof and antichain violation construction are restated locally.'),namespace='historical',locator=GH+'php_codex_handoff/manuscript/chapters/07_elimination.md#lem-pebblingpc')
add(152,'imp:pebbling','depends_on','The recorded all-field NS pebbling degree input excludes low-degree y(1-x_N) certificates after specialization.',namespace='historical',locator=GH+'php_codex_handoff/manuscript/chapters/07_elimination.md#imp-pebbling')
# One concise claim-specific inventory disposition, with all precise roles in edges.
standalone={89:'Freshness follows directly from the physical occurrence convention and disjoint branches; no global sharing assertion is imported.',92:'Live-forest claims are proved by direct induction on inherited consequent history.',93:'Self-contained constant specialization of a fresh block with its actual input assumptions; no learned-input premise.',107:'Exact paired-factor identity and ordinary-degree lower bound prove the local optimum directly; no same-degree global transfer follows.',109:'Weighted optimum uses local unique factorization, disjoint support and anchor exchange; earlier linear packing is contextual.',110:'Degree-ordered basis and companion/field images are explicit; source scheduling is a separately scoped application.',114:'Directional identity and local degree ledger are explicit; earlier distribution proof is a scoped refinement, not a new unrelated result.',121:'The direct replay is a self-contained fresh constant specialization; the scalar conversion is only the alternative full-MP comparison.',125:'Finite structural evidence supplies nonliteral input and bad-sharing witnesses, not countermodels to valid copy proofs.',127:'Finite complete traces and missing-goal models exercise the partial cut; no new trace replay was performed.',130:'Saved finite syntax/forest construction demonstrates incomplete coverage, not essential-support hardness.',132:'Self-contained Boolean-poset inversion and union bound; the safe h>D regime is explicitly inactive.',136:'Recorded nested target traces and models distinguish goal-dependent selected images from specialized retained ancestor axioms.',139:'Structural conditional forests apply the local algebra analytically; no claim that their conditional leaves are primitive-Frege axioms.',141:'Explicit alternating source/image certificates and recorded finite models check literal constant propagation.',144:'Saved literal/copy witnesses preserve nonconstant images and reject false zero-collapse after removing goals.',147:'Self-contained zero-sum coefficient model rules out only the excluded aggregate-only residues.',148:'The free-input NOR degree argument proves constant-assignment accuracy necessity; no PHP-constrained or polynomial-coefficient lower bound is asserted.',150:'Ordinary polynomial support induction refines the compatible Booleanity portfolio only.',155:'Antichain violation cube proof is explicit; the familiar topological PC proof is restated, not a new source audit.',156:'Explicit F3 identities, field image, Boolean-cube optimality and saved replay traces; no new numerical checks.',159:'Retained child models project onto every old assignment, permitting reuse of the prior antichain constant-row lower bound.'}
import importlib.util
spec=importlib.util.spec_from_file_location('deps',R/'tools/claim-dependencies.py');deps=importlib.util.module_from_spec(spec);spec.loader.exec_module(deps)
text=(R/'notebook.html').read_text();book=deps.notebook_parser(text);E=Evidence();reviews=[]
for i in range(88,160):
 c=C[i];targets=re.findall(r'\]\((https://[^)]+)\)',c['record']);targets += [v for e in rows if e['source']['id']==c['id'] for v in e['evidence']]
 # Fingerprint actual containing headings for nonheading anchors; no silent source omission.
 normalized=[]
 for x in targets:
  if '/#' in x:
   a=x.split('/#',1)[1];_,_,actual,_=deps.source_excerpt(book,text,a);x=WEB+actual
  normalized.append(x)
 note=standalone.get(i,'Reviewed the actual proof/application passages and the individually scoped roles recorded in this proposal; direct algebraic steps remain in the source, and proof-system/goal/copy hypotheses are retained.')
 reviews.append({'id':c['id'],'claim_sha256':claim_digest(c),'state':'reviewed','note':note,'next_action':None,'evidence':[{'target':x,'sha256':E.sha256(x)} for x in dict.fromkeys(normalized)]})
scan=json.loads((R/'research/results/index_dependency_review_20260919/candidates.json').read_text());decisions=[]
for x in scan['candidates']:
 if x['source'] not in {c['id'] for c in C[88:160]}:continue
 matching=[e for e in rows if e['source']['id']==x['source'] and e['target']['namespace']=='current' and e['target']['id'] in x['targets']]
 if len(matching)==1:
  e=matching[0];decisions.append({'candidate_id':x['id'],'candidate_sha256':x['candidate_sha256'],'state':'accepted','relation_id':e['id'],'reason':'Reviewed exact source role: '+e['scope']})
 else:decisions.append({'candidate_id':x['id'],'candidate_sha256':x['candidate_sha256'],'state':'rejected','relation_id':None,'reason':'Coarse/shared-region reference or duplicate of separately scoped roles; the explicit reviewed inventory replaces automatic ownership.'})
p=Path(__file__).parent/'patch_continued.json';p.write_text(json.dumps({'baseline_revision':REV,'completed_range':[88,160],'edges':rows,'reviews':reviews,'candidate_decisions':decisions,'scope':'Source-relative inventory only; no mathematical or kernel re-verification. Coordinator deduplicates existing edge IDs and refreshes incident endpoint review hashes.'},indent=2)+'\n');print(json.dumps({'reviews':len(reviews),'edges':len(rows),'candidate_decisions':len(decisions),'output':str(p)}))
