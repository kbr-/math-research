"""Review decisions for the assigned source-packet batch; does not edit the registry."""
import json,sys,subprocess,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'tools'))
from claim_registry import load
D=Path(__file__).parent; data=load(); packets=json.loads((D/'packets.json').read_text())
notes='''680|Cycle/filling interface for extending matching marginals, including the smallest cell counts.
681|Relabeling interface transports moments without losing the retained row set.
682|Prescribed matching moments extend in the stable range; this is not arbitrary source extension.
683|Field-uniform telescoping tool retains the empty-family case and sharp coefficient ceiling.
684|Usual-CNF initial bridge supplies actual values; full DAG replay is a separate theorem.
685|Unit-span treatment closes the tautological-block case without changing the removal ceiling.
686|Finite DAG controller requires actual initial-value derivations; the conditional premise is retained.
687|Affine coordinate completion is a reusable supporting interface, not the full kernel construction.
688|Selected-coordinate ideal membership gives literal witnesses including degree zero.
689|Ordinary affine pullbacks and restriction witnesses preserve the literal degree ceiling.
690|Exponential binomial decay supplies the quarter-budget estimate with its numerical hypotheses.
691|Coordinate-pair packing prepares the residual separator; it does not alone prove separation.
692|Cube-sum degree drop is a general polynomial interface with explicit fixed residual images.
693|Proper affine blocks admit rank-sized coordinates and original-input witnesses.
694|Common ordinary kernel construction supplies simultaneous witnesses; unit blocks remain separate.
695|Cube isolation extracts maximal-row coefficients without unnecessary outside-degree assumptions.
696|Concrete residual restriction transports functional-unary generators and decoder coordinates.
697|Eventual parameter room closes the polynomial-inventory and polylogarithmic-degree budget.
698|Boundary-only reconstruction needs all prefixes; no essential occurrence in every PHP proof follows.
699|Old-degree versus retained-boundary tradeoff constrains this reconstruction scheme only.
700|Weighted mixed-port reuse is already covered and leaves global consistency unresolved.
701|Scalar multiples of one old functional fail, while correlated extension is not excluded.
702|Nonsingular old pairings represent functionals by densities, not Boolean source values.
703|Finite GF(4) example rules out the proposed projection recipe, not PHP hardness.
704|Prescribed row masses coexist with nonsingular pairings in the stated stable range.
705|Row-local density repair reuses existing normalization and gives no multirow theorem.
706|Point-support lower bound obstructs the support-only union bound; arbitrary correlated maps remain open.
707|A genuine cofactor can have large specialization span, without proving indispensable query span.
708|Finite retained-interface preservation does not extend to a universal same-degree theorem.
709|Fresh-block loss is quantified but its cumulative cost remains too large for the target.
710|Finite exact witness refutes general same-degree preservation over a second-level base.
711|Finite losses increase across the tested ranks; no untested rank or helper family is certified.
712|Coefficient criterion is an exact reformulation, not a solution of general conservativity.
713|Rank-two conservativity is an explicit rediscovery of a recorded substitution result.
714|Level-one conservativity remains conjectural despite the recorded exact controls.
715|Placement audit locates finite losses at the existing second-level frontier.
716|Third-level inputs escape the rank-two map's hypotheses; the restricted extension is only sketched.
717|Frontier assessment retains the later correction to the high-threshold rebalancing claim.
718|Flat-restriction dimension improves the prior crude counting estimate.
719|Parameter rebalance lowers the high threshold but leaves narrow-term readers.
720|Imported q-matching switching lemma is known upstream; missing bipartite versions are not inferred.
721|A representing and refining tree gives complete old-only images with explicit degree costs.
722|Polylogarithmic image consequence is only recorded for the nonbipartite setting.
723|Bipartite switching proof supplies an explicit encoding with finite round-trip controls.
724|Bit-term decoding reduces to pairwise incompatible unary matching terms.
725|Switched-image transfer accommodates sums of incompatible terms at the recorded cost.
726|Restriction-family incompatibility motivates the compact family; later refinements narrow it.
727|Subcube encoding handles the explicit light-row window, not pinned rows in general.
728|Pinned-row construction refutes short syntactic trees on the fixed subcube.
729|Encoding limitation identifies a width window; later flat preservation is a separate result.
730|Random-flat restrictions preserve the compact base and degree accounting.
731|Light/heavy dichotomy yields the recorded size regime, not the full literal frontier.
732|Failed round trips refute the q-skip encoding; the later wide-round skip has different hypotheses.
733|Hole-query partition works without an onto axiom and supports algebraic tree images.
734|Window assessment has corrected encoding and matching scopes; its original intrinsic limit is not universal.
735|Single-target reader rules out pigeon-only trees; hole queries resolve the example.
736|Alive-pair matching reduction isolates the needed tail bound rather than proving it.
737|Dense label classes force satisfaction under the explicit degree threshold.
738|Sparse matching tail controls heavy rounds under its degree condition.
739|Affine-rank counting bounds the number of selected labels in the random flat.
740|Unary switching survives with the recorded ordering correction; mixed tails are separate.
741|Original adaptive rule is refuted; corrected hole-only and both-endpoints rules are distinct claims.
742|Matched-first preference survives with the appropriate tree-specific round count.
743|Height budget remains useful, but the original blanket switching/composition claim is not proved.
744|Alive-versus-matched comparison supplies a reusable probability estimate for pair sets.
745|Tail comparison is conditional on the explicit light width and residual parameters.
746|Expected eligibility does not supply the missing high-probability correlation argument.
747|Distinct-row full-class bound is tree-specific with recorded role and ordering corrections.
748|Bounded loading gives the stated round control; it is not a theorem about arbitrary loading.
749|Outside loading bounds satisfaction through the uniform bijection.
750|Label-set round bound retains the corrected exponential constant and tree choice.
751|Round bound survives; the indexed switching clause remains qualified by the composition gap.
752|Finite positive and negative decoder controls are evidence only for the enumerated instances.
753|Adaptive-rule counterexample explains repeated trigger holes and invalid heavy-query bounds.
754|Hole-only replacement proves trigger-hole control but fails for general sparse readers.
755|Matching satisfaction uses disjoint light rows and labels under the full-column setup.
756|Full-column round bound survives; switching requires the separately qualified composition.
757|Sparse reader refutes a universal small-height claim for the hole-only rule.
758|Both-endpoints rule recovers matching triggers with two queries per round.
759|Two-tier satisfaction extends the disjoint matching argument to dense classes.
760|Two-tier round theorem retains corrected constants and the conditional switching clause.
761|Activated sparse tail estimate is subsumed by the later union version up to constants.
762|Activation-bounded extension keeps the corrected threshold and qualified composition.
763|Two-stage exposure is a reduction to an unproved integrated count for arbitrary columns.
764|General column bound remains conjectural beyond its recorded restricted cases.
765|Activated-union bound supplies the common sparse matching mechanism.
766|Row-spread round bound retains the corrected threshold and qualified switching clause.
767|Pattern-bounded round theorem is a restricted precursor, with composition still qualified in its record.
768|Rank-step correction increases constants in specific predecessors without retracting all their bounds.
769|Multirow mass controls rounds; later current-term composition restores switching in its light range.
770|Size corollary is restricted by its exponent and the later composition's light range.
771|Few light rows allow arbitrary tail shapes within the explicit residual and composition conditions.
772|Exposed crowded-row round bound survives; the switching clause is qualified in the indexed assessment.
773|Crowded-row size corollary raises the exponent only under its tail-budget hypotheses.
774|Complete-term ordering preserves matching rounds and charges exposed-row exceptions.
775|Two-role decoder needs sparse pinning for richness, despite successful finite controls.
776|Few-row two-role switching retains sparse pinning and the later composition hypotheses.
777|Exposed two-role theorem controls the specified light mass, not arbitrary two-role readers.
778|Two-role size corollaries inherit sparse pinning and the current composition's domain conditions.
779|Historical composition gap is real; later repairs discharge it only in their specified scopes.
780|Pinned-term dichotomy covers total size below the threshold, not all per-reader claims.
781|Pair-space restriction connects the slack and compact distributions with a quantitative factor.
782|Decoder and count require the stated sparse-pinning richness, with bounded finite controls.
783|Slack round bound remains valid but is unnecessary for the later compact composition.
784|Sparse-pinning composition is a superseded valid special route, not a retraction.
785|Dense-pinning obstacle belongs to the old decoder; current-term composition resolves it.
786|Compact decoder avoids the slack transfer but initially retains its own-row rule.
787|Own-row richness is a valid sufficient condition made unnecessary by a later decoder.
788|Compact composition repairs the probability-space gap under its original column-sparse hypotheses.
789|Dense-cube obstacle concerns the old own-row code and is resolved by current-term decoding.
790|Two-role compact composition retains sparse pinning; later work removes column sparseness.
791|Current-term decoder removes the dense-label ambiguity, with explicit negative controls.
792|Current-term composition unifies recorded round bounds within its explicit light and pinning conditions.
793|Wide-move composition remains conditional on a bound known to fail for its tree.
794|Shared cube defeats the complete-term tree, not switching by an appropriate hole-query tree.
795|Wide-row annihilation justifies the static skip under the stated algebraic leaf conditions.
796|Root-fixed minimum cover bounds wide queries and avoids the failed adaptive choice.
797|Wide matching tail uses explicit incidence mass and affine-rank bounds.
798|Round transfer covers named proofs, with exposed-row cases supplied only later.
799|Wide-round composition is a proved implication conditional on both quantitative tree bounds.
800|Pin-free split rows switch under the mass and size conditions; arbitrary mixtures are not covered.
801|Role-separated split-row switching reaches the recorded subquadratic regime only.
802|Reordered wide tree preserves prior claims and enables the exposure argument.
803|Exposed-row facts depend on the corrected wide-first node order.
804|Named round bounds transfer to the reordered tree; some clauses add no wider scope.
805|Few wide rows give a simple matching bound independent of pattern width.
806|Few total tail rows permit every width but retain pinning and light-range conditions.
807|Few wide rows improve the size exponent at the cost of the row-count restriction.
808|Counting distinct rows instead of incidences sharpens the wide mass estimate.
809|Pin-free single-row readers switch at every size and width; multirow terms remain separate.
810|Encoding an independent cover changes the count; this variant was not implemented in the checker.
811|Pinned wide-mass route still needs concentration and does not solve the literal conjecture.
812|General literal switching is parked and conjectural; dense forms need a compatible separate mechanism.
813|Dense-form question is answered for generic cases only; structured gaps remain.
814|Generic dense forms remain generic under fixed compact restrictions, limiting restriction gains.
815|Restricted rank gives complete images at a cost proportional to that rank.
816|Random low-rank terms admit a covering certificate above the explicit span threshold.
817|Balanced rank defeats the generic covering hypothesis without refuting all PHP-relative approaches.
818|Small-board closure checks see no dense-image gain and retain a positive control.
819|Substitution bound is a restatement with a PC formulation, not a new general conservativity theorem.
820|Augmented-base finite checks have one degree of slack and do not test the second-level losses.
821|Dimension count rules out plain dense elimination in the target finite regime, not all structured methods.
822|Imported extension-variable literature has unnested/arity restrictions and does not cover the source.
823|Proposed collapse returns to the recorded frontier; no new general induction is obtained.
824|Case-split reformulation has additive per-term loss and is explicitly a recorded tool.
825|Pure-source reduction is proved but the required generic value-hardness question remains open.
826|Low-degree tipping counts are finite evidence and do not test the needed asymptotic hardness.
827|Image-or-value claim remains open for compiled sources; the arbitrary-source obstruction is only a candidate.
828|Twisted-source reduction has settled structured cases and an open generic row-mixing case.
829|Safe linear constraints preserve hardness only in the recorded rank range.
830|Generic-subspace degree lower bound is conjectural and not decided by the three data points.
831|Imported linear-constraint literature supplies context only; proofs and transfers were not newly checked.
832|Residual-coordinate elimination identifies the exact collision-flat degree problem.
833|Residual closure checks do not test H1 in a nontrivial regime and remain finite evidence.
834|Pointwise weights and product designs fail at linear codimension; other design forms remain open.
835|Parity-tree depth bounds bit degree for collision-flat axioms under the stated convention.
836|Compact-base bit degree is bounded on the order of n using the recorded parity-tree argument.
837|Generic-subspace incompatibility blocks combining two specific value choices, not Claim G itself.
838|Route review identifies the subspace wall and does not establish a new general hardness result.
839|Generic-subspace row-width lower bound controls bounded-width queries, not unrestricted parities.
840|Density delayer reduces a tree bound to concentration in a collision flat.
841|Finite spectra and two closed forms leave the general spectral maximum and transfer open.
842|Sequential boost bound is tight on its examples but gives no unrestricted parity-depth progress.
843|Parity-tree line is parked; labelled heuristic ceilings remain heuristic.
844|Constant-row clamp reduces exclusion to old-base avoidance hardness without substitution cost.
845|Few-block conservativity pays additively in block count and stops before the general inventory range.
846|Hitting-set count narrows the earlier exactly-if claim and preserves the linear-codimension wall.
847|General-step review isolates HW as an open obligation, with no finite evidence in its required regime.
848|No-fall criterion turns exact filtration stability into PC hardness; the stability premise is unresolved generally.
849|Top-degree dimension count forces falls without proving generic saturation before that point.
850|Finite NS rank data support a pattern but do not prove semiregularity or HW.
851|Relative semiregularity is conjectural, stronger than HW, and lacks a general proof method.
852|Codimension must be measured modulo row relations; satisfying values alone do not imply hardness.
853|Two-form criterion excludes degree-two falls under a sufficient, not necessary, condition.
854|Alternating-form counts support the degree-two first moment; higher relative rank counts are separate.
855|Uniform parity theorem is asymptotic and degree two only, not a general HW theorem.
856|Decoded-label parity theorem is unary degree two and does not bound the needed bit degree.
857|Finite tests check T2 and small counts, not the asymptotic U and Lb theorems.
858|HW is parked because the higher-degree relative rank count is missing.
859|General subspace-consequence transfer is verified but is not a general PC refutation degree bound.
861|Generic CNF initial bridge supplies the encoded-clause value with its exact budget.
862|Generic affine-DAG criterion is sufficient; only bit PHP is shown to meet the separation hypothesis.
863|Density exponential form is a finite parameter inequality, not an independent asymptotic lower bound.
864|Short-proof consistency control verifies the easiest contradiction, not all known short Res(parity) proofs.
865|Preprint revision is editorial and reuses existing mathematical and kernel evidence.
'''
notes={int(line.split('|',1)[0]):line.split('|',1)[1] for line in notes.strip().splitlines()}
# Explicit reviewed classification exceptions; default working_proof means the recorded argument,
# not an independent replay or an assertion of novelty.
established=set(range(680,698))|{720,859,861,862,863,864}
conditional={686,743,751,756,760,762,766,767,772,793,799,825}
context={700,705,715,716,717,726,729,734,736,811,821,822,823,831,838,843,847,858,865}
conjecture={714,764,812,813,827,830,851}
finite={703,708,711,752,818,820,826,833,841,850,857}
refutation={710,728,732,735,741,753,757}
negative={698,699,701,703,707,710,711,716,726,728,729,732,734,735,741,743,753,757,768,779,785,789,794,811,817,821,823,834,837,846,852}
general={681,683,685,687,688,689,690,692,693,695,697,702,704,706,709,712,713,718,721,724,725,733,744,745,749,781,782,786,791,814,815,816,819,824,832,835,840,842,844,848,849,853,854,859,861,862,863,864}
known={720,713,819,824,822,831}
patch=[]
for i,c in enumerate(data['claims'][680:],680):
 if i==860:continue
 p=packets[i-680]; status='working_proof'
 for val,group in [('established',established),('conditional',conditional),('context',context),('conjecture',conjecture),('finite_check',finite),('refutation',refutation)]:
  if i in group:status=val
 if i<683:topics=['matching-php','moment-designs','topological-methods']
 elif i<698:topics=['affine-linear-algebra','degree-accounting','polynomial-calculus']
 elif i<720:topics=['ens','degree-accounting','moment-designs' if i in {701,702,703,704,705,706} else 'substitution']
 elif i<813:topics=['query-models','matching-php','ens']
 elif i<832:topics=['affine-linear-algebra','polynomial-calculus','bit-php']
 elif i<844:topics=['bit-php','affine-linear-algebra','query-models']
 elif i<859:topics=['matching-php','polynomial-calculus','affine-linear-algebra']
 else:topics=['resolution-parities','polynomial-calculus','affine-linear-algebra']
 if i in negative:topics.append('method-obstructions')
 if i in finite:topics.append('finite-certificates')
 if i in {859,861,862,863,864}:topics.append('degree-accounting')
 if i==865:topics=['publication','bit-php','resolution-parities']
 category='negative_result' if i in negative else 'general_tool' if i in general else 'context' if i in context or i==720 else 'route_specific'
 evidence=list(dict.fromkeys(passage['target'] for passage in p['passages']))
 assert evidence,(i,c['id'])
 sig={'category':category,'rationale':notes[i], 'novelty':'known' if i in known else 'not_claimed','publication_status':'not_applicable','references':evidence,'next_action':None}
 if i==865:sig['publication_status']='preprint'
 vals={'mathematical_status':status,'topics':topics,'significance':sig}
 reviews={k:{'state':'reviewed','evidence_targets':evidence,'note':('Recorded status and scope: ' if k=='mathematical_status' else 'Topic classification follows the object and method: ' if k=='topics' else 'Significance is methodological, not a fresh novelty audit: ')+notes[i],'next_action':None} for k in vals}
 patch.append({'id':c['id'],'position':i,'baseline_claim_sha256':hashlib.sha256(json.dumps({k:c[k] for k in ('id','summary','assessment','record')},sort_keys=True,ensure_ascii=False).encode()).hexdigest(),'fields':vals,'reviews':reviews})
result={'schema_version':1,'baseline_revision':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'assigned_range':[680,len(data['claims'])],'scope':'Metadata orientation using exact existing assessments and bounded source evidence; no new mathematical proof, Lean replay or novelty search. Original text and formalization untouched.','preserved':['cor:bit-PHP-exponential-parameter-bound'],'proposed_topic_definitions':[],'claims':patch}
(D/'patch.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print('Prepared',len(patch),'claim patches; original publication seed preserved.')
