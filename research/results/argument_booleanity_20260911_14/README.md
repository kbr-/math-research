# Flattened projection and isolated Booleanity proofs

11 September 2026. The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-11-booleanity-ports)
contains the full syntax clarification, projection identities, and conditional
degree-preserving PC/NS removal theorem. Coverage of all direct companion uses
in a PHP simulation remains open.

## Reproduce

With the shared resource controls active, from the repository root:

```bash
mkdir -p research/tmp
./compute.sh --threads 1 c++ -std=c++17 -O2 -Wall -Wextra -Werror -pedantic \
  research/tools/check_projection_booleanity.cpp -o research/tmp/check_projection_booleanity
./compute.sh --threads 1 research/tmp/check_projection_booleanity \
  --out research/results/argument_booleanity_20260911_14/checks-REPRO.jsonl
```

Use a new output path. GCC 11.4.0, C++17, one thread, exact modular polynomial
arithmetic. No dependencies were installed. The compilation and all four
mathematical cases passed; no unrelated suites or rendering checks were run.

## Full output and scope

`checks-01.jsonl` is 566,449 bytes. Cases use p=2,3, accuracy h=2, and argument
arity m=3,4. The source-shaped argument is an OR of negated Boolean atoms, so
its input tuple is x0,...,x(m-1); the other argument b is the Boolean atom xm.
Argument coefficient IDs start at m+1, followed by the inner block's IDs.
Each complete block stores its coefficient IDs, products, inputs, prefixes,
and companions. Original atoms are Boolean; coefficient variables have full
field domains, including when p=3.

The original root is stored exactly in factored form as its input tuple and
accuracy, with independent fresh coefficient variables understood. It is not
expanded before immediately substituting its first vector and zeroing the
remaining one. All resulting companion polynomials and certificates are explicit.
Polynomial terms use `[coefficient, [sorted repeated variable IDs]]`; ordinary
powers are retained. Certificate arrays have matching axiom/cofactor indices.

The output includes both the Booleanity-macro identity and the identity obtained
by expanding its argument-companion certificate. It also retains all upper
coefficient field-image certificates with their typed domain exponents.

| Quantity | Ordinary degree |
| --- | ---: |
| Argument product a | 4 |
| Inner product I | 10 |
| Original root product | 22 |
| Root companions before substitution | 32, then 23 for each other input |
| Root image certificates | 14, then 10 |
| Inner image certificates | 9, 6 |
| Argument Booleanity certificate | 8 |

Controls reject applying the unflattened two-input assignment to the actual
wide root. Zeroing the argument coefficients makes its Booleanity polynomial
zero while sending its first direct companion to x0. The saved Boolean-domain
model x0=1, all other old variables zero, separates this direct request from a
vanishing Booleanity request. This is a local satisfiable-domain control, not
a PHP instance or a lower-bound counterexample.

The companion-only access condition is essential. The removal theorem requires
an outer PC proof with isolated Booleanity subproofs, or a supplied outer NS
factorization with those Booleanity polynomials. It does not extract that
interface automatically from arbitrary flattened data. Auxiliary image proofs
must be included in any subsequent global support audit.

## Provenance and timing

`provenance.json` hashes the checker, shared kernels, and complete output. Inputs
were the precise earlier notebook identities and the saved source flattening
convention; no new external source lookup was needed.

`timing.html` is embedded in the entry. Initial preparation covers completing
the preceding checkpoint. A brief overhead window records the publication-review
rejection and the successful retry using the user's existing explicit Spin
authorization. The proof and notebook were completed in the mathematics phase
before final preparation. Full evidence is archived under
`research/provenance/session-records/argument_booleanity_20260911_14/`.
