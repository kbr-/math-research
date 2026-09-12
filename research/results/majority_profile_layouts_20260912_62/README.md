# Majority profiles and compatible copy layouts

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-12-majority-profile-layouts)
contains the full sampling proof, matching algorithm, parameter ledger, and
conditional NS/PC elimination theorem. The profile hypothesis is not established
for every source family.

## Exact large fixtures

Both cases have 6000 columns, ordinary pigeons 0 through 5999, and distinguished
pigeon 6000. In column j, its class contains it and all ordinary i with
`(i-j mod 6000) < 4500`; the other class is the complement. Raw graph degrees
on both ordinary sides are exactly 4500, so epsilon=1/4 applies.

| p | K | Matching prefix | Remaining side | Residual holes | Minimum sampled degree | Rewirings |
| -: | -: | -: | -: | -: | -: | -: |
| 2 | 613 | 483 | 5517 | 8 | 414 | 26 |
| 3 | 614 | 474 | 5526 | 8 | 415 | 27 |

The prefix matches row i to column i. Saved row and column orders are generated
from seed `202609120062+p` by mt19937_64 and an explicit unbiased rejection-sampled
Fisher-Yates shuffle, rows first and columns second. The full orders are retained;
consecutive K-element groups define the layout. Column group zero is empty.

All 162 group-pair adjacency matrices have both minimum degrees greater than K/2.
The 144 matchings required outside the empty column groups contain 88,344 verified
edges. Every matching is saved and checked as a bijection using allowed edges.
The two source permutations are also checked independently as complete permutations
of the unmatched labels. This is one recorded candidate per field, not a Monte
Carlo estimate of the theorem's success probability.

## Scalar and algorithm controls

The sufficient union bound is checked exactly as
`2*n^2*15^floor(K/2) < 16^floor(K/2)`. Its positive numerator is saved as little-endian
base-2^32 words, and the denominator as a power of two. A bounded small-integer
multiplier supplies the exact comparison without a new library or floating point.

The short-path matcher is exhaustively checked on all 209 four-by-four graphs
with both minimum degrees greater than two. The output includes every graph mask
and matching. Three additional graphs carry explicit Hall-deficient subsets:
one has only the left majority condition, one only the right condition, and one
has minimum degree two on both sides at size five. These are controls on the
sufficient hypotheses, not claims that every other graph lacks a matching.

## Complete projection blueprint

For row group a, left-copy position d, and residual column j, the source cell at
`row_order[a*K+d]` and `column_order[(j+1)*K+pi_a,j(d)]` maps to y_a,j. Other
unmatched ordinary cells are zero. The distinguished row maps to
`q_j=1-sum_a y_a,j` across column group j+1. The prefix has its standard matching
images and group-zero columns are zero. The saved matching arrays specify every pi.

The [universal copy theorem](https://kbr-.github.io/math-research/#column-copy-map)
provides all original-degree base certificates for this combinatorial layout.
The program does not expand or enumerate the enormous original axiom system.
Likewise, local statistic images follow from the verified active-row membership
conditions: the distinguished-class sum is one outside the empty group and zero
inside it; the complementary sum is zero everywhere in these fixtures.

The chosen copy counts are conservative. These finite residual sizes are tests
of the construction, not a claim that the 6000-hole fixtures already contradict
the source simulation's degree. The theorem's comparison is asymptotic and
conditional on its source-profile hypothesis.

## Reproduce

```bash
./compute.sh run CHECK --threads 1 --category local_processing --timeout 90 -- \
  g++ -O2 -std=c++17 -Wall -Wextra -pedantic \
  research/tools/check_majority_profile_layouts.cpp -o /tmp/check_majority_profile_layouts
./compute.sh run CHECK --threads 1 --category computation --timeout 120 -- \
  /tmp/check_majority_profile_layouts --out PATH-TO-NEW-OUTPUT.jsonl
```

The checker refuses to overwrite output. `checks-01.jsonl` preserves every
grouping, matching, scalar bound, graph control, and mapping recipe. It stores
only one local adjacency matrix at a time and streams the output. Compilation
and all checks passed. `provenance.json`, the timing fragment, and the archived
session retain complete evidence.

The initial sampling outline was measured in the preceding cycle. This interval's
opening mathematical phase also includes implementation planning and the initial
filtering argument proposed for the next cycle.
