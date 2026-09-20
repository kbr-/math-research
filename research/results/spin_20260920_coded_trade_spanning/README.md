# Full simultaneous-predicate image at old degree two

This evidence accompanies the notebook's
[coded-trade theorem and simultaneous lift](https://kbr.is-a.dev/math-research/#entry-2026-09-20-coded-trade-spanning).
It checks the whole compatible target space on one bounded board, rather than
only verifying targets constructed from a known higher lift.

The board has three rows, sixteen labels and one predicate on each row:
`f(label) = label & 1`. Old degree-two top moments are extended through degree
three. The robust deletion budget is six; every nonzero affine combination of
the constant and the predicate has at least eight nonzero coordinates.

Reproduce with a fresh output path:

```bash
./compute.sh --threads 1 g++ -O2 -std=c++17 -Wall -Wextra -Werror \
  research/tools/check_coded_trade_lift.cpp -o /tmp/check_coded_trade_lift
./compute.sh --threads 1 /tmp/check_coded_trade_lift --out /tmp/joint-image-ranks.json
```

All arithmetic is exact over primes 2, 3 and 5; there is no randomness. Source
columns are injective ordered triples, enumerated lexicographically. For each
row i, the remaining rows are listed in increasing order, with their injective
label pairs lexicographically ordered. Source marginal equations sum the missing
row. Conditioning equations use the same order and weight that row by its low
bit. The joint matrix stacks ordinary marginals before conditioning rows.

Target coordinates are the three conditioning arrays in that same pair order.
Their constraints first require zero ordinary marginals: target i, fixed coordinate
position (0 then 1), then its fixed label. Cross-contraction constraints follow,
in lexicographic row-pair order (i<j), then the remaining row's label. The i-target
conditioned at j enters positively, the j-target conditioned at i negatively.
These deterministic definitions reconstruct every matrix from the source code.

The largest matrix has 1,440 rows and 3,360 columns, stored as bytes. The output
preserves all exact ranks and complete increasing pivot-column lists, with
zero-based indices. Across all three fields, the ordinary marginal rank is 673;
the joint rank is 1,256; and the target-constraint rank is 137 on 720 coordinates.
Thus actual image and compatible target space both have dimension 583. The
symbolic necessity proof supplies image containment; the rank equality checks
surjectivity. No new dependency, floating-point calculation or large assignment
search is used.

The earlier eight-label dual remains the failed-hypothesis control and was not
rerun. These finite checks are corroboration of the general all-field proof,
not an end-to-end proof-source design or a Frege lower bound.
