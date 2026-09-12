# Ternary triples and the exact coefficient-degree frontier

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-12-ternary-affine-triples)
contains the universal integer identity, its original-degree certificates, and
the general polynomial coefficient-degree/accuracy frontier over the proper ideal.

## Reproduce the finite discovery and checks

From the repository root with active resource controls:

```bash
./compute.sh run CHECK --threads 1 --category local_processing --timeout 90 -- \
  g++ -O2 -std=c++17 -Wall -Wextra -pedantic \
  research/tools/check_ternary_affine_triples.cpp -o /tmp/check_ternary_affine_triples
./compute.sh run CHECK --threads 1 --category computation --timeout 90 -- \
  /tmp/check_ternary_affine_triples --out PATH-TO-NEW-OUTPUT.jsonl \
  --seed 20260912 --attempts 2000
```

The saved session is `ternary_affine_triples_20260912_52`, with `search-01.jsonl`
in this directory. Output is never overwritten. The program reuses the existing
normal-form and exact NS kernels through `STABLE_IDEAL_NORMALIZERS_NO_MAIN`;
earlier suites are not called and their standalone behavior is unchanged.

Each attempted partition splits the 26 nonzero column states into two sets of
thirteen. Rational linear equations choose a factor vanishing on each set.
All 2,000 attempts are recorded, including partitions, ranks, feasibility,
and both coefficient solutions whenever the pair is feasible.

There were 1,876 feasible covers and 1,707 with power-of-two denominators.
The selected compact cover was attempt 21, score 1022, with ten nonzero scalar
coefficient terms and integer coefficients. Rational arithmetic is exact with
explicit magnitude guards; every feasible system is reconstructed exactly.

## Extracted formula

Old variables are `a1,b1,a2,b2,a3,b3`, at indices 0 through 5. Each pair is Boolean
and mutually exclusive. Let `g_i=a_i-b_i`, `q_i=1-a_i-b_i`, `eta_i=2a_i-1`.
The two coefficient rows are

```
(q_2, eta_2, 0)
(-q_3, 0, eta_3)
```

The factors are congruent to `q_2*(1-g_1)` and `q_3*(1+g_1)` over the proper column
ideal. Their product is congruent to `q_1*q_2*q_3`, the common-zero selector.
The notebook supplies a degree-four identity for this congruence, degree-five
companion certificates, and sharp degree-eight product Booleanity.

All 27 rational state products were checked. Further exact checks over F3, F5,
and F7 produced 30 complete NS certificates and 81 canonical source models.
Fresh source coefficients occupy indices 6 through 11, one row at a time.
All original companion degrees are five. Each coefficient field image has its
degree-p certificate. Compilation and all mathematical checks succeeded.

## Output and proof scope

State codes use base three: empty, positive cell, negative cell in each column.
Rational coefficient vectors use sparse `[coordinate,numerator,denominator]`
records. Their coordinates are input index j, then constant and the six old cells.
Modular polynomials and NS certificates use the existing `pc_boundary.hpp` format.
The file preserves the chosen vectors, exact factor values on every rational
state, all prime-field certificates, and all source lifts.

The finite computation checks the triple. The general frontier is proved by the
symbolic construction and degree lower bound, not an exhaustive search:

```
odd p: h_min(n,T) = ceil(2n/(2T+1))
p=2:   h_min(n,T) = ceil(n/(T+1))
```

It applies to the proper Boolean/column ideal. Full PHP row equations or other
companions are excluded from the lower-bound claim. Affine and constant maps
preserve NS/PC proof degree; higher coefficient degree T has the stated at-most-T
substitution cost for T>=1.

Two publication requests were rejected by automatic approval review before
execution during this cycle; they were separate from the successful mathematics.
Research and local checkpointing continued while a fresh override question was
pending. `provenance.json`, `timing.html`, and the archived session preserve the
actual source dependencies, outputs, and measured intervals.
