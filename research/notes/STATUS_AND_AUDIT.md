# Status and proof-audit ledger

**Historical import summary and dated audit evidence, not a live status page.**
The initial sections of [notebook.html](../../notebook.html) hold authoritative
current status and later corrections. Preserve the dated findings below; append
new supporting audit evidence only when needed, without synchronizing summaries.

**Snapshot:** 10 September 2026. **No payoff theorem is established.** This ledger summarizes the status recorded by the manuscript; it does not add a new mathematical correction.

## Imported working theorem stack (snapshot)

| Stack | Stable source labels | Status and limits |
|---|---|---|
| Field reductions, selectors, PC reuse/substitution | `lem:fieldreduction`, `lem:selectors`, `lem:reuse`, `lem:substitution` | Working preliminary proofs. Audit first because many results depend on them. |
| Corrected Koszul and generic witness | `cor:koszul`, `lem:hilbert`, `thm:generic` | Working non-Boolean results in the explicitly bounded range; not a Boolean ENS theorem. |
| General block elimination | `thm:one-elimination`, `thm:additive` | Working additive PC elimination. Does not preserve an arbitrary base functional and need not preserve proof length. |
| Nested and core/residual batches | `thm:nested`, `lem:nestedquotient`, `thm:cores`, `lem:corequotient` | Working proofs with precise span, degree, freshness, and supplied-consequence hypotheses. |
| Static affine optimization | `lem:ordering`, `lem:batchcost`, `lem:subsetdp` | Optimizes one specified sufficient bound; not all algorithms or proof transformations. |
| Spread obstruction | `lem:spread`, `thm:spreadcost` | Admissible data with unaffordable optimum in that criterion; no augmented PHP refutation is supplied. |
| Affine rigidity | `thm:rigidity` | Conditional on exact imported base/residual degree lower bounds. Not numerically checked by A11. |
| Final inference | `thm:conditionalpayoff` | Conditional theorem with three explicit missing/matching hypotheses. |

## Audit obligations before building on the main stack

1. **Encoding:** list the exact axioms in Razborov and Krajíček and compare to `eq:base`, including Booleanity and row exclusion. Track residual boards under partial matchings. Do not infer the match from the name “PHP.”
2. **Freshness:** reverse-level elimination must leave the removed block's fresh variables absent from every remaining axiom. Same-level blocks share only old variables, not fresh ones.
3. **Active axioms:** use original joint-variable degrees even after specialization; discarded/inactive companions cannot silently become new low-degree axioms. Check constant/zero inputs separately.
4. **Selector multiplication:** verify every transformed source line and every mapped multiplication rule stays under the claimed degree ceiling. New field equations must be annihilated/derived within the same ceiling.
5. **Bounded field reduction:** membership in the product-domain field ideal gives a degree-nonincreasing reduction by univariate generators. Membership in the full unsatisfiable base ideal does not give a cheap certificate for free.
6. **PC reuse:** learn final polynomials and reuse those lines. Do not multiply every line of an earlier high-degree derivation by the selector without paying for it. Do not apply PC reuse to an NS certificate as though the certificate degree had the same closure property.
7. **Core/consequence quotient:** every relation used to create a span inclusion must have an available bounded-degree derivation. Preserve the maximum generator/residual degrees in the theorem's assumptions.
8. **Imported parameters:** extract actual simulation degrees, levels, companion count, accuracy, and encoding. Do not assume a bound on static chain count, residual rank, or essential cofactor support unless the source proves it.
9. **Finite checks:** A09/A10 verify finite primitive-PC transformations on synthetic propagation systems; A11 verifies finite algebra/optimization, not general PHP feasibility. Scope is part of every check claim.

These entries are questions to check, not allegations that a gap has already been found. Record a discovered error below with a precise statement, counterexample or missing inference, and affected dependency labels.

## Open target

Affordable transformation of each relevant translated degree-$D$ NS refutation into a base PC refutation below the available linear degree threshold, or an equivalent normalized joint design. A static decomposition of all admissible input spaces is not sufficient uniformly.

## New audit findings after import

The first local session read the full manuscript and performed a focused audit
of the central reuse/substitution/elimination arguments. This is not a formal
verification of all 68 working proofs. Source checks are recorded in IMPORT_LOG.md.

| Date | Claim label | Verified hypothesis / issue | Evidence | Consequences |
|---|---|---|---|---|
| 2026-09-10 | `lem:reuse`, `lem:substitution`, `lem:fieldreduction`, `lem:selectors` | No gap found in the reviewed arguments. Zero products and nonzero original multiplication predecessors are treated separately; reuse does not flatten certificates. | Chapter 1 and original TeX lines 59-107. | These tools remain usable as working proofs. |
| 2026-09-10 | `thm:one-elimination`, `thm:additive`, `thm:nested` | Weighted original axiom lines fit the stated ceiling; later freshness is obtained by reverse-level deletion. Earlier input derivations are reused, not reweighted in full. | Chapters 7-8; selected original TeX; no historical suites rerun. | No new gap found in the focused audit; no proof-length bound inferred. |
| 2026-09-10 | `thm:cores` | Absorption fits TD+gamma <= TD+(p-1)gamma. If the substituted common factor vanishes, the axiom image is zero; otherwise degree additivity in the ordinary polynomial ring bounds its factor. | Chapter 8 / original TeX lines 64-103. | General T>=1 argument reviewed; no claim of a new exhaustive computational check. |
| 2026-09-10 | `imp:php` (ordinary-design part) | Krajicek's exact base contains our equations plus row exclusions. Sign change and deletion match the weaker base and residual boards. | Krajicek v3 pp. 10-11, including visual inspection of p. 10. | Ordinary-design encoding match checked. PC threshold still awaits Razborov's original paper. |
| 2026-09-10 | Krajicek p. 10 identity | Printed Boolean-redundancy identity has a plus/minus typo over odd primes; correct formula is -x_ij Q_i - sum_{k!=j} Q_{i;j,k}. | Direct expansion and original PDF page. | Harmless here: Boolean axioms are explicitly included. No historical manuscript rewritten. |
| 2026-09-10 | `imp:simulation` | Theorem 5.2 explicitly cites BIKPRS 6.7(1) and retains (h+1)^{O(ell)} degree dependence. | Krajicek v3 p. 13. | Recorded simulation statement matched; original construction/cofactors awaiting BIKPRS PDF. |
| 2026-09-10 | `imp:pebbling`, `cor:genericbatchfalse` | Encoding and all-field degree correspondence match; c=1 gives the required single-sink polynomial-size family. | Pebbling v1 equations (2.5)-(2.6), Theorem 3.1, Definition 4.7, Lemma 4.9. | Imported input supporting the generic-design obstruction checked at the cited source-statement level. |
| 2026-09-10 | New: `local:zero-cofactor-pruning` | Constant-specialize fresh variables of unused blocks throughout the complete certificate. | RESEARCH_LOG.md, first local entry. | Irrelevant blocks carry no charge. No uniform smallness theorem for surviving support. |


### Follow-up after user-supplied PDFs

- `imp:php`: Razborov's published Definition 2.4 and Theorem 3.1 match the
  stronger Boolean-quotient system. Ordinary-PC proofs map to its degree
  convention without increase; deleting row exclusions and applying partial
  matchings verifies the base and residual PC thresholds. The imported
  hypothesis of `thm:rigidity` is discharged at the source-statement level.
- `imp:simulation`: BIKPRS Theorem 6.7(1), Definition 6.8, and the concluding
  proof on pp. 28-31 now inspected. The balanced derivation tree has height
  O(log S), while ENS levels follow formula depth. No cheap bound on essential
  block/cofactor support is thereby proved. SOURCE_AUDIT.md records the coverage.
- All new work now lives in research/. The original handoff was restored and
  all 128 package files verified against its ZIP. Earlier pending-source entries
  above describe the initial import and are superseded by this follow-up.
