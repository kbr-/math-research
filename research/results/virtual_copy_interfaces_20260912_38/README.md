# Copy agreement from conditional value interfaces

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-12-virtual-copy-interfaces)
contains the full local theorem and conditional structural induction.
The uniform bound is max(A*, U*+L, 2L). Completed input-equality polynomials are
multiplied using PC reuse, so their proof cost is not increased at each connective.
The theorem assumes all supplied interfaces over one actual retained system;
it does not select that system or supply a full Frege compilation.

## Reproduce

With the shared controls active, from the repository root:

    ./compute.sh start virtual_copy_reproduction
    ./compute.sh run virtual_copy_reproduction --threads 1 --category local_processing --timeout 120 -- g++ -std=c++17 -O2 -Wall -Wextra -pedantic research/tools/check_virtual_copy_interface.cpp -o /tmp/math-check-virtual-copy-interface
    ./compute.sh run virtual_copy_reproduction --threads 1 --timeout 120 -- /tmp/math-check-virtual-copy-interface --out research/results/virtual_copy_reproduction/checks.jsonl

The output path must be new. Exact C++ arithmetic and the existing PC kernel are
used. A small include guard on the previous OR checker exposes its weighted-unit
engine without executing its main or previous suites. Standalone behavior of
that checker is unchanged. No dependency, environment, or framework rule was added.

## Complete evidence

`checks-01.jsonl` preserves thirty complete PC traces over F2, F3, and F5:
eighteen conditional units, three input-equality proofs, and nine copy proofs.

- Different genuine tuples (x,z) and (y,z), with retained equality x-y=0.
  Conditional units have degree two and the copy proof degree four. Each field
  has four common models, one missing-equality control, and four controls
  omitting individual annihilator companions.
- A genuine accuracy-one product on all eight seven-vertex pebbling inputs,
  compared to virtual value zero on the same tuple. The genuine/virtual unit
  witnesses have degrees four/three; the copy proof has degree seven. The
  virtual witness uses only old variables and the extra input assumptions.
  All 128 old Boolean points per field extend to retained models. Removing any
  one of the eight companions admits a point with genuine value one.
- A genuine product on (x_6,z), compared to virtual zero on (1,z), over the
  consistent positive-pebbling base with the contradictory sink equation absent.
  The linear equality x_6-1 has a degree-three PC proof. Reusing its final line
  gives a degree-three copy proof for the quadratic product. Each field has
  two common models, seven controls removing a dependency of the equality,
  and one control removing the required x_6 times product companion.

Totals are 402 common models and 63 missing-witness controls. Every line is
recomputed and verified, and final-line corruption is rejected. Both build and
mathematical execution succeeded. The structural induction is an analytic proof;
the tests are targeted local certificates, not exhaustive formula verification.

## Schema and provenance

The first JSONL record describes the encoding. Polynomials are arrays of
`[coefficient, [[variable, exponent], ...]]`, with field-reduced coefficients;
the empty array is zero. A proof header supplies all axioms, final line, maximum
ordinary degree, and the number of following line records. Rules `a`, `l`, and
`m` are axiom introduction, linear combination, and one-variable multiplication.
Index -1 denotes zero and is never an extra axiom.

Case records preserve the input tuples and relevant degree costs. Point records
save the full assignment, both values, their difference, and the omitted axiom
index when applicable. Different-genuine fixtures use old x,y,z at 0,1,2. The
pebbling fixtures use vertices 0 through 6; the equality-reuse fixture adds z
at index 7. Fresh coefficient variables follow the old variables in block order.
There is no sampling, truncation, or unrecorded random seed.

`provenance.json` hashes the three checker sources, the shared kernel, complete
new output, this README, and the claim index. Source versions of earlier cycles
remain identified by their original commits and provenance records. The final
timing is embedded in the notebook and full command evidence is archived under
`research/provenance/session-records/virtual_copy_interfaces_20260912_38/`.
Preparation includes the preceding checkpoint's archival, public-history audit,
and push. No previous suite or rendering audit was rerun for this cycle.
