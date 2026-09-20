# Balanced minimum source: exact certificate controls

The complete proof is in
[`ordering-affine-source-refutation`](https://kbr.is-a.dev/math-research/#ordering-affine-source-refutation).
These finite cases verify its ordinary polynomial identities and original-degree
budgets. They do not test the asymptotic graph-ordering PC lower bound.

The fixed workload has four ordered vertices, a balanced partition tree, and the
four-vertex path as the graph in the no-local-minimum axioms. It checks primes
2, 3, 5 and accuracies 1, 2, with at most 38 variables and ceiling 18. There is
no matrix search, assignment enumeration, randomness, or new dependency.

From the repository root, reproduce using a fresh output path:

```bash
./compute.sh --threads 1 g++ -O2 -std=c++17 -Wall -Wextra -Werror \
  research/tools/check_ordering_minimum_source.cpp -o /tmp/check_ordering_minimum_source
./compute.sh --threads 1 /tmp/check_ordering_minimum_source --out /tmp/ordering-certificates.json
```

`certificates.json` contains 60 complete ordinary NS identities, the original
generator arrays and degree costs, all nonzero cofactors, and the residuals after
removing transitivity contributions. All identities and ceilings pass; every
omitted-transitivity control fails the exact identity. All fresh coefficient
field equations are supplied but unused. Product-prefix identities are also
checked directly while building the blocks.

A polynomial is a list of `[coefficient, [sorted variable ids with repetitions]]`
terms over the case's prime field. `old_pairs` maps each oriented-order coordinate
to its old variable id. Remaining ids are the actual fresh ENS coefficients.
Each certificate cofactor is `[generator_index, polynomial]`; an omitted index
means zero. Reconstruction is exactly `target = sum(cofactor * generator)` in
the ordinary polynomial ring, without implicit multilinear reduction. The
reported ceiling includes each original generator cost plus cofactor degree.

The initial build failed on three misleading-indentation warnings; the corrected
source compiled with all warnings treated as errors before the successful run.
The earlier paper-scope audit and source URLs are preserved in
[`../spin_20260920_PC_inventory_review/sources.json`](../spin_20260920_PC_inventory_review/sources.json).
No third-party full text is distributed here.
