# Partial MOD frontiers with an unchanged conclusion interface

Recorded 11 September 2026. Full statements and proofs are in
[the notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-11-partial-mod-frontiers).
The source theorem keeps the complete MP proof, removes covered argument roots
in both antecedent occurrences, and retains a possibly nonconstant MOD scalar.
Its image proofs use conclusion inputs; they are not unconditional old-system
normalizers.

## Reproduce

From the root, with the resource controls active, use new session/output names:

```bash
./compute.sh start partial_repeat
./compute.sh run partial_repeat --threads 1 --category local_processing -- \
  c++ -std=c++17 -O2 -Wall -Wextra -Werror -pedantic \
  research/tools/check_partial_mod_frontiers.cpp -o research/tmp/check_partial_mod_frontiers
./compute.sh run partial_repeat --threads 1 -- \
  research/tmp/check_partial_mod_frontiers --out research/results/partial_repeat/basic.jsonl
./compute.sh run partial_repeat --threads 1 -- \
  research/tmp/check_partial_mod_frontiers --out research/results/partial_repeat/conditional.jsonl \
  --true-arguments-only
```

The checker refuses existing outputs and uses no random seed or external
libraries. The shared PC kernel is `research/tools/pc_boundary.hpp`. All
polynomial arithmetic and verification run in C++ over the specified prime field.

`checks-01.jsonl` contains the first eight cases and 72 complete PC traces.
`checker-first-run.cpp` is its exact source version; compile that snapshot with
the same flags plus `-I research/tools` for an exact first-run reproduction.
The current tool's default covers the same mathematical cases with the additional
argument-mode metadata introduced for the stronger controls.

`checks-02-conditional.jsonl` contains only the two added cases, 18 full traces,
and two verified satisfiable models. The completed first suite was not rerun.
All compilations and computations succeeded.

## Cases, old systems, and controls

Cases 0--7 use p=2,3, with direct input width/accuracy (2,1), (4,1), and (2,2),
plus a width-two, accuracy-one case with earlier-product inputs for each prime.
Direct inputs are old Boolean variables constrained to zero. Earlier-product
inputs are accuracy-one blocks on `(x,1-x)`; summing their two companions proves
their product zero. These systems force the upper products P,Q to one. The
antecedents are positive MOD-zero and negative MOD-one.

These old systems are satisfiable: set direct inputs to zero and coefficients
to zero; in the earlier-product cases set each lower block's second coefficient
to one at original variable value zero, making its product zero, and leave upper
coefficients zero. The first fixtures already have old proofs of the selected
inputs, so they do not by themselves establish essential use of the goal context.

Cases 8--9 are the stronger width-three, accuracy-one controls over p=2,3.
The old base fixes the first selected input and the retained argument's input to
one. Companions then derive P=Q=0. The positive residue is 2 modulo p; the negative
residue is one. The recorded model sets those two old variables to one, the first
coefficient of P, its independent copy, and Q to one, and all others to zero.
Every original axiom vanishes, and every goal input except the first covered
coordinate is zero. That companion's zero-substitution image is one. Thus even
the old system plus all other goal inputs cannot justify the missing image.

The consequent in every case is the disjunction of the first argument and the
negation of the second, with input tuple `(g,Q)`. Q remains a nonconstant ordinary
polynomial after the partial cut. Its zero coordinates, if present in a binary
source expansion with a FALSE child, are unused and omitted. The bypassed grouping
for the first argument in the flattened consequent is not used in the input proof.

Two separate coverage controls use the Boolean model (x,y)=(0,1): a goal tuple
containing only x cannot justify the zeroed y-companion of an `(x,y)` block.
Every main case also checks that zeroing Q would change the named goal input Q
to one. That would be a different interface and is not part of this result.
The fixtures are algebraic source-pattern checks, not PHP refutations or an
arbitrary Frege compiler.

## Proof records and ledgers

Each case records the selected coefficient ranges, retained Q range, source
products, goal inputs, and axiom group indices. Primitive-axiom entries -1 in the
stronger cases mean that no such old input axiom is supplied. Proof records give
the complete axiom arrays and every line. Polynomials use
`[coefficient, [[variable_id, exponent], ...]]`; coefficients are modulo the case
prime. Rules a,l,m mean axiom, two-term linear combination, and multiplication by
one variable. Line index -1 is zero, not an extra axiom.

The 90 traces consist of ten selected-pair copy proofs and twenty each of
antecedent invariants, implication input refutations, full MP joins, and partial
replays. Every ordinary line degree and final polynomial is verified, final-line
corruption is rejected, and cleaned lines contain no removed variables. The
antecedent proof uses no private coefficients from the implication copy; the
implication input proof uses no coefficients from the antecedent-child copy.

`degree-support.json` is the first-run ledger; `degree-support-complete.json`
combines both runs and all four coverage/conditional-image controls. Whole-trace
and final-cone degrees are kept distinct. The small streaming extraction commands
are saved verbatim in the archived journal; they read metadata rather than
recomputing the polynomials. `provenance.json` hashes both checker versions,
their shared kernel, the complete outputs, and both ledgers.

## Dependencies and timing

This cycle extends the learned-input, signed scalar, and expanded private-cut
proofs already available at parent checkpoint `499e952`. The global proof uses
the existing 2L PC copy bound with its actual hypotheses; it does not promote
that ceiling to an NS statement. No new paper audit or site rendering was run.

`timing.html` and the archive at
`research/provenance/session-records/partial_mod_frontiers_20260911_28/`
preserve all measured command records and output. Initial partial-cut formulation
overlapped the preceding checkpoint; later proof writing, implementation, stronger
control design, and final preparation were marked separately. One notebook patch
missed an exact text match and was reapplied in smaller pieces; no mathematical
or computation failure resulted. Final archival and Git work after the snapshot
are measured in the next continuous cycle.
