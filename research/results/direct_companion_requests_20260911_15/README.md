# Direct companion requests and the cost of normalizers

11 September 2026. The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-11-direct-companion-requests)
contains the general NS normalization obstruction, its pebbling consequence,
and all proofs of the small path tradeoff. These are controls on a proposed
normalization inference; they do not prove a lower bound for our PHP problem.

## Reproduce

With shared resource controls active, from the repository root:

```bash
mkdir -p research/tmp
./compute.sh --threads 1 c++ -std=c++17 -O2 -Wall -Wextra -Werror -pedantic \
  research/tools/check_direct_requests.cpp -o research/tmp/check_direct_requests
./compute.sh --threads 1 research/tmp/check_direct_requests \
  --out research/results/direct_companion_requests_20260911_15/checks-REPRO.jsonl
```

Use a new output path. GCC 11.4.0, C++17, one thread, exact arithmetic through
the existing PC engine. No dependencies were installed. Compilation and every
mathematical case passed; no unrelated suite or rendering build was run.

## Complete evidence

`checks-01.jsonl` is 162,500 bytes. It contains the path calculation over
p=2,3,5,7 and the complete binary constant-vector audit. The path has four
Boolean variables x0,...,x3 and five nondomain generators, in order:

```
1-x0, x0*(1-x1), x1*(1-x2), x2*(1-x3), x3
```

The first four axiom indices in each PC trace are Boolean equations; the next
five are the displayed generators or the corresponding ENS companions.
All PC lines and rule parameters are retained. Polynomial encoding is
`[coefficient, [[variable_id, exponent], ...]]`. Zero line index -1 is a zero
contribution, not an additional axiom.

The degree-two dual uses squarefree monomial masks 0,1,2,3,6 with value one and
all other degree-at-most-two masks with value zero. It annihilates every one of
the 13 eligible nondomain rows and the Boolean equations. The explicit affine
NS certificate has degree three. The degree-two PC trace uses final-line reuse;
its deliberate final-line corruption is rejected.

The output also retains the affine coefficient field proofs, the accuracy-three
constant normalizer's domain identity, and the degree-at-most-five positive
antecedent trace. Its Booleanity-only countermodel sets all variables, including
the five fresh block coefficients, to zero: the block product is one, its
Booleanity polynomial is zero, and its first direct companion is one.

The binary audit stores all 16 input-value vectors and a countermodel for every
one of the 1,024 ordered pairs of constant test vectors. Test-vector masks use
the five generator coordinates; assignment masks use the four old variables.
The successful three vectors have masks 3,12,16. The all-field minimum-accuracy
proof uses the seven nonzero Boolean patterns on input coordinates 0,2,4 and
uniqueness of multilinear representation; finite binary enumeration supplements
that proof rather than replacing its all-field argument.

## Source provenance and timing

`provenance.json` hashes the checker, PC engine, output, the historical chapter
used for the encoding/PC proof, and the local Pebbling PDF. The PDF is private
reference material and is not included in this checkpoint.

Targeted source reading checked equations (2.5)-(2.6), Theorem 3.1, Proposition
4.8, and Lemma 4.9 in the previously audited arXiv:2001.02481v1 text. The
single-sink Gamma(1,r) family has Theta(r^3) vertices, standard pebbling price
r+2, and at least that reversible price. The all-field NS correspondence also
holds in the multilinear convention. The existing historical degree-three PC
proof was read at its exact statement and argument.

`timing.html` is embedded in the notebook. Initial preparation covers completing
the preceding checkpoint. Reading includes interpretation; the coding window
also includes proof/degree analysis while preparing the control and considering
the next local-replay question. Final notebook proof writing was marked
mathematics. Full command evidence is archived under
`research/provenance/session-records/direct_companion_requests_20260911_15/`.
