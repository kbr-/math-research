# Complete binary rank-two-bottom source exclusion

The [notebook entry](https://kbr.is-a.dev/math-research/#entry-2026-09-14-combined-rank-two-source-exclusion)
contains the full working argument. A common homogeneous kernel treats
independent quadratic pairs and all needed affine branches simultaneously.
The final coefficient images use only old variables, so selector and
coefficient degrees add. A larger cube-volume multiplier space permits the
resulting old degree n^(3/4) times polylog(n).

This covers the complete binary two-level source with proper rank-two affine
bottom tuples, arbitrary overlapping parent tuples, polynomial inventory,
and polylogarithmic proof degree, at any common accuracy. It includes arbitrary
raw coefficient uses. Higher-rank bottoms, further nonlinear levels, and the
corresponding odd-prime source class remain open.

## Reproduce

Use an active timing session and resource controls, from the repository root:

~~~sh
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra \
  research/tools/check_combined_quadratic_source.cpp -o /tmp/math-combined-quadratic
./compute.sh run TURN --threads 1 --timeout 180 -- \
  /tmp/math-combined-quadratic --out NEW_OUTPUT_PATH
~~~

The checker uses the already available C++ toolchain and Boost multiprecision
headers. It refuses an existing output path. No dependencies were installed.

## Complete exact evidence

`combined-source-checks.jsonl` contains all original polynomials, coefficient
maps, NS cofactors, and conditional assignments. Polynomials use
`[coefficient,[variable IDs with repetitions]]`; large integers are decimal
strings. Zero entries in the sparse counting tables are implicit.

- A mixed local system contains one high-independent-pair tuple, a
  low-pair pencil with a rank-nine affine branch, and a smaller overlapping
  pencil with a low-rank affine branch. Its squarefree cubic kernel has a
  nonzero Boolean residual in the quadratic ideal representation. An ordinary
  zero-flat restriction detects why that residual cannot be omitted.
- Forty-one weighted source images and one kernel-residual certificate give
  42 complete ordinary NS witnesses. The shared verifier reconstructs every
  target and checks every generator multiple. All source coefficient domains
  are included. The maximum coefficient-image degree is four, the sum of a
  degree-two selector and degree-two affine coefficients.
- All 448 old Boolean assignments with nonzero kernel give complete local
  source models. An unweighted companion fails at a zero-kernel point.
  These are local Boolean-domain models, not models of the PHP base.
- Three complete standard-monomial enumerations check the independent-pair
  quotient and its exact rational bound. In particular, (v,R,k)=(12,6,4)
  gives quotient dimension 473 and homogeneous domain dimension 495.
  Treating the product constraints as an affine flat would incorrectly give
  dimension one.
- The complete truncated degree/weight distribution at n=2048, ell=11,
  k=6 verifies the cube-volume space's dimension and exact Markov inequality.
  It strictly contains the row-cap-two space. Two full cube placements
  include three-axis rows and satisfy the deleted-label bound.
- Exact sufficient parameter inequalities for M=n^2 and D=ell^2 pass at
  ell=128 and 256. At ell=64, the space and image-count conditions pass but
  the old-degree bound fails. Only integer bounds on logarithms and square
  roots are used. The enormous symbolic branch inventory is never materialized.

For the last controls, set H=3*ell+ceil(log2(ell))+4, R=ceil(sqrt(v*H)),
and choose the least integer k satisfying both k^2 >= v*(2*ell+2*R+3)
and R*k^2 >= v^2*H. The exact checks 6*k <= n+1 and 192*k <= n ensure
the multiplier-space dimension bound; the remaining inequalities are in the
notebook's finite theorem. The saved values distinguish the passing and
failing parameter regimes.

All mathematical checks passed. Three initial indentation warnings were
fixed before the mathematical run; the final compilation was clean.
Existing matching-moment suites were used as dependencies and not rerun.
The local map, counting, and parameter fixtures check distinct proof
interfaces; they are not one numerically instantiated large PHP proof.

`check-metadata.json` records focused artifact and link checks.
`provenance.json` hashes sources and evidence. The timing journal and full
command outputs are archived under the matching session name in
`research/provenance/session-records/`. Preparation also includes the user's
separately requested publication prerequisites and README checkpoints.
