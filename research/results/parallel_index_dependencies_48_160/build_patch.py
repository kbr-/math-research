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
# Roles are manually reviewed; indices are pinned by the output's source digests.
for s,t,k,n in [
(48,4,'depends_on','The MP coefficient identity and degree ledger give the balanced-tree NS recurrence.'),
(49,40,'refines','Keeps the substituted target explicit in the same final-cofactor transfer argument; the proof is restated locally.'),
(50,35,'depends_on','Boundary-only removal uses the earlier row/collision clause product certificates.'),
(50,36,'depends_on','Simultaneous clause removal uses the existing affine clause assignments and coefficient field images.'),
(50,49,'depends_on','The original-degree target-image transfer changes the final product target into one.'),
(51,48,'depends_on','DIRECT-AP supplies the theorem-approximation derivation before any clause assumptions.'),
(51,50,'depends_on','The final boundary and ordinary clause substitution turns that derivation into the weak-base refutation.'),
(51,47,'applies','Only the combined h>=4 variant adds the preceding eligible schema preprocessing.'),
(52,1,'depends_on','Uses the core telescoping identity to assign the first coefficient vector; the local overhead does not establish global transfer.'),
(53,38,'applies','Sharp source Booleanity supplies the residual premises for source inputs; the abstract theorem accepts supplied certificates.'),
(54,36,'depends_on','Uses the ordinary row/collision affine witness on the selected subtuple and zero on the additional coordinates.'),
(55,53,'depends_on','CORE-images and CORE-budget provide the retained-core mode and its original-degree images.'),
(55,54,'depends_on','Clause-containing mode supplies the additional base-witness cases.'),
(55,51,'depends_on','Extends the combined direct-PHP structural induction at the same LD0 ceiling.'),
(56,53,'depends_on','Companion-image proof reuses CORE-images, after explicit factor-bin packing for independent linear inputs.'),
(57,56,'cites','The introductory discussion applies FACTOR-T to literal forests; the counterexample itself is a direct bounded-height tautology construction.'),
(58,1,'depends_on','The two block prefix identities yield the exact COPY identity and coefficient bounds.'),
(59,58,'depends_on','OR step invokes COPY and COPY-NS; MOD and negation steps are given locally.'),
(60,59,'depends_on','Proper input/value copy certificates pay the additional NS agreement cost.'),
(60,4,'depends_on','The original MP expansion is modified by antecedent and consequent copy differences.'),
(60,50,'applies','Its ordinary-PHP consequence uses the already established final and clause substitutions.'),
(61,53,'refines','Allows supplied nonliteral matched-input differences and charges their NS excess Gamma explicitly.'),
(63,61,'depends_on','Uses MATCH-products and MATCH-image with final-line PC reuse instead of multiplying whole NS certificates.'),
(63,61,'refines','At a common PC ceiling removes the NS matching surcharge under the stated coordinate-degree hypothesis.'),
(62,59,'applies','Only the supplementary comparison along a proof-line chain invokes FORMULA-COPY; the chain-height proof is graph-theoretic.'),
(65,7,'depends_on','Negative axiom boundaries require fresh one-block old-target elimination.'),
(65,64,'depends_on','Weighted replay converts positive antecedents, negative conclusions and value conclusions.'),
(65,59,'depends_on','The general line-scoped invariant uses old comparison certificates with ceiling C_copy.'),
(65,38,'depends_on','Value-conclusion conversion uses sharp old Booleanity through 2L.'),
(66,65,'depends_on','Specializes the signed invariant to canonical proper evaluations with literal comparisons C=0.'),
(66,65,'refines','Canonical sharing eliminates only the copy-agreement cost, while private outer boundaries stay fresh.'),
(67,65,'depends_on','The signed positive boundary invariant refutes the input tuple of final clause products.'),
(67,66,'applies','The optional shared-proper construction gives the sharper SHARED-PROPER ceiling.'),
(67,50,'depends_on','Ordinary clause and final-PHP substitutions identify the extra inputs with weak-base generators.'),
(67,63,'applies','The supplemental proper-input core-cover consequence requires the retained-core and factor-count hypotheses.'),
(68,59,'cites','Explains why the uniform NS copy ceiling cannot be silently replaced by an actual-input-degree multiple.'),
(68,61,'cites','Identifies the NS matching budget that remains relevant; degree padding is explicitly unused.'),
(68,67,'cites','The established PC endpoint requires no padding; the elementary padding construction is not incorporated there.'),
(70,69,'depends_on','Reuses the explicit degree-four PC target derivation, old satisfying model and saved degree-four separator to build the normalized design.'),
(71,7,'applies','The negative fixture explicitly executes old-target elimination and records its finite-prime degree costs.'),
(71,64,'applies','Positive antecedent/value-conclusion traces instantiate weighted replay using actual companions and domain Booleanity.'),
(71,65,'applies','The saved signed MOD traces instantiate the invariant; they are not an arbitrary Frege compiler.'),
(72,63,'refines','Specializes the common-PC-ceiling principle to zero coefficient assignments; no retained core or factor-count premise is needed.'),
(73,72,'depends_on','Zero-removal uses strictly earlier input proofs at one common ceiling.'),
(73,87,'depends_on','The repaired application uses constructed strict-support certificates; proper-descendant containment alone is insufficient.'),
(73,66,'depends_on','Canonical proper coordinates match the recognized signed leaf inputs in the shared-proper simulation.'),
(73,71,'applies','The supplementary negative-fixture replay uses NEG-inputs; it does not justify the general strict-support hypothesis.'),
(76,74,'depends_on','Positive roots extract older coefficient witnesses from the supplied ordinary NS unit certificate.'),
(76,75,'depends_on','Triangular polynomial replay composes all positive/negative local assignments with explicit T and C costs.'),
(76,73,'depends_on','Negative roots use the repaired zero-mode input certificates.'),
(76,87,'depends_on','Strict-support construction replaces the false automatic proper-descendant justification.'),
(76,50,'depends_on','The PHP endpoint combines existing clause and final-product modes with the selected axiom roots.'),
(77,74,'applies','The saved nested projection coefficients instantiate zero-specialization extraction; the separate degree-seven composition is an explicit prescribed-witness control.'),
(78,77,'corrects','Clarifies the double-negation wrapper needed for the saved upper projection tuple; polynomial identities and the general extraction theorem remain unchanged.'),
(79,1,'depends_on','The flattened projection uses the exact argument-block prefixes; the remaining companion representations are explicit identities.'),
(80,1,'depends_on','Retained OR-product Booleanity uses the ordinary prefix identity with fresh unchanged coefficients.'),
(81,80,'depends_on','Each isolated Booleanity-port image receives the sharp specialized certificate fitting its original polynomial degree.'),
(81,79,'applies','The supplementary projection specialization has all inner/root companion images zero; applicability to a complete PHP proof remains unproved.'),
(82,65,'obstructs','Shows that the positive-antecedent weighted replay cannot replace required actual companions by Booleanity alone; it does not refute the invariant with those companions.'),
(83,1,'depends_on','Telescoping the substituted product produces the NS input cofactors after domain vanishing is proved.'),
(84,83,'depends_on','NS-normalizer converts the imported pebbling NS degree lower bound into the coefficient-degree obstruction.'),
(84,74,'cites','Contrasts the stronger supplied NS certificate in positive-leaf extraction; that lemma is not needed for the obstruction proof.'),
(85,83,'depends_on','Only the claimed optimal affine coefficient degree at accuracy one invokes NS-normalizer; the finite NS/PC and constant-accuracy proofs are explicit.'),
(86,73,'corrects','The original negative-leaf support explanation incorrectly inferred strict ENS level from arbitrary proper containment.'),
(86,76,'corrects','The original all-axiom-root automatic application used the same false strict-level inference; conditional triangular theorem survives.'),
(86,72,'cites','The conditional learned-input theorem already assumes strict support and is not retracted.'),
(86,75,'cites','The conditional triangular theorem retains its stated strictly earlier-ring hypothesis.'),
(86,65,'cites','Private-boundary elimination uses freshness rather than the false strict-level inference and is not retracted.'),
(87,38,'depends_on','Earlier substituted argument Booleanity certifies the schematic Boolean-domain identities.'),
(87,86,'corrects','Constructs sufficient strict-support certificates under the genuine flattened source convention, repairing the support gap identified in that audit.'),
]: add(s,t,k,n)
# Source-theorem links use local published audit/immutable handoff locators, not fresh source claims.
BIK=GH+'research/notes/SOURCE_AUDIT.md#bikprs-actual-simulation-structure'
for i,n in [(48,'Audited balancing, Lemmas 6.10 and 6.12 supply approximation and logical-axiom certificates.'),(60,'Source axiom-template bounds and balancing supply coherent line-scoped leaf certificates.'),(65,'The axiom-leaf bound A is the source simulation input; the elimination argument is new relative to that bound.'),(86,'Section 1 depth convention and Definition 6.8(5) flatten OR clusters, permitting same-level proper subgroups.'),(87,'Lemmas 6.11–6.12 give finite schematic comparison bounds; the local proof separately supplies strict-support reasoning.')]:
 add(i,'BIKPRS-1996-simulation','depends_on',n,namespace='external',locator=BIK)
add(57,'thm:nested','cites','Contrasts the historical fresh genuine-refutation batch theorem with raw inclusion forests; the example does not disprove that theorem.',namespace='historical',locator=GH+'php_codex_handoff/manuscript/chapters/08_batching.md#thm-nested')
add(84,'lem:pebblingpc','depends_on','Historical degree-three topological PC derivation supplies the cheap-PC side of the separation.',namespace='historical',locator=GH+'php_codex_handoff/manuscript/chapters/07_elimination.md#lem-pebblingpc')
add(84,'imp:pebbling','depends_on','Reuses the previously imported all-field Gamma(1,r) NS lower bound and encoding; no new paper audit.',namespace='historical',locator=GH+'php_codex_handoff/manuscript/chapters/07_elimination.md#imp-pebbling')
for i,n in [(56,'Removed polynomial coefficient field equations have typed-domain certificates through pT.'),(74,'Extracted older coefficients have domain certificates beta^p-beta through pA.'),(80,'MOD-value Booleanity is obtained by degree-nonincreasing typed-domain division.'),(83,'Boolean-cube vanishing of P_beta supplies an ordinary NS domain certificate within its degree.'),(87,'Schematic vanishing uses Boolean-domain division before substituting earlier argument certificates.')]:
 add(i,'lem:fieldreduction','depends_on',n,namespace='historical',locator=GH+'php_codex_handoff/manuscript/chapters/01_foundations.md#lem-fieldreduction')
notes={
48:'The source axioms and MP recurrence are explicit; no ordinary row-assumption prelude is used.',49:'The cofactor argument is given directly and refines hierarchical normalization by preserving the substituted target.',50:'Separated boundary-only clause certificates, simultaneous clause assignments, and target-image transfer.',51:'Core direct theorem uses DIRECT-AP plus final/clause removal; extra preprocessing is only the combined variant.',52:'Local telescoping identity with supplied Booleanity, not a global compatibility theorem.',53:'Affine images are proved directly; source Booleanity is an application of the abstract supplied premise.',54:'Ordinary clause witness is extended by zero additional coordinates and global affine replay.',55:'Combines the three explicitly identified modes under disjoint selection and retained-core requirements.',56:'Reviewed factor-bin construction, retained-core companion images, domain images and independent-input sharpness.',57:'Direct tautology counterexample; contextual forest estimates and historical fresh batching are citations, not counterexample premises.',58:'Exact prefix expansion and local NS/PC accounting; no dependency on future formula-copy claims.',59:'Source-depth induction invokes the block COPY identity, with local MOD-power algebra.',60:'Copy certificates and original MP identity supply the simulation; imported leaf bounds are identified separately.',61:'Extends literal core cover with matched differences and explicit NS Gamma budget.',62:'Chain graph proof is self-contained; its additional comparison corollary uses formula-copy agreement.',63:'Reuses matched-core product/image identities with PC final-line multiplication; scoped refinement not NS strengthening.',64:'Self-contained weighted inference replay with supplied input-product proofs; no Booleanity premise.',65:'Reviewed all signed leaf, antecedent and conclusion conversions, freshness and degree recurrence.',66:'Resolved shared containing-anchor ambiguity: this is the C=0 canonical-proper specialization of the preceding invariant.',67:'Uses boundary invariant plus ordinary PHP substitutions; optional core-cover and shared-proper claims remain separately scoped.',68:'Elementary domain-padding observation is independent; its cited copy budgets are context, not assumptions.',69:'Explicit COPY-gap identity and recorded finite dual certify the finite separation; no new numerical replay.',70:'Resolved shared-anchor ownership to the normalized-design paragraph, which uses the old model and degree-four target/dual data.',71:'Finite trace demonstration uses old-target and weighted replay and instantiates the signed invariant.',72:'Direct strict-level zero substitution replay; related common-ceiling theorem is a refinement relationship.',73:'Read original and repair: current application requires strict-support lemma and common ceiling max(B,A_*), not mere proper containment.',74:'Direct cofactor zero specialization plus typed-domain reduction, conditional on supplied older-ring NS certificate.',75:'Direct well-founded level induction and polynomial PC substitution with supplied earlier image proofs; no flattened-NS conclusion.',76:'Read original and corrected ledger; root removal now uses strict-support construction, witness extraction and triangular replay.',77:'Saved witness extraction example is separate from its explicit prescribed-degree composition control; syntax clarification remains linked.',78:'Corrects only the source-syntax interpretation of the saved upper tuple, not its polynomial identities.',79:'Exact flattened input tuple, telescoping identity and packed inner factors give local Booleanity requests.',80:'Retained products use prefix certificates; MOD case uses typed domains; Boolean-constant hypothesis is essential.',81:'Port-image replacement uses specialized Booleanity with the original-degree cofactor budget, and only applies to isolated ports.',82:'Direct all-zero coefficient countermodel blocks Booleanity-only positive antecedent conversion; input equations are not retained axioms.',83:'Direct soundness, Boolean-domain division and telescoping proof; only old domain base and all-companion images qualify.',84:'Imported pebbling NS lower bound and historical PC-three proof instantiate normalizer obstruction; not a PHP lower bound.',85:'Explicit finite PC proof, NS identity and dual plus punctured-cube constant-accuracy proof; normalizer lemma supplies accuracy-one T optimality.',86:'Read source convention and exact downstream corrections; only automatic strictness claims fail.',87:'Read positive and negative strict-support constructions, source comparison input and substituted earlier Booleanity.'}
E=Evidence();reviews=[]
for i in range(48,88):
 c=C[i];targets=re.findall(r'\]\((https://[^)]+)\)',c['record'])
 targets += [e for r in rows if r['source']['id']==c['id'] for e in r['evidence']]
 if i in (73,76):targets += [WEB+'levels-positive-support',WEB+'levels-negative-support']
 targets=[x.replace('#copy-shared-proper','#copy-signed-boundary-elimination').replace('#copy-design-control','#copy-ns-pc-separation') for x in targets]
 targets=list(dict.fromkeys(targets))
 reviews.append({'id':c['id'],'claim_sha256':claim_digest(c),'state':'reviewed','note':notes[i],'next_action':None,'evidence':[{'target':x,'sha256':E.sha256(x)} for x in targets]})
# Resolve only uniquely matching accepted candidates; unresolved or contextual many-target links stay explicit.
scan=json.loads((R/'research/results/index_dependency_review_20260919/candidates.json').read_text());decisions=[]
for x in scan['candidates']:
 if x['source'] not in {c['id'] for c in C[48:88]}:continue
 matching=[e for e in rows if e['source']['id']==x['source'] and e['target']['namespace']=='current' and e['target']['id'] in x['targets']]
 if len(matching)==1:
  e=matching[0];decisions.append({'candidate_id':x['id'],'candidate_sha256':x['candidate_sha256'],'state':'accepted','relation_id':e['id'],'reason':'Reviewed exact source role: '+e['scope']})
 else:
  decisions.append({'candidate_id':x['id'],'candidate_sha256':x['candidate_sha256'],'state':'rejected','relation_id':None,'reason':'Candidate is a coarse/shared-region reference or duplicates multiple individually scoped roles; explicit reviewed edges and source inventory supersede its automatic ownership proposal.'})
out={'baseline_revision':REV,'assigned_range':[48,160],'completed_range':[48,88],'scope':'Source-relative dependency curation, not proof re-verification. Existing edge IDs must be deduplicated by coordinator; all incident endpoint review hashes need refresh.','edges':rows,'reviews':reviews,'candidate_decisions':decisions,'remaining_range':[88,160]}
p=Path(__file__).parent/'patch.json';p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'reviews':len(reviews),'edges':len(rows),'candidate_decisions':len(decisions),'output':str(p)}))
