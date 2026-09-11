# Distribution refinement and source support audit

Recorded 11 September 2026. The full statements, proofs, and qualifications are
in [the notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-11-distribution-refinement).
This refines the existing DIST-H identity; it does not claim a new identity.

## Reproduce

From the repository root, with the resource controls active, use a fresh timing
session and output path:

```bash
./compute.sh start distribution_repeat
./compute.sh run distribution_repeat --threads 1 --category local_processing -- \
  c++ -std=c++17 -O2 -Wall -Wextra -Werror -pedantic \
  research/tools/check_distribution_refinement.cpp \
  -o research/tmp/check_distribution_refinement
./compute.sh run distribution_repeat --threads 1 -- \
  research/tmp/check_distribution_refinement --out research/results/distribution_repeat/checks.jsonl
```

The checker refuses to replace an output. No random seed or external library is
used. Arithmetic is exact in F2 and F3. `checks-01.jsonl` contains the complete
polynomials, certificates, assignments, original-degree budgets, and controls.
Polynomials are arrays `[coefficient, [variable IDs with repetitions]]`; all
coefficients are reduced modulo the stated prime. A factored block record gives
its complete inputs and coefficient assignments without expanding a root that
is immediately specialized. The Frobenius helper computes q^p by multiplying
each monomial's exponents by p; it is checked against ordinary powering on small
polynomials, and every saved domain certificate is reconstructed exactly.

Seventeen local cases vary accuracy one/two, OR-headed or doubly-negated B,
OR-headed or non-OR C, and one higher-degree A. The last case uses
`a=(x0^2+x1)^2` in F3. Two recursive accuracy-two cases normalize the inner
distribution instance before using it in another one. The inner assigned prefix
of degree seven exceeds the inapplicable fresh-prefix ceiling six; its weighted
bound still fits. All accuracy-two image budgets and recursive weighted bounds
pass. Ordinary accuracy-one budget failures and missing-information countermodels
are expected controls, not failed runs. The higher-degree accuracy-one case
separates local admissibility from the proposed weighted-prefix invariant; it
does not disprove all other accuracy-one constructions.

For local fixtures, A uses variables 0 and optionally 1, the B core uses 2--4,
and C uses 5--6; subsequent IDs name the recorded block coefficients. Recursive
fixtures begin with x,y,z at 0--2. Each record supplies its relevant block,
variable, or domain metadata. The final summary records 17 local and two
recursive cases, all passed. Compilation and the timed checker run succeeded.

## Source and scope

The source audit used the personal BIKPRS author-layout PDF, Section 1 and
Lemmas 6.10--6.12, with targeted extracted-text passages at lines 170--219 and
1484--1528. DOI: [10.1007/BF01294258](https://doi.org/10.1007/BF01294258).
The PDF hash is recorded in `provenance.json`; the source is not redistributed.
The source specifies a fixed but unspecified Boolean Frege basis, so the
distribution pattern is not asserted to be an axiom of every such basis.
The highest-OR-layer omission is an analytic support induction for the specified
theorem simulation, not a finite test of arbitrary proofs or repeated elimination.

Earlier notebook dependencies are DIST-H, the hierarchical source-template
normalization theorem, the repaired strict-support leaf construction, and the
inherited signed scalar simulation. The proposed MOD follow-up uses an existing
interpolation identity and must supply its own accuracy-two image certificates.

## Evidence and timing

`provenance.json` hashes this checker, its shared headers, the full result, and
the privately available source PDF. `timing.html` and the archived session at
`research/provenance/session-records/directional_distribution_20260911_24/`
preserve the measured interval and all timed command outputs.

The interval includes finalization of the preceding checkpoint, source reading,
mathematics, coding, checks, and this checkpoint's preparation. Initial proof
formulation was interleaved with source reading. Compaction and restoration
remain in the phases active at the time; no retrospective split is invented.
The actual phase markers separate later code planning and drafting from proof
work. Final archival and Git work after the snapshot are measured in the next
continuous cycle. Two mistyped paths in direct read-only lookups returned no
file; these were navigation errors, not computation or mathematical failures.
