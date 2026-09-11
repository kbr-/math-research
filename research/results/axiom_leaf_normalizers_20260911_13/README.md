# Positive-leaf witnesses and triangular PC pruning

11 September 2026. The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-11-axiom-leaf-normalizers)
contains the complete extraction, transfer proof, and ordinary-PHP accounting.
The resulting family excludes recognized axiom-boundary proper copies of either
sign. General proper arguments and interior schema blocks still remain.

## Reproduce

With the shared resource controls active, from the repository root:

```bash
mkdir -p research/tmp
./compute.sh --threads 1 c++ -std=c++17 -O2 -Wall -Wextra -Werror -pedantic \
  research/tools/check_leaf_normalizers.cpp -o research/tmp/check_leaf_normalizers
./compute.sh --threads 1 research/tmp/check_leaf_normalizers \
  --out research/results/axiom_leaf_normalizers_20260911_13/checks-REPRO.jsonl
```

Use a new output path. GCC 11.4.0, C++17, one thread, exact finite-field arithmetic
through the existing polynomial/domain kernels. No dependencies were installed.
The first compilation failed on two indentation warnings; the corrected build
and every mathematical case passed. No old suites or rendering builds were run.

## Complete output

`checks-01.jsonl` is 32,180 bytes. It contains two nested source fixtures, over
p=2 and p=3, with four extracted leaf witnesses and two degree-growth controls.
Source certificates have degrees 6 and 12, extracted units 3 and 7. All local
and composed companion identities and coefficient field images reconstruct
exactly. The source errors remain nonzero older companions, making omission of
the error invalid. A retained later block changes under the lower substitution.

Every line is a JSON object. Polynomials use terms
`[coefficient, [variable_id, ...]]` with sorted repeated IDs for ordinary powers.
This is the shared sparse-polynomial encoding, not the exponent-pair encoding
used by the separate PC trace engine. No Boolean reduction changes the source
ordinary-degree ledger. Domain records retain the full quotient cofactors.

In each source fixture, x,y are variables 0,1 and are Boolean. Coefficient
variables have field domains r^p-r. Block allocation order is:

| Block | Coefficient IDs |
| --- | --- |
| Inner P0 | 2,3 |
| Canonical a0 | 4,5 |
| Inner P1 | 6,7 |
| Canonical a1 | 8,9 |
| Private lower leaf | 10,11 |
| Private upper leaf | 12,13 |

Complete blocks, axiom/cofactor arrays, local assignments, and composed
assignments accompany each case. Certificate targets are reconstructed before
being written. Typed-domain certificates are also independently reconstructed
by the existing domain verifier; this is not a formal Frege-proof compiler.

The separate growth control uses Boolean x,y at 0,1 and two synthetic blocks
with coefficient IDs 2,3 and 4,5. Each local assignment has degree three; its
composed maximum degree is seven. The final field images have explicit
certificates using only x^2-x and y^2-y. The control rejects substituting the raw
local degree for the composed one. Constant alternative normalizers exist, so
the control establishes no optimality or lower bound for all normalizers.

## Provenance and timing

`provenance.json` hashes the checker, shared kernels, complete output, and the
locally supplied BIKPRS PDF. The paper is private reference material and is not
included in the commit. Targeted reading was Lemmas 6.11–6.12, printed pages
30–31, particularly the stated set of disjunction blocks supplying the leaf
certificate. Earlier notebook transfer proofs supplied the remaining inputs.

`timing.html` is embedded in the entry. Initial preparation includes finishing
and publishing the preceding checkpoint. The coding window includes mathematical
degree analysis and a short source-scope lookup while the checker was being
prepared; it is not a retrospective measurement of pure implementation time.
The final proof and notebook drafting were marked mathematics, and preparation
was used only after the statement and evidence were stable. Full command evidence
is under `research/provenance/session-records/axiom_leaf_normalizers_20260911_13/`.

## Syntax clarification — 11 September 2026, following cycle

The upper two-input fixture uses the substituted projection argument `not not A0`.
Its approximation is still a0, but the wrapper prevents flattening the conclusion
into the outer disjunction. A bare OR argument A0 requires the wider input tuple
handled in [the following entry](https://kbr-.github.io/math-research/#ports-syntax-clarification).
The saved polynomial certificates and degree bounds are unchanged; the preceding
description had left the wrapper unspecified.
