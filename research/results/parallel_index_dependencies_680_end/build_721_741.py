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
raw='''721|cites|cor:polylog-high-threshold-cube-volume|The complete image meets the earlier frontier's desired interface; the image proof only needs representation, refinement and old axioms.
722|depends_on|imp:beame-q-matching-switching-lemma|Uses its q=2 probability estimate with explicit residual-size and tree-height choices.
722|depends_on|lem:switched-reader-old-image|Converts the simultaneously shallow trees into complete old-only images.
722|cites|obs:middle-rank-frontier|Dense parity inputs lie outside the literal hypothesis; no bound for them is inferred.
723|cites|imp:beame-q-matching-switching-lemma|Adapts the encoding strategy to the bipartite board; proves the new count explicitly rather than importing unchecked bipartite constants.
723|applies|lem:switched-reader-old-image|Only its corollary converts bounded bipartite trees to old images; the probabilistic encoding lemma itself is independent.
723|cites|thm:literal-family-matching-restriction|Compares the residual old-board application with the earlier literal-family restriction.
725|depends_on|lem:switched-reader-old-image|Reuses the companion and Booleanity leaf arguments; cross-term cancellation extends its coefficient identity.
725|refines|lem:switched-reader-old-image|Inputs may be sums of mutually incompatible unary terms instead of individual terms.
726|cites|lem:compact-bit-subcube-restriction|Identifies the fixed compact family needed by the weight step.
726|cites|lem:positive-literal-matching-switch|The width-one subcube case is already available through swap encoding.
726|cites|thm:compact-bit-literal-inventory-restriction|The literal inventory theorem is an available restricted case, not a proof of general switching.
727|applies|lem:bit-term-decoder-image|Only the image consequence decodes bit terms to mutually incompatible unary terms.
727|applies|lem:sum-input-switched-image|Only the image consequence converts the short trees to complete ENS images.
727|cites|cor:polylog-high-threshold-cube-volume|Its parameter conclusion composes with the weight ledger but does not prove the general frontier.
728|obstructs|lem:subcube-bit-switching|Blocks extending its light-row hypothesis to all pinned rows in the fixed subcube; does not refute the stated lemma.
729|refines|obs:restriction-family-obstruction|Makes the residual-pigeon entropy and outside-label encoding limitation explicit for this encoding class.
730|refines|lem:compact-bit-subcube-restriction|Generalizes coordinate subcubes to arbitrary affine residual flats with explicit generator-image certificates.
730|applies|lem:cube-volume-multiplier-space|Transports the multiplier-space tool to the residual affine coordinates.
730|applies|lem:flat-restriction-dimension|Uses the flat restriction count in the transported residual coordinate system.
730|applies|lem:multi-axis-cube-residual-detector|The signed coordinate detector applies in the identified residual cube coordinates.
731|depends_on|lem:subcube-bit-switching|The unchanged light encoding gives the shallow tree for the light terms.
731|depends_on|lem:random-flat-restriction-preservation|Heavy terms whose patterns miss the flat vanish modulo residual Booleanity with the requisite degree accounting.
731|applies|lem:sum-input-switched-image|The image consequence ignores the vanishing decoded heavy terms in the leaf certificates.
732|obstructs|lem:subcube-bit-switching|The q-skip modification breaks its extension decoder; the unchanged canonical light encoding remains valid.
733|refines|lem:switched-reader-old-image|Extends the tree partition/image interface to hole queries with an empty branch and no onto axiom.
733|refines|lem:sum-input-switched-image|The same hole-query partition extends the sum-input leaf-image argument.
734|cites|obs:subcube-code-obstruction|The original window analysis uses the earlier encoding entropy restriction, later narrowed in scope.
735|refines|ex:fixed-subcube-pinned-rows-refuted|A single-target reader gives the random-flat pigeon-only obstruction and exact bad-event probability.
735|applies|lem:hole-query-node-functional|One hole query resolves the example, demonstrating that the restriction is on pigeon-only trees.
735|corrects|obs:literal-window-structure|Distinct heavy rows alone do not characterize the window obstruction; holes and the appropriate tree must also be controlled.
735|cites|thm:random-flat-literal-switching|The reader family lies above the prior positive size regime, so that theorem is not refuted.
736|refines|obs:literal-window-structure|Replaces separate row/hole cardinality criteria by an alive-pair matching/cover obligation.
736|cites|ex:random-flat-pigeon-only-refuted|Single-target example shows many rows alone need not force large matching number.
736|depends_on|thm:random-flat-literal-switching|Uses the residual-flat annihilation of pinned terms outside Q in the alive-pair reduction.
740|depends_on|lem:dense-labels-satisfied|The unary theorem's proof uses the dense-label satisfaction bound; the imported negative-association premise is under source audit.
740|depends_on|lem:sparse-matching-tail|Bounds the sparse part of the alive-pair matching number.
740|depends_on|lem:dense-labels-in-flat|Bounds the number of dense labels contained in the random flat.
740|depends_on|lem:hole-query-node-functional|Cover queries yield correct annihilating empty branches in the decision tree.
740|applies|lem:subcube-bit-switching|The separate-light/unary corollary uses light switching, with its later light-first ordering correction preserved.
740|cites|obs:alive-pair-matching-obligation|Mixed-tail extension remains an obligation, not a consequence of the unary theorem.
'''
for line in raw.strip().splitlines():
 i,k,t,n=line.split('|',3);add(int(i),k,t,n)
notes={721:'The explicit leaf-sum proof uses representation/refinement and old point/exclusion axioms; the frontier link is the requested application.',722:'The numeric union bound uses imported q=2 switching, and old images use the preceding leaf theorem; nonbipartite scope preserved.',723:'The bipartite encoding is proved with its own count; the old-image theorem enters only the corollary.',724:'Row-wise expansion and functional exclusions give the decoder identity directly; no separately indexed theorem is invoked.',725:'Companion/Booleanity proof explicitly reuses the single-term image lemma; incompatible inputs supply the new identity cancellation.',726:'Family comparison is a scope audit of existing restriction and literal results; it does not prove impossibility of every compact-family encoding.',727:'The extension encoding/richness count is local; decoding and image tools enter the stated application. Full-width pins are not covered.',728:'Adversary construction is explicit in the fixed subcube; it obstructs only a generalization beyond the earlier width hypothesis.',729:'Encoding-family obstruction refines a previously recorded family mismatch; the later pair-space improvement must not be silently treated as a proof of this older universal phrasing.',730:'Affine substitution checks the actual generators locally, and named multiplier/flat/cube tools are transported as applications.',731:'Light switching and algebraic annihilation are the two mechanisms; the q-skip candidate sharing its source region is a refuted attempted modification, not an input.',732:'Recorded round-trip counterexample and decoder mechanism refute the modification; no positive theorem is imported to certify failure.',733:'Direct degree-two branch identities extend both leaf-image interfaces; no onto axiom or general switching theorem is used.',734:'Correction link points into later pair-space encoding and creates ambiguous source ownership. Original window assessment is inventoried but its full repair chain requires exact scope review.',735:'Local single-target construction and hole-query control prove the obstruction; the older fixed-subcube construction is refined, not simply invoked as the full proof.',736:'Matching/cover reduction is explicit, but its dense-class imported negative-association premise has a concrete scope counterexample requiring source audit.',737:'The source invokes negative association of arbitrary uniform-bijection indicator columns, which fails already for X11 and X22 of a 2x2 uniform permutation. This challenges the cited premise, not automatically the final quantitative lemma.',738:'Read the exact sparse proof: symmetric sum, uniform residual rows and Markov suffice. Links in the later both-endpoints transfer are downstream applications, not prerequisites.',739:'Read the exact affine-rank/transitivity proof and union count; no separately indexed theorem is imported.',740:'Proof explicitly combines dense satisfaction, sparse matching and flat-rank bounds, then a cover tree. Dense satisfaction source premise is unresolved; later light-first correction applies to the extra corollary only.'}
for i in range(721,741):
 c=cs[i];pending=i in {734,736,737,740}
 action=('Resolve the original window statement against the later pair-space correction, separating ownership of linked propositions.' if i==734 else 'Audit the Joag-Dev–Proschan source hypotheses; replace the invalid blanket bijection negative-association inference with a valid bound or record the resulting proof gap, then inspect the exact use in this claim.') if pending else None
 rows.append({'position':i,'id':c['id'],'state':'pending' if pending else 'reviewed','evidence':evidence(i),'note':notes[i],'next_action':action,'source_fields_sha256':hashlib.sha256(json.dumps({k:c[k] for k in ('id','summary','assessment','record')},sort_keys=True,ensure_ascii=False).encode()).hexdigest()})
for i in [736,737]:
 edges.append({'id':cs[i]['id']+'::depends_on::JoagDev-Proschan-1983-NA','source':{'namespace':'current','id':cs[i]['id'],'locator':None},'target':{'namespace':'external','id':'JoagDev-Proschan-1983-NA','locator':'https://kbr.is-a.dev/math-research/#dense-labels-satisfied'},'type':'depends_on','evidence':evidence(i),'review_status':'reviewed','scope':'The recorded argument invokes the imported negative-association assertion for a uniform bijection. Applicability is disputed by the 2x2 diagonal-indicator control; this edge records proof reliance, not validity of the import.','review':{'revision':rev,'date':'2026-09-19','reviewer':'Codex parallel dependencies_680_end','note':'Dependency role explicit, source scope pending.'}})
(D/'patch_721_741.json').write_text(json.dumps({'base_revision':rev,'range':[721,741],'claims':rows,'relationships':edges},indent=2)+'\n');print('inventories',len(rows),'pending',4,'edges',len(edges))
