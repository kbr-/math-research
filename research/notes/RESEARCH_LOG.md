# Continuing research log

This file is for new local work. The preceding investigation is preserved in the manuscript, not reconstructed as fictional dated sessions here.

## Entry template

### Date/session — proposed statement

**Question:** the exact theorem or counterexample being attempted.

**Status:** conjecture / working proof / conditional working proof / finite check / refuted / superseded.

**Objects and quantifiers:** base system, field, degrees, block/level count, dependence on proof size.

**Dependencies:** stable labels in the manuscript and exact external source locations.

**Argument:** self-contained proof or identified failed inference. Distinguish source-derived material from the new inference.

**Degree accounting:** include every substitution, weighting, field reduction, and proof-reuse ceiling. Explain why active cofactor conditions are genuinely tested.

**Checks:** actual command, seed/parameters, outputs, negative controls, failures/retries, and whether the base is PHP or another domain.

**Effect on the goal:** what is newly covered and the precise remaining obligation. Do not claim a special-case success proves global coverage.

**Timing:** total instrumented elapsed, reading windows, computation, external tools, failures, and limitations.

<a id="local-zero-cofactor-pruning"></a>

### 2026-09-10 / import_20260910_01 — focused audit and zero-cofactor pruning

**Question.** After importing the manuscript, what refutation-dependent reduction
is already justified, without assuming the missing global compression theorem?

**Status.** Focused proof audit; elementary working pruning lemma
`local:zero-cofactor-pruning`. This is a local clarification of the unused-block
observation in Theorem 8.1, not a novelty claim or the missing affordable theorem.
No old claim is superseded.

**Objects and quantifiers.** Fix any prime p, any Boolean/field old base F, and
any finite leveled ENS system with fresh coefficient-variable groups R_a, all
companions E_{a,i}, and all required extension field equations. Fix an actual
ordinary-polynomial NS certificate

\[
1=\sum_{f\in F}q_f f+\sum_{a,i}q_{a,i}E_{a,i}
  +\sum_{r}s_r(r^p-r),
\qquad \deg(q_FF)\le D
\]

for every nonzero summand. Cofactors are collected within each axiom's
coefficient; their possible sharing of extension variables is unrestricted.

**Lemma.** If every companion coefficient q_{a,i} of a block a is zero, its
fresh variables may all be set to zero throughout the certificate. The resulting
identity has degree at most D, uses no axioms of a, and has the same ENS form on
the surviving blocks after updating their inputs by the same substitution.
Zero input coordinates and blocks can be cleaned up by further constant
substitutions. Iterating zero-cofactor deletion and this cleanup terminates.
Consequently, a block with zero companion coefficients need not be retained
merely because its variables occur in other cofactors or in later inputs.

**Proof.** Let sigma fix the original variables and all surviving fresh variables,
and send R_a to zero. Apply this ring homomorphism to the entire identity.
The left side remains one, the base axioms are fixed, and each removed field
axiom becomes zero. There were no nonzero companion summands for a. For a
surviving block b, its fresh variables are fixed and its companion becomes

\[
\sigma(E_{b,i})=\sigma(g_{b,i})
 \prod_{u=1}^{h_b}\left(1-\sum_j r_{b,u,j}\sigma(g_{b,j})\right).
\]

No surviving input acquires a dependence on a later level, and no fresh
coefficient variable enters an input of its own block. Each surviving field
axiom remains r^p-r. This establishes the identity and structural claim.

There is one syntax detail: if a surviving input becomes identically zero, its
coefficient variables may disappear from that block's polynomial companions
while still occurring in later inputs or cofactors. Set these now-unneeded
coefficient variables to zero everywhere as well. Drop identically zero
companions, remove all-zero blocks, recompute the identity, and repeat. This
preserves the strict convention that surviving new variables are introduced in
an earlier nonzero block, rather than silently treating unintroduced field
variables as original Boolean variables. Each cleanup removes variables or
blocks, so the process is finite. Complete the companion list of every retained
nonzero tuple with zero coefficients where needed.

Constant substitution is degree-nonincreasing on every entire original
summand. Therefore every nonzero image summand still has degree at most D.
This proves the lemma. In particular, we have constructed a new certificate;
we have not enlarged the original certificate's permissible cofactor space.

**Degree accounting and a candidate quantity.** Let pi' be the resulting pruned
certificate, with surviving maximum input degrees delta'_a. Converting pi' to
PC and applying `thm:additive` gives the certified bound

\[
B_{\rm support}(\pi)=D+(p-1)\sum_{a\in A(\pi')}\delta'_a.
\]

This quantity depends on the actual certificate and its specialization, not
just on the originally supplied collection of extension spaces. Where
nested/core-residual hypotheses hold, replace the sum by the corresponding
certified batch compositions. For one affine level, the exact subset recurrence
of `lem:subsetdp` can be applied to the pruned family. These are sufficient
bounds only; the recurrence need not be computationally affordable and no
uniform upper bound in D,h,log M is established.

**Method controls (symbolic, not newly executed suites).**

- Append any number of spread blocks that carry zero companion cofactors in a
  certificate. Pruning removes them without a degree charge. Their appearance
  solely in other cofactors is harmless under the substitution argument.
- The prefix-pebbling certificate contains genuinely used blocks and long
  adjacent-block propagation. The lemma does not declare that propagation cheap
  merely from sparse support. Its prefix spans are nested, so the existing
  `thm:nested` yields D+(p-1) (input degree one). Its base also has PC degree at
  most three. This is consistent with the ordinary-design counterexample and
  does not transfer that counterexample to high-PC-degree PHP bases.
- The static spread family without a certificate remains data only. If many
  such blocks survive with essential nonzero coefficients, the present pruning
  lemma supplies no reason for a small charge. Proving that actual translations
  admit a cheaper representation is precisely the unresolved task.

**Focused audit.** The PC reuse/substitution and selector identities were checked
against the original TeX. The one-block, reverse-level, nested, and core/residual
proofs were reviewed for freshness, only-used-axiom degree bounds, and reuse of
previously derived final polynomials. No genuine gap was found in those reviewed
arguments. In particular the core absorption proof bounds both summands by
TD+gamma, within TD+(p-1)gamma, and does not assume the core inputs vanish merely
because a functional gives them value zero. This review is neither exhaustive
verification of the complete manuscript nor an audit of missing primary proofs.

**External dependencies and unresolved work.** Krajicek v3 confirms ENS syntax,
ordinary-design base/residual matching by deletion, and the recorded simulation
statement. The exact BIKPRS construction and Razborov PC threshold still require
the two missing PDFs. The source's formula-to-polynomial lemma includes row
functionality, so the ordinary-PHP transfer to our base remains to be formalized.
The Krajicek source's odd-prime sign typo is recorded separately in IMPORT_LOG.md;
it does not alter the explicitly listed axioms.

**Checks.** Only bundle integrity, reference acquisition/extraction, and source
inspection were performed. A09-A11 were read for scope, not rerun. No floating
point ranks, numerical experiments, or new historical-suite results are claimed.
Failures/retries are in the import timing logs.

**Effect on the goal.** Context and two external inputs are now checked at the
specified source-statement level; an elementary certificate-aware pruning step
is explicit. The uniform affordable elimination/joint-design theorem, original
simulation cofactor audit, PC source match, and ordinary-PHP proof transfer remain
open. No Frege lower bound has been obtained.

**Timing.** See logs/import_20260910_01.summary.json for the final instrumented
window, exclusive categories, and failed runs. Initial handoff discovery predates
instrumentation; reading includes interpretation and some early mixed tool work.

**Follow-up.** The user supplied the two missing references. Their targeted
source checks are complete in SOURCE_AUDIT.md, including the PC-degree convention
bridge and the original balanced simulation construction. The corresponding
pending-source statements above describe the earlier import stage. All current
work was moved into research/; the historical package was restored unchanged.


### 2026-09-10 — Research-turn reporting workflow

Administrative update: every research attempt now requires an append-only
notebook entry and a measured category/elapsed timing table, including failed
proof attempts and turns with no useful result. The report exporter provides
`--html-out`, validates totals, and requires a completed session. Eight bounded
integration checks passed. This turn did not attempt a new mathematical claim.
The live example is `notebook.html#entry-2026-09-10-reporting-workflow`; its raw
timing/evidence is archived under session `notebook_timing_tables_20260910_01`.

### 2026-09-11 / mp_composition_20260911_01 — exact local MP composition

**Status.** Working local identities and degree bounds; conditional base-PC
composition interface. The full statement, proof, degree ledger, controls, and
remaining obligation are in [the notebook](../../notebook.html), entry
`entry-2026-09-11-mp-composition`. Stable subanchors: `mp-two-cases`,
`mp-booleanity`, `mp-certificates`, and `mp-elimination-gap`.

**Evidence.** The [result record](../results/mp_composition_20260911_01/README.md)
contains reproduction commands, exact source locators, output schema, and scope.
The compiled checker `research/tools/check_mp_composition.cpp` writes complete
[checks.jsonl](../results/mp_composition_20260911_01/checks.jsonl): 36 exact
ordinary-ring identity/degree cases, 36 omitted-correction controls, and three
zero-specialization countermodels. Both checker runs passed; the second
strengthened the specialization control. These are synthetic local checks,
not PHP refutations or a mechanical verification of global elimination.

**Timing.** The notebook embeds the generated
[timing table](../results/mp_composition_20260911_01/timing.html); completed logs
are preserved in `research/provenance/session-records/mp_composition_20260911_01/`.
Policy and initial availability reads preceded instrumentation. No historical
suite was rerun and no package was installed.

### 2026-09-11 / implication_boundary_20260911_01 — one-block consequence and boundary transfer

**Status.** Working PC transformations with explicit freshness and degree
hypotheses. The complete proofs, parameter accounting, controls, and unresolved
global composition are in [the notebook](../../notebook.html), entry
`entry-2026-09-11-implication-boundary`. Stable subanchors:
`boundary-old-consequence`, `boundary-weighted-replay`,
`boundary-mp-elimination`, and `boundary-controls`.

**Evidence.** The [result record](../results/implication_boundary_20260911_01/README.md)
documents the new compiled checker and the complete
[trace output](../results/implication_boundary_20260911_01/checks-01.jsonl).
Forty transformations over p = 2, 3, 5, 7 and h = 1, 2 passed, including
24 old-consequence cases and 16 MP cases. The output preserves 96 proofs and
14,657 inference lines; all transformed traces reject a corrupted final line.
Eight additional controls exercise the annihilator and freshness hypotheses.
These are synthetic cases, not PHP computations or formal verification.
The [summary](../results/implication_boundary_20260911_01/summary.json)
preserves the full degree ledger and source/output hashes.

**Timing.** The generated
[table](../results/implication_boundary_20260911_01/timing.html) is embedded in
the notebook, with evidence archived under
`research/provenance/session-records/implication_boundary_20260911_01/`.
Goal creation preceded instrumentation. Initial source review included early
argument development; the suite ran once, after a warning-clean compilation.
No historical suite was rerun and no package was installed.

### 2026-09-11 / boundary_overlap_20260911_02 — target annihilators and matching restrictions

**Status.** Working transfer, affine-rigidity, and restriction arguments.
The complete claims, proofs, rejected nonnesting inference, and scope are in
[the notebook](../../notebook.html), entry
`entry-2026-09-11-target-annihilators`. Stable labels and proof anchors are in
[the claim index](../CLAIM_INDEX.md).

**Evidence.** The [result record](../results/boundary_overlap_20260911_02/README.md)
documents four exact ordinary-PHP C2 calculations, four subset-incidence ranks,
13 weighted coefficient identities and omission controls, and four finite spread
families with all 160 pair checks. The
[full output](../results/boundary_overlap_20260911_02/checks-03.jsonl)
preserves sparse bases, monomial maps, field moduli, graph inputs, and every
normalization result. Earlier outputs preserve an indexing failure and the
successful corrected matrix suite; these are implementation history, not
counterexamples to the mathematical statement.

**Timing.** The [table](../results/boundary_overlap_20260911_02/timing.html)
is embedded in the notebook, with the completed session archived under
`research/provenance/session-records/boundary_overlap_20260911_02/`.
The preparation phase includes the requested claim-index work. Mathematical
checks were retained; routine site builds and broad notebook audits were omitted.

### 2026-09-11 / restriction_resistant_spread_20260911_03 — small-matching avoidance

**Status.** Working counting proof and explicit finite certificate for an
obstruction to constant normalization. Full statements, parameters, and limits
are in [the notebook](../../notebook.html), entry
`entry-2026-09-11-resistant-spread`, and indexed in
[the claim index](../CLAIM_INDEX.md).

**Evidence.** The [result record](../results/restriction_resistant_spread_20260911_03/README.md)
describes the exact seeded construction. The
[certificate](../results/restriction_resistant_spread_20260911_03/certificate-01.jsonl)
preserves the invertible matrix, seven rank-24 spaces, their restricted inputs,
and 392 dual witnesses covering all 56 single-cell matchings. Compilation and
execution passed on the first attempt. The example is extension data, not a
PHP refutation, and does not exclude richer elimination methods.

**Timing.** The
[table](../results/restriction_resistant_spread_20260911_03/timing.html)
is embedded in the notebook; the completed session is archived under
`research/provenance/session-records/restriction_resistant_spread_20260911_03/`.
The next framework improvement is a small provenance helper to replace repeated
hashing and bookkeeping code.
