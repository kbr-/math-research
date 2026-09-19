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
add(634,'lean-finite-augmented-chain-api',[], 'Definitions, finite-sum linearity, support and extension-by-zero equivalence are proved directly. The original ChessboardChain proposition is an interface target, not assumed filling or a theorem prerequisite.')
add(635,'lean-augmented-boundary-squared-zero',[('depends_on','third-party:finite-augmented-chain-api','Uses its ambient insertion boundary and supported chain interface.')], 'Finite involution proof is explicit; no filling/homology theorem is imported as a premise.')
add(636,'lean-augmented-chain-naturality',[('depends_on','third-party:finite-augmented-chain-api','Uses supported chain spaces and exact-face equivalence for naturality and incidence bridge.')], 'Injection/preimage identities and boundary reindexing are proved directly. H02 is imported by the file but squared-zero is not a prerequisite of the stated naturality/bridge proof; no import-only dependency inferred.')
add(637,'chessboard-parameter-arithmetic',[], 'All min/floor and induction inequalities are proved explicitly from natural/integer arithmetic; only library omega is imported, not project homology claims.')
add(638,'lean-augmented-cone-contraction',[('depends_on','third-party:finite-augmented-chain-api','Supplies insertion boundary, support and augmented endpoint conventions.')], 'The full contraction identity and support preservation are elementary direct proofs; no independent filling hypothesis is assumed.')
add(639,'lean-chessboard-star-cover',[('depends_on','third-party:finite-augmented-chain-api','Supplies the finite downward-closed complex and matching-face definitions.')], 'Star closure and coverage use direct row/column counting; H04 acyclicity and H05 nerve vanishing are explicitly separate later applications.')
add(640,'lean-chessboard-star-cover',[('depends_on','third-party:finite-augmented-chain-api','Uses its augmented complex interface for intersections, covers and vertex-nonempty nerves.')], 'Only the generic definitions paragraph owns this claim. Shared star-cover proof and unused transitive chain-map imports are not prerequisites of the definitions.')
add(641,'lean-simplex-boundary-acyclicity',[('depends_on','lem:augmented-cone-contraction','Explicit cone filler in full simplex remains on boundary at k+1<b.')], 'Top-degree exclusion and small boundary cases are proved with the strict support-size inequality.')
add(642,'lean-finite-cover-double-complex',[
 ('depends_on','def:finite-complex-cover','Uses intersection, cover and vertex-nonempty nerve support conventions.'),
 ('depends_on','third-party:augmented-boundary-squared-zero','Supplies square-zero of each insertion boundary.'),
 ('depends_on','lem:augmented-cone-contraction','Supplies positive-vertex-degree horizontal fillers by coning the index coefficients.')],
 'Commutation is a direct finite-sum interchange; support and nerve-edge qualifications are explicit. The shared source anchor does not make the chessboard star-cover theorem a dependency.')
add(643,'entry-2026-09-15-lean-chessboard-star-intersections',[
 ('depends_on','third-party:chessboard-star-cover','Reuses closed-star matching-extension characterization.'),
 ('depends_on','lem:augmented-subcomplex-relabeling','Transports the exact complement-face correspondence to chain equivalences and actual fillings.')],
 'Read the entire containing article to include the unanchored supporting proof; face exclusion is local and filling transport uses the extracted relabeling interface.')
add(644,'entry-2026-09-15-lean-chessboard-star-intersections',[
 ('depends_on','third-party:augmented-chain-naturality','Uses H03 push-boundary compatibility and injectivity for inverse chain maps and filling transport.')],
 'The unanchored support-exhaustive relabeling subsection owns this general result. Its chessboard application does not make star intersections a prerequisite, avoiding a spurious cycle.')
add(645,'lean-chessboard-star-nerve',[
 ('depends_on','third-party:chessboard-star-intersections','Identifies full intersection as empty-face-only and characterizes the nerve.'),
 ('depends_on','third-party:simplex-boundary-acyclicity','Supplies the exactness range after literal nerve equality.'),
 ('depends_on','third-party:chessboard-star-cover','Supplies star insertion closure.'),
 ('depends_on','lem:augmented-cone-contraction','Turns star closure into all-degree star exactness.')],
 'Proper-family vertex witnesses are explicit; the four recorded proof dependencies are used for full intersection, nerve range and star exactness.')
add(646,'entry-2026-09-15-lean-homological-cover-lemma',[
 ('depends_on','lem:finite-cover-double-complex','Supplies double coefficient support, commuting square-zero boundaries and positive-degree horizontal exactness.')],
 'Read the unanchored Complete alternative proof in the containing article. Nerve-edge and column fillings use the theorem hypotheses; finite chain induction is supplied locally, not a spectral-sequence import.')
add(647,'lean-chessboard-homological-bound',[
 ('depends_on','lem:augmented-cone-contraction','Fills the augmentation base case at a chosen vertex.'),
 ('depends_on','third-party:augmented-chain-naturality','Transposes boards by inverse boundary-compatible chain maps.'),
 ('depends_on','third-party:chessboard-star-cover','Supplies first-row star subcomplex coverage.'),
 ('depends_on','third-party:chessboard-star-nerve','Supplies nerve exactness and single-star exactness.'),
 ('depends_on','third-party:homological-cover-lemma','Combines nerve and intersection exactness.'),
 ('depends_on','third-party:chessboard-star-intersections','Supplies actual filling transport to smaller rectangular boards.'),
 ('depends_on','third-party:chessboard-parameter-arithmetic','Supplies exact intersection degree and induction-decrease inequalities.')],
 'Strong induction is explicit; the shared-anchor relabeling helper is encapsulated in star-intersection transport rather than asserted as a second independent source premise.')
add(559,'lean-chessboard-filling',[
 ('depends_on','third-party:chessboard-parameter-arithmetic','Identifies nu(s,N)=s in the stable range.'),
 ('depends_on','third-party:augmented-chain-naturality','Transports original incidence cycles/fillings through exact-face chain equivalences.'),
 ('depends_on','third-party:chessboard-homological-bound','Supplies supported filler at the required cell count.')],
 'The full original-interface proof is explicit and uses these three interfaces. BLVZ is theorem attribution; no assumed filling result or circular dependency on its own statement module.')
out={'schema_version':1,'base_revision':rev,'positions':[r['position'] for r in rows],'claims':rows,'relationships':edges,'scope':'Topological exact scope and complete owning proofs reviewed; no fresh kernel replay.'}
(root/'research/results/parallel_index_dependencies_520_680/patch_topology.json').write_text(json.dumps(out,indent=2)+'\n');print(len(rows),'inventories',len(edges),'edges')
