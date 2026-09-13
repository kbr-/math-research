# Compact restriction: literal inventory and dense affine survival

The [full notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-13-compact-bit-inventory-restriction)
proves a degree-preserving restriction theorem for polynomially many
one-level signed-bit ENS blocks. It retains N=Theta(sqrt(n)) holes in a
coordinate label subcube, fixes all other pigeon labels bijectively outside
that cube, and removes the blocks at logarithmic accuracy.

The finite criterion is M beta^r<1, with r=2h+1<=q=n-N,
p=(N+1)/(n+1), alpha=n/(q-r+1), and
beta=max(p+alpha/2,(p+alpha/n)^(1/ell)).
For M<=n^a, h=ceil((a+1)ell) and N=2^floor(ell/2) suffice for large n.
The original NS/PC degree is preserved. General affine and later-level
inputs do not inherit this literal-family theorem.

## Complete finite witness

<code>restriction-and-code.jsonl</code> uses:

| Parameter | Value |
| --- | ---: |
| Original holes n and bit width ell | 1,024 and 10 |
| Retained holes N and bit width s | 32 and 5 |
| Pigeons / live pigeons | 1,025 / 33 |
| Accuracy h / input rank r | 6 / 13 |
| Signed-bit blocks | 64 |
| Seed | 202609130107 |

Half the literal blocks put ten bits in one pigeon and three in another;
half spread their 13 bits across different pigeons. All are proper,
independent mismatch tuples. The first sampled restriction kills all 64
by making a saved input constant one. Setting that coefficient in the
first factor row to one, and all the block's other coefficients to zero,
makes its product zero.

The same restriction retains full rank 13 for a dense affine block:
g_j=sum_i C_ij b_(i,0). Its complete 1025-by-13 matrix and all 8,192
codeword weights are saved. Minimum nonzero weight is exactly 457.
The surviving affine inputs remain independent and have an explicit
common Boolean zero, so their span is proper and above the affine packing
threshold 2h=12. The common zero is not a satisfying PHP assignment.

Every old equality pair was checked. There are 528 live-pair images,
491,536 zero fixed-pair images, and 32,736 zero mixed-pair images.
Exactly 165 old Booleanity equations retain a variable.
The complete restriction arrays determine each individual axiom image.

## Encoding and replay

An old bit variable has ID pigeon*ell+bit. The kept label cube is exactly
the labels 0..N-1, with high bits zero.
Each literal input record is [variable_ID, constant], representing that
bit plus the constant over F2.

The dense matrix is stored by rows as 13-bit masks. Its weight table is
indexed by all input vectors v=0..8191; entry v is the weight of C*v.
This is complete exact enumeration, not a random rank sample.

Every trial record saves the sorted live-pigeon list, all fixed labels
(-1 for a live pigeon), the first constant-one input index of each literal
block, and the dense residual rank. The complete sampled outside-label
bijection is therefore reconstructible.

The accepted witness stores the residual affine constant mask, all
Gaussian pivot rows and their live-row combination masks, and a solution
mask on the live pigeons' bit-zero coordinates. Set those bit-zero
variables according to the mask and all other residual bits to zero.
Substitution gives zero in every dense affine input.
These certificates establish its rank and properness after restriction.

## Exact probability ledger

<code>exact-bounds.json</code> checks both rational inequalities equivalent
to M beta^r<1:

~~~text
M (p+alpha/2)^r < 1,
M^ell (p+alpha/n)^r < 1.
~~~

The displayed literal union bound is approximately 0.765461793.
Dense rank failure is at most
(2^13-1)*binom(568,33)/binom(1025,33), approximately 0.0000185107239.
The ledger also verifies positive probability of both effects simultaneously,
using exact rational comparisons with the remaining probability margin.
All numerators and denominators are retained as decimal strings; approximate
values are display only and never determine pass/fail.

## Scope of the dense control

The dense block prevents copying the literal random-killing bound to
arbitrary affine inputs followed by rank-at-most-2h affine packing.
It does not rule out a favorable adaptive restriction or elimination.
Its rank is only 2h+1: the existing three-per-bin polynomial packing uses
coefficient degree two and transfers an NS certificate through at most 2D.
The notebook states this remedy explicitly. It is not a hard affine family
for the overall lower-bound goal.

## Reproduction

~~~bash
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra \
  research/tools/check_compact_bit_restriction.cpp -o /tmp/math-compact-bit-restriction
./compute.sh run TURN --threads 1 -- \
  /tmp/math-compact-bit-restriction --out NEW_RESTRICTION.jsonl
./compute.sh run TURN --threads 1 -- \
  python3 research/tools/check_compact_restriction_bounds.py \
  --evidence NEW_RESTRICTION.jsonl --out NEW_BOUNDS.json
~~~

The tools refuse existing output paths and install no dependencies.
All heavy enumeration and numerical loops are compiled C++; the Python
controller performs only the small exact rational ledger using compiled
integer arithmetic. Compilation and both runs passed on the first attempt.
Source, this description, and complete outputs are pinned by
<code>provenance.json</code>. The notebook timing and session archive retain
the measured work and full command outputs.
