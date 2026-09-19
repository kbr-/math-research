import json,re,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'tools'))
from claim_reviews import Evidence,claim_digest
D=json.loads((R/'research/claims/index.json').read_text());C=D['claims'];REV=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
WEB='https://kbr.is-a.dev/math-research/#';GH='https://github.com/kbr-/math-research/blob/main/'
rows=[];notes={}
def add(s,t,k,scope,namespace='current',locator=None):
 source=C[s]['id'];target=C[t]['id'] if isinstance(t,int) else t
 anchor=re.search(r'/#([^ )]+)',C[s]['record'])[1]
 rows.append({'id':source+'::'+k+'::'+('' if namespace=='current' else namespace+':')+target,'source':{'namespace':'current','id':source,'locator':None},'target':{'namespace':namespace,'id':target,'locator':locator},'type':k,'scope':scope,'evidence':list(dict.fromkeys(re.findall(r'\]\((https://[^)]+)\)',C[s]['record']))),'review_status':'reviewed','review':{'revision':REV,'date':'2026-09-20','reviewer':'Codex GPT-6 Astra parallel dependency worker','note':'Reviewed source-relative prerequisites and direct proof roles, reusing existing source audits; no new theorem or kernel verification.'}})
for s,t,k,n in [
(260,258,'depends_on','The total-exception trimming supplies n0 and the remaining maximum exception budget B.'),
(260,248,'depends_on','The strict-majority construction and its recorded congruent-K parameter argument supply the residual N and finite union-bound conditions.'),
(262,241,'refines','Reuses the capacity proof cell-clearing method directly on separating column probes; the local argument is restated rather than invoking the common-partition theorem.'),
(263,261,'depends_on','Distinct bit signatures force singleton local classes and the exact minimum exception count n squared.'),
(263,262,'depends_on','Separating occupied profiles exclude simultaneous degree-two affine freezing on a hard residual.'),
(263,'thm:affine-column-state-normalizer','depends_on','The independent block realization is eliminated by the existing single-column normalizer; this contrasts with input freezing.'),
(264,'thm:affine-column-state-normalizer','depends_on','The affine state interpolation and degree-complete column reduction give original-degree companion and field certificates.'),
(264,'thm:stable-ideal-ENS-input-replacement','applies','Selector-aware normal forms permit a later certified input-replacement application; the elementary output-class count does not itself require that theorem.'),
(265,264,'depends_on','Coefficient and selector output partitions determine the explicitly charged common-refinement product.'),
(265,239,'depends_on','Orbit-sum recognition expresses the proper normal form in refined class statistics.'),
(265,'thm:stable-ideal-ENS-input-replacement','depends_on','Full actual later-input normal forms are replaced with original-degree companion certificates, preserving cancellation accounting.'),
(265,245,'depends_on','A qualifying compatible local-statistic layout freezes the remaining package without per-level cost.'),
(266,263,'depends_on','Uses the bit-labelled single-column input family as its explicit initial package.'),
(266,265,'depends_on','Selector-aware output compression permits later use of coefficient/selector outputs under the stated package hypothesis.'),
(266,238,'depends_on','The common odd-label class and K=p-1 yield the displayed linear residual parameter.'),
]:add(s,t,k,n)
for s,n in [(262,'The local degree-two refutation contradiction uses the existing all-field residual PHP lower bound for N at least three.'),(267,'Only the stated PHP corollary invokes the existing weak-base degree bound; affine defining-extension preservation itself is proved directly.')]:
 add(s,'Razborov-1998-Theorem-3.1','depends_on',n,'external',GH+'research/notes/SOURCE_AUDIT.md#razborov-base-and-residual-pc-lower-bound')
add(269,'lem:fieldreduction','depends_on','Boolean monomial reduction of F(sum y) supplies the degree n+1 certificate before dividing by the nonzero factorial.','historical',GH+'php_codex_handoff/manuscript/chapters/01_foundations.md#lem-fieldreduction')
notes.update({260:'Trimming and majority layout are actual inputs; the 1/12 density is a sufficient asymptotic application with finite conditions retained.',261:'Direct coefficient-signature comparison at proper column states proves recognition, exact exception minimum and span invariance; no prior claim needed.',262:'Direct degree-two cell-clearing proof plus residual PHP lower bound; common-partition capacity is a method refinement, not an additional hypothesis.',263:'Separated raw-signature obstruction from the independent ENS normalizer realization; neither asserts unavoidable Frege source structure.',264:'Read coefficient interpolation and selector refinement including common-zero choices and actual degree ledger; column normalization supplies certificates, input replacement is only a later application.',265:'Reviewed joint refinement product, orbit-sum recognition, cancellation-sensitive input replacement and compatible-layout premise; no compatibility inferred merely from bounded classes.',266:'Explicit first-one-bit grouping composes the hybrid normalizer theorem with common-partition freezing; later uses of raw inputs remain excluded.',267:'Affine NS and PC replay and prime-field Frobenius identity are proved locally; PHP degree consequence alone imports Razborov, and sparse size is not preserved.',268:'Explicit telescoping identity, top-monomial target degree and inactive-axiom countermodel are proved locally; no lower bound for alternative gate interfaces inferred.',269:'Direct modular satisfying point and factorial certificate, using Boolean monomial reduction; abstract occupancy models do not lift to PHP.'})
for s,t,k,n in [
(271,270,'depends_on','Nonzero top coefficient of the independent Boolean encoding survives in at least one prime-field coordinate; the product-column restriction uses the same independent-input function.'),
(272,'thm:affine-column-state-normalizer','depends_on','Affine column normalization supplies companion/field image certificates and the common-zero selector predicate.'),
(272,'thm:stable-ideal-ENS-input-replacement','depends_on','Certified full-input normal forms preserve the original axiom ledger before the refined layout.'),
(272,239,'depends_on','Orbit-sum recognition expresses the proper reduced inputs in selector-refined statistics.'),
(272,245,'depends_on','The compatible-layout theorem eliminates the resulting local-statistic package.'),
(272,265,'refines','When only selector products are read, coefficient-output distinctions are dropped; at most two occupied classes per removed block remain.'),
(273,'thm:level-ordered-virtual-axiom-boundaries','depends_on','The constructor syntax restricts actual level-s input dependence to earlier selector products.'),
(273,'thm:virtual-source-PHP-endpoint','depends_on','The endpoint sends removed selectors to base polynomials and retains genuine products on actual mapped inputs.'),
(273,'thm:stable-ideal-ENS-input-replacement','applies','The modulo-proper-ideal representation supports certified normal-form replacement; ordinary degree is not redefined.'),
(274,272,'depends_on','Selector-only hybrid transfer removes the grouped bit blocks and preserves the stated later package.'),
(274,238,'depends_on','The common nonzero-label class yields the displayed residual size.'),
(274,266,'refines','Reading only the grouped selector removes the extra coefficient distinctions in the earlier bit-package control.'),
(275,'thm:virtual-source-PHP-endpoint','cites','The two-negative-literal coefficient pair repeats the endpoint pair; the local certificate is fully restated.'),
(276,275,'depends_on','Positive-literal common-zero selectors realize chosen binary label bits with explicit legal-column semantics.'),
(276,261,'applies','The singleton-profile instance gives minimum exception count n squared; no proof-essentiality is inferred.'),
(277,'thm:virtual-source-PHP-endpoint','cites','The open bridge starts with the already-recorded weak PHP source endpoint; it is not a proof of source-family elimination.'),
(277,'thm:triangular-polynomial-pc-pruning','cites','Route audit records this conditional replay tool and its missing structural coverage, not a deduction of the open bridge.'),
(278,'thm:virtual-source-PHP-endpoint','applies','Row exclusions are adjoined only after obtaining the weak source endpoint, preserving its existing proof without deriving those axioms.'),
]:add(s,t,k,n)
add(278,'Razborov-1998-Theorem-3.1','depends_on','The audited functional PHP convention and quotient multiplication charge imply the same ordinary-ring residual degree bound.','external',GH+'research/notes/SOURCE_AUDIT.md#razborov-base-and-residual-pc-lower-bound')
notes.update({270:'Direct multilinear uniqueness and nonzero top-coefficient proof; field encoding parameters are retained and no auxiliary-variable lower bound follows.',271:'Uses the preceding encoding polynomial degree, then a direct nonzero-coordinate argument and proper-product-domain restriction; one-column collision collapse is retained.',272:'Direct two-class selector observation plus affine column normalization, certified input replacement, orbit recognition and compatible local layout; coefficient occurrences in proof lines remain permitted.',273:'Audited constructor syntax and endpoint map; optional packing/sharing is excluded, and selector-only dependence does not establish useful base support.',274:'Grouping comparison uses selector-only hybrid/common-partition transfer and refines the prior bit-output example; regrouping an existing proof is not authorized.',275:'Complete literal-sign cases and explicit coefficient images are local; source endpoint pair is provenance, not an additional assumption.',276:'Binary coding realizes arbitrary partitions via the positive-literal selector classification; the exception corollary uses exact inventory recognition and does not assert source indispensability.',277:'Recorded source endpoint and triangular-replay citations. Remaining older nested-span/core-residual and failed-batching references need complete target reconciliation before this multi-entry route inventory is closed.',278:'Uses audited functional Razborov convention and direct quotient replay/matching restriction; source endpoint is the application being strengthened, not a derivation of row exclusions.',279:'Self-contained canonical switching injection and falling-factorial count; no independence or prior probability theorem is assumed.'})
for s,t,k,n in [
(281,279,'depends_on','Positive switching bounds the bad live matching event for every literal tuple.'),
(281,280,'depends_on','Negative-literal survival bounds the second exceptional event before the global union bound.'),
(281,275,'depends_on','One-column literal coefficients extend verbatim to functional row/column stars and fit original companion degrees.'),
(281,278,'depends_on','Functional matching restriction supplies the preserved base and the residual degree contradiction for the all-blocks application.'),
(282,278,'depends_on','Functional residual lower bounds justify the rectangle and column-permutation contradictions in the affine-consequence extension.'),
(283,20,'refines','Refines the earlier resistance template to a union bound over residual vertex sets, covering all matching-induced constant shifts.'),
(283,282,'applies','Only the assertion that affordable affine base consequences add nothing invokes functional affine rigidity; the random full-rank construction itself is linear algebra.'),
(284,283,'depends_on','The uniform rank family supplies pairwise-zero quotient intersections and no constant-one pair span on every square-root residual.'),
(284,282,'depends_on','Functional rigidity excludes any gain from adjoining affordable affine base consequences.'),
(285,'thm:direct-ordinary-php-transfer','applies','The separate ordinary NS source endpoint supplies the certificate type needed for this rate lemma; the PC endpoint alone is insufficient.'),
(285,278,'applies','The functional auxiliary strengthening can also be made after the NS source endpoint; this is an application, not the weighted tree argument premise.'),
(286,285,'depends_on','Compares the stated diagonal guarantee with the extracted strict probability inequality and binary query-height budget.'),
(289,285,'cites','The covariance probe is an independently derived necessary test for distributions proposed for the recorded ENS rate; it does not use that rate to prove the probe inequality.'),
]:add(s,t,k,n)
add(282,'thm:rigidity','refines','Extends the historical affine-consequence argument to the explicitly functional auxiliary base using its verified residual degree interface.','historical',GH+'php_codex_handoff/manuscript/chapters/09_decomposition.md#thm-rigidity')
add(284,'thm:spreadcost','depends_on','The exact core-residual decomposition argument gives min(D+M,T(r)D) from pairwise-zero geometry.','historical',GH+'php_codex_handoff/manuscript/chapters/09_decomposition.md#thm-spreadcost')
for s,identifier,kind,scope in [(285,'Krajicek-2301.10617v3-Theorem-3.2','depends_on','The existing audit of Lemmas 3.3-3.4 and Theorem 3.2 supplies averaging and conflict-tree construction, with the sharper weighted rate retained.'),(286,'Krajicek-2301.10617v3-Problem-3.5','cites','The audited diagonal parameter guarantee is compared with the strict sufficient rate; this is not a refutation of the source problem.'),(287,'Krajicek-2301.10617v3-Lemma-4.3','depends_on','Imported conflict-to-live-cell reduction; the local explanation retains both prefix chains and the original degree budget.')]:
 add(s,identifier,kind,scope,'external','https://arxiv.org/abs/2301.10617v3')
notes.update({280:'Direct exact disjoint-event count and elementary factorial upper bounds; no independence assumption beyond uniform conditional matching.',281:'Switching/survival estimates, locally recalled bipartite-cover argument, and explicit star normalizers yield simultaneous coverage; functional lower-bound consequence remains scoped to removal of all needed blocks.',282:'Historical rigidity method extends using explicitly functional base/residual bounds; full local coefficient rectangle and column permutation argument inspected.',283:'Residual-subboard full-rank union bound refines the earlier template; functional rigidity is needed only for the affordable-affine-consequence application.',284:'Uniform rank geometry feeds the historical exact criterion cost; this is an obstruction to that criterion, not an augmented-PC degree lower bound.',285:'Imported averaging/tree construction with finite weights and factor fallback; direct NS endpoint and auxiliary strengthening are applications, not inferred from PC alone.',286:'A direct numerical comparison of the extracted rate with the audited Problem 3.5 parameter guarantee; stronger distributions or further implications remain open.',287:'Imported Lemma 4.3 with both prefix chains spelled out; design distribution and degree-fit premises retained, no fresh paper verification.',288:'Resolved widened ownership to the free-column paragraph only: direct row-defect binary search independent of the imported live-cell reduction; no unmatched-row conclusion.',289:'Direct random bilinear probe and finite averaging proof, with residual covariance rank equality; rate bridge is contextual and no distribution-rank bound is asserted.'})
for s,t,k,n in [
(290,'lem:uniform-degree-two-affine-rigidity','refines','The prior moment construction with zero same-row cross-moments is strengthened to a complete functional-base quadratic affine-space law.'),
(290,289,'cites','Uses the recorded covariance definition; the rank probability bound is independently derived from uniform margin fibers and four-cycle variations.'),
(291,290,'depends_on','The full quadratic covariance law gives the pair-measure rank bound and nonzero-row regularity estimate.'),
(291,289,'depends_on','Lifted covariance rank equals residual rank; the final conditional rate consequence uses the binary probe.'),
(291,285,'applies','Only the final probability-budget consequence compares with the ENS sufficient rate; full higher marginal is still a premise.'),
(293,292,'applies','The finite checker constructs the exact matching-moment NS equations from the boundary-filling setup, not iterative PC closure.'),
(294,292,'depends_on','Row-set cycle filling extends prescribed quadratic moments once the imported vanishing range is supplied.'),
(295,294,'depends_on','Surjective extension supplies the full uniform quadratic marginal in the required higher-degree range.'),
(295,291,'depends_on','Regular-pair counting controls uniform distinct maps after projecting to the actually queried degree.'),
(295,289,'depends_on','The binary covariance probe gives the short deterministic counterattack.'),
(295,285,'applies','The counterattack is compared with the sharp ENS rate; it does not refute the source theorem or weaker probability question.'),
(296,290,'depends_on','The complete quadratic law certifies that the explicitly assigned moments satisfy all degree-two NS constraints.'),
(296,294,'depends_on','Prescribed rank-two moments extend through R under N>=2R-1.'),
(297,296,'obstructs','Rules out a positive query-survival guarantee for the one-collision mean prototype, for every choice of higher extension and weights; not every low-rank design.'),
(297,285,'applies','The prototype fails the ENS sufficient rate only when its permitted height covers the explicit attack height.'),
(299,289,'refines','Extends the variable-level binary covariance probe to the full degree-t polynomial space over F_p; the argument is restated with degree2t budget.'),
]:add(s,t,k,n)
for s,identifier,kind,scope,url in [
(294,'BLVZ-1994-Theorem-1.1','depends_on','The previously audited chessboard connectivity range gives the required reduced homology vanishing for N>=2k-1.','https://doi.org/10.1112/jlms/49.1.25'),
(297,'Byramji-Impagliazzo-2025-Remark-A.4','rediscovers','The dated attribution audit identifies the earlier unary near-permutation parity-search mechanism; this claim extends it to designs and refines the explicit XOR height.','https://arxiv.org/html/2511.20023v1'),
(298,'Laurent-Mourrain-2009-Theorem-1.4','cites','Attributes the established flat-extension technique; the finite-field quadratic-generator operator argument is given directly rather than importing the theorem as an unproved step.','https://arxiv.org/abs/0812.2563'),
(299,'Krajicek-2301.10617v3-Definition-3.1','cites','The audited query model bounds degree and height but not descriptions, allowing dense degree-t queries.','https://arxiv.org/abs/2301.10617v3'),
]:add(s,identifier,kind,scope,'external',url)
notes.update({290:'Uniform affine-fiber counting and allowed four-cycle variations establish the analytic law; prior construction is explicitly refined and finite samples are unnecessary.',291:'Reviewed recovery of matching/projected residual map from nonzero covariance rows and distinction between uniform pairs and distinct maps; higher marginal remains conditional here.',292:'Matching monomial reduction, triangular independence and direct row-set cycle/filling induction give the conditional NS extension criterion; no PC closure or unconditional homology input assumed.',293:'Exact finite linear-algebra evidence instantiates matching-moment equations; sample covariance values do not establish full-space probabilities and no historical computation was rerun.',294:'Imports the audited BLVZ connectivity theorem and applies the prior boundary-filling construction; normalization and NS scope remain explicit.',295:'Combines verified higher marginal, distinct-map comparison and covariance probe against the ENS sufficient rate; no conclusion about nonuniform families or general Frege.',296:'Explicit rank-two quadratic moments are checked via the complete degree-two law, then extended by the recorded theorem; no query guarantee asserted.',297:'Reviewed original attack and later attribution entry: pointwise mechanism is a rediscovery, while design extension/XOR height are explicit refinements; attack targets the specified mean pattern.',298:'Self-contained flatness/operator argument and centered-rank identity; general flat-extension technique is attributed by citation, without positivity or unproved theorem invocation.',299:'Direct full-query-space version of binary probe; arbitrary descriptions and degree2t<=D are essential, and source definition only identifies its model scope.'})
for s,t,k,n in [
(300,298,'depends_on','Full polynomial covariance rank grows sufficiently at the chosen degree, including the stronger binary estimate.'),
(300,299,'depends_on','The full-space probe gives a counterattack within the stipulated height.'),
(300,285,'obstructs','The sufficient survival premise is unavailable in the stated degree regime; the conditional implication itself remains valid.'),
(300,295,'refines','Extends the obstruction from the uniform residual candidate to every design distribution in the stated degree range.'),
(301,296,'applies','The seven-hole finite extension starts from the explicit rank-two prototype.'),
(301,292,'applies','Row-set boundary filling constructs the saved quartic moment extension.'),
(301,298,'cites','The finite ranks illustrate variable/full-polynomial covariance distinction; they do not prove the general rank theorem.'),
(301,297,'cites','The five-hole control demonstrates that rank two does not imply the one-collision first-moment premise; it does not refute that qualified attack.'),
(302,285,'depends_on','Counts the partial sums, block factors and input-factor fallback in the source weighted ENS conflict tree.'),
(302,299,'cites','The full-space probe also has few distinct queries, so query count alone cannot exclude it.'),
(303,'lem:theorem-approximation-simulation','depends_on','Balanced source inventory and depth recurrence supply the simulation whose representation is refined.'),
(303,'prop:php-final-boundary-pruning','depends_on','Affine boundary/clause substitution and explicit image certificates transfer the circuit accounting to weak PHP.'),
(303,'lem:mp-composition','depends_on','Exact cofactor recurrence composes shared local multiplier/cofactor circuits.'),
(304,303,'depends_on','Compact source certificate bounds the query and leaf circuit descriptions.'),
(304,302,'depends_on','Exact source-tree inventory bounds partial-sum and omitted-factor constructions.'),
(304,285,'depends_on','Weighted ENS averaging supplies the conditional contradiction from the restricted-class survival premise.'),
(304,307,'cites','Later compact attack invalidates the needed coarse-budget premise, not the conditional implication.'),
(306,299,'refines','Replaces full uniform coefficient sampling by small-bias sampling in the same covariance query tree.'),
(306,298,'applies','Moment rank bounds transfer to multilinear query space when applying the abstract rank-dependent probe.'),
(306,305,'applies','The explicit generator gives the compact circuit-size specialization of the abstract small-bias bound.'),
(307,298,'depends_on','Full covariance rank supplies the universal rank floor at the chosen degree.'),
(307,305,'depends_on','Generator with chosen extension-field size meets the required bias and circuit budget.'),
(307,306,'depends_on','Small-bias probe bound retains a strict gap after the explicit error accounting.'),
(307,303,'applies','The PHP source symbol budget exceeds the compact counterattack descriptions asymptotically.'),
(307,304,'obstructs','The source criterion cannot supply its survival premise at the stated coarse polynomial circuit budget; tighter restrictions remain open.'),
(307,300,'refines','Makes the unrestricted rate obstruction succinct with explicit query circuits.'),
(308,305,'applies','Finite-field distribution and truncated-product fixtures test the explicit generator, with fixed-functional negative controls.'),
(309,'lem:mp-telescoping','depends_on','Existing prefix coefficients give the polynomial-in-accuracy OR comparison identity.'),
(309,303,'depends_on','Reuses local approximation, formal-axiom and domain-witness accounting, replacing the exponential OR expansion.'),
(309,'lem:mp-composition','depends_on','Unrolling the cofactor recurrence on the balanced proof tree yields shallow path products.'),
(309,'prop:php-final-boundary-pruning','depends_on','Affine PHP endpoint image certificates preserve polynomial size and constant extra depth.'),
]:add(s,t,k,n)
add(303,'BIKPRS-1996-simulation','depends_on','The existing audit of Lemmas6.2,6.9-6.12 and Theorem6.7 supplies local simulation and balancing inputs to the circuit accounting.','external',GH+'research/notes/SOURCE_AUDIT.md#bikprs-actual-simulation-structure')
add(305,'AGHP-1992-small-bias-construction','cites','Attributes the classical finite-field evaluation plus random-linear-functional method; the multivariate coefficient construction and zero-count proof are given locally.','external','https://www.wisdom.weizmann.ac.il/~/oded/p_aghp.html')
notes.update({300:'Rank growth plus full-space probe rule out the stated survival premise universally in the explicit degree range; earlier uniform result is refined, not a Frege upper bound.',301:'Saved finite construction uses rank-two starting moments and boundary filling; countercontrols distinguish unsatisfiability and the one-collision promise without refuting qualified lemmas.',302:'Source tree counted directly from the weighted averaging construction; term identity is in design values and complements omit factors rather than divide.',303:'Read omitted witness/accounting passages: simulation, MP, boundary images and audited BIKPRS local/balancing statements supply exact prerequisites; shared circuit representation does not assert shallow formulas.',304:'Separated original valid conditional criterion from later compact obstruction; same anchor ownership must not turn attack prerequisites into prerequisites of the earlier implication.',305:'Direct polynomial zero-count induction and truncated-product recurrence establish bias/circuit bounds; classical small-bias method credited as provenance.',306:'Character orthogonality proves general small-bias kernel bound; prior probe is refined, moment rank and explicit generator are applications under their own degree/bias premises.',307:'Combines rank, generator and small-bias probe with explicit error gap, then compares source budget; obstruction targets survival premise, not validity of the conditional criterion.',308:'Exact distribution/Fourier and recurrence fixtures apply the generator construction; negative control fixes the multiplier and no PHP-design sampling is inferred.',309:'Uses existing telescoping and MP recurrence, prior local source accounting and endpoint images; balanced path unrolling changes formula depth/size, not degree conventions.'})
for s,t,k,n in [
(311,310,'depends_on','Least-nonzero-degree contraction bounds the selected mixture component; independent summation amplifies the bias.'),
(311,306,'applies','Degree-preserving Boolean reduction identifies values/pairings of unreduced shallow formulas in the covariance application.'),
(312,311,'depends_on','Degree-mixture sums supply depth-three factors and depth-four product queries.'),
(312,306,'depends_on','The same small-bias covariance calculation yields the strict probability gap.'),
(312,307,'refines','Retains compact-obstruction degree/height/error parameters while replacing its circuit generator by shallow formulas.'),
(312,309,'obstructs','Generic source query budgets with arithmetic depth at least four cannot support the needed survival premise; the representation theorem remains valid.'),
(313,310,'applies','Exact coefficient tests check least-degree contraction bias with non-Boolean raw-power negative controls.'),
(313,311,'applies','Exact mixture distributions test bias amplification inputs; fixed positive degree fails the constant test.'),
(314,292,'depends_on','Matching-moment equations and row-set filling method extend from arbitrary prescribed degree.'),
(314,294,'refines','Strengthens quadratic extension to every starting degree within the same audited board range.'),
(314,293,'cites','Four-hole cubic failure lies outside the stated range and is retained as a scope control, not a premise.'),
(316,314,'depends_on','Stable filtration identifies affordable PC consequences with the low-degree NS space.'),
(316,315,'depends_on','An augmented refutation would learn every common-vanishing degree-k polynomial at the explicit budget.'),
(316,278,'applies','Auxiliary strengthening transfers the exclusion to the weak source base without deriving row exclusions.'),
(317,316,'depends_on','Explicit asymptotic dimension ratios establish the sufficient exclusion inequality at k logarithmic in family count.'),
(317,283,'applies','The formerly resistant residual family satisfies the required positive fractional ranks.'),
(317,284,'cites','Bypasses that method-specific core-cost obstruction; it does not contradict its optimized-cost statement.'),
(318,316,'applies','Exact integer examples test both dimension and board-size sufficient inequalities separately.'),
(318,317,'applies','Scaled examples use the logarithmic parameter prescription without instantiating all resistant matrices.'),
(319,283,'refines','Dyadic ranks and a uniform residual-size union bound extend the earlier fixed-residual construction.'),
]:add(s,t,k,n)
add(314,'BLVZ-1994-Theorem-1.1','depends_on','The audited connectivity theorem supplies every row-set filling step for N>=2B-1.','external','https://doi.org/10.1112/jlms/49.1.25')
add(314,'lem:duality','depends_on','Finite-dimensional annihilator duality converts design extension to the stable NS filtration identity before PC closure.','historical',GH+'php_codex_handoff/manuscript/chapters/01_foundations.md#lem-duality')
add(315,'thm:one-elimination','refines','Extends the weighted-specialization principle to one common vanishing polynomial for all affine blocks; local weighted replay and original cofactor ledger are explicitly proved.','historical',GH+'php_codex_handoff/manuscript/chapters/07_elimination.md#thm-one-elimination')
notes.update({310:'Self-contained diagonal-minor rank and iterated contraction argument, including tensor precursor and Boolean-reduction qualification; no prior lemma required.',311:'Uses least-degree contraction and independent-sum bias amplification; Boolean reduction bridge is the covariance application, not an unsupported raw-power assertion.',312:'Resolved shared anchor to compact obstruction theorem307, not original circuit criterion304; shallow sampler plus same rank/small-bias error calculation defeats generic depth>=4 budgets.',313:'Exact generator/least-degree fixtures and fixed-degree/raw-power controls instantiate prior bounds; no new design sampling or universal inference from samples.',314:'Matching-moment extension from arbitrary degree uses audited BLVZ and annihilator duality, then a direct PC multiplication induction; equality is not asserted for augmented systems.',315:'Read affine ideal-membership proof and weighted PC/NS replay separately; method refines historical one-block elimination with a shared vanishing target and original degree activity.',316:'Dimension comparison invokes common-vanishing learning and stable filtration; matching monomial/row relation counts are derived locally, and weak-base corollary uses explicit strengthening.',317:'Applies the dimension criterion with logarithmic k and verifies the formerly resistant family rank fraction; the old method-specific obstruction remains valid.',318:'Finite integer checks apply sufficient inequalities with separate failure controls; no source-matrix existence witness or augmented refutation is inferred.',319:'Refines residual-rank construction using one union bound across dyadic ranks and residual board sizes; affine shifts and lack of source-proof essentiality retained.'})
for s,t,k,n in [
(320,319,'depends_on','The multiscale inventory preserves a middle-rank class on every usable residual board.'),
(320,314,'depends_on','Stable affine consequences do not enlarge row span in the permitted residual degree range.'),
(320,284,'depends_on','The existing exact core-cost formula gives the older numerical-test obstruction.'),
(320,316,'obstructs','Its sufficient dimension inequality fails on the selected class for every feasible k; the exclusion theorem is not refuted.'),
(321,319,'applies','Exact union sums certify only the stated family-existence ranges.'),
(321,320,'applies','Exact usable-board and feasible-degree checks instantiate both numerical criterion gaps.'),
(323,319,'refines','Uses integer-rank full stacks instead of dyadic pair tests to force complete joint independence modulo rows.'),
(324,323,'depends_on','Full-stack residual independence supplies the selected disjoint affine coordinate groups.'),
(324,322,'depends_on','Exact common-kernel basis gives first nonzero degree equal to the group count, also after affine row cleanup.'),
(324,315,'obstructs','No nontrivial Boolean/row common class fits this learning ledger on the selected family; quadratic-base membership and other methods are not excluded.'),
(325,322,'applies','Finite kernel bases and pairwise-only control test exact Hilbert counts and the full-independence hypothesis.'),
(325,323,'applies','Exact full-stack union sums instantiate the stated sufficient existence range.'),
(325,324,'applies','Usable-board budget checks instantiate the method-specific first-degree obstruction.'),
(326,315,'refines','Replaces Boolean common vanishing with degree-c full-base relative membership and separates actual target degree s from certificate ceiling c.'),
(326,'thm:target-annihilator-batch','cites','Contrasts the distinct nested-span/annihilator hypothesis; no such supplied annihilators are used here.'),
(327,326,'depends_on','Relative learning would put a shared target into affordable old PC consequences.'),
(327,314,'depends_on','Stable filtration identifies those low-degree PC consequences with the old NS space, contradicting a nonzero relative class.'),
(328,327,'applies','Finite exact quotient/intersection fixtures test the relative interface at its explicit N,h,D,c budget.'),
(328,326,'obstructs','The random fixture has no useful class at any affordable membership ceiling for this learning ledger; no asymptotic source obstruction or augmented refutation is inferred.'),
(328,314,'depends_on','Stable affine consequence space identifies the thirteen control classes and rules out R1 when R2 is zero.'),
(328,'cor:php-clause-containing-pruning','applies','The successful control reuses the already-handled clause-span case with a local degree-two identity.'),
]:add(s,t,k,n)
add(329,'lem:mixedsystem','depends_on','The first mixed-support band specializes the historical sufficient diagonal coefficient-operator construction to singleton/pair components.','historical',GH+'php_codex_handoff/manuscript/chapters/06_moments.md#lem-mixedsystem')
add(329,'thm:window','cites','Places the first mixed band beyond the earlier D<=3h automatic window; the window is not assumed to cover this band.','historical',GH+'php_codex_handoff/manuscript/chapters/06_moments.md#thm-window')
add(329,'lem:duality','depends_on','Finite-dimensional kernel-annihilation/separation characterizes feasibility of the displayed pair functional equations.','historical',GH+'php_codex_handoff/manuscript/chapters/01_foundations.md#lem-duality')
notes.update({320:'Uses multiscale geometry, stable row quotient and prior exact core ceiling; dimension inequality is only a sufficient test and actual common kernel remains open here.',321:'Exact arithmetic audit instantiates existence and criterion inequalities, with an explicitly failed sufficient-range control; no affine matrices or refutations constructed.',322:'Direct invertible affine-coordinate and squarefree-monomial argument gives complete common kernel; explicit pairwise-dependent example isolates full-joint-independence necessity.',323:'Full-stack probabilistic construction refines dyadic pair-rank inventory; constants shift harmlessly and no essential proof occurrence is claimed.',324:'Combines exact kernel and full-stack residual construction; certificate/row-cleanup extension retains the distinction from full quadratic PHP membership.',325:'Exact Boolean-space kernels and union-budget fixtures test specified constructions; no PHP refutation search and no inference beyond finite parameters.',326:'Read full weighted companion/field/cofactor ledger: relative-base learning refines prior Boolean method, with separate c and s; target-annihilator theorem is contrast, not prerequisite.',327:'The conditional relative interface combines full-base learning and stable filtration; rank alone does not establish a nonzero class.',328:'Read exact finite NS quotient/intersection role and successful clause-span control; affordable-level obstruction uses the actual learning ledger and does not imply a degree-four refutation.',329:'Specializes the historical sufficient mixed system by original cofactor support, then applies linear separation to pair unknowns; this is not a characterization of every joint design.'})
for s,t,k,n in [
(330,329,'depends_on','The first-band mixed equations and pair-duality kernel criterion assemble singleton/pair extensions.'),
(330,314,'applies','Functional-PHP corollary uses stable filtration and normalized old designs; general transfer only assumes old PC-annihilating functionals.'),
(331,330,'refines','Restricts separation to complete-diagonal cofactor support edges of a supplied certificate, rather than all pairs.'),
(331,329,'depends_on','Extracted certificate identities have exactly the displayed pair-duality form and original band budgets.'),
(332,330,'applies','Verified finite pair-space separation gives the stated NS exclusions, not augmented PC exclusions.'),
(332,328,'depends_on','Reuses the exact eleven-hole affine input fixture and quotient evidence.'),
(332,'lem:mp-identities','cites','Actual MP-A source tuples are nested, explaining a limitation of full pair separation; not a premise for the finite exclusion.'),
(333,329,'depends_on','Classifies the specified polynomial-array kernel from pair duality under the faithful old-quotient hypothesis.'),
(334,330,'depends_on','The supported singleton/root construction supplies one feasible scalar prescription before equal-span coordination.'),
(335,333,'depends_on','Faithful-pair kernel classification reduces distinct spans to zero and equal spans to one scalar compatibility.'),
(335,334,'depends_on','Coordinated equal-span scalar choices cancel the only remaining pair-dual obstruction.'),
(335,329,'depends_on','Pair feasibility and the mixed-system equations yield the joint extension.'),
(335,330,'depends_on','Reuses supported roots and extension assembly; optional separated edges work for arbitrary singleton choices.'),
(335,331,'applies','Certificate-specific version needs only its actual complete-diagonal support edges.'),
(335,314,'applies','Functional-PHP exclusion and degree-two faithfulness test use the stable base filtration.'),
(336,331,'depends_on','Uses actual extracted cofactor arrays and support cancellation in the supplied NS certificate.'),
(336,333,'depends_on','Affine-reduced arrays satisfy the faithful pair kernel classification.'),
(336,334,'depends_on','Same-span coordination generalizes to the displayed larger singleton domains.'),
(336,330,'depends_on','Supported root construction and the alternative separated-pair square argument remain valid throughout the first band.'),
(336,335,'refines','Extends the faithful first-boundary transfer to specified certificates with affine-reduced arrays; no full-design extension for u>1 asserted.'),
(337,328,'depends_on','Reuses exact ambient rank certificates from the eleven-hole fixture.'),
(337,335,'applies','Faithful pair theorem supplies the degree-four NS exclusion despite every product pair overlapping.'),
(337,314,'depends_on','Stable quotient inclusion identifies lower-degree common relative classes and admissible old budget.'),
(337,326,'obstructs','All affordable common-relative-class premises fail for this finite translated family, while the pair-moment method succeeds.'),
(338,333,'applies','Exact pair kernels test distinct/equal spans, redundant representations and the failed-faithfulness control.'),
(338,334,'applies','Matched/mismatched scalar controls test the need for equal-span singleton coordination.'),
(338,335,'applies','Matched explicit joint moments test the supported mixed extension in finite Boolean controls.'),
(339,314,'depends_on','Stable degree-two affine consequences exclude residual affine relations once the rectangle kernel is zero.'),
]:add(s,t,k,n)
add(330,'lem:pcbased','depends_on','Specializes the historical PC-based supported singleton construction with the exact L+1 and D domain ceilings.','historical',GH+'php_codex_handoff/manuscript/chapters/07_elimination.md#lem-pcbased')
notes.update({330:'Read omitted supported singleton, square and assembly arguments; uses historical PC-supported construction plus first-band pair duality, with functional stability only for the PHP consequence.',331:'Certificate coefficient extraction yields actual kernel relations and supports edge-specific separation; original NS cofactor budgets are essential.',332:'Finite evidence reuses exact old fixture and applies separation theorem; nested MP and u>=2 overlaps are scope controls, not augmented PC counterexamples.',333:'Direct affine hyperplane argument classifies the already-defined pair kernel under injectivity; redundant generator coefficient directions are not polynomial-array directions.',334:'Read enlarged root-coupling map: tuple-independent feasibility gives one scalar per equal span, using original supported construction and finite separation.',335:'Combines kernel classification, scalar coordination and mixed assembly; optional separated edges/certificate-specific support and functional-PHP application retain their scopes.',336:'Read full array-reduction cancellation: certificate-specific extension uses affine representatives, supported roots and coordinated scalars; actual affine-reduction source obligation remains explicit.',337:'Inherited ambient certificates plus faithful-pair theorem give finite NS exclusion; failure of shared-class premises is computed separately and aggregate-input necessary test is not claimed sufficient.',338:'Exact pair-kernel/moment controls distinguish coefficient redundancy, harmful uncoordinated choices and harmless failed faithfulness; does not solve every large pair system independently.',339:'Direct matching-coefficient rectangle equations plus old affine stability give a sufficient injection test; nonzero Hessian kernels are not automatically old relations.'})
for s,t,k,n in [
(340,339,'depends_on','Rectangle equations localize the alternating relation Hessian into deleted-row/two-column coefficient directions.'),
(341,340,'depends_on','Strong deletion rank forces at most one independent localized direction after adding an independent affine antecedent.'),
(341,335,'applies','Only the stated faithful-pair application uses the transfer theorem; its proposed original theorem-boundary use is withdrawn by the later scope audit.'),
(341,350,'cites','Later source audit retains the algebraic theorem but identifies the suggested original level-one theorem-boundary application as vacuous.'),
(342,339,'applies','Exact rectangle kernels test the sufficient quadratic injection condition, including a matching-cell control.'),
(342,340,'applies','Deletion/localized-direction certificates distinguish sufficient conditions from actual old relations.'),
(342,341,'applies','Strong deletion certificates verify the conditional algebraic antecedent theorem on the finite coefficient fixture, not an essential Frege source occurrence.'),
(343,'thm:stable-ideal-ENS-input-replacement','cites','Contrasts a special affine row-replacement bridge with stable-ideal replacement; arbitrary full-PHP membership is not assumed.'),
(344,343,'depends_on','Affine row representatives replace inputs using original-degree telescoping certificates before restriction.'),
(344,335,'depends_on','Residual faithful-pair transfer excludes the first-boundary augmented NS refutation.'),
(344,314,'depends_on','Stable residual filtration upgrades quadratic faithfulness to the required bounded old quotient.'),
(344,278,'applies','The weak-base corollary uses explicit functional strengthening and matching restriction.'),
(344,339,'applies','Rectangle test may certify residual core faithfulness; the theorem still requires an actual common support cover.'),
(344,340,'applies','Localized directions help recognize candidate removable supports but do not imply a small common cover.'),
(345,344,'applies','Covering matching plus faithful residual core excludes the explicit 192-block family at degree four.'),
(345,342,'depends_on','Inherited dense-core coefficient certificates supply the original fixture before residual checks.'),
(345,'thm:affine-column-state-normalizer','depends_on','Degree-complete column division identifies common Boolean vanishing functions as old consequences in the scope-control argument.'),
(346,'lem:mp-telescoping','depends_on','Uses existing source prefix formulas before exact complete-diagonal extraction.'),
(346,'lem:mp-identities','depends_on','The actual MP-A correction and antecedent term supply the paired coefficient identity.'),
(346,331,'applies','The extracted arrays use the prior complete-support coefficient convention.'),
(346,336,'cites','Explains why a local correction alone is not the completed certificate required by the affine-array corollary.'),
(346,'thm:mp-boundary','cites','Consistent with the existing requirement of both premise proofs; no correction of that theorem.'),
(346,350,'cites','Later audit distinguishes these formal nonzero-antecedent controls from original assumption-free theorem boundaries.'),
(347,346,'depends_on','Exact prefix/product degrees and diagonal extraction give the displayed antecedent and three-block contribution ledgers.'),
(347,'lem:mp-composition','depends_on','The completed NS coefficient recurrence inserts the antecedent cofactor multiplier before global collection.'),
(348,346,'applies','Finite ordinary-polynomial fixtures check exact mixed coefficients and omitted-antecedent controls.'),
(348,347,'applies','Saved premise/triple-support terms test the supplied construction degree ledger, not minimum NS degree.'),
(349,'lem:theorem-approximation-simulation','applies','The audited direct theorem convention gives exact affine binary level-zero polynomials; source scope is assumption-free original structural level.'),
]:add(s,t,k,n)
add(346,'lem:coefficient','depends_on','Historical complete-diagonal coefficient operators specify extraction with all other fresh variables zero.','historical',GH+'php_codex_handoff/manuscript/chapters/06_moments.md#lem-coefficient')
notes.update({340:'Rectangle Hessian proof localizes only quadratic directions; small localized span is sufficient and nonzero localized directions are not automatically relations.',341:'Reviewed algebraic deletion-rank proof and later dated source correction: algebra remains valid, but original theorem-boundary antecedent is zero, so that proposed application is vacuous.',342:'Exact inherited coefficient/deletion/rectangle evidence applies algebraic criteria; no full old quotient, joint design or essential source proof was computed.',343:'Self-contained telescoping row-replacement certificate with original cofactor degrees; stable-ideal result is scope contrast, not a general full-base reduction assumption.',344:'Combines row replacement, one actual covering restriction, residual faithfulness and first-boundary transfer; recognition criteria do not supply the missing shared-support hypothesis.',345:'Explicit family uses inherited dense-core evidence and verified covering/wrong-column images; column division explains Boolean common-class failure, not all full-base relative membership.',346:'Historical coefficient operators applied to existing prefix/MP identity; antecedent term supplies the missing pair coefficient. Later source audit retained and formal-input scope kept.',347:'Exact ordinary-degree ledger for a supplied antecedent certificate and possible triple support; global cancellation or better certificates are not ruled out.',348:'Finite exact ordinary-polynomial extraction and ledger tests instantiate prior propositions; next-step path query is navigation rather than prerequisite.',349:'Binary no-OR exactness and a direct affine functional separation prove zero/unit-span cleanup; restricted to original-level assumption-free theorem/constant-formula occurrences.'})
for s,t,k,n in [
(350,349,'depends_on','Original-level theorem affine exactness and scalar boundary cleanup show the antecedent is zero.'),
(350,341,'corrects','Withdraws only the suggested nonzero-independent-antecedent application to original level-one theorem boundaries; the conditional algebraic faithfulness theorem remains valid.'),
(350,346,'corrects','Formal nonzero affine MP controls are not essential original theorem-boundary instances; exact polynomial extraction identities remain valid.'),
(350,'cor:php-nonboundary-pc-transfer','cites','Earlier nonboundary reduction is consistent context, not silently imported as an NS conversion.'),
(350,'thm:source-highest-or-level-unused','cites','Highest-OR support theorem has its own constructed PC/signed endpoint scope, retained separately.'),
(351,'lem:block-copy-agreement','applies','Existing prefix/block-agreement expansion proves the equal-affine-span proper comparison example.'),
(351,'prop:line-scoped-simulation','cites','Independent proper copies require comparison certificates; their actual sharing must not be inferred from boundary freshness.'),
(351,309,'cites','Path-product expression does not determine proper-copy sharing or surviving comparison contributions.'),
(352,'cor:binary-full-affine-span-packing','depends_on','Binary domain-only Booleanity and affine rank packing give the explicit chosen cleanup passes.'),
(352,'cor:merge-first-affine-normal-form','depends_on','Affine quotient/shared-span image certificates justify canonical equal-flat coefficients and zero comparison targets.'),
(352,303,'applies','Compact Frobenius witness construction gives domain-only source circuits within the structural majorants.'),
(353,309,'depends_on','Uses the already-proved proper OR-union certificate before collecting companion cofactors.'),
(353,346,'depends_on','Exact complete-diagonal prefix extraction identifies the two-foreign-block coefficient.'),
(354,353,'depends_on','The ordinary OR-union certificate gives the degree-six upper bound; lower separation is the saved exact degree-five NS calculation.'),
(355,353,'applies','Exact source support equations test collected coefficients above the packing threshold.'),
(355,354,'applies','The recorded complete degree-five elimination/separator certifies the computer-assisted target-degree conclusion; h=2 retains only its upper bound.'),
(355,352,'applies','Domain-only Booleanity certificates test the chosen source-interface cleanup.'),
(356,'note:nested-projection-syntax','depends_on','Double-negation syntax barriers prevent OR flattening while preserving child values.'),
(356,352,'depends_on','Domain-only binary certificates justify packing the upper two-input block at its original degree.'),
(356,353,'depends_on','Local proper OR-union certificates provide the source-compatible degree6h comparison modules.'),
(357,356,'depends_on','The explicit grid specifies independent child signals and fresh union scopes for coefficient collection.'),
(357,353,'depends_on','Summed local union certificates and exact prefix extraction give genuine collected two-foreign-block supports.'),
(358,356,'depends_on','The source-compatible grid supplies the proper comparison registry whose graph is analyzed.'),
(358,357,'depends_on','Collected cofactor supports certify the displayed child/union incidence edges.'),
(358,'lem:proof-line-core-chains','cites','Boundary-chain height statement concerns different vertices and is not contradicted by the proper comparison graph.'),
(359,356,'depends_on','Independent signal coordinates and the fixed grid target permit the explicit omitted-block Boolean countermodels.'),
]:add(s,t,k,n)
add(356,'BIKPRS-1996-simulation','applies','Audited balancing gives logarithmic proof height with constant formula-depth overhead for the explicitly constructed bounded-depth theorem proofs.','external',GH+'research/notes/SOURCE_AUDIT.md#bikprs-actual-simulation-structure')
notes.update({350:'Source correction follows binary theorem cleanup; only suggested original MP boundary applications are withdrawn, not conditional algebra or finite checks. Earlier PC/signed reductions remain scoped citations.',351:'Exact proper affine-subspace semantics and an existing block-agreement example clarify retained objects; neither theorem-boundary removal nor private freshness proves essential support.',352:'Reuses binary domain division, affine quotient sharing and rank packing with original NS image certificates; only selected modules disappear, not arbitrary comparison/value companions.',353:'Actual collected OR-union companion coefficients use existing identity and prefix extraction; full polynomial cancellation and lack of universal essential-support claim retained.',354:'Explicit degree-six identity plus saved full degree-five NS separation and degree-preserving affine restriction establish only Boolean-base h=1 target claim; no PHP-base inference.',355:'Complete finite polynomial and elimination evidence applies the source-interface identities; h=2 lacks matching lower-bound claim and no high-dimensional historical suite replay occurred.',356:'Audited syntax barriers, binary domain packing and local union modules give a source-compatible grid; theorem proof balancing is imported, but no unique source compiler certificate is asserted.',357:'Collects the actual grid certificate and isolates coefficients via fresh union scopes; alternative certificates may have different support.',358:'Elementary separator/hitting-set proof applies to the genuine displayed proper registry; proof-line boundary-chain theorem remains valid for different vertices.',359:'Explicit models after removing each possible block refute derivability of the fixed coefficient-dependent target; target-changing preprocessing, extra axioms and PHP target one remain outside scope.'})
for identifier,anchor,note in [('thm:one-elimination','07_elimination.md#thm-one-elimination','Audits the generic degree sum and mutually conditional one-block learning, rather than asserting simultaneous elimination.'),('thm:nested','08_batching.md#thm-nested','Identifies nesting as an actual well-founded simultaneous-learning hypothesis, absent from arbitrary source-family size.'),('thm:cores','08_batching.md#thm-cores','Lists the established core-residual method and its missing source coverage.')]:
 add(277,identifier,'cites',note,'historical',GH+'php_codex_handoff/manuscript/chapters/'+anchor)
add(277,'obs:pebbling-antichain-probes','applies','The failed batching attempt reuses the Boolean-grid degree control to refute automatic cross-block scalar image certificates; it is not an augmented refutation.')
for edge in rows:
 if edge['source']['id']==C[277]['id']:
  edge['evidence'] += [WEB+'batching-attempt-dependency',WEB+'batching-attempt-composition',WEB+'batching-attempt-cross-block-control']
notes[277]='Completed the multi-entry route audit: source endpoint, historical one-block/nested/core methods and triangular replay are scoped citations; failed simultaneous scalar replay applies the earlier Boolean-grid control. The bridge itself remains open; reviewed metadata does not resolve it.'
LO,HI=map(int,sys.argv[1:3]) if len(sys.argv)>2 else (260,270)
E=Evidence();reviews=[]
for i,note in sorted(notes.items()):
 if not LO<=i<HI:continue
 c=C[i];targets=re.findall(r'\]\((https://[^)]+)\)',c['record'])
 targets=[t.replace('#design-free-column-search','#pseudo-live-cell-interface') for t in targets]
 if i==277:targets += [WEB+'batching-attempt-dependency',WEB+'batching-attempt-composition',WEB+'batching-attempt-cross-block-control']
 reviews.append({'id':c['id'],'claim_sha256':claim_digest(c),'state':'reviewed','note':note,'next_action':None,'evidence':[{'target':t,'sha256':E.sha256(t)} for t in dict.fromkeys(targets)]})
ids={c['id'] for c in C[LO:HI]};rows=[e for e in rows if e['source']['id'] in ids]
out={'source_revision':REV,'range':[LO,HI],'reviews':reviews,'relationships':rows,'decisions':[], 'scope':'Source-relative direct dependency inventory; no new mathematical proof or external literature audit.'}
(Path(__file__).parent/f'patch-{LO}-{HI}.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
print('reviews',len(reviews),'edges',len(rows))
