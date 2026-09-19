#!/usr/bin/env python3
from pathlib import Path
exec((Path(__file__).parent/'batch1.py').read_text().split('\nadd(360,')[0])
GH='https://github.com/kbr-/math-research/blob/main/'
rows=[
(383,'Razborov-1998-Theorem-3.1',GH+'research/notes/SOURCE_AUDIT.md#razborov-base-and-residual-pc-lower-bound','depends_on','The audited functional row-exclusive PHP bound applies over every field at degree at least n/2+1; the recorded Boolean-quotient bridge handles ordinary PC.','compact-bit-PC-lower-bound'),
(385,'BIKPRS-Theorem-6.7(1)',GH+'research/notes/SOURCE_AUDIT.md#bikprs-actual-simulation-structure','depends_on','The audited concluding proof supplies polynomial-size logarithmic-height balancing with constant formula-depth overhead; no selector sparsity is inferred.','ordinary-PHP-to-compact-bit-source'),
(454,'Hakoniemi-Limaye-Tzameret-2026-v1-Proposition-21','https://arxiv.org/abs/2605.04544v1','cites','Recorded audit of the displayed subset-sum step on PDF pages 27-28; the paper main CNF theorem is not challenged.','roabp-PHP-field-scope-audit'),
(454,'Forbes-Shpilka-Tzameret-Wigderson-2021','https://theoryofcomputing.org/articles/v017a010/','cites','Screened for model/background definitions only, not imported PHP lower bounds.','roabp-PHP-field-scope-audit'),
(454,'Elbaz-Govindasamy-Lu-Tzameret-2025-v1','https://arxiv.org/html/2506.17210v1','cites','Screened for model/background definitions only, not imported PHP lower bounds.','roabp-PHP-field-scope-audit'),
(479,'BIKPRS-Theorem-6.7(1)',GH+'research/notes/SOURCE_AUDIT.md#bikprs-actual-simulation-structure','cites','The actually read concluding proof cites a balancing lemma but provides no selector-input sparsity guarantee.','sparsity-source-audit-and-endpoint-choice'),
(479,'BIKPRS-Definition-6.8',GH+'research/notes/SOURCE_AUDIT.md#bikprs-actual-simulation-structure','cites','The actual source syntax underlies the prefix-conjunction pattern; no unread book implementation is asserted.','sparsity-source-audit-and-endpoint-choice'),
(479,'Byramji-Impagliazzo-2025-v1','https://arxiv.org/html/2511.20023v1','cites','Abstract-only re-screen of the previously audited size-depth source; no broader size theorem imported.','sparsity-source-audit-and-endpoint-choice')]
for pos,target,loc,kind,scope,anchor in rows:
 source=cs[pos]['id'];edges.append({'id':source+'::'+kind+'::external:'+target,'source':{'namespace':'current','id':source,'locator':None},'target':{'namespace':'external','id':target,'locator':loc},'type':kind,'scope':scope,'evidence':[WEB+anchor],'review_status':'reviewed','review':{'revision':REV,'date':'2026-09-19','reviewer':'Codex parallel dependency worker 360-520','note':'Resolved against the exact existing local audit text; no repeated primary-source retrieval.'}})
notes={383:'The compact decoder and interpolation transfer are combined with the exact audited Razborov Theorem 3.1 functional-base bound; the recorded ordinary-PC convention bridge applies.',385:'The explicitly supplied guarded truth-table and boundary maps are followed by balancing from the audited BIKPRS concluding proof and the binary modular source theorem. No sparsity guarantee is assumed.',454:'The displayed characteristic countermodel is proved directly; exact version/Proposition 21 and background-only literature screens are now separately cited. The cited main CNF theorem is not refuted.',479:'The actually read BIKPRS concluding proof and Definition 6.8 are cited, and its unread Krajicek reference is kept as bibliographic attribution only, not a separately imported theorem. The prior bit-PHP abstract screen and the PC endpoint choice are separate.'}
invs=[]
for pos in (383,385,454,479):
 c=cs[pos];targets=[p['target'] for p in packets[pos-360]['passages']]
 if pos in (383,385):targets.append(GH+'research/notes/SOURCE_AUDIT.md'+('#razborov-base-and-residual-pc-lower-bound' if pos==383 else '#bikprs-actual-simulation-structure'))
 invs.append({'id':c['id'],'position':pos,'baseline_claim_sha256':claim_digest(c),'state':'reviewed','note':notes[pos],'next_action':None,'evidence':[{'target':t,'sha256':e.sha256(t)} for t in targets]})
write_json(a.out,{'schema_version':1,'baseline_revision':REV,'claims':invs,'relationships':edges,'scope':'Overrides the four pending inventory dispositions in batch2/batch3 after exact local provenance lookup. Merge with their earlier resolved edges.','counts':{'resolved_pending':4,'relationships':len(edges)}})
print('Resolved four pending provenance questions;',len(edges),'source-scoped citation/dependency edges')
