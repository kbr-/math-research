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
raw='''710|corrects|ex:retained-interface-finite-preservation|Narrows any general extrapolation from the positive finite check; confirms its actual degree-five ranks and preserves that finite result.
710|cites|thm:fresh-block-conservativity-loss-bound|Observed loss one is compatible with the larger proved ceiling; the finite witness is checked independently.
711|refines|ex:same-degree-interface-preservation-refuted|Extends the exact finite loss experiments across ranks two, three and four without asserting all-rank growth.
711|applies|thm:fresh-block-conservativity-loss-bound|The archived rank-three witness realizes the recorded sufficient gain criterion with coefficient-free helper cofactors.
711|cites|thm:affine-level-full-relative-old-preservation|PHP-relative clamping is a separate possible escape from the satisfiable-base composition costs.
712|refines|thm:fresh-block-conservativity-loss-bound|Exact fresh-coefficient equations subsume its constant specialization and sufficient gain criterion; proof is direct coefficient comparison.
713|rediscovers|lem:rank-two-bottom-quadratic-transfer|The same-degree affine rank-two statement is its top-level special case.
713|depends_on|lem:rank-two-bottom-quadratic-transfer|Primary proof uses the already recorded affine coefficient substitution at unchanged degree.
713|depends_on|lem:fresh-block-coefficient-criterion|The separately labelled second proof derives the result from the coefficient equations.
713|cites|ex:rank-dependent-fresh-block-loss|Rank-three failures and rank-two controls distinguish the exact scope; examples are not premises of the universal rank-two proof.
714|cites|lem:fresh-block-coefficient-criterion|Proposes the coefficient-moment dual as an approach; it does not prove conservativity over the specified level-one bases.
714|cites|prop:full-costed-source-coupled-marginals|Compares the raw-coefficient moments with the existing formal-selector marginal interface.
714|cites|check:augmented-php-degree-small-boards|Later finite PHP-base control is supporting evidence only, not proof of the conjecture.
715|applies|thm:affine-level-full-relative-old-preservation|Dualizes the actual weighted substitution into the described normalized one-level functional.
715|cites|conj:level-one-fresh-block-conservativity|Contrasts its free-moment question with the available multiplicative extension.
715|cites|obs:second-level-affine-flat-indicator-inputs|Locates the surviving low products at the previously recorded flat-indicator frontier.
715|applies|lem:rank-two-bottom-quadratic-transfer|Reinterprets a rank-two-bottom three-level source as quadratic-bottom two-level input.
715|cites|thm:combined-rank-two-source-exclusion|Selects its map for further scope review, not as a theorem already covering the proposed third level.
715|cites|prop:compact-virtual-zero-clause-source|Uses the recorded sparse input shape in the placement assessment.
716|depends_on|thm:combined-rank-two-source-exclusion|The obstruction inspects its actual old-only map, low-branch indicators and kernel hypothesis.
716|cites|cor:bounded-indicator-sum-source-transfer|Bounded sums remain covered; unrestricted sums fall outside that quotient lemma.
716|cites|lem:combined-quadratic-affine-kernel|The restricted high-only sketch invokes its dimension ledger but is explicitly not a completed extension theorem.
717|cites|conj:level-one-fresh-block-conservativity|A parked alternative, not a proved implication in the frontier assessment.
717|cites|obs:third-level-rank-two-map-obstruction|Records the preceding third-level scope obstruction and restricted unproved proposal.
717|cites|thm:dependent-rank-source-collapse|Rank-below-accuracy induction motivates the failed rebalancing attempt; it is not refuted.
719|depends_on|lem:flat-restriction-dimension|The exact multilinear flat-image count replaces the crude ordinary polynomial dimension bound.
719|depends_on|thm:combined-rank-two-source-exclusion|Uses the affine specialization of the multiplier space, literal witnesses, low-rank map and unchanged degree ledger.
719|corrects|obs:middle-rank-frontier|Withdraws only the claim that increasing weight degree cannot lower the high threshold in the cube-volume framework.
719|cites|thm:literal-family-matching-restriction|Literal switching is proposed as the next step for narrow literal terms; it is not used in the parameter corollary.
'''
for line in raw.strip().splitlines():
 i,k,t,n=line.split('|',3);add(int(i),k,t,n)
notes={710:'Finite elimination/model checks produce the counterexample; the prior positive example is a checked control and only its general extrapolation is corrected.',711:'Exact archived cofactors and least-degree checks establish the finite examples; the sufficient gain criterion identifies their form, and PHP clamping is comparison.',712:'Direct expansion in multilinear fresh coefficients proves the equivalence locally; prior loss criteria are special cases rather than required lemmas.',713:'Both primary substitution proof and explicitly alternative coefficient proof are inventoried, without treating the alternatives as jointly necessary.',714:'This is an unproved conjecture with finite evidence and a dual reformulation; cited evidence and interfaces are not asserted as proof dependencies.',715:'Review applies known maps to locate the composition frontier; the proposed extra high-only level is not claimed proved.',716:'Targeted map review identifies the hypotheses that fail for low branch indicators and unrestricted bottom sums; the restricted extension stays a sketch.',717:'Frontier assessment inventories the named routes; its incoming cube-volume correction narrows the rebalancing assertion without retracting rank-below-accuracy induction.',718:'Read complete elementary affine-coordinate dimension proof and binomial ratio estimate; no direct indexed theorem is required.',719:'Read complete parameter ledger and explicit correction. Exact flat dimension and the combined finite theorem are the proof inputs; literal switching is a later application proposal.',720:'Imported Beame q-matching lemma is the source statement itself, with its exact section/lemma and nonbipartite scope; unavailable bipartite papers are citations only.'}
for i in range(710,721):
 c=cs[i];rows.append({'position':i,'id':c['id'],'state':'reviewed','evidence':evidence(i),'note':notes[i]+' Recorded direct-claim relationships inventoried; no new proof or literature audit.','next_action':None,'source_fields_sha256':hashlib.sha256(json.dumps({k:c[k] for k in ('id','summary','assessment','record')},sort_keys=True,ensure_ascii=False).encode()).hexdigest()})
c=cs[720];edges.append({'id':c['id']+'::cites::Beame-1994-Lemma-4','source':{'namespace':'current','id':c['id'],'locator':None},'target':{'namespace':'external','id':'Beame-1994-Lemma-4','locator':evidence(720)[0]},'type':'cites','evidence':evidence(720),'review_status':'reviewed','scope':'Beame, A Switching Lemma Primer (1994), Section 5, Lemma 4, printed pages 13–17; imported nonbipartite q-matching statement and recorded source provenance.','review':{'revision':rev,'date':'2026-09-19','reviewer':'Codex parallel dependencies_680_end','note':'Explicit bibliographic source read from the imported-statement record; no fresh external lookup.'}})
(D/'patch_710_721.json').write_text(json.dumps({'base_revision':rev,'range':[710,721],'claims':rows,'relationships':edges},indent=2)+'\n');print('closed',len(rows),'edges',len(edges))
