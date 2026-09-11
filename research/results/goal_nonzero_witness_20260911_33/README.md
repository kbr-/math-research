# Proved nonzero inputs and exact product images

Research cycle `goal_nonzero_witness_20260911_33`, 11 September 2026.
The local normalizer bound, opposite-sign source criterion, integration proof,
and scope are in the [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-11-goal-nonzero-witness).
This extends the existing constant-coefficient specialization of the polynomial
normalizer argument to goal-relative witnesses and specialized retained ancestors.

## Complete evidence

`checks-01.jsonl` contains twelve deterministic cases over F2/F3/F5: selected
width 2/4 at accuracy one, width 2 at accuracy two, and one copied-witness case
per prime. Each saves a complete source PC trace and its complete replay, the
embedded normalizer-witness prefix, every axiom image with original/image
degrees, and the supplied companion-image proof line references.

Literal cases use selected inputs `(x,y,...)`, goal `1-x`, and retained parent
`Q=P_(P,z)`. The witness `H=1-x` has degree one. Source degrees are four/eleven;
replayed degrees are three/five. The copied cases use independent earlier
`R_A=P_(t), R_B=P_(t)`, selected inputs `(1-R_A,y)`, and goal `R_B`. The witness
`H=R_A` has a degree-four copy proof. Source and replayed degrees are five and
four. These are explicit trace degrees, not minima.

The first selected coefficient is assigned one and all others zero. In every
case the product image is the actual nonconstant polynomial H. The retained
parent image is `product_u(1-s_u H-t_u z)`, not the expression obtained by
replacing H by zero. The checker verifies that every replayed line is the exact
substitution of its source line, the named goal is fixed, removed coefficients
are absent, and each deliberately corrupted final line is rejected.

Twelve common models satisfy both systems including the goal, with another
selected input equal to one. Twelve further models satisfy the specialized
retained system with the goal omitted, while H and a selected companion image
are one. At the latter points the correct parent is zero and the incorrectly
collapsed parent is one. These controls separate conditional derivability of
zero from being the zero polynomial. The systems are satisfiable local target
fixtures, not PHP refutations or primitive-Frege proof compilations.

All compilation and checks passed. No dependency was installed and no prior
structural or rendering suite was rerun. The global argument uses the existing
private-support invariant; the new computations test witness degree, actual
nonconstant images, and full local PC replay.

## Encoding and reproduction

The checker reuses `pc_boundary.hpp`. A polynomial is a list
`[coefficient, [[variable, exponent], ...]]`. Coefficients are exact field
residues, with ordinary collected degrees; zero has degree -1 in this kernel.
Each source/replayed proof has its own axiom array and line references.
The coefficient ranges are half-open `[first,end)`. The axiom-image ledger maps
original indices to retained indices, using -1 for removed axioms. The supplied
image proofs replace selected companion uses rather than adding those images
as axioms. Witness metadata locates its prefix in the corresponding full trace.

Run from the repository root with the shared resource controls active. Use a
fresh output path; the checker refuses to replace a result.

```bash
./compute.sh start nonzero_witness_reproduction
./compute.sh run nonzero_witness_reproduction --threads 1 --category local_processing -- \
  c++ -std=c++17 -O2 -Wall -Wextra -Werror -pedantic \
  research/tools/check_goal_nonzero_witness.cpp \
  -o research/tmp/check_goal_nonzero_witness
./compute.sh run nonzero_witness_reproduction --threads 1 --timeout 120 -- \
  research/tmp/check_goal_nonzero_witness \
  --out research/results/NEW-goal-nonzero-witness.jsonl
```

Run the executable only after compilation succeeds. All point coordinates are
saved. In missing-goal models the selected coordinates are already absent from
the retained system, so their displayed values have no mathematical role.

## Provenance and timing

The claim-index lookup located the earlier polynomial-normalizer theorem and
complementary-disjunction rule. Their exact hypotheses were read before stating
this goal-relative corollary; no new identity or literature novelty is claimed.

`provenance.json` hashes the complete output, new checker, and reused PC kernel.
`timing.html` is embedded in the notebook. Full command/timing evidence is in
`research/provenance/session-records/goal_nonzero_witness_20260911_33/`.
Preparation includes the preceding checkpoint and its timing-rule refinement.
The planned markers after publication and after the awaited computation moved
interpretation into the mathematical phase before further work began.
