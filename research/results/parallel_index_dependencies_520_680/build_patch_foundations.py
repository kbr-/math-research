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
add(659,'ordinary-polynomial-proof-foundations',[], 'Primitive rules, degree containment, monotonicity and the ordinary bases are defined and proved directly. Paper/base links are encoding provenance, not assumed PC/NS equivalence or lower bounds.')
add(660,'lean-pc-completed-line-reuse',[('depends_on','def:ordinary-polynomial-proof-foundations','Uses primitive derivations and individually charged NS spaces for multiplication/inclusion.')], 'Monomial expansion, domain degree additivity and NS span induction prove all three statements directly; historical lemma is formalization provenance.')
add(661,'lean-row-linear-polynomial-space',[], 'Explicit monomial indexing, coefficient basis and finite cardinalities supply dimension, support degree and maximal coefficient. No quotient injection or previous separation theorem is used.')
add(662,'lean-ordinary-restriction-dimension',[], 'Stars-and-bars injection and direct substitution degree argument prove the general bound. Row-linear space is an optional example, not a premise; formal library basis/counting results remain library-level dependencies.')
add(663,'lean-pc-degree-substitution',[('depends_on','lem:reuse','Uses completed-line multiplication at actual predecessor degree in weighted replay.')], 'Substitution degree is proved by monomials and replay induction is explicit. Historical substitution is source provenance, not an additional proof assumption.')
# The article includes the unanchored certificate proof after the statement.
boolean_article='entry-2026-09-15-lean-boolean-reduction'
# Find actual owning article ID instead of assuming a spelling.
import re
book=(root/'notebook.html').read_text();pos=book.index('id="lean-binary-degree-controlled-Boolean-reduction"');boolean_article=re.findall(r'<article\b[^>]*id="([^"]+)"',book[:pos])[-1]
add(664,boolean_article,[('depends_on','lem:reuse','R02 NS multiplication closure charges the telescoping reduction error terms at their original ordinary degree.')], 'Read the unanchored full certificate and grid-injectivity proof. Finite-field evaluation injectivity is a library ingredient explained in place; the broader historical mixed-domain lemma is only partially formalized here.')
add(665,'lean-linear-annihilator-extension',[], 'Basis extension and compatible gluing are standard linear algebra with the complete construction written out and Mathlib API identified. No polynomial calculus theorem is a premise of this independent interface.')
add(666,'lean-pc-finite-separation',[
 ('depends_on','third-party:linear-annihilator-extension','Supplies normalized separation within the actual bounded-degree vector space.'),
 ('depends_on','def:ordinary-polynomial-proof-foundations','Supplies PC/NS containment in the bounded polynomial space.'),
 ('depends_on','lem:reuse','Supplies NS-to-PC inclusion, the remaining assertion in the historical lemma.')], 'The bounded-subspace preimage application is explicit; no positivity or same-degree PC=NS is introduced.')
add(667,'lean-squarefree-forbidden-pair-certificate',[('depends_on','def:ordinary-polynomial-proof-foundations','Uses legal generator-multiple membership in the ordinary NS span.')], 'Squarefree product factorization and cardinality degree bound are direct. The file may import Boolean support definitions, but no Boolean-reduction theorem is needed for this one-multiple identity.')
add(668,'lean-affine-form-polynomial-interface',[], 'Coefficient expansion, evaluation at zero/unit vectors, linearity and ordinary degree bound are direct; finite-field nonlinear interpolation is neither used nor claimed.')
add(669,'lean-affine-system-linear-algebra',[('depends_on','lem:affine-form-polynomial-interface','Uses faithful coefficient-form polynomial representation for literal span identities and exact degree.')], 'Finite-coordinate annihilator duality is a standard library theorem spelled out in the proof; no project-specific normalized separation theorem is invoked. The t=0 direction case is handled explicitly.')
add(670,'lean-affine-coordinate-completion',[('depends_on','lem:affine-system-linear-algebra','Supplies common zero and independence of linear parts for a proper affine family.')], 'Standard dual basis extension and double-dual coordinates are constructed explicitly; free-coordinate range/injectivity and cardinality follow locally.')
add(671,'lean-compact-bit-decoder-coordinates',[
 ('depends_on','lem:substitution','Uses its ordinary substitution degree inequality in both directions around the explicit linear left inverse.'),
 ('cites','thm:compact-bit-PHP-PC-degree','Earlier decoder certificate proof is source context; this coordinate lemma gives an explicit alternative left inverse.'),
 ('cites','thm:transported-bit-consequence-filtration','Earlier coordinate argument is provenance, not a prerequisite of the left-inverse calculation.')], 'The unit-column retraction is proved directly. No compact collision image or lower bound is needed for coordinate injectivity.')
add(672,'lean-compact-bit-ordinary-PC-decoder',[
 ('depends_on','lem:compact-bit-decoder-coordinates','Supplies the ordinary affine decoder map and degree bound.'),
 ('depends_on','lem:binary-degree-controlled-Boolean-reduction','Supplies original-degree Boolean axiom image certificates.'),
 ('depends_on','lem:two-functional-row-state-interpolation','Supplies collision image certificate on two one-hot rows.'),
 ('depends_on','lem:reuse','Supplies NS-to-PC image derivations.'),
 ('depends_on','lem:substitution','Supplies degree-preserving primitive replay after image certification.')], 'Original source axiom degrees and injective row relabeling are proved in the passage; no extra B>=ell premise is inserted.')
add(673,'lean-functional-matching-normal-form',[
 ('depends_on','lem:binary-degree-controlled-Boolean-reduction','Reduces powers within original degree before eliminating nonmatching monomials.'),
 ('depends_on','lem:squarefree-forbidden-pair-certificate','Kills each nonmatching squarefree monomial with one supplied collision multiple.'),
 ('depends_on','def:ordinary-polynomial-proof-foundations','Supplies original Boolean/row/column functional-base encoding and NS spaces.')], 'Normal-form kernel and all row-generator identities were read, including the unanchored row-equation subsection. The subsequent bounded moment-functional theorem uses linear extension but is a different indexed result, not a premise of normal form.')
add(674,'lean-fresh-ENS-block-degree',[
 ('depends_on','lem:substitution','Degree-preserving injective renaming follows from a degree-one substitution left inverse.'),
 ('applies','lem:affine-system-linear-algebra','The final proper-span application uses its exact degree-one input assertion; the generic degree theorem assumes that assertion directly.')], 'Fresh coefficient specialization supplies lower bounds and domain degree additivity supplies product equalities. Proper-span theory is only the stated application.')
add(675,'lean-fresh-ENS-scalar-cleanup',[
 ('depends_on','lem:substitution','Replays the scalar map at degree bound one with zero companion/domain images.'),
 ('depends_on','lem:fresh-ENS-block-degree','Uses canonical fresh-block definition and renaming interface; not its exact-degree equality theorem.')], 'The zero and binary unit assignments are explicit. General-field scalar idempotence and h>=1 in the unit case remain hypotheses.')
add(676,'lean-finite-affine-map-polynomial-bridge',[
 ('refines','lem:affine-form-polynomial-interface','Generalizes the coordinate index to arbitrary finite types and checks agreement with the Fin n interface.'),
 ('cites','def:affine-clause-PC-system','Motivating downstream registry accepts arbitrary finite old-coordinate types; no registry theorem is used to prove the bridge.')], 'The coefficient/evaluation/injectivity argument is direct. Compatibility with existing representation is checked rather than inferred from an import.')
add(677,'lean-low-rank-ENS-specialization',[
 ('depends_on','lem:binary-degree-controlled-Boolean-reduction','Converts companion vanishing to ordinary NS witnesses through r+1.'),
 ('depends_on','lem:fresh-ENS-block-degree','Uses canonical block specialization/renaming interface for the actual product identity.')], 'Basis partition and ordered telescoping are supplied directly with library product identities. The separately formalized ENS telescoping theorem is not a proof dependency.')
add(678,'lean-finite-affine-map-span-witnesses',[
 ('depends_on','lem:affine-system-linear-algebra','Transports its vanishing and unit-span coefficient witnesses along a coordinate bijection.'),
 ('depends_on','lem:finite-affine-map-polynomial-bridge','Transfers affine-map coefficient identities into ordinary polynomials linearly.'),
 ('cites','lem:semantic-weakening-PC-degree','Motivating consumer, not a premise of the coordinate-transport theorem.'),
 ('cites','def:affine-clause-PC-system','Explains the finite-coordinate requirement, not an assumed simulation result.')], 'The reindexing is surjective and linear; the proof does not infer nonlinear polynomial equality from pointwise equality.')
add(679,'lean-simultaneous-affine-family-removal',[
 ('depends_on','lem:low-rank-ENS-specialization','Supplies low-rank coefficients and ordinary Boolean companion certificates.'),
 ('depends_on','lem:binary-degree-controlled-Boolean-reduction','Supplies f^2-f and all coefficient-domain image certificates.'),
 ('depends_on','lem:reuse','Supplies old-axiom multiplication and NS-to-PC conversion.'),
 ('depends_on','lem:substitution','Supplies one global fixed-weight primitive replay.'),
 ('depends_on','lem:fresh-ENS-block-degree','Canonical fresh-product renaming identifies local and global registry images; exact companion degrees are only a source-scope application.')], 'The explicit dependency-refinement paragraph excludes proper-span cleanup, affine coordinates and exact degree equality from the generalized removal theorem. Supplied high literal witnesses remain assumptions, not falsely closed dependencies.')
# Record source formalization relationships with a separate historical namespace.
for i,label,anchor,scope in [(660,'lem:reuse','lem-reuse','Full historical completed-line reuse statement, including NS multiplication/inclusion.'),(663,'lem:substitution','lem-substitution','Full historical substitution/replay statement with verified zero-boundary cases.'),(664,'lem:fieldreduction','lem-fieldreduction','Binary Boolean-domain scope only; not the full all-prime mixed-domain historical statement.'),(666,'lem:duality','lem-duality','Full historical polynomial separation/inclusion statement.')]:
 c=x['claims'][i];row=next(r for r in rows if r['id']==c['id']);edges.append({'id':c['id']+'::formalizes::historical:'+label,'source':{'namespace':'current','id':c['id'],'locator':None},'target':{'namespace':'historical','id':label,'locator':'https://github.com/kbr-/math-research/blob/main/php_codex_handoff/manuscript/chapters/01_foundations.md#'+anchor},'type':'formalizes','scope':scope,'evidence':row['evidence'],'review_status':'reviewed','review':{'revision':rev,'date':'2026-09-19','reviewer':'Codex parallel dependency reviewer','note':'Exact source correspondence recorded; no new kernel replay.'}})
out={'schema_version':1,'base_revision':rev,'positions':[r['position'] for r in rows],'claims':rows,'relationships':edges,'scope':'Foundation statement and proof roles reviewed, including unanchored certificate and row-equation subsections.'}
(root/'research/results/parallel_index_dependencies_520_680/patch_foundations.json').write_text(json.dumps(out,indent=2)+'\n');print(len(rows),'inventories',len(edges),'edges')
