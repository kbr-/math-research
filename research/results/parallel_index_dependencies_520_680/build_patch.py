import json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[3];sys.path.insert(0,str(root/'tools'))
from claim_reviews import claim_digest
x=json.loads((root/'research/claims/index.json').read_text());cs={c['id']:c for c in x['claims']};rev=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();web='https://kbr.is-a.dev/math-research/#';rows=[];edges=[]
def add(i,anchors,relations,note):
 c=x['claims'][i];ev=[web+a for a in anchors.split()];rows.append({'id':c['id'],'position':i,'claim_sha256':claim_digest(c),'state':'reviewed','evidence':ev,'note':note,'next_action':None})
 for typ,target,scope in relations:
  assert target in cs,target
  edges.append({'id':c['id']+'::'+typ+'::'+target,'source':{'namespace':'current','id':c['id'],'locator':None},'target':{'namespace':'current','id':target,'locator':None},'type':typ,'scope':scope,'evidence':ev,'review_status':'reviewed','review':{'revision':rev,'date':'2026-09-19','reviewer':'Codex parallel dependency reviewer','note':'Owning proof/application passage reviewed, including implicit intra-entry references; no new mathematical or kernel audit.'}})
add(520,'compact-source-polynomial-rank-obstruction',[
 ('depends_on','thm:dependent-rank-source-collapse','Section 3 supplies one-level endpoint D=O(h^d) after accuracy is chosen for the fixed registry.'),
 ('depends_on','lem:accuracy-dependent-affine-exclusion','Section 4 and RANK-accuracy supply the old-degree contradiction and quantitative rank threshold.'),
 ('cites','obs:label-substitution-selector-count-failure','Scope warning: label conversion need not preserve the original selector rank.')],
 'Accuracy invariance and asymptotic arithmetic are supplied locally; source collapse and adjustable-accuracy affine exclusion are the two proof inputs. Label-conversion warning is not a proof prerequisite.')
add(521,'selector-span-profile-exact-checks',[
 ('applies','lem:rank-adapted-original-source-prefixes','Nine exact witnesses instantiate adapted-basis prefix accounting with individual input degrees.'),
 ('applies','lem:accuracy-dependent-affine-exclusion','Four exact dimension cases test its numerical comparison, not a final finite-board refutation exclusion.')],
 'Finite matrices, NS identities and complete models are direct evidence; applied interfaces are the adapted-prefix and accuracy-dimension constructions. No asymptotic theorem is certified by the finite checks.')
add(522,'top-row-linear-monomial-detector',[
 ('depends_on','lem:all-prime-compact-bit-decoder','Uses the affine bit decoder to transport the target to functional matching PHP.'),
 ('depends_on','lem:signed-cube-row-linear-separation','Uses signed disjoint coordinate edges and residual matching design annihilator; only the top-term hypothesis is relaxed.'),
 ('refines','lem:signed-cube-row-linear-separation','Extends detection to polynomials whose selected top term is row-linear while other terms may not be.')],
 'Direct signed-edge construction already supplies matching marginals and old stability; the new proof isolates the top coefficient locally. No unrelated cube-packing theorem is needed beyond that construction.')
add(523,'safe-leading-row-target-product',[
 ('refines','thm:conditioned-row-linear-quotient-dimension','Reuses leading-row avoidance with the weaker requirement that the product only have a row-linear leading term.'),
 ('applies','lem:top-row-linear-monomial-detector','The detector gives the stated consequence when its board/degree hypotheses hold.')],
 'Leading monomial multiplication and the Boolean zero-divisor control are proved directly; earlier conditioned result supplies method provenance, not a necessary premise of the leading-product identity.')
add(524,'affine-level-old-row-linear-target-separation',[
 ('depends_on','thm:all-prime-affine-family-exclusion','Reuses scalar cleanup, simultaneous low/high coefficient substitution, field/companion certificates and weighted PC replay.'),
 ('depends_on','lem:safe-leading-row-target-product','Chooses multipliers off leading target rows to retain a nonzero row-linear top term.'),
 ('depends_on','lem:top-row-linear-monomial-detector','Contradicts the resulting decoded old PC consequence within TARGET-range.')],
 'The modified restriction-dimension estimate is proved explicitly in the owning passage. Replay and target detection are separate prerequisites; no augmented PC=NS inference is used.')
add(525,'affine-level-row-linear-moment-extension',[
 ('depends_on','thm:affine-level-old-row-linear-target-separation','The zero intersection supplies the direct-sum functional extension.'),
 ('cites','thm:critical-bit-affine-family-extension','Contrasts full-old NS preservation at a narrower critical band with this partial-old PC statement.'),
 ('applies','thm:power-affine-complete-system-transfer','Additional qualitative application transfers old-target exclusion to the power-input source class.'),
 ('applies','thm:shared-probe-original-degree-images','Additional qualitative application transfers old-target exclusion to the shared-probe source class.')],
 'The finite-dimensional direct-sum extension is written out, so no later Lean extension lemma is retroactively a proof premise. Two complete-system transfers support only the final applications.')
add(526,'affine-selector-moment-scope-controls',[
 ('depends_on','lem:prime-disequality-initial-PC-values','Reuses the initial/weakening witness to force a proper pair-difference selector to zero.'),
 ('obstructs','cor:affine-level-row-linear-moment-extension','Blocks strengthening its old-moment freedom to arbitrary independent selector moments; the actual corollary remains valid.')],
 'The one-bit coupling identity is explicit. The pair-difference example invokes the prior initial witness; neither control is a refutation of the scoped old-moment extension theorem.')
add(527,'affine-old-target-exact-checks',[
 ('depends_on','ex:cube-dual-complete-marginal-checks','Loads complete archived binary matching moments rather than recomputing marginals.'),
 ('depends_on','ex:odd-prime-affine-complete-checks','Loads the complete archived signed F3 moments.'),
 ('applies','lem:top-row-linear-monomial-detector','New polynomial evaluations test detection with within-row lower terms.'),
 ('applies','obs:affine-selector-moment-scope-controls','Exact NS identities and models test coupling and forced-zero controls.')],
 'Archived complete moments are actual input data; new witness and dimension checks are explicit finite output. They are not finite instances of the final PC degree inequalities.')
add(528,'multi-axis-cube-residual-detector',[
 ('depends_on','thm:all-field-matching-filtration','Supplies normalized residual matching design and ordinary old PC/NS stability in range.'),
 ('refines','lem:top-row-linear-monomial-detector','Replaces selected coordinate edges by multi-axis cubes with explicit deleted-column accounting.'),
 ('refines','lem:signed-cube-row-linear-separation','Generalizes the signed-edge moment construction to multiple selected bits per row.'),
 ('cites','thm:transported-bit-low-degree-rigidity','Higher-dimensional signed differences are reused as method provenance; the residual construction and its marginal proof are supplied here.')],
 'All cube signs, support cases, marginals and coefficient isolation are proved locally. The imported matching existence/stability theorem is the nonlocal mathematical premise.')
add(529,'target-first-cube-packing',[
 ('depends_on','lem:disjoint-coordinate-cube-packing','Packs the target cubes when the sum of their axis counts is below ell.'),
 ('refines','lem:safe-leading-row-target-product','Extends the same leading-row avoidance argument to a squarefree target; the earlier statement alone only covered row-linear targets.'),
 ('cites','lem:bounded-row-degree-bit-quotient-injection','Comparison only: applying its uniform estimate to the whole product would lose target/multiplier separation.')],
 'Target-volume inequality, greedy edge packing and residual-cost cancellation are explicit. The existing coordinate-cube lemma is implicit by name and resolved to its exact stable label.')
add(530,'affine-level-full-old-low-degree-separation',[
 ('depends_on','thm:affine-level-old-row-linear-target-separation','Reuses the row-excluded ordinary restriction dimension calculation and covers constant targets.'),
 ('depends_on','thm:all-prime-affine-family-exclusion','Supplies simultaneous old-only substitution and original-degree weighted PC replay.'),
 ('depends_on','lem:multi-axis-cube-residual-detector','Separates the squarefree leading target product from old PC consequences.'),
 ('depends_on','lem:target-first-cube-packing','Supplies disjoint cubes and residual room at the HC-range bounds.')],
 'Boolean multilinear reduction and the converse inclusion are stated explicitly; this inventory records the named source-relative proof inputs without attributing the all-prime proof to a later binary-only formal lemma.')
out={'schema_version':1,'base_revision':rev,'range':[520,531],'claims':rows,'relationships':edges,'scope':'Reviewed direct source-relative dependencies, applications and qualified refinements; no transitive closure or new proof audit.'}
(root/'research/results/parallel_index_dependencies_520_680/patch_520_531.json').write_text(json.dumps(out,indent=2)+'\n');print(len(rows),'inventories',len(edges),'edges')
