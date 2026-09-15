# Finite Boolean covers and source-scope screening

The [notebook entry](https://kbr.is-a.dev/math-research/#entry-2026-09-15-finite-Boolean-cover-barrier)
contains the full cover obstruction and certificate-combination proof.

## Mathematical scope

Suppose a finite collection of polynomial systems G_j covers the old Boolean
cube, and each system's zero set has an output polynomial V_j agreeing with an
approximate majority. If b_j bounds the equations and output of entry j, then
the sum of b_j is greater than the Hamming-ball radius.

At one wrong graph point, choose one violated equation from each entry,
including its output equation. Their product separates that wrong point from
the whole graph. Fixing the output gives a nonzero monochromatic certifier,
so the existing all-field Hamming-ball lemma supplies the lower bound.
The number of equations within an entry is unrestricted.

Separately, degree-D_j ordinary NS refutations of F plus each cover entry
combine into an old refutation through sum D_j. The proof uses telescoping and
Boolean certificates for products choosing one equation from every entry.
It asserts a degree bound, not a polynomial certificate-size bound.

For complete menus of the recorded three-level approximate-majority source,
this total-degree accounting cannot fit below the old compact PHP barrier.
The claim does not apply merely because a gadget can be appended to a proof:
essential occurrence and proof-specific coverage remain separate.
PHP-relative constructions and other certified combinations are not excluded.

The random-menu calculation is only a nonuniform existence control under
S(1-1/p)^h < 1. No pseudorandom generator was built, no claim of a short-seed
impossibility was made, and no new numerical run was needed.

## Repository dependencies

- `approximate-majority-all-field-certifiers`, with its original attribution;
- `polynomial-size-three-level-majority-source` and its complete semantics;
- ordinary Boolean division and original NS generator-multiple accounting.

## Targeted primary-source scope check

Yogesh Dahiya, Meena Mahajan, and Sasank Mouli,
*New Lower Bounds for Polynomial Calculus over Non-Boolean Bases*,
SAT 2024, DOI: 10.4230/LIPIcs.SAT.2024.10.

https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.SAT.2024.10

Inspected the abstract, Theorem 1.2, Definitions 2.2 and 4.1, and adjacent scope
text. The extension equations use polynomials in original variables.
The inventory, arity, size, and generalized-PHP lifting hypotheses were not
proved for our full source, so the theorem was not applied.
The publisher identifies CC BY 4.0; no PDF or full-text copy is added here.

The search also located the ITCS 2026 proceedings version of the
Lu–Santhanam–Tzameret result already screened in cycle 150:
https://doi.org/10.4230/LIPIcs.ITCS.2026.99
Its abstract retains the unresolved tautology status of the DNF family.
No new theorem from that proof is imported.

## Review and evidence

The review checks graph coverage, selection of nonzero factors at a wrong
point, the all-field product, exact Boolean NS degree accounting, and the
condition D_j >= b_j when comparing the cover barrier to branch budgets.
It also preserves the distinction between complete evaluation sources and
actually necessary proof modules.

`check-metadata.json` records the focused checks; `provenance.json` hashes this
note and metadata. Timing and complete local command outputs are archived.
