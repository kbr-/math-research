# Profiles for covered mixed auxiliary OR unions

The [notebook proof](https://kbr.is-a.dev/math-research/#entry-2026-09-14-mixed-star-union-profile)
uses one affine core on the old truth bits of selected shared-bit subgroups.
Composed prefixes have cost 6h-2, within the original flattened union weight
h(2h+1), with no degree factor for the number of grouped bottom literals.

Overlapping input positions receive every relevant prefix contribution.
This is a costed source-profile construction, not a raw union-coefficient map.

## Reproduce

~~~sh
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra research/tools/check_mixed_star_union.cpp \
  -o /tmp/math-mixed-star-union
./compute.sh run TURN --threads 1 -- \
  /tmp/math-mixed-star-union --out NEW_OUTPUT_PATH
~~~

Use a new path and run from the repository root with active resource controls.

## Complete evidence

The binary h=2 fixture has three constrained star cores, five pair-bottom
inputs, and two union cores. Its star index sets are {0,1}, {0,2}, and {3,4};
its union tuples are {0,1,2} and {0,1,2,3,4}.

Thirteen ordinary NS certificates preserve all terms for both profiles and
the actual OR relation B012-B01*x2. Original union degree ten and input degree
four remain in the ledger. The setup includes complete retained axioms and
original source products; those products document degrees and are not claimed
to be mapped by a raw coefficient transfer.

Polynomials use [coefficient,[variable IDs with repetitions]]. Profile records
give the original input order and all prefix coefficients. Every axiom reference
in a certificate refers to the setup's retained-axiom list.

All 54 canonical models satisfying the core constraints are retained. Three
additional models isolate a missing overlapping-prefix term, star constraint,
or union companion. An exact negative control removes c*R_a from the corrected
OR certificate and is rejected by the shared NS verifier.

The small star cores have rank two, so these are conditional-profile checks,
not numerical instances of asymptotic high-rank exclusion. The old base is local
Booleanity, not PHP. All checks passed with a clean final compilation.

Source/dependency hashes, complete command evidence, and measured timing
accompany the checkpoint.
