# Explicit affine-bin rank criterion and merge-first packing

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-12-affine-basis-packing)
states the result and proof. The affine-bin extension already existed. This cycle
makes its row count explicit and applies it after equal-span grouping, before
the final packing decision. It does not claim a new universal optimal normalizer.

## Criterion

For a degree-ordered certified Boolean basis of rank r with r_aff affine members,
the bin rule needs max(r-r_aff,ceil(r/2)) rows. Thus r<=2h and r-r_aff<=h suffice.
The product H has W=sum(deg b_j)<=h(delta+1). Degree-adapted input representations
give NS companion-image proofs through W+deg(g_i), within the original degree.
Affine coefficient field images have degree-p domain certificates.

At each level/accuracy, group equal literal spans first and choose the basis from
their actual input union. A retained class fails at least one of the two rank
inequalities. The input Booleanity witnesses must be current and strictly earlier.
The source-derived portfolio supports the level induction; arbitrary systems
would need those hypotheses checked again after lower changes.

## Reproduce

From the repository root with the shared controls active:

    ./compute.sh start affine_basis_reproduction
    ./compute.sh run affine_basis_reproduction --threads 1 --category local_processing --timeout 120 -- g++ -std=c++17 -O2 -Wall -Wextra -pedantic research/tools/check_affine_basis_packing.cpp -o /tmp/math-check-affine-basis-packing
    ./compute.sh run affine_basis_reproduction --threads 1 --timeout 120 -- /tmp/math-check-affine-basis-packing --out research/results/affine_basis_reproduction/checks.jsonl

The output path must be new. The checker uses exact C++ modular polynomial
arithmetic and the existing NS/PC helpers. No earlier suite is called and no
dependency is installed. Both the original build and run succeeded.

## Complete evidence

`checks-01.jsonl` preserves 21 normalizations over F2, F3, and F5:

- Free inputs at (r,h)=(1,1),(2,1),(3,2),(4,2),(3,3), including tight and padded
  affine rows.
- The rank-four mixed basis (x_0,x_1,x_2*x_3,x_4*x_5) at h=2. Its companion
  image bounds are tight, and both source and mapped NS consequences have
  degree twelve.
- The equal-span tuples (x,y,xy) and (xy,x-xy,y-xy), at h=2. The second list
  supplies no affine member, while the union supplies x,y. Exact forward and
  inverse basis matrices and the composed coefficient maps are retained.

All 350 NS certificates include basis/input Booleanity, sharp product Booleanity,
every companion and coefficient-field image, and full original/mapped NS
consequences. The latter consist of product Booleanity terms and a selected
coefficient field equation; their mapped polynomial is nonzero in every case.
For the shared-span case, source degree twelve maps to degree two over F2 and
degree eight over F3/F5. Nonconstant affine field images are actually used in
the composed consequences when available, including the coefficient 2-x.

All 318 old Boolean points of the positive fixtures have saved full lifted
source assignments satisfying the source axioms and the retained old domains.
The mixed negative control uses (x_0,x_1*x_2,x_3*x_4,x_5*x_6) at h=2. Its
required Boolean normalizer function is multilinear of degree seven, above the
affine product ceiling six. All 384 points of its three Boolean cubes are saved.
No coefficient-matrix enumeration is claimed; nonexistence uses the analytic
degree argument. Two odd-characteristic controls show that pairing (x+y,z)
without Booleanity of x+y leaves a nonzero companion, even though coefficient
field images have valid domain certificates.

## Schema and provenance

Polynomials use `[coefficient, [[variable, exponent], ...]]`; the empty array
is zero. Coefficients and basis matrices are reduced modulo the record's prime.
NS records contain complete axiom and cofactor arrays, target, and maximum
ordinary summand degree. Reconstruction checks exact equality and the bound.
Ranks are computed in the ordinary polynomial coefficient space, without
Boolean reduction or floating-point arithmetic.

Each case saves its input matrices, basis, bin groups, exact coefficient map,
variable ranges, product image, and source/mapped degrees. Domain equations
are Boolean for the original variables and field equations for coefficient
variables. Point records are complete. The non-Boolean controls also save their
nonzero Boolean-domain remainder and a valid affine field-image certificate.

`provenance.json` hashes the checker, its reused helper and kernel, complete
output, this README, and claim index. Timing is embedded in the notebook and
full command evidence is archived under
`research/provenance/session-records/mixed_affine_basis_packing_20260912_44/`.
The initial marked reading window includes early planning; no retrospective
split was invented. No rendering or historical-suite rerun was performed.
