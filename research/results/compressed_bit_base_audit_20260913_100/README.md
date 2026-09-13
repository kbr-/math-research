# Compact bit-PHP base and source bridge

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-13-compact-bit-base)
contains the exact auxiliary system, two-row interpolation proof, affine
decoder transfer, PC degree lower bound, transported consequence filtration,
and source connection to the original ordinary-PHP research target.

All assertions here are over F2. The same-degree decoder theorem requires
n=2^ell with ell>=2. Intrinsic NS stability of the compact bit base is not
asserted. The stable class J_k is defined by transport from functional unary
PHP and is not identified with the compact base's NS space.

## Complete decoder certificates

The file <code>compact-bit-base-certificates.jsonl</code> uses ell=1,2,3,4.
For each ell it works with two unary rows of n=2^ell variables. The decoder
bit images are sums of cells whose labels have the corresponding bit set.

Each case records:

- Every decoder bit polynomial.
- The complete decoded equality polynomial.
- Its ordinary two-row reduction and bilinear state interpolation.
- Every nonzero old axiom/cofactor pair proving the equality image.
- Complete degree-two decoder Booleanity image certificates.

The row reduction uses Booleanity and explicit same-row exclusions.
Homogenizing constants and single-row terms uses the row sums minus one.
The final interpolation is the sum of same-column cross-row monomials,
which are old collision generators.

| ell | n | Equality certificate terms | Equality NS degree |
| ---: | ---: | ---: | ---: |
| 1 | 2 | 4 | 2 |
| 2 | 4 | 14 | 2 |
| 3 | 8 | 60 | 3 |
| 4 | 16 | 250 | 4 |

The ell=1 case deliberately exhibits the degree-two homogenization cost for
a degree-one target. It is outside the same-degree compact-base theorem.
Its unary-OR packing record is an algebraic control, not an actual one-input
OR occurrence in the source presentation.

The missing-functionality control uses n=4 and one-coordinates 0,1,2,7
in the two-row indexing below. All other coordinates are zero. It satisfies
the local two-row weak base, including both row parities and all column
collisions, but makes the decoded equality one. It does not satisfy the
same-row exclusions. No model of the full n+1-pigeon system is claimed.

## Actual source-clause packing

For each ell, take h=ceil(ell/2) and the affine clause inputs

    g_t = b_(0,t)+b_(1,t).

Pair successive inputs in coefficient rows using coefficients 1 and 1-g_t;
an unpaired input uses coefficient one. The complete block, coefficient
substitution, and resulting equality product are saved.

Every companion image g_t*E has a complete old-bit Booleanity certificate
through degree ell+1, within its original degree 2h+1. Every nonconstant
coefficient-field image has its complete degree-two certificate. The record
also retains the final boundary's original companion degree 2h^2+3h and
its equality-image degree ell.

There are 38 NS certificate records in total: four equality decoder images,
20 decoder bit-domain images, ten packed companions, and four nonzero packed
coefficient-field images. Every identity and degree bound passed.

## Encoding

Ordinary polynomials use [coefficient,[variable,...]] terms, with repeated
indices representing powers and coefficients in F2.

Decoder records use unary variable index row*n+label, for rows zero and one.
Hole labels run from zero to n-1, and bit t is the t-th least significant bit.
All accompanying axiom/cofactor pairs use that unary coordinate space.

Packing records use bit coordinate row*ell+t. Fresh coefficient variables
start after the 2*ell bit coordinates; their rows and input order are listed
in the full block record. The two record types have distinct coordinate spaces.

No certificate is reconstructed from a numerical rank alone. All nonzero
axiom multiples are present, including their original row/column/domain
identities. The weak-system control includes a full bit assignment by its
one-coordinate list and the rule that all unlisted coordinates are zero.

## Reproduction

Use a new output path from the repository root:

~~~bash
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -std=c++17 -O2 -Wall -Wextra -pedantic \
  research/tools/check_compact_bit_base.cpp -o /tmp/check_compact_bit_base
./compute.sh run TURN --threads 1 -- \
  /tmp/check_compact_bit_base --out NEW_CERTIFICATES.jsonl
~~~

The checker refuses existing output paths. No random seed or additional
dependency is used. Source, exact-polynomial headers, this description, and
the complete data are pinned by <code>provenance.json</code>. The matching
session archive preserves timing and all command outputs.

The lower bound, Frege proof conversion, and transported filtration are
analytic arguments in the notebook. No hypothetical full Frege proof was
instantiated, and no intrinsic compact-base NS filtration was computed.
