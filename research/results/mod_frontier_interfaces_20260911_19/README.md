# MOD frontier degree and original support

11 September 2026. The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-11-mod-frontier)
proves domain-only MOD Booleanity after polynomial substitution, the common
PC copy ceiling, and a lower bound on the original block support of an unchanged
comparison. The support examples are cheaply normalizable; they do not give an
extension-elimination lower bound.

## Reproduce

With shared resource controls active, from the repository root:

```bash
mkdir -p research/tmp
./compute.sh --threads 1 c++ -std=c++17 -O2 -Wall -Wextra -Werror -pedantic \
  research/tools/check_mod_frontier.cpp -o research/tmp/check_mod_frontier
./compute.sh --threads 1 research/tmp/check_mod_frontier \
  --out research/results/mod_frontier_interfaces_20260911_19/checks-REPRO.jsonl
```

Use a new output path; this checker creates the parent directory if necessary.
GCC 11.4.0, C++17, one thread, exact finite-field arithmetic, and the unchanged
`pc_boundary.hpp` engine were used. No dependencies were installed. Compilation
and every mathematical check passed on the first run. The complete accepted
`checks-01.jsonl` is 1,329,476 bytes.

## Expanded polynomial cases

Seven cases use widths 1,2,3 over F2 and F3, and width one over F5. At width m,
the first m variables are Boolean x_j. They are followed by 2m coefficients
for the left blocks, then 2m for the right blocks, with consecutive coefficient
pairs inside each family. Every block has accuracy one and inputs (x_j,1-x_j).
All coefficients have their Fp field equations. The outputs are
beta = (sum P_j)^(p-1) and beta' = (sum Q_j)^(p-1).

All 24 PC traces preserve their complete axiom arrays, polynomial lines,
ordinary degrees, and inference data. They comprise:

- Seven generic COPY proofs followed by final-line MOD multiplication.
- Seven cheaper aggregate proofs using P_j = x_j P_j + (1-x_j) P_j.
- Seven Booleanity proofs from domain equations alone.
- Three width-one Booleanity proofs after replacing the left first coefficient
  by x times its second coefficient, with no use of the replaced variable's
  own domain equation.

The generic comparison degrees are 4,4,8 for p=2,3,5. The input-unit comparison
degrees are 3,4,8. Domain-only Booleanity degrees are 4,8,16, respectively;
after the nonlinear substitution they are 6,12,24, matching twice the new value
degree. Every trace verifies and rejects a corrupted final line.

Polynomial monomials use the boundary engine format
`[coefficient, [[variable_id, exponent], ...]]`. Inference rules are a (axiom),
l (linear combination), and m (variable multiplication), with line -1 denoting
zero. The formal value degree is measured in the ordinary ring before any
Boolean or field reduction.

## Complete support countermodels

Each expanded case records an explicit full assignment for every omitted left
or right family. All x_j are one. Every non-omitted block has first coefficient
one and second zero, so its product is zero. The omitted family has both
coefficients zero, so its product is one. The checker evaluates all retained
axioms and the comparison polynomial directly; only the omitted family's
companions are excluded. Both output Booleanity conditions still hold.

Eight further cases use widths 8 and 64 over p=2,3,5,7. They record every omission
with the exact same complete factored assignment convention and the two output
values, without expanding the wide polynomial. They cover up to 128 required
original families. There are 26 expanded and 576 factored omission assignments.
These controls certify the stated support phenomenon, not a lower bound against
substitutions: assigning both coefficients one in every block makes every
product identically zero.

## Provenance and timing

`provenance.json` hashes the checker, unchanged shared engine, and full output.
The proof builds on the notebook's earlier COPY identity, PC reuse, and
mixed-domain reduction; no new source paper was needed or downloaded.

`timing.html` is embedded in the notebook. Initial preparation includes the
previous checkpoint's archive, publication audit, and authorized push. Marked
mathematics includes proof review and notebook drafting, with implementation
marked separately as coding. No unrelated mathematical suite or rendering
build ran. Complete command evidence is archived under
`research/provenance/session-records/mod_frontier_interfaces_20260911_19/`.
