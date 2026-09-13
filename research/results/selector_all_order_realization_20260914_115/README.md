# Every-order selector realization and degree elimination

The [notebook entry](https://kbr.is-a.dev/math-research/#entry-2026-09-14-all-order-selector-realization)
proves the exact affine-flat cut rank, balanced-code construction, every-order
source-selector obstruction, and degree-preserving normalizer for the same
family. These are not complete PHP refutations or new PHP lower bounds.

## Reproduce

From the repository root with the resource controls active:

~~~sh
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra \
  research/tools/check_all_order_selector_codes.cpp \
  -o /tmp/math-all-order-selector-codes
./compute.sh run TURN --threads 1 -- \
  /tmp/math-all-order-selector-codes --out NEW_OUTPUT_PATH
~~~

The output must be new. No dependencies were installed. The code uses exact F2
arithmetic and the existing sparse_polynomial.hpp kernel for ordinary identities.

## Complete evidence

code-and-cut-certificates.jsonl contains:

- All 560 target/cut cases for the rank-three eight-column cube: evaluation
  and multilinear coefficient matrices, both side ranks, and exact cut rank.
- One full repeated-basis control, where the code-weight hypothesis fails and
  a balanced half has rank two instead of the required three.
- All columns and all nonzero row-codeword weights for r=4,9,16,
  v=320,640,1088. Seeds are 202609140115+h; the generator is mt19937_64,
  with each column given by its low r bits. All first trials were accepted.
- Thirty-eight complete ordinary NS templates for the source family at h=2,3,4,
  including the free modifier variable and original companion-degree ceilings.

Matrix rows are integers with the least-significant bit representing column
zero. Code columns are r-bit vectors with row zero in the least-significant
position; the weight list is indexed by nonzero masks 1 through 2^r-1.
The exact rank algorithm uses XOR elimination, without floating-point arithmetic.

The large code witnesses certify the weight hypothesis for all row combinations.
The proved half-rank lemma then certifies every coordinate order; the program
does not enumerate those orders. The finite cube checks independently compare
the explicit truth matrices, Boolean coefficient matrices, and rank formula.

NS templates preserve their full targets and cofactor/axiom pairs in formal
linear-form variables t_j and the modifier z. For each saved matrix A,
t_j maps to its fully specified linear form in x. The axiom t_j^2-t_j maps
exactly to the sum of A[j,i]*(x_i^2-x_i). This supplies complete composed
certificates as factored expressions; no expanded dense old-variable polynomial
is silently omitted or claimed to have been computed.

Source/output hashes, timing, and complete command logs accompany this
checkpoint. Its initial preparation includes resolving the previous commit's
license-review rejection by directly verifying the versioned CC BY record.
