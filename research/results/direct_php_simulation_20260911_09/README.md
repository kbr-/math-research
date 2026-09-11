# Direct PHP theorem simulation and final-boundary removal

11 September 2026. Session: `direct_php_simulation_20260911_09`.
The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-11-direct-php-simulation)
contains the full proofs and limitations.

The balanced source induction derives the PHP theorem's approximation Z without
clause assumptions. Setting the final block's coefficients to zero maps Z to one;
earlier clause certificates justify its companion images at their original
degree 2h^2+3h. One affine substitution also removes the ordinary clause blocks,
preserving the NS degree D0. This avoids the MOD-row prelude. The preceding
template preprocessing combines at LD0. Global elimination remains open.

The notebook also proves the local relative implication identity P_(a,G)->b(1-a).
Its image certificates can exceed original budgets and use same-level cores.
This identity is justified by displayed algebra, with no new finite test claimed.

## Complete evidence

`checks-01.jsonl` contains 16 cases: primes 2, 3, 5, 7; accuracies 1 and 2;
and row widths 2 and 3. It preserves 32 boundary-only NS certificates, 104
combined companion-image certificates, and 156 coefficient-field certificates.
Every certificate is reconstructed as an ordinary polynomial identity and
checked against its original axiom degree. All 32 essential-base omission
controls are nonzero. The final target becomes one in every case.

At h=1, eight cases include a later generic ENS block depending on the final
boundary. Rebuilding it from specialized inputs matches direct substitution for
all 16 companions; leaving them unchanged fails every control. Full original
polynomials, coefficient maps, cofactors, and degree budgets are retained.
These are local clause/boundary checks, not complete PHP refutations or a formal
verification of the source Frege balancing and simulation.

## Reproduction

From the repository root, with the shared controls active:

```bash
mkdir -p .resource-runtime/bin
./compute.sh --threads 1 c++ -std=c++17 -O3 -Wall -Wextra -Werror \
  research/tools/check_direct_php_boundary.cpp \
  -o .resource-runtime/bin/check_direct_php_boundary
./compute.sh --threads 1 --timeout 180 \
  .resource-runtime/bin/check_direct_php_boundary \
  --out research/results/direct_php_simulation_20260911_09/checks-REPRO.jsonl
```

The checker refuses an existing output path. The run used GCC 11.4.0, C++17,
one thread, and the shared exact sparse-polynomial/ENS headers, with degree guard
64. No dependencies were installed.

## Coordinates and certificates

JSONL schema 1. Polynomials are term lists `[coefficient, [variable_ids]]`;
sorted repeated IDs encode powers. Identities hold in the ordinary polynomial
ring over the stated field, before domain reduction.

For width n, variables 0 through n-1 are the row; variable n is the second
collision variable. Put x=x_0 and y=x_n. `base_axioms` is
`[sum(row)-1, x*y, x*x-x]`. Fresh IDs follow for the row, collision, and boundary
blocks. Each saves inputs, product, prefixes, companions, and coefficient IDs.

`boundary_only_axioms` lists row companions, both collision companions, the row
equation, and the collision equation, in that order. Boundary-only cofactor
arrays refer to that list; combined companion and field certificates refer to
`base_axioms`. Certificate degree is the maximum nonzero summand degree.

One removed coefficient per case maps to x; its field image x^p-x has cofactor
1+x+...+x^(p-2) on x^2-x. Other coefficient images are constants and give zero.
At h=1 the later block has inputs `[Z-P, 1-Z*Q]`, where P,Q are the row/collision
products. Its own coefficients remain unchanged. Both original and specialized
blocks and their paired companion degrees are saved. No later-block test is
claimed for h=2.

## Provenance and timing

`provenance.json` hashes the checker, shared headers, accepted output, and the
same locally supplied BIKPRS PDF identified in `research/notes/SOURCE_AUDIT.md`.
This turn read extracted lines 1480-1548: Lemmas 6.10-6.12 and the arbitrary-line
induction in Theorem 6.7(1). The paper's full text is not part of this directory.
Earlier notebook MP, clause, and hierarchical-image proofs were read, not
retested as historical suites.

The interval starts with the preceding checkpoint's finalization and includes
the finalization helper, its two isolated integration checks, a user-requested
context-accounting report, and the finer timing-category trial. That trial began
partway through preparation; earlier mixed intervals were not retrospectively
split. `timing.html` is the measured export embedded in the notebook; the session
archive retains full command output.
