# Transported bit quadratics and a source-family application

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-13-bit-quadratic-consequences)
proves that J_2 contains only bit Booleanity consequences for ell>=3,
identifies the exact ell=2 exception, and applies the existing faithful-pair
theorem to every one-level affine-bit ENS family at D=3h+1.

The application requires n=2^ell>=8 and n>=6h+1. It is an ordinary NS
design/old-consequence statement with no family-count charge. It does not
transfer augmented PC proofs or cover the completed source's larger degree
and later levels. Old bit consequences land in J_D, not necessarily in the
compact base's own C_D.

## Exact quotient data

The four files contain complete degree-two NS computations:

| File | Labels | Column exclusions | Old normal dimension | Old NS rank | Bit source dimension | Image rank | Extra kernel |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| bit-quadratics-n4.jsonl | 4 | yes | 141 | 75 | 56 | 46 | 10 |
| bit-quadratics-n8.jsonl | 8 | yes | 2,089 | 549 | 379 | 379 | 0 |
| bit-quadratics-n16.jsonl | 16 | yes | 32,913 | 4,233 | 2,347 | 2,347 | 0 |
| bit-quadratics-n4-no-columns.jsonl | 4 | no | 181 | 75 | 56 | 56 | 0 |

The old normal basis first reduces Boolean powers, same-row exclusions,
and (when selected) column exclusions. The remaining old NS space is built
from every row generator with every allowed constant or variable multiplier.
No multiplication closure of derived polynomials is taken.

Every Boolean bit monomial through degree two is then mapped by the affine
decoder. The output includes its base-elimination trace, image-elimination
trace, source combination, and any new image or kernel basis row.
These are full exact rank certificates, not sampled input spaces.

For n=4, all ten kernel vectors are verified to span exactly the canonical
pair-equality indicators. For n=8,16, the source maps are injective. The
missing-column control shows that the four-label relations disappear when
the source base has only functional row constraints.

## Encoding and reconstruction

All arithmetic is in F2. Vectors are sorted lists of nonzero monomial
coordinates. Each board record gives the complete old normal monomial list:
[-1,-1] is one, [a,-1] is x_a, and [a,b] is a surviving quadratic product.
Old cell index a is row*n+label. Its row and column are obtained by quotient
and remainder on division by n.

The bit input records identify row, bit position, and complete old affine
polynomial. Bit ID is row*ell+bit, and label bit zero is least significant.
The bit source monomial list uses the same sentinel convention, with only
squarefree quadratic products: bit Booleanity has already been factored out.

Each base step starts from the specified row equation times its indicated
multiplier; -1 means multiplier one. XOR the preceding basis rows named in
its trace to obtain the saved reduced row, or zero for a dependent step.

For a bit image step:

1. Construct the decoder image of its labeled source monomial using the
   supplied affine inputs and old normal monomial rules.
2. Apply the saved base trace.
3. Apply the saved image trace.
4. Verify the new image basis row and its source combination, or the zero
   image and recorded kernel relation.

The equality-kernel records give the compact equality vectors and their
complete kernel-membership traces. The n=8,16 cases also save four-hole
rectangles isolating every entry of a cross-row bit matrix; the analytic proof
applies the same label construction to every pair of pigeon rows.

## Reproduction

The new mode reuses the existing quadratic quotient implementation. Compile
once, then use fresh output paths:

~~~bash
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -std=c++17 -O2 -Wall -Wextra -pedantic \
  research/tools/check_quadratic_relative_kernel.cpp \
  -o /tmp/check_quadratic_relative_kernel
./compute.sh run TURN --threads 1 -- \
  /tmp/check_quadratic_relative_kernel --out NEW_N4.jsonl \
  --bit-quadratic --holes 4
./compute.sh run TURN --threads 1 -- \
  /tmp/check_quadratic_relative_kernel --out NEW_N8.jsonl \
  --bit-quadratic --holes 8
./compute.sh run TURN --threads 1 -- \
  /tmp/check_quadratic_relative_kernel --out NEW_N16.jsonl \
  --bit-quadratic --holes 16
./compute.sh run TURN --threads 1 -- \
  /tmp/check_quadratic_relative_kernel --out NEW_NO_COLUMNS.jsonl \
  --bit-quadratic --holes 4 --no-columns
~~~

No random seed or additional dependency is used in this mode. Existing output
paths are refused. Historical modes were not rerun. The final source, shared
header, this description, and all four complete outputs are pinned by
<code>provenance.json</code>. Timing and full command outputs are archived with
the session.
