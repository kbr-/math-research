# A residual-size-uniform obstruction to the recorded rank tests

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-13-multiscale-affine-rank)
contains the complete construction, probability bound, degree accounting,
and method-specific conclusion.

For each dyadic rank r<=n, form a class of n homogeneous affine input tuples
of rank r. A single random-coefficient union bound gives an inventory such
that, on every matching residual N>=4*ceil(log2(n+1)), the class with
N/2<r<=N retains its ranks, pairwise-zero intersections modulo rows, and
nonconstant-one spans. There are O(n log n) blocks, fewer than 2*n^2 input
forms, and O(n^4) binary coefficients. This is a refinement of the earlier
fixed-residual resistance construction.

At h>=ceil(log2(n+1)), D>=2h+1, every board usable for the target D<=N/2
lies in that uniform range. The selected class's older optimized ceiling
min(D+n, max(1,ceil(r/h)-1)*D) exceeds N/2.

For the new learning budget B=max(1,k-1)*D+k, stability requires N>=2B-1.
Writing v=N(N+1), this implies

    b_k(v-r) >= (1-k*r/v)*b_k(v) >= b_k(v)/2.

Two selected blocks therefore make the dimension test's left side at least
the whole ambient dimension, so its strict inequality fails for every
feasible k. Improving only the base-quotient lower bound cannot repair this
test, even with the exact quotient dimension.

This does not show that the common vanishing kernel is trivial. Its
dimension can be larger than the lower estimate obtained by adding the
separate restriction ranks. Nor does it rule out richer transformations or
properties of the actual source certificate. No augmented refutation or
essential source-proof family is constructed.

## Complete exact audit

multiscale-checks.jsonl contains:

- Every summand of the subboard/pair union bound, as an integer numerator
  divided by a recorded power of two.
- The exact total numerator and denominator at each tested lower cutoff.
- Every usable residual board and its older optimized degree ceiling.
- Every feasible k and its ambient, restriction, matching, and row-relation
  counts, testing both the two-block inequality and the full criterion.
- Explicit summaries and a failed-sufficient-bound control.

All large integers are decimal strings; all other parameters are integers.
No randomness or floating-point arithmetic is used.

| Original n | Certified existence range | Usable boards | Feasible degree cases |
| ---: | --- | ---: | ---: |
| 64 | 28<=N<=64 | 35 | 66 |
| 128 | 32<=N<=128 | 95 | 262 |

For the criterion audit, h=ceil(log2(n+1)), D=2h+1, and every 2D<=N<=n is
tested. All 130 board ceilings exceed their targets, and all 328 degree
cases fail the new dimension test. The control n=64 with cutoff N_min=8
has a union sum at least one; this enlarged existence range is not certified.
A failed sufficient union bound is not a proof of nonexistence.

These checks evaluate the existence bound and numerical criteria, without
constructing or testing the large affine matrices themselves. The universal
claims follow from the notebook argument. No historical suite was rerun.

## Reproduction and provenance

Use a fresh session and output path:

~~~bash
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -std=c++17 -O2 -Wall -Wextra -pedantic \
  research/tools/check_multiscale_affine_obstruction.cpp \
  -o /tmp/check_multiscale_affine_obstruction
./compute.sh run TURN --threads 1 -- \
  /tmp/check_multiscale_affine_obstruction --out NEW_OUTPUT.jsonl
~~~

Compilation and execution succeeded under the shared CPU and combined-memory
limits. Boost multiprecision was already available; no dependencies were added.
provenance.json pins the checker, complete output, this record, and the earlier
resistance/common-vanishing evidence records. No new external paper was needed.

Initial preparation includes the preceding checkpoint and publication.
The first thoughts about analyzing the actual common vanishing space arose
in this cycle; its mathematical resolution is the next task. The notebook
records the process assessment: the audit rejected the proposed residual-size
shortcut, and the small complete fixtures kept the verification focused.
No additional framework rule was warranted.
