# Bounded affine probes and actual sums of indicators

The [notebook entry](https://kbr.is-a.dev/math-research/#entry-2026-09-14-bounded-probe-sum-source)
contains the working theorem and its source application. Every input has a
fixed degree bound s and depends on at most r independent affine probes.
High independent-probe groups give a degree-preserving monomial reduction;
the other nodes branch to smaller probe dimension. One common kernel and
one old-only coefficient map handle the complete system.

For fixed r,s and polynomial inventory, the old degree is
n^(S/(S+1)) times polylog(n), with S=sum_j min(s,j).
Actual two-level sources with fixed bottom rank b and at most c bottom-product
summands per parent input have r=bc,s=b. Thus sums of two rank-two indicators
are covered at old degree n^(7/8) times polylog(n). Arbitrarily many summands
or growing probe dimension remain open; degree two alone does not bound
the number of probes.

## Reproduce

From the repository root, with an active timing session and resource controls:

~~~sh
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra \
  research/tools/check_bounded_probe_source.cpp -o /tmp/math-bounded-probe-source
./compute.sh run TURN --threads 1 --timeout 180 -- \
  /tmp/math-bounded-probe-source --out NEW_OUTPUT_PATH
~~~

The checker refuses an existing output path. No dependencies were installed.

## Complete exact evidence

`bounded-probe-source-checks.jsonl` stores ordinary polynomials as
`[coefficient,[variable IDs with repetitions]]`. Large integers are exact
decimal strings; binary matrix rows use the listed column order.

The 522 NS certificates comprise:

- 495 complete reductions of every ordinary monomial through degree four in
  eight variables, pulled back through an invertible affine coordinate
  change with a constant shift;
- one extra ideal-relation certificate whose reduction remainder is
  nonzero, protecting the distinction from a full quotient normal form;
- 22 complete weighted original axiom images for an actual overlapping
  two-level summed-input source, including every coefficient domain;
- four probe-restriction comparisons, including b+cd and 1+cd.

The reduction uses the actual nonfactorable generators
y0*y1+y2*y3 and y4*y5+y6*y7. The full old generators, coordinate maps,
normal remainders, and ordinary cofactors are retained. These generators
construct kernel witnesses; the theorem does not add them to the old PHP base.

There are 120 normal monomials. Their complete evaluation matrix on 100
common-zero points has rank 100; the matrix, RREF, and pivots are saved.
This is a direct control against treating the reduction-image bound as
an exact quotient dimension.

Seven nonzero combinations of three disjoint quadratic sums have support
sizes 1536, 1920, or 2016 on twelve bits, with polar ranks four, eight,
or twelve. Their input span contains no nonzero affine-flat indicator.

The actual source has bottom products ab, cd, ef and parent inputs
ab+cd, ab+ef. Both parent coefficients map to a, and the common weight is
a*(cd+ef). All twelve nonzero-weight old assignments give complete source
models. An unweighted companion fails at a zero-weight point. A separate
expanded-input model refutes the naive map that sums expanded coefficients
to represent one summed input; it is not a universal transfer impossibility.

For r=4,s=2,M=n^2,D=ell^2, exact integer parameter checks satisfy every
sufficient condition at ell=256 and 512. At ell=128, the range, space, and
image-count conditions pass while the old-degree bound fails. The saved
thresholds use integer upper bounds on the logarithms; branch inventories
remain symbolic.

Compilation and every check passed. The local algebra fixtures and large
integer parameter cases test distinct interfaces; they are not one large
numerically instantiated PHP proof.

`check-metadata.json` records focused artifact and new-link checks;
`provenance.json` records source and evidence hashes. Timing and full command
outputs are archived under this session name in
`research/provenance/session-records/`.
