# Source audit — completed import, 10 September 2026

All four direct references are acquired and extracted. Acquisition is not a
claim of independently verifying every proof in every paper. Earlier failures
remain in the import log. Source paths below are relative to `research/`.

## Razborov: base and residual PC lower bound

User supplied `references/user_supplied/Razborov.pdf`; the document identifies
itself as *Computational Complexity* 7 (1998), 291-324. SHA-256:
`a733438feeda422d58c004b2331b742380d11d84e587990a2fd240466ecda47f`.
Exact download URL was not supplied; do not fabricate it.

Read extracted lines 1-32, 130-164, and 214-251; visually inspected PDF pages
6-7 (printed pp. 296-297). Definition 2.4 has row equations 1-sum_j x_ij and
both row/column exclusions, in the Boolean quotient. Theorem 3.1 gives degree
at least n/2+1 over every field for every m>n.

**Degree-convention bridge.** Definition 2.1 works in the multilinear Boolean
quotient and charges multiplication by x the degree of its predecessor plus one.
Map each line P of our ordinary-ring degree-D PC proof to its Boolean reduction.
Linear combinations commute with reduction. For a nonzero ordinary multiplication
P -> xP, deg(P)+1<=D, so the source inference charge is also <=D. Zero lines can
be omitted. Boolean axioms map to zero; row axioms differ only by sign. Thus an
ordinary-PC refutation of our weaker base gives a degree-at-most-D source proof
from the stronger row-exclusive system. Its lower bound therefore applies.

Under a partial matching of t pigeons to t distinct holes, assigned rows/columns
become constants and the surviving equations are exactly our base on m-t rows
and n-t columns, plus zeros. Since m-t>n-t, the same theorem applies. This
discharges the imported base/residual PC hypothesis used by `thm:rigidity`.
It does not prove the missing elimination theorem or ordinary-PHP proof transfer.

## BIKPRS: actual simulation structure

User supplied `references/user_supplied/BIKPRS.pdf`, a six-author, author-layout
copy with the cited title. SHA-256:
`78fff21cb13fb81d110bcfacba57d9be5a7dbd0ab36e1e1e2e4207fbcb09f4d2`.
Exact origin/version beyond document identification was not supplied. Do not
label it the publisher's paginated version without further evidence.

Read the title, Definitions 6.1/6.4/6.5, Theorem 6.7(1), Definition 6.8,
the first part of Lemma 6.9, Lemmas 6.10-6.12, and the concluding proof of
6.7(1). Extracted ranges: 1-28, 1120-1148, 1191-1231, 1246-1255,
1360-1455, 1484-1563. This is targeted reading, not a full-paper proof audit.

Theorem 6.7(1) (PDF p. 26) supplies |E|<=S^{O(1)}, extension depth ell+C,
arbitrary accuracy h>=1, and NS degree (d_0+log S)(h+1)^{O(1)}, with the
depth dependence made explicit by Krajicek Theorem 5.2 as O(ell).
Definitions 6.1 and 6.4 include Boolean original variables and field-valued
extension variables with their respective domain equations.

The proof first replaces the Frege proof by a polynomial-size tree-like proof
of height O(log S), with only constant additive formula-depth overhead.
Definition 6.8 creates blocks from the complements of approximations of the
children of disjunctions. The source encodes TRUE by zero; account for this
when transferring Boolean formulas. Polynomial input degrees grow with formula
depth; Lemma 6.10 bounds them by (ell+1) max{p-1,h}^{ell}.

Lemmas 6.9-6.12 provide local algebraic derivations. The final NS certificate
is assembled by induction on derivation height, yielding the logarithmic S
factor. Local multipliers and their products along proof branches determine
cofactors; no bound on residual rank, chain count, or essential cofactor support
small enough for our elimination has been established by this import. Balanced
derivation height alone must not be silently promoted to that missing theorem.

## Previously checked inputs

Krajicek v3: exact ENS syntax; ordinary-design lower bound and residual-board
matching by axiom deletion; simulation statement. Full extracted text read.
The p. 10 Boolean-redundancy display has an odd-prime sign typo, harmless because
Boolean axioms are explicitly included. Details are in IMPORT_LOG.md.

Pebbling v1: equations (2.5)-(2.6), Theorem 3.1, Definition 4.7, and Lemma 4.9
match the pebbling encoding, any-field NS-degree correspondence, and the
Gamma(1,r) single-sink family needed by the generic-design obstruction.

**Remaining obligations:** affordable refutation-sensitive elimination/joint
design, exact ordinary-PHP proof transfer, and final quantified parameter closure.
