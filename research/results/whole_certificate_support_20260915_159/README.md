# Comparison-component boundary compression

The [notebook entry](https://kbr.is-a.dev/math-research/#entry-2026-09-15-comparison-boundary-compression)
contains the full statements, ordinary NS proofs, interface conditions, and
remaining source-coverage obligation.

## Mathematical scope

A same-level component of old-affine ENS products can have its internal union
and equal-flat copy relations represented by Boolean interpolation in its
exposed boundary products. Unrealizable boundary types have complete NS
witnesses through the sum of boundary weights plus one. Internal interpolated
ports cost at most twice that sum.

With one proper retained boundary product, every virtual value is one of
0, 1, P_boundary, or 1-P_boundary. Union ports become constant multiples of
P_boundary^2-P_boundary, so their new witnesses fit the original ceilings.
The affine-in-earlier-selector source grammar is preserved in this case.

The source transfer needs an explicit modular proof and the stated parameter
interfaces. A direct companion or input-prefix use cannot be silently hidden.
All affected later inputs are rebuilt and all retained own field equations
remain present. For multiple boundary products, degree can scale with their
number and later inputs can become nonlinear. No full-source small-boundary
theorem or new unrestricted Frege bound is claimed.

Grouping raw companion contributions was also checked. The actual OR-union
aggregates have cyclic coefficient dependencies, so grouping alone is not a
triangular one-input ENS replacement.

## Reproduction

With an active timing session and the shared resource controls:

    ./compute.sh run TURN --threads 1 --category local_processing -- \
      g++ -O2 -std=c++17 -Wall -Wextra \
      research/tools/check_comparison_boundary.cpp \
      -o /tmp/math-comparison-boundary
    ./compute.sh run TURN --threads 1 --timeout 180 -- \
      /tmp/math-comparison-boundary --out NEW_OUTPUT_PATH

The checker refuses an existing output path. It reuses the existing compiled
sparse-polynomial, ENS, and NS-witness helpers. No dependency was installed.
The first compile and run succeeded.

## Exact output and source data

`boundary-compression-checks.jsonl` uses the repository polynomial encoding:
`[coefficient, [sorted variable IDs with repetitions]]`. Powers remain ordinary
powers until a displayed certificate is used.

For each p = 2,3,5 and h = 1,2:

- The boundary has rank r = 2h+1 and original product weight w = 2h.
- Four affine tuples realize all four value pairs at the chosen outside/inside
  boundary points. Sixteen additional tuples are their ordered unions.
- Every original tuple, coefficient-variable group, accuracy, and virtual
  image is retained. The given product recipe, companion rule g_i*P, and field
  rule r^p-r specify the full original source without expanding unused blocks.
- One complete boundary block and a complete later two-input block are rebuilt.
  Their original formal nonlinear coefficient matrix has rank two; its image
  has rank one. The later port retains ceiling 7 for h = 1 and 18 for h = 2.
- The ordinary NS checks cover 16 unions, 4 copies, 20 Booleanity ports,
  1 later port, and 3 infeasible-type certificates.
- Type witnesses cover positive inconsistency (cost 2w+1), containment
  (cost 2w), and all p coordinate hyperplanes (cost pw).

The result is 264 exact NS certificates and 18 complete retained-system models.
Every target, complete axiom table, cofactor, actual witness degree, original
budget, and model assignment is retained. Pattern-certificate axiom tables are
separate from the one-boundary rebuilt-system tables.

The models include the required coefficient fields, with non-Boolean values
for odd primes. Controls expose a wrong retained-boundary value, a hidden
internal companion use, and a hidden zero-flat/prefix use. Four further
odd-prime models satisfy all fields and later companions while omitting the
boundary companions; boundary Booleanity is nonzero.

These are satisfiable local source controls. They are not finite PHP
refutation or size-lower-bound computations.

## Review and dependencies

The proof reuses the complete OR-prefix identities, ordinary Boolean division,
the explicit modular source interface, and its Boolean-parameter templates.
The review checks:

- affine zero-set feasibility over F_p, distinct from feasibility in the old
  PHP base or just on the old Boolean cube;
- the W+1/W type-certificate bounds and the retained boundary Booleanity;
- literal preservation of boundary values under interpolation;
- the difference between parameter uses and genuine prefix/companion uses;
- level-order reconstruction of later products with one degree scaling;
- original weighted cofactor and witness ceilings, without resetting them
  to smaller collected image degrees;
- the binary scope of the full Frege-source application.

`check-metadata.json` records the focused review and saved-output checks.
`provenance.json` hashes this note, checker, relevant helpers, full output,
and metadata. Timing and complete command outputs are archived under the
session label.
