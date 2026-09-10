# Status and proof-audit ledger

**Snapshot:** 10 September 2026. **No payoff theorem is established.** This ledger summarizes the status recorded by the manuscript; it does not add a new mathematical correction.

## Current working theorem stack

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

_No independent audit has been performed by the new local session yet._

| Date | Claim label | Verified hypothesis / issue | Evidence | Consequences |
|---|---|---|---|---|
