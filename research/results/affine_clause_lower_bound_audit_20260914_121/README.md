# Second audit of the bit-PHP lower-bound chain

The [notebook entry](https://kbr.is-a.dev/math-research/#entry-2026-09-14-bit-PHP-lower-bound-audit)
rederives complete moment constraints, arbitrary-row-count extension, old PC
closure, a cube-times-residual separating functional, and a separate
ordinary-restriction proof of the needed one-level exclusion at h=3*ell.
The same working Res(parity) size consequence follows from the direct simulation.

## Reproduce the independent moment checks

~~~sh
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra \
  research/tools/check_cube_dual_design.cpp \
  -o /tmp/math-cube-dual-design
./compute.sh run TURN --threads 1 -- \
  /tmp/math-cube-dual-design --out NEW_OUTPUT_PATH
~~~

Use the repository root and active resource controls. The output must be new.
The checker uses standard C++ and exact F2/integer operations, with overflow
guards and no dependency installation. Its moment implementation is separate
from the PC trace kernel used by the preceding cycle.

## Complete sparse evidence

cube-dual-moments.jsonl preserves two fixtures:

- n=8, ell=3, k=2, B=4: 284 nonzero moments and 648 nontrivial marginal rows.
- n=32, ell=5, k=6, B=8: 69184 nonzero moments and 299136 such rows.

Each cell is row*n+column. Ordinary monomials are Boolean-reduced; row/column
collisions have value zero. Every unlisted matching moment is zero.
These are zero-normalized annihilator directions, not probability distributions.

Each marginal record gives its multiplier matching, missing row, every
nonzero extension-moment index, and its right-moment index (-1 means zero).
All nonzero moments contribute all faces; all nonzero lower moments contribute
all missing-row right sides. Every omitted marginal is therefore identically
zero. The represented full row systems have respectively 184041 and
1903909999986644001 equations; the program did not enumerate the zero portions.

The file also records all bit-axis evaluations on the selected rows and the
complete failures caused by removing one top moment. Other row-linear basis
elements have value zero by the moment support. The second fixture tests k>ell
and a repeated bit direction on distinct rows.

The finite checks validate the displayed separating functionals and complete
moment constraints. They do not numerically instantiate the asymptotic
size lower bound. Its proof and exact parameter/dependency checks are in the
notebook. No gap was found in this internal audit; external review is not claimed.

All 45,569,198 output bytes, source hashes, timing, and command evidence are
preserved. A preliminary compiler indentation warning was corrected before
the mathematical run.
