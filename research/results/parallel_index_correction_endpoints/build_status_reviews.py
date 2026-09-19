import json,sys,hashlib,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'tools'))
from claim_registry import load,references
from claim_reviews import claim_digest,Evidence
D=Path(__file__).parent;x=load();by={c['id']:c for c in x['claims']};e=Evidence();p=json.loads((R/'research/results/parallel_index_dependency_merge/proposal-final.json').read_text());edges={a['id']:a for a in p['relationships']};report=json.loads((R/'research/results/parallel_index_dependency_merge/report-final.json').read_text());groups={}
for a in report['correction_targets']:groups.setdefault(a['id'],[]).append(a)
notes={
'ex:triangular-witness-degree-growth':'Retain finite_check: the double-negation syntax wrapper realizes the saved upper tuple; identities, numeric degrees and finite controls remain valid. No universal normalization lower bound follows.',
'cor:negative-leaf-proper-pruning':'Retain working_proof with repaired support and ceiling: genuine strict-level certificates replace the false proper-containment inference; negative-only removal costs max(B,A_*), not automatic no-loss for every earlier ceiling.',
'cor:all-axiom-boundary-proper-pruning':'Retain working_proof under the repaired strict-support construction and revised T_*^d/C_* ledger. The earlier asymptotic conclusion is recovered; original support justification is not reinstated.',
'ex:retained-interface-finite-preservation':'Retain finite_check: the later counterexample confirms the original degree-five interface ranks but rules out universal same-degree preservation over other bases. The finite positive record is not retracted.',
'obs:middle-rank-frontier':'Retain context: the cube-volume claim that larger k cannot lower the high threshold is withdrawn. The row-linear estimate and general frontier are separate; this is a partial correction, not a theorem proving closure.',
'obs:literal-window-structure':'Retain context: distinct rows alone were insufficient, and the old entropy ceiling concerns the slack encoding. Pigeon-only and pair-space records identify the corrected matching/tree and moved-row scopes. No universal impossibility conclusion survives.',
'lem:adaptive-heavy-query-rule':'Retain refutation for the original adaptive matching-count assertion: a pigeon query need not remove its trigger hole. Hole-only and both-endpoints rules are different corrected algorithms; their validity does not restore the old claim.',
'obs:full-class-holes-are-labels':'Retain working_proof only for corrected hole-only query or both-endpoints round conventions, and the 2^(3c+4) label-set constant. This local rank/tree correction is independent of probability-product gaps in other lemmas.',
'obs:window-height-budget':'Retain conditional: the old mixed compact/slack composition and blanket O(N) height are not proved. The surviving algebraic degree budget requires an actual correct tree and same-family composition. Current-term composition has its own explicit p_R premise.',
 'thm:compact-pair-space-composition':'Retain working_proof for the conditional decoder implication with supplied round bound p_R and original column-sparse hypotheses; later current-term composition removes column-sparseness. Its application corollaries do not gain valid probability premises from supersession.',
 'thm:two-role-compact-composition':'Retain working_proof for the conditional decoder implication with supplied round bound, sparse own pinning and original column-sparseness. Later supersession removes only the last restriction, not all two-role hypotheses or probability premises.',
 'thm:wide-move-composition':'Retain conditional: the implication explicitly requires a wide-move bound not established for the original tree, with a recorded counterexample to that bound. Wide-round composition substitutes a different tree/matching hypothesis; it does not prove the original missing premise.'}
extra={
'ex:triangular-witness-degree-growth':['ports-syntax-clarification'],
'cor:negative-leaf-proper-pruning':['levels-leaf-pruning','levels-negative-support'],
'cor:all-axiom-boundary-proper-pruning':['levels-leaf-pruning','levels-positive-support'],
'ex:retained-interface-finite-preservation':['same-degree-interface-preservation-refuted'],
'obs:middle-rank-frontier':['polylog-high-threshold'],
'obs:literal-window-structure':['pigeon-only-random-flat-refutation','pair-space-encoding'],
'lem:adaptive-heavy-query-rule':['adaptive-rule-gap','hole-only-rule','both-endpoints-rule'],
'obs:full-class-holes-are-labels':['rank-step-correction','both-endpoints-rule'],
'obs:window-height-budget':['composition-gap-statement','current-term-rule-theorem'],
 'thm:compact-pair-space-composition':['current-term-rule-theorem'],
 'thm:two-role-compact-composition':['current-term-rule-theorem'],
 'thm:wide-move-composition':['wide-rounds-composition']}
rows=[];reserved=[]
for cid,items in groups.items():
 c=by[cid]
 if cid not in notes:
  reserved.append({'id':cid,'current_status':c['mathematical_status'],'corrections':items,'decision':'Coordinator owns NA-related mathematical status. Historical constant/composition correction alone preserves the narrowed round/conditional statement; apply the separate NA audit to actual probability reliance.'});continue
 targets=list(dict.fromkeys([t for a in items for t in edges[a['edge']]['evidence']]+['https://kbr.is-a.dev/math-research/#'+a for a in extra[cid]]))
 rows.append({'id':cid,'source_fields_sha256':claim_digest(c),'current_mathematical_status':c['mathematical_status'],'proposed_mathematical_status':c['mathematical_status'],'state':'reviewed','note':notes[cid],'next_action':None,'evidence':[{'target':t,'sha256':e.sha256(t)} for t in targets],'scope':'Status review only; preserve original text, all other field values, and coordinator NA qualifications.'})
result={'base_revision':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'input_registry_sha256':hashlib.sha256((R/'research/claims/index.json').read_bytes()).hexdigest(),'correction_edges_reviewed':len(report['correction_targets']),'distinct_targets':len(groups),'status_reviews':rows,'coordinator_reserved':reserved,'removed_false_obligation':'The amended-away edge to obs:proper-or-subgroups-share-level is not in the final graph and must not trigger a status change.'}
(D/'status-review-proposals.json').write_text(json.dumps(result,indent=2)+'\n');print('correction edges',len(report['correction_targets']),'targets',len(groups),'status reviews',len(rows),'NA coordinator-owned',len(reserved))
