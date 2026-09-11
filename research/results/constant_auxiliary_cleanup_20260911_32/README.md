# Constant propagation through private auxiliary blocks

Research cycle `constant_auxiliary_cleanup_20260911_32`, 11 September 2026.
The full local identities, global composition proof, and limitations are in the
[notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-11-constant-auxiliary-cleanup).
The constant normalizers are instances of the existing modes; this cycle checks
their propagation and integration with the preceding private-ancestor invariant.

## Saved evidence

`checks-01.jsonl` saves twelve exact chains over F2/F3/F5: one, two, or five
parents at accuracy one, and one parent at accuracy two. The initial block is
`P0=P_(x,y)`, with goal assumptions `x=y=0`. Odd parents have inputs `(Pprev,z)`;
even parents have `(Pprev,Pprev)`. The initial goal-relative unit cut makes P0
one. Odd parents then admit product-zero assignments; even parents have all-zero
inputs and admit product-one assignments.

The complete data include all original products, prefix polynomials, companions,
coefficient IDs, current inputs before each cut, explicit constant assignments,
product and companion images, and original/image coefficient field equations.
There are twelve goal-relative unit cuts, eighteen constant product-zero cuts,
and nine all-zero-input unit cuts. Every parent companion image is identically
zero. The initial companion images are the actual goal inputs, not zero axioms.

Each chain has an explicit source NS certificate for `T=x+E_last,first`:
`xP0 + (x Vx)x + (x Vy)y + E_last,first`. The entire assignment maps it to the
degree-one certificate for the goal input x. Both certificates and the check
that the original identity specializes correctly are saved. These are 24
satisfiable target certificates, not PHP refutations or minimum-degree claims.
Twelve common models and twelve missing-x-goal controls check their scope.

Four further cases use `(2,z)` over F3/F5 at accuracy one/two. The correct first
coefficient `2^-1` kills the product and every companion; the all-zero assignment
instead leaves the first companion equal to two while satisfying all coefficient
field equations. These are controls for the assignment, not full companion models.

All compilation and checks passed. No dependency was installed. The preceding
global forest suite was not rerun: its invariant supplies the unchanged
structural argument, and these checks target the newly added image modes.

## Encoding and reproduction

Polynomials are lists `[coefficient, monomial]`; monomials are sorted lists of
variable IDs, repeated for exponents. Coefficients are exact residues modulo the
case prime. IDs 0/1/2 are x/y/z; each block records its fresh coefficient IDs.
NS certificate terms include both the actual axiom polynomial and its cofactor.
Degrees are ordinary collected polynomial degrees; the sparse kernel reports
zero degree for the zero polynomial. No field reduction lowers the ledger.

From the repository root, with resource controls active, choose a new output
path. The checker refuses to overwrite a result.

```bash
./compute.sh start constant_cleanup_reproduction
./compute.sh run constant_cleanup_reproduction --threads 1 --category local_processing -- \
  c++ -std=c++17 -O2 -Wall -Wextra -Werror -pedantic \
  research/tools/check_constant_auxiliary_cleanup.cpp \
  -o research/tmp/check_constant_auxiliary_cleanup
./compute.sh run constant_cleanup_reproduction --threads 1 --timeout 120 -- \
  research/tmp/check_constant_auxiliary_cleanup \
  --out research/results/NEW-constant-cleanup.jsonl
```

Run the executable only after compilation succeeds. The finite chains were
chosen to check sequential propagation without constructing large expanded
high-accuracy products; no asymptotic claim is inferred from their sizes.

## Provenance and timing

The claim-index lookup identified the existing mixed constant and earlier-zero
modes; their exact notebook conditions were consulted. The new global proof
uses the preceding ancestor-private invariant and protected-clause endpoint.
No outside source or historical suite was imported.

`provenance.json` hashes the complete output, checker, and both symbolic headers.
`timing.html` is embedded in the notebook. Complete command evidence is archived
under `research/provenance/session-records/constant_auxiliary_cleanup_20260911_32/`.
Preparation includes the previous checkpoint and initial mathematical planning;
coding also includes initial result interpretation and next-step planning.
These intervals were not retrospectively relabeled. The existing timing guidance
will be refined separately to place planned markers immediately after awaited
checks/checkpoints, before interpreting their output.
