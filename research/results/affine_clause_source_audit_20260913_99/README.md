# Affine-clause source audit and unary-to-bit controls

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-13-affine-clause-source-audit)
contains the source comparison, flat/clause dictionary, proper-point mismatch,
complete algebraic transfer proof, bit-base filtration obstruction, and updated
attribution of the earlier near-permutation query idea.

The audit did not construct a Res(parity) refutation or an affine DAG.
The algebraic encoding maps and their degree budgets are separate from such
a proof-system translation.

## Primary sources and reading scope

<code>source-audit.json</code> records exact versions, links, inspected sections,
the publisher access failure, and two newer abstract-only screens.

The core mathematical reading used the official HTML for:

- Gryaznov, Ovcharov, and Riazanov, arXiv:2404.08370v2, Sections 2.1, 3.1.1,
  and the functionality caveat in Section 4.1.2.
- Byramji and Impagliazzo, arXiv:2511.20023v1, Theorem 1.3, Section 3.2,
  Lemma A.2, and Remark A.4.

The versioned PDFs are cached locally and pinned by
<code>source-provenance.json</code>. Their full contents were not imported
into context or audited. Both use arXiv's nonexclusive distribution license;
the PDFs and future full-text conversions are excluded from public Git.
The public clone preserves the source links, hashes, scope, and original research.

To reacquire the personal copies from the repository root:

~~~bash
./compute.sh run TURN --threads 1 --category network_tool -- \
  curl --fail --location --max-time 30 \
  --output research/references/cache/GOR2024-v2.pdf \
  https://arxiv.org/pdf/2404.08370v2
./compute.sh run TURN --threads 1 --category network_tool -- \
  curl --fail --location --max-time 30 \
  --output research/references/cache/BI2025-v1.pdf \
  https://arxiv.org/pdf/2511.20023v1
~~~

## Complete local algebraic image certificates

<code>unary-bit-transfer-checks.jsonl</code> uses F2 and bit lengths ell=1,2,3,4.
There are n=2^ell labels. A label indicator is the product of its selected bits
and complemented bits. The partition sum is exactly one as an ordinary polynomial.

For each length, the file saves all indicator polynomials for two pigeon rows,
complete Booleanity and same-row exclusion image certificates, each bit
collision image, and two ENS image blocks at accuracies h=1,2.

| ell | Labels | Booleanity certificates | Row-exclusion certificates | ENS images |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 2 | 2 | 1 | 2 |
| 2 | 4 | 4 | 6 | 2 |
| 3 | 8 | 8 | 28 | 2 |
| 4 | 16 | 16 | 120 | 2 |

Every old quadratic base image has its supplied NS witness through 2*ell.
For the two-input ENS examples the original companion degree is 2h+1,
the actual image degree is (h+1)*ell+h, and the carried upper bound is
ell*(2h+1). Complete products, prefixes, companions, and fresh layouts are saved.

The bit variables of row i have indices i*ell+t. The two original unary
variables in the ENS checks have separate slots 100 and 101; they map to
label zero in row zero and label n-1 in row one. Fresh coefficients begin
after the 2*ell bit coordinates and are unchanged by the map.

Polynomial terms have form [coefficient,[variable,...]], with repeated indices
for powers. A domain-certificate cofactor at position t multiplies
b_t^2-b_t. All coefficients are exact residues in F2. No implicit Boolean
reduction is used for the recorded identities or original degree ceilings.

## Filtration and interpretation controls

<code>bit-equality-filtration.jsonl</code> contains the full list of collision
axioms for a fixed pair of pigeons, with all sum coefficients equal to one.
Their exact sum is

    E = product_t (1+b_(i,t)+b_(i',t)).

For ell=1,2,3,4, E has degree ell and belongs to I_(2ell). It is outside I_ell:
the degree-2ell collision axioms are inactive there, while the all-zero bit
point satisfies all domains and gives E=1. These are complete certificates
and separating points, not numerical rank estimates.

The image suite also preserves:

- The top multilinear coefficient and full-cube parity of a single incidence
  indicator, ruling out an affine bit-query representation for ell>=2.
- The weak-row assignment (1,1,1,0), which has parity one but is not one-hot
  and does not survive decoding to one label and back.
- A normalized three-point root with a zero-mean, nonzero flat-conditioned
  singleton; its two parity-split child means are both one in F2.

These controls identify exact scope failures. They do not refute every possible
proof translation, probability construction, or alternative bit-base presentation.

## Reproduction

Use fresh output paths:

~~~bash
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -std=c++17 -O2 -Wall -Wextra -pedantic \
  research/tools/check_unary_bit_transfer.cpp -o /tmp/check_unary_bit_transfer
./compute.sh run TURN --threads 1 -- \
  /tmp/check_unary_bit_transfer --out NEW_IMAGES.jsonl
./compute.sh run TURN --threads 1 -- \
  /tmp/check_unary_bit_transfer --out NEW_FILTRATION.jsonl --equality-filtration
~~~

No random seed or extra dependency is used. Existing output files are refused.
<code>provenance.json</code> pins the final code, shared exact-polynomial headers,
complete outputs, and this reproduction record. Timing and all protected
command outputs are retained in the corresponding session archive.
