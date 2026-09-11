# Hierarchical normalization of source templates

11 September 2026. Timing session: `tautology_normalization_20260911_07`.
Full identities, hypotheses, proofs, and scope:
[notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-11-axiom-normalization).

## Scope and complete output

The general proof concerns consistent BIKPRS formula approximations and explicitly
selected block families: ordinary clauses, disjunctions containing complementary
formula occurrences, and the classical implication-distribution pattern.
At uniform accuracy at least four, their supplied earlier-level NS certificates
fit original companion budgets. A single recursively composed substitution has
degree at most the structural approximation bound L and transfers a degree-D
NS refutation through degree LD. Coverage of MOD axioms and arbitrary derived
proof lines is not asserted.

`checks-01.jsonl` preserves the complete focused symbolic computation:

- Eight complementary-disjunction cases over primes 2, 3, 5, 7, with h = 1, 2.
  All 32 expanded companion images vanish identically. Sixteen controls omit
  a necessary product-input or prefix coefficient.
- Thirty-six implication-distribution cases: both outer-disjunction choices
  for B and C at h = 1, 2, plus one h = 4 case over each prime.
  The normalizer error is explicitly represented by earlier B companions or
  the Boolean equation for the atomic B. Every error is nonzero as an ordinary
  polynomial, so discarding its certificate is detected.
- Twenty local certificates fit their original factor degree. The other
  sixteen are h = 1 cases whose particular certificates exceed that budget.
  They are valid local identities, not instances of the degree-compatible
  global theorem without further accounting. No impossibility claim about
  other witnesses follows.
- Four two-stage compositions retain the raw and composed coefficient witnesses.
  A removed block's prefix vector becomes its assigned first vector.
  Actual substitution degree is three; the product of raw witness bounds is 18.
  Leaving upper coefficient witnesses uncomposed fails each control.

These are exact polynomial identity checks in small symbolic systems, not PHP
refutations or a formal verification of the general preprocessing theorem.

## Reproduction

From the repository root, with the shared resource controls active:

```bash
mkdir -p .resource-runtime/bin
./compute.sh --threads 1 c++ -std=c++17 -O3 -Wall -Wextra -Werror \
  research/tools/check_axiom_normalizers.cpp \
  -o .resource-runtime/bin/check_axiom_normalizers
./compute.sh --threads 1 --timeout 240 \
  .resource-runtime/bin/check_axiom_normalizers \
  --out research/results/tautology_normalization_20260911_07/checks-REPRO.jsonl
```

Use a new output path; the program refuses to replace accepted results.
The accepted computation used GCC 11.4.0, C++17, one thread, and exact modular
arithmetic. The shared headers are `sparse_polynomial.hpp` and `ens_symbolic.hpp`.
No dependencies were installed.

## Data conventions

JSONL schema 1. Terms are `[coefficient, [variable_ids]]`; a sorted variable list
retains repeated IDs as powers. These are ordinary polynomials before domain
reduction. Every block records its inputs, full product, all prefix coefficients,
all companions, accuracy, and coefficient-variable IDs by factor and coordinate.

The distribution tests reserve five old Boolean variables: A uses ID 0, atomic
B uses ID 1, a disjunctive B has complement inputs 1-x_1 and 1-x_2, and C uses
ID 3 or complement inputs 1-x_3 and 1-x_4. Fresh coefficient IDs follow.
U is the product for inputs (a,b,f), V for (a,g) or (a,1-b), and the outer tuple
is (U,V,a,f). The recorded normalizer coefficients use that outer order.

Each distribution record gives the full error H, its earlier-axiom cofactors
and axioms, and original-degree accounting. Every outer companion image is
represented completely by its recorded input times H. This factorized exact
representation avoids expanding large outer products after the common identity
has already been checked.

The composition records give the full lower source blocks, the upper input
tuple, and both coefficient vectors. The upper block is represented by these
inputs and its accuracy; it is not unnecessarily expanded. All higher-factor
coefficients of a selected block become zero.

## Provenance and timing

`provenance.json` records hashes and byte sizes for the checker, both shared
headers, and the accepted output.
The preceding ordinary-PHP transfer and clause-block arguments are preserved in
commit `aca4bd3`, at notebook anchors `php-transfer-theorem` and
`php-clause-pruning`. The telescoping identity and source approximation
conventions are linked directly from the new notebook proof.

`timing.html` is the measured export embedded in the notebook. The basic
excluded-middle witness was considered while finishing the preceding cycle;
this interval measures its global accounting, extensions, checks, and recording.
The session archive retains the complete timing journal and command output.
