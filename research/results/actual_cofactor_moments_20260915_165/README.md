# Actual cofactor and old point-support audit

The [notebook entry](https://kbr.is-a.dev/math-research/#entry-2026-09-15-cofactor-point-support-audit)
contains the support proof, sharp three-point control, source specialization-span
argument, old matching separator, and remaining proof-specific obligation.

## Results and limits

A normalized degree-D NS design for an unsatisfiable Boolean system with
generator degrees at most gamma needs at least 2^(D-gamma+1) points in every
Boolean-point representation. The proof isolates a support point using at most
floor(log2 K) literals. In characteristic two, projection of the weights to F2
gives an odd support subset, improving the bound by one when D>=gamma.

For the unary PHP bases gamma=2. Therefore optimizing point support alone cannot
make the old support-count union bound active: K*2^(-h)<1 requires h>=D. This
restricts that sufficient guarantee, not every structured scalar assignment.
The earlier literal-copy map remains a pointwise positive control.

The three displayed assignments on four pigeons and three holes have weights
one and form a complete degree-two design on exactly three points. Their only
column-collision patterns are (1,1,0) and (1,0,1). An explicit degree-three
collision multiple has value one, so the original support is not a higher-degree
design. All data and the complete check argument are in the notebook table.

One accuracy-h ENS product on r coordinates has scalar-specialization span
equal to all input products through h. Its Boolean dimension is the sum of
binomial(r,s), s<=h; the actual cofactor 1-P omits the constant. For diagonal
cell inputs on distinct rows and columns, signed row cubes show independence
modulo old I_B when B>=h, m>=B, and N>=max(2B-1,2h+1). The example is a genuine
source template, but is not claimed indispensable after global proof rewrites.

## Evidence

No numerical run was needed. Evidence consists of the complete analytical
arguments and three-point table. Metadata records the original source revision,
exact dependency anchors, parameter review, and touched-link/append-only checks.
Provenance hashes this note and metadata; timing and command output accompany
the checkpoint. No source-specific joint functional or Frege bound was obtained.
