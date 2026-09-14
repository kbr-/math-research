# Old-bit source profiles after affine-core constraints

The [notebook proof](https://kbr.is-a.dev/math-research/#entry-2026-09-14-shared-core-old-bit-profiles)
uses eligible affine-core zero equations to interpret each selected shared-bit
parent by its old probe bit. Later source inputs must absorb that bit into their
old-affine part. Canonical quadratic pair-bottom values remain selector columns
for the adapted-rank criterion.

## Reproduce

~~~sh
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra research/tools/check_shared_core_clamp.cpp \
  -o /tmp/math-shared-core-clamp
./compute.sh run TURN --threads 1 -- \
  /tmp/math-shared-core-clamp --out NEW_OUTPUT_PATH
~~~

Run from the repository root with active resource controls and a new output path.
The checker uses the shared exact NS reconstruction and term-degree helper.

## Evidence and scope

The binary accuracy-two fixture contains two star parents, four pair-bottom
blocks, two constrained affine star cores, and one third-level affine core.
The original star products and third-level inputs have degree ten; the third
product's original weight is 22. Mapped input degree six and interpreted affine
degree one do not replace those original bounds.

Fifteen complete NS witnesses preserve actual targets and all cofactors. Their
degree checks include parent-to-bit comparisons, source prefix residuals,
companions, and Booleanity. Polynomial terms use
[coefficient,[variable IDs with repetitions]]. The setup includes original source
blocks, original and mapped inputs, affine target blocks, and the full retained
axiom list. Bottom coefficients use the scalar map proved in the preceding cycle.

All 288 canonical retained-system models are saved. In 36 the third value is one,
and each star value is one in 144. A wrong-zero-projection control demonstrates
the necessary old-bit offset. A missing-core-constraint model violates a derived
third-level companion.

These rank-two cores test conditional profiles, not asymptotic high-rank
eligibility. The finite old base contains Booleanity, not PHP. All checks passed
with a clean compilation.

The timing session also includes the preceding, separately committed shared
NS-helper refactor and its byte-identical evidence reproductions. Source hashes,
full command evidence, and measured timing accompany this checkpoint.
