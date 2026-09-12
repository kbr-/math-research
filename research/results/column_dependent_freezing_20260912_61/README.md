# Column-dependent partition freezing

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-12-column-dependent-freezing)
contains the general permutation map, exact fixed-layout compatibility test,
package elimination proof, and discrete-common-refinement construction.

For each residual row a and column j, a permutation of source copy labels sends
each ordinary source row's cell to exactly one copied column. The distinguished
row supplies the complementary occupancy q_j in every copy. Row sums and all
degree-one/two base image certificates survive. Different columns can therefore
freeze different pigeon partitions.

## Complete finite checks

All cases have residual N=3 and no initial matching prefix:

| p | K | Source holes | Source pigeons | Base images | Nonzero NS certificates |
| -: | -: | -: | -: | -: | -: |
| 3 | 2 | 8 | 9 | 369 | 99 |
| 2 | 3 | 12 | 13 | 1105 | 148 |
| 5 | 4 | 16 | 17 | 2465 | 197 |

Total: 3,939 original base images, including 444 nonzero NS certificates and
explicit zero-image records. All images fit their original generator degrees.
The residual N=3 lower bound excludes a degree-two refutation, so these checks
cannot be hidden behind a degree-two base contradiction.

The shifts are v_a=(0,a mod K,floor(a/K)), for a=0,1,2,3, and the copy
permutation is pi_a,j(d)=d+v_a(j) modulo K. The output saves these shifts and
every affine cell image. Polynomial variables are row-major residual y_a,j at
index 3*a+j, using the existing coefficient/exponent-pair encoding.

Each copied column uses the partition into its active source rows and their
complement. Empty columns use the one-class partition. All 36 whole-column
occupancies and all 63 local partition statistics are literal constants.
Membership signatures verify 9, 13, and 17 singleton classes in the respective
global common refinements. This does not freeze every global singleton-class
statistic in every column; individual source cells remain residual variables.

## Complete statistic families

Each case has one accuracy-one block containing its entire local-statistic
inventory: one full-column sum for every empty column and both class sums for
every copied column. All 63 companion and 63 coefficient-field images vanish.
The source inputs are fully specified by saved column indices and row lists.
The standard product and companion formulas, fresh coefficient indices, and
original degrees 1,3,p complete the source definition without a large symbolic
source-ring expansion.

The existing individual-cell and invalid-copy-count controls are checked on
these new maps. The invalid-count point satisfies only residual row equations,
not the full PHP base. The general theorem allows arbitrary permutations and
matching prefixes; these finite fixtures use the stated cyclic shifts and no
prefix. Multilevel package collapse is proved by the already established
constant-assignment argument, rather than an additional multilevel run here.

## Reproduce

```bash
./compute.sh run CHECK --threads 1 --category local_processing --timeout 90 -- \
  g++ -O2 -std=c++17 -Wall -Wextra -pedantic \
  research/tools/check_column_dependent_freezing.cpp -o /tmp/check_column_dependent_freezing
./compute.sh run CHECK --threads 1 --category computation --timeout 90 -- \
  /tmp/check_column_dependent_freezing --out PATH-TO-NEW-OUTPUT.jsonl
```

The checker refuses to overwrite output. `checks-01.jsonl` preserves all maps,
certificates, signatures, and source-family data. All mathematical checks passed.
The shared base checker now accepts optional copy shifts and a family callback;
its default entry point also compiled cleanly, and its historical suite was
not rerun. Its default map and family remain the same.

`provenance.json`, the timing fragment, and the archived session preserve the
full dependency sources, output, and measured work. The initial permutation
outline was measured in the preceding cycle; this interval also includes the
preliminary majority-density argument proposed for the next cycle.
