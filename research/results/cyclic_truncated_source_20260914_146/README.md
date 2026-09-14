# Binary cyclic sources at arbitrary lengths

The [notebook entry](https://kbr.is-a.dev/math-research/#entry-2026-09-14-arbitrary-cyclic-source)
proves the working finite theorem and complete source transfer. Write
t=e*u, with e a power of two and u odd. Local coefficient coordinates at
the u-th roots of unity turn cyclic products into truncated convolutions.
Frobenius permutes roots while preserving each local coefficient index.
Weights minus the squared index give at least t/2 disjoint leading pairs.

These are degree-two identities in the original generators. Ordinary
witnesses descend to binary coefficients before the ENS map is defined.
The result covers arbitrary linear-size cyclic lengths on independent
affine operand probes, with old degree sqrt(n)*polylog(n), polynomial
inventory, and polylogarithmic source degree. It retains the full output
tuple; arbitrary projections and general quadratic tensors remain open.

## Reproduce

From the repository root, with resource controls and an active timing session:

~~~sh
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra \
  research/tools/check_truncated_cyclic_source.cpp -o /tmp/math-truncated-cyclic-source
./compute.sh run TURN --threads 1 --timeout 180 -- \
  /tmp/math-truncated-cyclic-source --out NEW_OUTPUT_PATH
~~~

The checker refuses existing outputs. No dependencies were installed.
The shared reduction accepts a supplied monomial order; its default remains
graded lexicographic. Auxiliary-field polynomial arithmetic is shared with
the preceding conjugate-field verifier.

## Complete exact evidence

`truncated-cyclic-source-checks.jsonl` stores polynomial terms as
`[coefficient,[variable IDs with repetitions]]`. Extension coefficients are
polynomial-basis bitmasks modulo the specified binary polynomial. Local
coordinate variables start at ID 1024. Large integers are decimal strings.

The seven local decompositions are:

| t | Odd part u | Multiplicity e | Field dimension | Weighted disjoint pairs |
| --- | ---: | ---: | ---: | ---: |
| 2 | 1 | 2 | 1 | 1 |
| 3 | 3 | 1 | 2 | 3 |
| 4 | 1 | 4 | 1 | 2 |
| 6 | 3 | 2 | 2 | 3 |
| 8 | 1 | 8 | 1 | 4 |
| 10 | 5 | 2 | 4 | 5 |
| 12 | 3 | 4 | 2 | 6 |

Every operand map is inverted and checked in both directions. All roots,
Frobenius permutations, Taylor matrices and inverses, operand probes,
original inputs, local products, selected divisors, and degree-two
generator pullbacks are retained. The product checks include all local
coefficients, including the odd indices omitted from the divisor list.

The 2,717 ordinary NS certificates comprise:

- 142 pullbacks of original Boolean and local product generators;
- 2,321 coordinate-reduction witnesses;
- two selected strict old-kernel witnesses over auxiliary fields and
  their two binary descents;
- 250 complete weighted source-axiom images over old Booleanity.

For t=4,6,8, the coordinate witnesses cover every ordinary monomial through
degree three: respectively 220,560,1140 monomials. At the other lengths,
they cover the constant, all linear variables and cubes, and every selected
leading pair multiplied by every variable. The saved remainder is checked
against all leading divisors. Every generator multiple is charged in
ordinary degree; weights select the order without changing degree budgets.

The default graded-lex heads form one star per root. At e>=4 the weighted
order supplies strictly more disjoint pairs; both head lists are saved.
The local coefficient of epsilon^2 in X^2 is one, whereas its ordinary
second derivative is zero in characteristic two. Nonbinary root cases
also retain an old Boolean point where naive local-coordinate Booleanity
fails and the correct Frobenius-domain equation holds.

## Full original sources

The source cases t=4 and t=6 use independent affine operand probes with
constant shifts. Their old dimensions are 9 and 13, and their complete
source-variable counts are 45 and 91. The four shifted probes at t=4,
and the corresponding triangular maps and shifts at t=6, are retained
explicitly in the setup records.

The checker extracts the old coefficient maps from strict local-kernel
witnesses and verifies their binary descents through degree three. The
weights are homogeneous squarefree cubics; parent coefficient images
are linear. Every companion, coefficient Boolean equation, and old Boolean
equation is included in the 81 and 169 source-image certificates, each
within its original axiom degree plus three. The source polynomials are
actual sums of reused bottom products.

All 64 and 1,536 nonzero-weight old assignments are retained as complete
source models. Model evaluation uses the original block inputs and products
to avoid repeatedly expanding their products. The full expanded source
axioms are saved and are used in the independent NS image reconstruction.
Each case also retains an unweighted-companion failure. These fixtures are
local Boolean systems, not PHP instances.

## Parameters and compatibility

For t=floor(v/2), M=n^2, and source degree ell^3, exact integer conditions
pass at ell=64 and 128. At ell=40 the range, image, and packing bounds pass,
but the row-cap domain estimate and old-degree room both fail. The actual
repeated-factor multiplicities in these cases are 4,32,64. Full numbers
and flags are retained; large multiplicative orders and field cardinalities
are not instantiated.

Compilation and all mathematical checks passed. A separate protected job
compiled the earlier conjugate-field verifier after the shared-helper
changes, ran its default mode, and compared the result byte for byte with
the saved 905-certificate cycle 145 output. The comparison passed.

`check-metadata.json` records the focused evidence and touched-link review;
`provenance.json` records code and evidence hashes. Timing and complete
command output are archived under this session name in
`research/provenance/session-records/`.
