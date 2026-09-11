# MOD recursion at accuracy two

Recorded 11 September 2026. Full statements and proofs are in
[the notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-11-mod-accuracy-two).
The earlier MOD interpolation identity is reused, not claimed as new. The new
results are the earlier-zero mode, simultaneous six-gate removal at accuracy
two, and the smaller complete-axiom certificate for this specialization.

## Reproduce

From the root, with resource controls active and a fresh session/output path:

```bash
./compute.sh start mod_two_repeat
./compute.sh run mod_two_repeat --threads 1 --category local_processing -- \
  c++ -std=c++17 -O2 -Wall -Wextra -Werror -pedantic \
  research/tools/check_mod_accuracy_two.cpp -o research/tmp/check_mod_accuracy_two
./compute.sh run mod_two_repeat --threads 1 -- \
  research/tmp/check_mod_accuracy_two --out research/results/mod_two_repeat/checks.jsonl
```

The checker creates the result directory, rejects an existing output, uses no
randomness or external libraries, and performs exact finite-field arithmetic.
The complete accepted `checks-01.jsonl` is 919,894 bytes. All 247 NS certificates
are reconstructed from the recorded axioms, and their degree bounds are checked.
All selected coefficient field equations specialize to zero.

Seven full six-gate cases use:

- Independent formal t,a over p=2,3,5,7, with t field-valued and a Boolean.
- p=3, t=x^2+y and a=1-z, with x,y field-valued and z Boolean.
- p=3 with a identically zero or one.

Four cases keep an accuracy-two argument block of width one or two over p=2,3.
They check its explicit earlier-companion Booleanity proof, the inner packed
gates, the forward earlier-zero assignment, and a further packed consumer.
Retained-system models realize argument values zero and one. Unit assignment
to the forward gate is shown to violate a direct companion, despite trivial
Booleanity of that unit product. These are satisfiable controls, not PHP
refutations. Three odd-prime points falsify the forward claim without argument
Booleanity; four explicit points falsify it without the inner packing relation.

The full formal-variable axiom image has degree 5,10,18,26 for p=2,3,5,7.
All six gate image budgets fit their original degrees. These are checks of the
polynomial identities and ledger, not an implementation of an arbitrary Frege
compiler or a proof of coverage for all wide argument blocks.

## Format and source dependencies

JSONL case records delimit each example. Polynomials use
`[coefficient, [variable IDs with repetition]]`, with coefficients reduced
modulo the case's prime. The retained-system record gives every axiom in the
order used by the certificate cofactor vectors and supplies the scalar input
polynomials. The source-gate records define a complete factored DAG by input
names, original degrees, and fresh coefficient IDs with their constant images.
`one_minus` expression records define negated values. Named gate-image records
give the expanded specialized products. Removed-variable slots in model arrays
are irrelevant; the points are models of the recorded retained system.

The source syntax, coherent MOD approximations, and interpolation identity were
read from `#mod-schema-blocks` and `#mod-pruned-polynomial`; the constant-mode
transfer and sharp Booleanity induction from `#mixed-global-modes` through
`#mixed-degree-transfer`. These were already recorded in the notebook at parent
checkpoint `94c810e`. This cycle did not reread or redistribute a source paper.
The new theorem explicitly excludes unaligned occurrence copies and arbitrary
input-basis or polynomial-normalizer compositions without their own ledger.

## Timing and provenance

`provenance.json` hashes the checker, its three shared headers, and the complete
output. `timing.html` gives the exclusive measured categories. The full journal
and command outputs are archived under
`research/provenance/session-records/mod_accuracy_two_20260911_25/`.

The interval includes the preceding checkpoint's archival and authorized push.
Some initial test selection was interleaved with the mathematical argument;
the separate coding phase covers implementation and its remaining design.
One notebook patch attempt was rejected because its hunks were out of order;
the corrected patch applied without changing the mathematics. All timed builds
and computations succeeded. Final archival and Git work after the snapshot are
measured in the next continuous cycle.
