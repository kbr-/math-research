# Local modus-ponens composition — 11 September 2026

The full working argument is in [the notebook](../../../notebook.html), entry
`entry-2026-09-11-mp-composition`. It reconstructs the local BIKPRS inference,
tracks exact NS cofactors, and distinguishes augmented PC reuse from the still
unproved elimination of extensions. This directory contains supporting finite
checks, not a proof of a PHP lower bound or of global elimination.

## Reproduce

From the repository root, with the resource controls active and a C++17 compiler:

```bash
mkdir -p research/tmp
./compute.sh --threads 1 c++ -std=c++17 -O2 -Wall -Wextra -pedantic research/tools/check_mp_composition.cpp -o research/tmp/check_mp_composition
./compute.sh --threads 1 research/tmp/check_mp_composition --out research/tmp/mp-checks.jsonl
```

The recorded run used timing session `mp_composition_20260911_01` and wrote
[checks.jsonl](checks.jsonl). Use a separate destination when reproducing so the
accepted output remains intact. No packages were installed. The executable is
scratch output; its source is tracked under `research/tools/`.

## Cases and output schema

All arithmetic is exact sparse ordinary-polynomial arithmetic in compiled C++.
Each monomial stores 32 byte-sized exponents; operations explicitly reject
exponent overflow, more than 32 variables, and more than 500,000 stored terms.
Coefficients are reduced modulo p after each operation; p is at most five, so
integer coefficient multiplication cannot overflow. All jobs also use the shared
resource controls. There is no random seed and no floating-point arithmetic.

The fixed suite has 36 cases:

- p = 2, 3, 5;
- h = 1, 2 for all five case families;
- h = 3 additionally for affine and nonlinear disjunction cases;
- families: disjunction_affine, disjunction_nonlinear, singleton_atom,
  singleton_neg_disjunction, singleton_mod_field.

The nonlinear cases use overlapping input variables; the negated-disjunction
case uses an earlier extension block; the modular case distinguishes a Boolean
original variable from an earlier field variable. These are synthetic algebraic
instances, not PHP instances. Each case checks telescoping, the applicable
ordinary-polynomial MP identity, original-axiom certificate degrees, and the
final-line product bounds used by PC reuse. The Booleanity certificates are
expanded where applicable. No PC proof trace is generated or mechanically
verified: the PC simulation argument is in the notebook.

Each JSONL record is one object:

- The first gives schema version 1, arithmetic, seed, and scope.
- A case row identifies `case`, `p`, `h`, variable count, and the degree envelope
  `L`. It records premise/conclusion degrees, multiplier degree, flattened local
  certificate degree, and the NS/PC ceilings proved in the notebook.
  `identity_residual_terms` must be zero.
- `omitted_correction_residual_terms` must be positive. It counts the ordinary-ring
  residual after deleting one nonzero correction, even when domain reduction
  could conceal the omission. These are 36 negative controls.
- Three `blanket_zero_specialization` rows give a satisfying Boolean-domain
  assignment and the nonzero specialized correction value, one per prime.
- The final summary records case counts and `all_passed`.

The checker ran twice: the second run strengthened the specialization control
to substitute into the actual constructed local correction and verify the full
residual polynomial x-1. Both executions passed. The final JSONL is the second
run's complete output. Compilation and execution logs, including both runs,
are preserved in the archived timing session.

## Source provenance

The exact-source reading used the already imported BIKPRS author-layout copy,
SHA-256 `78fff21cb13fb81d110bcfacba57d9be5a7dbd0ab36e1e1e2e4207fbcb09f4d2`.
Its bibliographic record is DOI
[10.1007/BF01294258](https://doi.org/10.1007/BF01294258). Relevant locators:
Section 1's Frege language/MP convention; Definition 6.1 and Lemma 6.2;
Definition 6.8 (PDF p. 28), Lemmas 6.9–6.12 (pp. 29–31), and the closing proof
of Theorem 6.7(1) (p. 31). These passages were read from the existing local text
extraction; the PDF was not downloaded or re-rendered in this turn. The source
PDF/full text is not included here. See `research/notes/SOURCE_AUDIT.md` for
original provenance and limitations.

Historical local dependencies inspected: Chapter 1's ordinary-ring conventions,
PC reuse and degree-nonincreasing domain reduction; Chapter 7's prefix-pebbling
control and one-block/additive elimination; Chapter 8's nested/core-residual
freshness and supplied-consequence hypotheses. Historical computational suites
were not rerun. The new identities, bounds, and conditional interface are fully
stated and argued in the notebook; none asserts the missing global theorem.

## Timing

[timing.html](timing.html) is the generated table embedded in the notebook.
Raw timing and command evidence are archived in
[the session record](../../provenance/session-records/mp_composition_20260911_01/).
Initial policy and availability reads preceded instrumentation. The final
snapshot excludes subsequent table embedding, archiving, Git, and response
finalization. Overlapping intervals are counted once.
