# Signed MOD scalar invariants

11 September 2026. The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-11-signed-mod-scalars)
proves the finite-domain conversions, signed scalar interface, and direct MP
recurrence. It preserves the inherited simulation bound without claiming that
one scalar has small original block support.

## Reproduce

With the shared resource controls active, from the repository root:

```bash
mkdir -p research/tmp
./compute.sh --threads 1 c++ -std=c++17 -O2 -Wall -Wextra -Werror -pedantic \
  research/tools/check_signed_mod_scalar.cpp -o research/tmp/check_signed_mod_scalar
./compute.sh --threads 1 research/tmp/check_signed_mod_scalar \
  --out research/results/signed_mod_scalar_20260911_20/checks-REPRO.jsonl
```

Use a new output path; its parent is created automatically. The accepted run
used GCC 11.4.0, C++17, one thread, exact modular arithmetic, and the unchanged
`pc_boundary.hpp` engine. No dependencies were installed. Compilation and
all checks passed. `checks-01.jsonl` preserves the full 152,741-byte output.

## Exact traces and assumptions

There are nine full PC traces for each p=2,3,5. Variable IDs 0,1,2 are Boolean
x and field-valued y,z. The scalar is u=xy+z-1, of ordinary degree two. The
zero base contains x-1 and z+y-1, with model (1,0,1); the nonzero base contains
x-1 and z+y-2, with model (1,0,2 mod p). These are satisfiable planted systems,
not PHP, and neither supplies u as an old axiom.

The traces include the scalar proof from old equations, both signed MOD value
proofs, all four conversions, a direct degree-two scalar refutation, and the
positive-MOD conclusion extraction weighted by u. The zero-value-to-scalar
conversion is literal for p=2 and uses the degree-2p Frobenius proof otherwise.
The reverse nonzero conversion and the direct scalar-weighted conclusion have
degree 2p in these traces. No optimality is claimed. Every final polynomial,
inference, and ceiling is checked, and every corrupted final line is rejected.

All axiom arrays and lines are saved. Polynomial monomials use
`[coefficient, [[variable_id, exponent], ...]]`; PC rules are a (axiom),
l (linear combination), m (variable multiplication), and line -1 denotes zero.
Domains are x^2-x, y^p-y, z^p-z. Degrees precede field or Boolean reduction.

The missing-domain control uses F9 = F3[i]/(i^2-2), represented by pairs
(a,b) for a+bi. It checks irreducibility and the assignment u=i,v=-i. This
satisfies uv-1 but has 1-u^2=2. Although uv-1 together with u has a degree-two
refutation, the nonzero MOD value is not a consequence without finite-domain
axioms. This distinguishes a required hypothesis from an implementation detail.

The notebook's scalar-support corollary follows analytically from the preceding
cycle's saved family-omission assignments. That historical suite was not rerun.
These local traces do not mechanically compile an arbitrary Frege proof.

## Provenance and timing

`provenance.json` hashes the checker, shared engine, and full output. The proof
uses the notebook's earlier weighted replay, domain division, and inherited
copy interface; no new source paper was read or downloaded.

`timing.html` is embedded in the notebook. Initial preparation includes the
previous checkpoint's archival, public-history audit, and authorized push.
Mathematics includes the conversion and recurrence proofs and notebook drafting;
coding was marked separately. No unrelated suite or rendering build ran.
Full command evidence is archived under
`research/provenance/session-records/signed_mod_scalar_20260911_20/`.
