# Old row-linear targets over the first affine ENS level

The [notebook proof](https://kbr.is-a.dev/math-research/#entry-2026-09-14-affine-old-target-freedom)
extends the affine refutation argument to nonzero old row-linear targets.
Leading-row avoidance prevents a Boolean zero divisor, and the signed cube
functional detects the resulting row-linear top-degree monomial even when
other terms are not row-linear.

Finite-dimensional duality then extends prescribed values on the old row-linear
subspace to an annihilator of the full degree-bounded PC consequence space.
Full old moment preservation and independent selector moments are not claimed.

## Reproduce

~~~sh
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra research/tools/check_affine_old_targets.cpp \
  -o /tmp/math-affine-old-targets
./compute.sh run TURN --threads 1 -- \
  /tmp/math-affine-old-targets \
  --moments research/results/affine_clause_lower_bound_audit_20260914_121/cube-dual-moments.jsonl \
  --out NEW_F2_OUTPUT_PATH
./compute.sh run TURN --threads 1 -- \
  /tmp/math-affine-old-targets \
  --moments research/results/odd_prime_affine_source_20260914_122/cube-dual-F3.jsonl \
  --out NEW_F3_OUTPUT_PATH
~~~

Run from the repository root with the resource controls active. Output paths
must be new. Exact C++ field arithmetic and guarded integer counts are used;
no dependencies are installed.

## Evidence and its scope

The two target-controls files preserve:

- Two new target products per field, evaluated against the archived complete
  n=8 and n=32 moment witnesses. The products contain within-row terms, while
  their detected leading terms have one coordinate per selected row.
- Explicit zero-divisor products and their complete old Boolean NS cofactors.
- Two complete selector NS certificates per field, showing a relation to an
  old bit and an old-collision-derived zero selector.
- Four typed selector models per field and a partial-moment assignment that
  violates the known selector relation.
- Three distinct exact dimension comparisons, included in each field output,
  showing why excluded leading rows must be charged.

The archived moment files retain every nonzero moment and every relevant
marginal. This cycle streams them and uses only the matching moments needed
for the new targets; it does not repeat their full marginal suite. Their hashes
are included with the new provenance and checked against their prior manifests.

Polynomials use [coefficient,[variable IDs with repetitions]]. In target
evaluations, bit IDs are row*ell+coordinate. Decoder evaluation uses Boolean
powers and same-row exclusions to obtain matching moments with the required
label bits. Selector examples have separate explicitly displayed variable
spaces and complete local axioms.

The finite selector systems are satisfiable local controls. The dimension cases
are component checks, not numerical PHP lower bounds. The partial-moment theorem
is existential and does not provide an efficient sampler.

All mathematical checks passed. A preliminary compiler indentation warning was
corrected, and the final reader validates the archived support and board parameters.
Source/dependency hashes, full command evidence, and measured timing accompany
the checkpoint.
