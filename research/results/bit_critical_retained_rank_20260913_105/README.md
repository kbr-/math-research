# Retained rank excludes critical equality kernels

The [full notebook proof](https://kbr-.github.io/math-research/#entry-2026-09-13-bit-critical-retained-rank)
extends the unconditional affine-bit NS design range to h+u+1=ell, at
D=3h+u, 1<=u<=h, h>=ceil(ell/2), ell>=4, and n=2^ell>=2D-1.
The actual affine packing map leaves only input spaces of rank above
2h>=ell. A leading-coefficient rank theorem excludes their non-Boolean
critical singleton kernels. Original-degree NS image certificates then
pull the residual design back to the entire original one-level family.

At minimum compact-source accuracy, the range reaches 4h-1 for even ell
and 4h-2 for odd ell. The theorem does not eliminate the completed larger
NS endpoint, transfer augmented PC proofs, or cover later extension levels.

## Exact finite coefficient computations

<code>exterior-kernels.jsonl</code> contains 193 complete kernel cases:

- All 63 nonempty graphs on four pigeon rows, for each ell=3,4,5: 189 cases.
- One tight rank-ell multiplication example at each ell=3,4,5: three cases.
- The excluded ell=2 complete graph on four rows: one case.

Work in the commuting square-zero algebra over F2, the associated graded
Boolean algebra. A graph gives the sum of the leading equality products
for its edges. The program computes the full linear annihilator by exact
binary elimination.

All 18 single-edge cases have exactly the ell-dimensional edge-difference
annihilator. All 171 multi-edge cases have zero linear annihilator.
The rank controls multiply by the product of the first ell-1 differences
on rows zero and one, modulo the full equality-leading span. Their preimage
is exactly that pair's ell-dimensional difference space.

At ell=2, the complete graph sum factors as the product of the all-row sums
in its two bit positions. Its linear annihilator has dimension two.
This is a genuine exception to the multi-edge lemma outside ell>=3.
The rank controls concern leading coefficients only, not full singleton
consistency kernels.

## Complete encoding and replay

Variable ID is row*ell+bit. An exterior monomial is an integer bit mask.
Products with a repeated variable are zero; all coefficients and additions
are in F2. Polynomial lists are sorted XOR sums of monomial masks.

Every case record gives the multiplier, entire output-monomial coordinate
list, and the expected kernel as a list of linear-vector masks. The variable
count is 4*ell. Every allowed-generator record includes its raw vector,
reduction trace, pivot or -1, and reduced vector.

Each input column is the multiplier times the indicated variable. Column
records retain its raw image, allowed-span reduction trace, previous-image
reduction trace, reduced vector, and complete source combination.
Vectors are sorted lists of nonzero coordinates.
XOR the named previous pivot rows to replay a reduction; update source
combinations with the same image trace. A zero image gives a kernel vector.
Case summaries save the allowed rank, image rank, and kernel dimension.

These are full leading-coefficient kernel computations, not whole PHP NS
matrices or finite verification of the universal source-family theorem.

## Reproduction

~~~bash
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra \
  research/tools/check_bit_equality_exterior.cpp -o /tmp/math-bit-equality-exterior
./compute.sh run TURN --threads 1 -- \
  /tmp/math-bit-equality-exterior --out NEW_OUTPUT.jsonl
~~~

Compilation and the sole numerical run passed on the first attempt.
The tool refuses existing output paths, uses no randomness, and installs
no dependency. Source, the shared binary linear algebra header, this
description, and complete output are pinned by <code>provenance.json</code>.
The notebook contains the timing table; the session archive retains its
journal and all command outputs.
