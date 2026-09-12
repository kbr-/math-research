# Compact source certificates and the remaining restricted-query question

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-12-compact-source-query-interface)
contains the full source audit, circuit-size argument, and restricted criterion.

For a fixed scalar specialization of a degree-D ENS/NS certificate with S
companions in M used blocks, its conflict tree uses at most S-1+h*M distinct
query polynomials and S*(h+1) possible leaf pairs. Counting queries alone does
not distinguish it from the full-space covariance probe.

The working representation refinement retains the balanced source simulation's
cofactors as shared, division-free arithmetic circuits. For fixed prime and
formula depth, balanced symbol inventory T, and v original variables, the
total circuit size is bounded by

    (v+T+h+1)^c * 2^(c*h)

for a fixed c depending on the presentation, prime, and depth. The construction
uses constant-degree formal axiom certificates, the source's at-most-4^h
local OR expansion, explicit approximation Booleanity and Frobenius identities,
and the exact MP cofactor recurrence. It retains the existing polylogarithmic
degree majorant. At h=O(log(n+S_proof)), the circuit size is polynomial in
n+S_proof, including after the affine ordinary-PHP boundary substitution.

Thus a survival guarantee against polynomial-size circuit-described queries
and leaf factors would imply the desired source contradiction with the same
height and probability parameters. No such guarantee is proved. The dense
full-space averaging argument does not supply a small-circuit witness, but
small-circuit attacks or compression modulo design relations remain possible.

## Source and proof scope

Read from the existing audited BIKPRS author copy:

- Lemma 6.2, extracted lines 1102-1195.
- Theorem 6.7 and the beginning of its reverse simulation, lines 1240-1305.
- Definition 6.8, Lemma 6.9, and local OR expansions, lines 1360-1482.
- Lemmas 6.10-6.12 and the balanced-tree induction, lines 1455-1548.
- The tree-like PC/NS discussion, lines 1033-1100, as context only; the
  representation proof uses the direct approximation route instead.

Read Krajicek arXiv:2301.10617v3, Theorem 3.2 proof, extracted lines 389-434.
The exact local source version and hashes are preserved in SOURCE_AUDIT.md
and this result's provenance manifest. No new third-party copy was acquired
or included publicly. Existing notebook dependencies were read at their exact
anchors: direct-theorem-approximation, direct-php-boundary, direct-php-transfer,
mp-certificates, and pseudo-ENS-rate-bridge.

The refinement proves a representation-size bound, not a small monomial
expansion or a constant-depth bound for every cofactor circuit. It is
conditional on a short source Frege proof; it does not construct that proof.
The source's reverse simulation still has an exponent depending on NS degree,
even in the favorable bounded-input-degree setting, so this alone provides
no polynomial-size Frege upper bound.

## Evidence and process

No numerical experiment was appropriate: the new work is a symbolic
operation count and certificate construction from the exact source identities.
The notebook contains the complete argument, including explicit handling of
Booleanity, field equations, sharing, scalar substitution, and leaf factors.
provenance.json pins the supporting notes and exact source bytes read.

Timing begins with the preceding checkpoint and publication. Source reading
and mathematical work were phase-marked. One initially guessed notebook
anchor did not exist; the claim index then supplied the correct anchor.
This was a navigation error, not a mathematical failure.

The source audit established a real restriction instead of inferring one
from degree or family count. No new workflow rule was needed; the next test
must challenge this actual circuit-bounded class before searching for another
design distribution.
