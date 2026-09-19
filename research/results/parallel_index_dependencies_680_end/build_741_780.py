import json,hashlib,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'tools'))
from claim_registry import load
D=Path(__file__).parent;x=load();cs=x['claims'];rev='dc1d95b4cb6a463436256b830afd69029c1dc3ed';by={c['id']:c for c in cs};packets={p['id']:p for p in json.loads((R/'research/results/parallel_index_classify_680_end/packets.json').read_text())};edges=[];rows=[]
def ev(i):return [p['target'] for p in packets[cs[i]['id']]['passages']]
def add(i,k,j,n):
 t=cs[j]['id'] if isinstance(j,int) else j
 assert t in by,t
 edges.append({'id':cs[i]['id']+'::'+k+'::'+t,'source':{'namespace':'current','id':cs[i]['id'],'locator':None},'target':{'namespace':'current','id':t,'locator':None},'type':k,'evidence':ev(i),'review_status':'reviewed','scope':n,'review':{'revision':rev,'date':'2026-09-19','reviewer':'Codex parallel dependencies_680_end','note':'Recorded proof role or explicit scope correction; a dependency edge does not certify its premise.'}})
raw='''741|cites|727|Original adaptive encoding was an attempted extension of the light decoder; no valid general consequence is retained from the refuted rule.
741|cites|740|Hole-query machinery motivates the attempted rule; unary switching is not a proof of the adaptive matching assertion.
742|refines|741|Adds matched-first preference to term selection; the original adaptive query-count assertion is separately refuted.
742|depends_on|758|The restored matching-number bound is for the both-endpoints tree, whose trigger pairs are disjoint.
742|cites|754|On the hole-only tree the appropriate bound is the hole count instead of matching number.
743|depends_on|719|The surviving degree budget uses the compact-board weight ledger after a valid switching step.
743|depends_on|lem:cube-volume-multiplier-space|The dimension/separation budget requires the recorded cube-volume window.
743|cites|754|Hole-only replacement changes the query count but does not itself close composition.
743|cites|758|Both-endpoints replacement changes heavy queries into twice the round count.
744|depends_on|737|The large-mass probability bound invokes the imported negative-association mechanism of dense satisfaction; that source premise is under audit.
746|depends_on|744|Uses the alive-unmatched comparison conditionally after exposing the tail rows.
746|depends_on|745|Uses the light-tail alive versus satisfied comparison for the expectation bound.
746|cites|741|Only the disjoint-tail/pinned-row normalization is used; not the refuted adaptive matching count.
747|depends_on|739|Uses the independent-points refinement of the affine-rank bound, with the precise constants in the record.
747|depends_on|742|Matched-first selection identifies unmatched eligible classes under the corrected tree convention.
747|cites|744|General pair sets need the comparison lemma; the full-class theorem has a simpler equivalence.
747|cites|745|Multirow tails are a proposed extension, not part of the stated single-row theorem.
748|depends_on|739|Uses affine-rank control of the survivor label sets in the flat.
748|depends_on|749|Outside loading controls the event that no class is satisfied.
750|depends_on|739|Its corollary uses affine-rank control of the label-set intersection, with corrected rank parameter.
750|depends_on|754|The hole-only tree makes trigger holes distinct; the adaptive tree does not.
750|cites|758|For the both-endpoints variant the same count bounds rounds and incurs two queries per round.
751|depends_on|749|Outside light loading supplies one of the six exclusion events.
751|depends_on|739|Survivor sets are controlled using the explicit independent-points rank estimate.
751|depends_on|742|Matched-first selection and the corrected tree determine which classes can trigger rounds.
751|cites|744|General pair-set comparison belongs to the further extension, not the full-class theorem itself.
751|cites|745|Tail comparison belongs to the further multirow extension rather than the core single-row argument.
752|applies|741|Finite positive and negative round trips test the original adaptive decoder without proving it universally.
752|applies|754|Later runs test the hole-only replacement on the stated finite instances.
752|applies|758|Later runs test the both-endpoints replacement and retain a failing two-role control.
752|applies|774|Complete-term runs resolve the recorded two-role finite control, not all reader instances.
753|corrects|741|An explicit full-column reader repeats one trigger hole after pigeon queries, refuting the adaptive matching bound.
753|cites|752|Independent round-trip records corroborate the failed-rule mechanism; they are not needed for the explicit adversary argument.
754|corrects|741|Replaces the false adaptive matching claim by a distinct-hole bound for a different, hole-only rule.
754|depends_on|733|Empty hole-query branches have the required algebraic partition/annihilation interface.
754|cites|757|Later sparse-reader failure limits the new rule without refuting its distinct-hole bound.
754|cites|752|Finite role-separated decoder controls support the replacement, without universal computational verification.
756|depends_on|755|Uses light-row matching satisfaction and the cover alternative in the full-column proof.
756|depends_on|739|Uses the corrected affine-rank bounds on survivor sets.
756|depends_on|754|The original theorem counts distinct hole triggers on the hole-only tree.
756|cites|758|Recorded transfer converts the statement to the both-endpoints round count.
757|obstructs|754|A single residual row pinned to all labels forces N hole queries, excluding a general small-height extrapolation but preserving the distinct-hole lemma.
757|cites|741|Adaptive rule solves this particular reader but remains invalid in general.
758|corrects|741|Querying both endpoints restores disjoint trigger pairs; it replaces the original adaptive rule rather than proving it.
758|depends_on|733|Both-endpoints rounds include hole queries with the actual empty branch.
758|applies|738|The sparse matching tail can bound rounds because the trigger pairs form a matching.
758|applies|742|Matched-first preference retains the unmatched-class reduction with the corrected round count.
759|refines|755|Extends the matching-satisfaction mechanism to sufficiently dense two-tier classes with changed constants.
760|depends_on|759|Uses the two-tier matching-satisfaction lemma in the dense-class case.
760|depends_on|738|Sparse classes are handled by the sparse matching tail.
760|depends_on|758|Counts heavy rounds on the both-endpoints tree.
760|refines|756|Contains the bipartite full-column theorem with the explicitly corrected thresholds.
761|refines|738|Adds activation by tail rows to the sparse matching count, relying on a product-measure comparison that needs source audit.
762|depends_on|760|Keeps the dense part of the two-tier proof and its corrected constants.
762|depends_on|761|Replaces the sparse-label hypothesis by an activated-degree bound.
763|cites|764|Reduces the general column conjecture to a weighted matching count; it does not establish the integrated estimate.
764|cites|760|Two-tier labels are a recorded special case, not a proof of the general conjecture.
764|cites|762|Activation-bounded labels are another restricted case.
764|cites|766|Row-spread case is recorded as partial progress only.
764|cites|767|Pattern-bounded case narrows the open hypothesis without settling arbitrary wide crowded patterns.
764|cites|770|Size-restricted multirow consequence is a partial case of the general column obligation.
764|cites|771|Few-light-row special case allows arbitrary size but not arbitrary row inventory.
764|cites|773|Crowded size corollary extends the restricted size range, not all sizes.
765|refines|738|Conditional exposure replaces raw sparse degree by the activated union of pinned rows.
765|refines|761|Union over activated classes strengthens the product-measure version up to constants, avoiding its row-event comparison in this proof.
766|depends_on|765|Activated-union count controls rounds at activation-sparse labels.
766|depends_on|739|The few-middle-labels branch uses the corrected independent-point affine-rank bound.
766|depends_on|758|Matching trigger pairs are counted on the both-endpoints tree.
767|depends_on|765|Small activated unions are bounded by the exposed uniform-row matching count.
767|depends_on|739|Uses the corrected rank step when the number of relevant labels is small.
767|depends_on|758|Heavy rounds are reduced to matching triggers.
767|refines|766|Pattern bounds subsume the stated row-spread special case within the common hypotheses.
767|refines|760|Contains the corresponding role-separated two-tier readers subject to the pattern bound.
768|depends_on|739|Recomputes the independent-point rank exponent for polynomial-size label sets.
768|corrects|750|Changes the label-set corollary constant to 2^(3c+4), preserving the corrected tree-specific bound.
768|corrects|756|Raises the F4 constant and full-column threshold; does not retract the underlying theorem schema.
768|corrects|760|Raises the G4 constant and two-tier threshold.
768|corrects|762|Carries the corrected two-tier threshold into the activation-bounded extension.
768|corrects|766|Raises the few-middle-labels rank constant and row-spread threshold.
769|depends_on|765|The small-light-union H2 estimate is the activated-union matching count.
769|depends_on|767|Reuses the heavy-host mechanism and extends its argument to multirow tails.
769|depends_on|742|Matched-first preference identifies the eligible unmatched hosts.
769|depends_on|758|The both-endpoints tree supplies matching trigger pairs for the round count.
769|refines|767|Multirow mass hypothesis contains the single-row pattern-bounded case with the recorded halved constant.
770|depends_on|769|Derives the size consequence from the theorem's union-mass threshold.
771|depends_on|765|Uses the activated-union count after exposing the few light rows.
771|depends_on|758|Uses matching trigger pairs on the corrected tree.
771|depends_on|742|Matched-first preference excludes hosts with a matched pair.
771|cites|769|Reuses its host notation and threshold; the few-row proof removes its mass hypothesis rather than applying the full theorem unchanged.
772|depends_on|769|Runs the H1–H4 multirow argument on the reduced reader after exposing crowded rows.
772|depends_on|771|Uses the few-exposed-rows probability and labeling-union mechanism.
772|depends_on|765|The reduced H2 step is the activated-union count.
773|depends_on|772|Counts crowded rows from total light mass and invokes the combined theorem.
773|refines|770|Improves the size exponent only with bounded-tail and auxiliary budget conditions.
774|refines|758|Reorders each round before all tail queries and preserves matching triggers.
774|depends_on|742|The term selection remains matched-first.
774|applies|769|Transfers its round argument to the complete-term tree using the declared structural facts.
774|applies|771|Transfers the exposed-row proof with charged exceptional rounds.
774|applies|772|Transfers the combined exposed-row proof with the same charging mechanism.
775|refines|727|Avoiding the moved row's pinned labels extends the light decoder to two-role readers under sparse-pinning richness.
775|depends_on|774|Complete-term ordering ensures the current pinned row cannot later be moved as a light row.
775|cites|743|The old height-budget composition is an application claim subsequently corrected, not a prerequisite of injectivity.
776|depends_on|771|Reuses the few-light-row exposure argument with two-role exceptions explicitly charged.
776|depends_on|774|Round transfer supplies the complete-term tree's matching and charging facts.
776|depends_on|775|The switching clause uses the two-role decoder under sparse pinning.
777|depends_on|772|Follows the crowded/exposed proof with a larger exposed set and an explicit two-role light-mass budget.
777|depends_on|774|Uses matching rounds and the complete-term structural facts.
777|depends_on|765|Applies the activated-union count to the pinned rows outside the exposed/light set.
777|depends_on|775|Sparse-pinning decoder supports the qualified switching clause.
778|depends_on|769|Corollary 1 uses the role-independent H1–H3 mass/count argument.
778|depends_on|774|Transfers the round argument to the complete-term tree.
778|depends_on|777|Corollary 2 is the size consequence of the exposed two-role theorem.
778|cites|776|A special few-row case is comparison, not the general proof of Corollary 1.
778|refines|770|Gives the sparse-pinning two-role form of the first size corollary.
778|refines|773|Gives the exposed/two-role form of the larger size corollary under added hypotheses.
779|corrects|743|Withdraws the unsupported composition sketch and its unconditional O(N) height conclusion.
779|cites|729|Swap repair must address the previously identified code-label ambiguity.
779|cites|734|The previous window entropy claim must not be confused with an already proved compact-family composition.
779|cites|731|The light/heavy dichotomy is explicitly unaffected by this separate mixed-term composition gap.
779|cites|740|Unary switching is explicitly outside this particular composition objection; that does not certify its independent probabilistic premises.
'''
for line in raw.strip().splitlines():
 i,k,j,n=line.split('|',3);add(int(i),k,int(j) if j.isdigit() else j,n)
# Source corrections identify the exact switching clause, not invalidity of each round bound.
for j in [751,756,760,762,766,767,769,770,771,772,773,776,777,778]:add(779,'corrects',j,'Only the then-asserted mixed-term switching composition is withdrawn pending a common-family decoder; the stated round bound is preserved and later repairs have their own hypotheses.')
notes={741:'Original adaptive rule is explicitly refuted; correction-region links to affected theorems are not backward proof dependencies.',742:'Matched-first selection is elementary; count statements are inventoried under the corrected hole-only and both-endpoints conventions.',743:'The weight-degree budget survives, but the blanket height/composition assertion is corrected; exact repaired scope must be separated.',744:'The proof explicitly invokes the same uniform-bijection negative-association inference in its large-mass bound; source applicability is disputed.',745:'Direct light-tail counting is recorded without a named claim prerequisite; verify the conditional exposure hypotheses if using it outside this role-separated scope.',746:'Expectation comparison uses the two preceding probability estimates and does not establish a high-probability correlated bound.',747:'Recorded proof uses negative association across distinct tail rows and a rank count; tree corrections are separate from the imported probability premise.',748:'Loading argument invokes row-event negative association; the corrected tree/rank scope does not resolve the imported probability hypothesis.',749:'Product over row-specific satisfaction events is explicitly justified by negative association; its applicability needs the source audit.',750:'Distinct-trigger-hole and rank argument survives only under corrected tree and rank constants; later transfer links are applications.',751:'Full-class proof uses loading/negative-association exclusions; preserving corrected constants does not discharge this newly identified source concern.',752:'Finite decoder runs are applications to named rules; later variants and failures retain their finite scope.',753:'Explicit repeated-trigger-hole counterexample corrects the adaptive rule; downstream consequences do not become prerequisites.',754:'Hole-only proof uses the actual hole-query branch identities and local counting; later sparse failure limits its application.',755:'Matching satisfaction applies a product bound to events involving disjoint rows and columns; the blanket permutation-NA justification needs audit.',756:'Full-column proof uses matching satisfaction and other product bounds, plus corrected rank constants and tree rule.',757:'Explicit one-row/all-label reader shows the hole-only tree can have N queries; it does not refute the distinct-hole lemma.',758:'Both endpoints are removed at every round, proving matching triggers locally; probability-bound transfer is application of earlier estimates.',759:'Dense-class matching satisfaction invokes the same disputed permutation-product mechanism and requires a separate valid bound.',760:'Two-tier proof combines sparse matching with dense satisfaction and corrected rank steps; probability premises remain to audit.',761:'Product-measure comparison assumes negative association of distinct row events, unlike the later conditional uniform-subset proof.',762:'Activation-bounded extension explicitly composes the two-tier proof with the activated tail estimate; both relevant premise scopes must be audited.',763:'The two-stage weighted matching reduction explicitly multiplies row-specific events via negative association; exact conditional permutation scope is unresolved.',764:'Unproved conjecture with recorded partial cases; those cases are citations only, and their own proof audits do not prove or refute the conjecture.',765:'Conditional on the flat and light exposure, residual pinned rows are a uniform subset; the elementary symmetric matching count is distinct from arbitrary permutation-entry NA.',766:'The many-label branch asserts NA and Chernoff for distinct-column occupant events; the source-scope concern applies directly.',767:'Heavy-host and large-union steps multiply avoidance probabilities across columns; the subset sampling steps must be distinguished from that questionable inference.',768:'Elementary rank exponent correction retains narrower theorems with larger constants; unaffected theorems in the same paragraph are not correction targets.',769:'H1/H4 use permutation-column avoidance and light-bijection satisfaction; H2 uses the separate valid uniform-subset matching count.',770:'The size arithmetic is a direct consequence of the mass theorem; its required imported probability premises still need audit.',771:'K1 explicitly uses NA of decreasing distinct-column occupant events; K2 is a separate rank/matching count.',772:'Exposed uniform-subset concentration is not itself challenged; inherited reduced-reader product steps still require the source audit.',773:'Size consequence inherits the combined theorem; no independent probability argument repairs its questioned premises.',774:'Local tree-order/matching facts are self-contained, while transfer clauses inherit the exact probability proofs of the named theorems.',775:'Injective coding and hypergeometric richness are the two-role proof mechanisms; no permutation-column product is used in the decoder identity itself.',776:'Exposure transfer and decoder preserve their explicit hypotheses; the inherited few-row probability argument needs the source audit.',777:'Reduced-reader product steps inherit the same permutation-event issue in H1/H4; decoder structure is separate.',778:'Two size consequences use different source arguments, retained separately; the inherited probability scope remains pending.',779:'Exact historical gap concerns compact versus slack probability spaces and undefined free-hole pins; it preserves round bounds and names later repair routes.'}
pending={743,744,746,747,748,749,751,755,756,759,760,761,762,763,766,767,769,770,771,772,773,774,776,777,778}
for i in range(741,780):
 c=cs[i];action=None
 if i in pending:action=('Resolve the corrected composition/height scope against the later current-term repair, without promoting the original unconditional claim.' if i==743 else 'Audit the precise permutation negative-association or inherited product-bound premise identified in the source; supply a valid replacement or record the scoped proof gap. Preserve independent tree/rank and uniform-subset arguments.')
 rows.append({'position':i,'id':c['id'],'state':'pending' if i in pending else 'reviewed','evidence':ev(i),'note':notes[i],'next_action':action,'source_fields_sha256':hashlib.sha256(json.dumps({k:c[k] for k in ('id','summary','assessment','record')},sort_keys=True,ensure_ascii=False).encode()).hexdigest()})
# Direct uses of the disputed imported premise are recorded as reliance, not as validation.
for i in [744,747,748,749,751,755,756,759,760,761,763,766,767,769,771,777]:
 edges.append({'id':cs[i]['id']+'::depends_on::JoagDev-Proschan-1983-NA','source':{'namespace':'current','id':cs[i]['id'],'locator':None},'target':{'namespace':'external','id':'JoagDev-Proschan-1983-NA','locator':'https://kbr.is-a.dev/math-research/#dense-labels-satisfied'},'type':'depends_on','evidence':ev(i),'review_status':'reviewed','scope':'Recorded permutation-event product/concentration step invokes imported negative association; applicability is under audit and is not certified by this reliance edge.','review':{'revision':rev,'date':'2026-09-19','reviewer':'Codex parallel dependencies_680_end','note':'Direct reliance identified in source; hypothesis match pending.'}})
(D/'patch_741_780.json').write_text(json.dumps({'base_revision':rev,'range':[741,780],'claims':rows,'relationships':edges},indent=2)+'\n');print('inventories',len(rows),'pending',len(pending),'edges',len(edges))
