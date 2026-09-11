# Polynomial coefficient normalization

Research date: 11 September 2026. Timing session:
`polynomial_normalization_20260911_04`.
The full statements, proofs, scope, and timing table are in the
[notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-11-polynomial-normalization).

## Results and evidence

- `checks-01.jsonl` contains the complete focused computation: 16 ordinary
  polynomial identities over primes 2, 3, 5, 7 with n = 1, 2, 4, 7;
  112 companion images, including added column forms; 16 field identities;
  and 32 controls omitting necessary collision or Boolean terms.
- Every partial matching of size q < 4 on the five-by-four board has a saved
  near-matching witness. Counts by q are 1, 20, 120, 240, for 381 total.
  These are row/input models with one column collision, not models of PHP.
- For the saved binary seven-hole spread, all seven spaces exclude affine
  coefficient normalizers with degree-two base certificates. Each augmented
  original-axiom space has rank 1,296 in 1,401 normalized monomial coordinates.
  Each saved separating functional was checked against all 1,824 original
  generators. A nonconstant-coordinate corruption was rejected in each case.
- The base degree-two space has rank 420 and affine part of dimension eight,
  exactly the row span. The saved base basis certifies closure under degree-two
  PC inference; this is not an unexamined identification of PC and NS spaces.
- All 28 collision-pair spaces on this board pass the same matrix routine as
  positive controls.

The general substitution and collision-pair theorems have separate mathematical
proofs. The spread result concerns T = 1, c = 2 in that theorem, with no matching
restriction. It does not exclude affine coefficients with larger base proof
degree, higher-degree coefficients, multiple factors, or direct companion
annihilation. The duals are degree-two designs for the auxiliary base-plus-input
systems, not the full ENS systems.

## Reproduction

From the repository root, with the documented resource controls active:

```bash
mkdir -p .resource-runtime/bin
./compute.sh --threads 1 c++ -std=c++17 -O3 -Wall -Wextra -Werror \
  research/tools/check_polynomial_normalization.cpp \
  -o .resource-runtime/bin/check_polynomial_normalization
./compute.sh --threads 1 --timeout 120 \
  .resource-runtime/bin/check_polynomial_normalization \
  --inputs research/results/restriction_resistant_spread_20260911_03/certificate-01.jsonl \
  --out research/results/polynomial_normalization_20260911_04/checks-REPRO.jsonl
```

Use a new output path: the checker refuses to replace existing results.
The accepted run used GCC 11.4.0, C++17, exact modular polynomial arithmetic,
and binary Gaussian elimination. No randomness or external libraries are used
in this new computation. Its spread input was generated earlier with the seed
documented in the preceding result record.

The first compilation failed on misleading-indentation warnings treated as
errors. The warnings were fixed; the next compilation and the full computation
passed. Complete measured command output is archived with this session.

## Data encoding

The source reader accepts the compact `accepted_space` records written by
`find_restriction_resistant_spread.cpp`; it is a reader for that fixed producer
schema, not a general JSON interface. It requires exactly seven indexed spaces
with 24 binary words each.

Polynomial terms have the form `[coefficient, [variable_ids]]). The sorted ID
list is a monomial with repetitions, not a set: repeated IDs retain powers.
Variables use row-major indexing `i*n+j`, with zero-based rows and columns.
These coefficient identities are checked before Boolean reduction.

Matching records use row/column pairs and a bit word for the Boolean assignment,
again in row-major order. Each row has one assigned hole. The recorded unmatched
pair shares one hole, and deleting its second pigeon leaves a permutation.

For the degree-two computation, the `degree_two_base` record gives the entire
monomial coordinate map. `[-1,-1]` is the constant, `[v,-1]` is a variable,
and `[u,v]` is a surviving quadratic product. Boolean squares reduce to their
variables and distinct-row products in one column reduce to zero. Same-row
products in distinct columns remain.

Binary vectors are arrays of hexadecimal 64-bit words, in increasing word order;
bit j represents coordinate j. The last word is zero outside the stated width.
Base echelon rows, their pivots, and all seven dual vectors are retained.
The saved affine inputs use bit 0 for the constant and bit 1+v for variable v.
The 1,824 dual checks are ordered as eight row equations and their 56 variable
multiples, then 24 block inputs and their 56 variable multiples.

## Provenance and timing

`provenance.json` records SHA-256 digests and byte sizes for the checker,
its accepted output, and the exact preceding spread certificate used as input.
The input mathematical construction is recorded at notebook anchor
`resistant-finite-certificate`, committed in `97d5acd`.

`timing.html` is the measured export embedded in the notebook. The interval
includes development of a candidate first considered in the preceding cycle,
the user-requested publication-policy clarification, and context restoration
after compaction. Command failures are operational events, not failed proofs.
The session archive preserves the full timing journal and command output.
