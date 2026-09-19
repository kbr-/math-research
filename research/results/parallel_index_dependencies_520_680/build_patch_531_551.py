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
add(531,'affine-level-full-old-moment-extension',[
 ('depends_on','thm:affine-level-full-old-low-degree-separation','Exact intersection equality makes the prescribed full-old functional well-defined.'),
 ('cites','obs:affine-selector-moment-scope-controls','Scope warning on independent selector moments, not a premise of the linear extension.'),
 ('applies','thm:power-affine-complete-system-transfer','Final application transfers the old moment window because old variables are fixed.'),
 ('applies','thm:shared-probe-original-degree-images','Final application transfers the window at a fixed-prime degree factor.')],
 'Linear extension is constructed directly from the previous intersection theorem. Complete-system transfers concern the final source-class applications only.')
add(532,'higher-cube-complete-moment-checks',[
 ('applies','lem:multi-axis-cube-residual-detector','New complete moment fixtures test multi-axis detection and marginal constraints.'),
 ('applies','lem:target-first-cube-packing','Chosen target and multiplier rows instantiate their separate cube/edge accounting.')],
 'The two complete finite witnesses and negative controls are explicit. The source names an earlier degree-two residual design without identifying its exact indexed owner; resolve that provenance before closing this inventory.')
rows[-1]['state']='pending';rows[-1]['next_action']='Resolve the exact earlier degree-two residual design used by check_cube_dual_design.cpp and add its source dependency; the detector application is already reviewed.'
add(533,'joint-high-selector-zero-preservation',[
 ('depends_on','thm:affine-level-old-row-linear-target-separation','Reuses row-excluded multiplier and detector argument for the row-linear conclusion.'),
 ('depends_on','thm:affine-level-full-old-low-degree-separation','Reuses full-old target multiplier and cube detector argument.'),
 ('depends_on','thm:all-prime-affine-family-exclusion','Uses its high-block image 1-f^(p-1) and existing Frobenius/Boolean image certificate.'),
 ('refines','thm:affine-level-full-old-low-degree-separation','Allows eligible zero-selector axioms while retaining the same old-target bounds.')],
 'The sole extra weighted axiom image f-f^p and original degree 2h charge are supplied explicitly; arbitrary low-rank zero assignments are not asserted.')
add(534,'joint-zero-old-moment-extension',[
 ('depends_on','thm:joint-high-selector-zero-preservation','Supplies the old-target intersection conclusions for the clamped consequence space.'),
 ('depends_on','obs:affine-selector-moment-scope-controls','Its literal-selector identity gives the explicit low-rank zero-assignment countercontrol.')],
 'The linear extension argument and all legal multiples of added zero equations are direct. The low-rank control is part of the indexed scope and reuses the earlier literal relation.')
add(535,'clamped-bottom-zero-source-profile',[
 ('cites','thm:dependent-rank-source-collapse','Fixes the source grammar, stage and original weights; does not prove this elementary zero-profile identity.'),
 ('cites','def:costed-ns-value-profile','Defines the profile obligations verified explicitly here.')],
 'With P=0 actually adjoined, its own retained prefix gives the residual P; companion and Booleanity witnesses are zero. No high-rank existence theorem is required to construct this conditional profile.')
add(536,'surviving-selector-rank-source-exclusion',[
 ('depends_on','lem:clamped-bottom-zero-source-profile','Supplies the selected zero-bottom source profiles.'),
 ('depends_on','lem:rank-adapted-original-source-prefixes','Builds profiles from the projected selector tuple while retaining every original input cost.'),
 ('depends_on','cor:costed-profile-unbalanced-PC-compiler','Supplies the fixed-depth no-height-loss PC ceiling.'),
 ('depends_on','thm:costed-virtual-or-source-transfer','Alternative modular NS reconstruction preserves supplied source degree.'),
 ('depends_on','thm:joint-high-selector-zero-preservation','Excludes the resulting affine family with selected zero equations.')],
 'The projection/rank inventory and original-degree ledger are explicit; two compiler alternatives are recorded with their distinct roles.')
add(537,'joint-selector-zero-exact-controls',[
 ('applies','thm:joint-high-selector-zero-preservation','Checks new weighted zero-axiom images, not asymptotic high-rank existence.'),
 ('applies','lem:clamped-bottom-zero-source-profile','Conditional source model tests retain zero profiles and actual prefix residuals.'),
 ('applies','obs:affine-selector-moment-scope-controls','Low-rank literal controls verify necessity of scope restrictions.')],
 'The finite source and all NS certificates are direct evidence. Small rank-two fixtures do not instantiate the asymptotic high-rank exclusion theorem.')
add(538,'dense-shared-bit-source-setup',[
 ('cites','thm:joint-high-selector-zero-preservation','Compares rank-two bottoms with its high-rank zero threshold.'),
 ('cites','thm:surviving-selector-rank-source-exclusion','Shows the displayed parent can fail its selector-rank premise.')],
 'The actual source grammar, identity selector matrix and original degree formulas are elementary setup; comparisons do not establish hardness.')
add(539,'shared-bit-bottom-complete-specialization',[],
 'All coefficients are assigned explicit zero/one constants; product, companion and field images are written out. No nontrivial prior indexed theorem is required for the local scalar identity.')
add(540,'shared-bit-parent-original-degree-map',[
 ('depends_on','lem:shared-bit-bottom-complete-specialization','Supplies the actual consistent bottom map giving inputs (1-x)(1-y_i).')],
 'The affine coefficient renaming, Boolean division in the single old bit, exact companion identity and field-domain images are given locally. The division is elementary monic division, not an invocation of a later binary-only formalization.')
add(541,'dense-shared-bit-complete-transfer',[
 ('depends_on','lem:shared-bit-bottom-complete-specialization','All bottom original-degree axiom images are certified.'),
 ('depends_on','lem:shared-bit-parent-original-degree-map','All parent original-degree axiom images and coefficient domains are certified.'),
 ('applies','thm:all-prime-affine-family-exclusion','Final exclusion over compact PHP applies the affine endpoint theorem.'),
 ('applies','thm:affine-level-old-row-linear-target-separation','Old-target consequence application transfers because old bits are fixed.'),
 ('applies','thm:affine-level-full-old-low-degree-separation','Full-old consequence application transfers because old bits are fixed.')],
 'Ordinary NS cofactor substitution and primitive PC replay are proved explicitly; the three endpoint statements are applications, not prerequisites of the complete transfer itself.')
add(542,'shared-bit-complete-source-checks',[
 ('applies','lem:shared-bit-bottom-complete-specialization','Checks one bottom map reused by overlapping parents.'),
 ('applies','lem:shared-bit-parent-original-degree-map','Verifies all original parent axiom images, product comparisons and domain controls.')],
 'Complete finite NS identities and models are direct evidence, independent of any claimed asymptotic PHP refutation exclusion.')
add(543,'canonical-pair-bottom-source-profiles',[
 ('depends_on','lem:shared-bit-bottom-complete-specialization','Supplies the complete consistent scalar map; prefix and Booleanity identities are displayed here.')],
 'The profile identity and its quadratic-versus-affine mixed-difference control are explicit; no rank-exclusion theorem is required.')
add(544,'shared-core-clamped-old-bit-profile',[
 ('depends_on','lem:shared-bit-parent-original-degree-map','Uses its affine core and actual parent-product difference for the parent-to-bit certificate.'),
 ('cites','def:costed-ns-value-profile','Defines the original-cost obligations checked explicitly.')],
 'The zero core equation is an explicit premise; prefix, companion and Booleanity certificates are supplied. High-rank eligibility is needed only when applying this conditional profile later.')
add(545,'shared-core-projected-source-criterion',[
 ('depends_on','lem:canonical-pair-bottom-source-profiles','Canonicalizes every reused selected pair bottom consistently.'),
 ('depends_on','lem:shared-core-clamped-old-bit-profile','Interprets selected parent values as old bits with original costs.'),
 ('depends_on','lem:clamped-bottom-zero-source-profile','Optional original high-bottom values are replaced by zero profiles.'),
 ('depends_on','thm:dependent-rank-source-collapse','Uses adapted-rank source induction and common-system compiler for the other blocks.'),
 ('depends_on','thm:joint-high-selector-zero-preservation','Excludes the common retained affine endpoint with its eligible core clamps.')],
 'Old-affine offsets, surviving quadratic names, strict source order and final inventory are accounted explicitly. The adapted-rank compiler encapsulates its existing reconstruction dependencies.')
add(546,'shared-core-third-level-exact-checks',[
 ('applies','lem:shared-core-clamped-old-bit-profile','Tests actual parent-to-bit comparisons and omitted-clamp controls.'),
 ('applies','thm:shared-core-projected-source-criterion','Tests projected third-level profiles while retaining original degree-ten input costs.')],
 'Finite satisfiable local models and exact witnesses test the conditional interfaces, not the high-rank threshold or PHP exclusion conclusion.')
add(547,'mixed-star-union-original-setup',[
 ('depends_on','lem:shared-core-clamped-old-bit-profile','Supplies the exact subgroup prefix relation with retained core residual.'),
 ('cites','obs:proper-or-subgroups-share-level','Fixes actual flattened-OR syntax and original same-level weights.')],
 'This source setup assumes consistent overlapping inputs and the core equations; it does not manufacture an extra ENS level or assert every tuple has the cover.')
add(548,'mixed-star-union-affine-core-profile',[
 ('depends_on','def:mixed-star-union-original-setup','Supplies original input weights, cover, consistent overlaps and subgroup prefix residuals.')],
 'Every union prefix, residual, companion, Booleanity identity and cost inequality is written out from the stated setup. No group-count degree loss or source exclusion follows automatically.')
add(549,'mixed-union-source-compiler-application',[
 ('depends_on','thm:mixed-star-union-affine-core-profile','Supplies complete profiles for covered dense auxiliary unions.'),
 ('depends_on','thm:shared-core-projected-source-criterion','Provides the other profiles and common-system compiler.'),
 ('depends_on','thm:joint-high-selector-zero-preservation','Supplies the clamped affine endpoint exclusion.'),
 ('depends_on','lem:costed-profile-product-closure','Supplies the actual OR sum-of-profile-costs ceiling, retaining residual corrections.')],
 'This is a source-criterion extension, with explicit overlap assignment in the negative OR terms. No PC-to-NS conversion or coverage of uncovered groups is used.')
add(550,'mixed-star-union-exact-checks',[
 ('applies','thm:mixed-star-union-affine-core-profile','Checks overlapping union profiles at their original flattened input weights.'),
 ('applies','lem:costed-profile-product-closure','Checks actual OR witness including all prefix-residual contributions.')],
 'Finite complete polynomials, NS witnesses and canonical/missing-hypothesis models are direct evidence. They do not instantiate high-rank asymptotic PHP exclusion.')
out={'schema_version':1,'base_revision':rev,'range':[531,551],'claims':rows,'relationships':edges,'scope':'Reviewed owning passages and actual proof roles; one residual-design source remains pending.'}
(root/'research/results/parallel_index_dependencies_520_680/patch_531_551.json').write_text(json.dumps(out,indent=2)+'\n');print(len(rows),'inventories',len(edges),'edges')
