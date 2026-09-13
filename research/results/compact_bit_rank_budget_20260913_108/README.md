# Packing and learning cover every one-level affine bit rank

The [complete notebook proof](https://kbr-.github.io/math-research/#entry-2026-09-13-bit-hybrid-affine-exclusion)
excludes polylogarithmic-degree NS and PC refutations over compact bit PHP
for every polynomial-size one-level affine-input family, when logarithmic
accuracy h is at least twice the bit width ell.

The proof combines two ingredients:

- The degree-k space L_k using at most one bit per pigeon row has dimension
  sum_(j<=k) binom(n+1,j)*ell^j and intersects J_k trivially when 4(k-1)<n.
- Ranks at most h(k+1) are packed with coefficient degree k; the other
  affine zero spaces supply a common vanishing polynomial f of degree k.
  Both assignments use only old variables, so their simultaneous degree is
  at most k. A refutation would learn nonzero f through B=k(D+1).

The exact dimension criterion is in the notebook. For polynomial inventory,
k=O(sqrt(n log(M+1))) makes it hold with B<n/2 at polylogarithmic D.
The result handles every affine rank mixture and all overlaps. It does not
preserve an arbitrary old design or eliminate later nonlinear levels.
No explicit enormous common polynomial or hypothetical refutation is built.

## Complete local NS image certificates

<code>hybrid-image-certificates.jsonl</code> uses two satisfiable Boolean-base
fixtures, h=1 and h=2, with k=3. Each contains:

- One rank-4h block, packed in h bins of four.
- Two opposing rank-one low blocks on u and 1-u.
- Two rank-(4h+1) affine blocks, with common predicate f=x0*x1*x2.

The opposing zero spaces cover the Boolean cube. Thus an all-block
common-vanishing predicate would have to be zero. The hybrid instead asks
for vanishing only on the high blocks. One high membership identity has
a nonzero Boolean remainder, testing actual degree-k ideal membership.

All 166 old Boolean NS certificates are retained in full: targets, every
cofactor, ordinary degree, and supplied ceiling. They cover both membership
identities, every weighted companion, all coefficient fields, old domain
multiples, and a maximal field-cofactor image.

The simultaneous map has degree three, compared with the product six of
the two separate substitution degrees. Omitting the weight or low-rank
packing produces a saved nonzero target on an old Boolean point.
The maximal field images reach B=18 for h=1,D=5 and B=24 for h=2,D=7.
These are individual image-degree controls, not optimality claims for the
whole refutation transfer.

The final boundary record sums the three compact pair equalities on three
rows at n=4,ell=2. Row-repeated terms cancel, leaving a nonzero degree-two
row-linear polynomial with an NS-two certificate. Here 4(k-1)<n fails.

Polynomials use the shared ordinary representation:
[coefficient, sorted variable-ID list with repetitions].
Fixture records give every original block, old/joint variable counts,
the weight, and the complete coefficient substitution.
Old Boolean generators are x_i^2-x_i in increasing old-variable order.
Every certificate's cofactor array uses that order.
Control records give all coordinates equal to one; other old coordinates
are zero.

## Row-linear coefficient duals beyond the bit width

<code>row-linear-cubes.jsonl</code> checks every coordinate-direction
multiset on six, seven, or eight rows with ell=5, n=32:

| Rows | Multisets | Product tuples |
| --- | ---: | ---: |
| 6 | 210 | 13,440 |
| 7 | 330 | 42,240 |
| 8 | 495 | 126,720 |
| Total | 1,035 | 182,400 |

These represent all ordered cases up to permutation of pigeon rows.
Each record gives the sorted direction list, chosen coset representatives,
leading coefficient one, and the complete zero parity arrays for all
missing-row indicator functions.
The two points of a line are representative and representative XOR
(1<<axis). Parity indices are cube-product choices with the omitted
row bit deleted. All tuples have distinct labels.

## Exact dimension and degree criteria

<code>hybrid-dimensions.jsonl</code> saves the full integer dimensions,
restriction bounds, and signed margins for four cases:

| n | M | h | D | k | B | Dimension | Degree |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| 2^20 | n | 40 | 81 | 4,096 | 335,872 | pass | pass |
| 2^22 | n | 44 | 200 | 9,216 | 1,852,416 | pass | pass |
| 2^22 | n | 44 | 200 | 1,024 | 205,824 | fail | pass |
| 2^22 | n | 44 | 227 | 9,216 | 2,101,248 | pass | fail |

The worst high rank is h(k+1)+1; any number of lower blocks can use packing.
The second case is beyond 4h+1=177, so this tests inventory-dependent
coverage outside the earlier universal band.

Dimensions are computed by exact binomial recurrences in compiled Boost
integers and stored as full decimal strings. No large input matrices or
polynomial spaces are instantiated. The controls fail different parts of
the stated common NS/PC criterion; they do not construct refutations or
exclude sharper NS-specific accounting.

## Reproduction

Use fresh output paths:

~~~bash
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra \
  research/tools/check_bit_hybrid_learning.cpp -o /tmp/math-bit-hybrid-learning
./compute.sh run TURN --threads 1 -- \
  /tmp/math-bit-hybrid-learning --out NEW_IMAGES.jsonl
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra \
  research/tools/check_row_linear_bit_cubes.cpp -o /tmp/math-row-linear-bit-cubes
./compute.sh run TURN --threads 1 -- \
  /tmp/math-row-linear-bit-cubes --out NEW_CUBES.jsonl
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra \
  research/tools/check_bit_hybrid_dimensions.cpp -o /tmp/math-bit-hybrid-dimensions
./compute.sh run TURN --threads 1 -- \
  /tmp/math-bit-hybrid-dimensions --out NEW_DIMENSIONS.jsonl
~~~

All three tools refuse existing output paths and use no randomness.
No dependency was installed; the Boost integer library was already present.
All compilations and runs passed on the first attempt.
Source, shared ordinary-polynomial headers, this record, and all data are
pinned by <code>provenance.json</code>. Timing and full command outputs are
archived with the session.
