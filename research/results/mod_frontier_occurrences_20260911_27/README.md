# Private MOD frontiers in the inherited occurrence schedule

Recorded 11 September 2026. Full working statements and proofs are in
[the notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-11-private-mod-frontiers).
The result integrates the matched frontier rule into the PC simulation. It does
not establish coverage of every wide block or remove every surviving canonical
copy of a selected formula.

## Reproduce

With resource controls active, use a fresh session and output path:

```bash
./compute.sh start private_mod_repeat
./compute.sh run private_mod_repeat --threads 1 --category local_processing -- \
  c++ -std=c++17 -O2 -Wall -Wextra -Werror -pedantic \
  research/tools/check_private_mod_frontiers.cpp -o research/tmp/check_private_mod_frontiers
./compute.sh run private_mod_repeat --threads 1 -- \
  research/tmp/check_private_mod_frontiers --out research/results/private_mod_repeat/checks.jsonl
```

No dependencies or randomness are used. The checker rejects existing output
paths. Graph work and finite-field value checks are implemented in C++.

Sixteen cases combine p=2,3, chain lengths 1,2,7,15, and one/three final OR
arguments of width five. Accuracy is two. A chain alternates matched MOD-to-OR
steps with ordinary MP: a matched consequent is itself an implication whose
right subtree is the next MOD antecedent. Signs and ordinary antecedent shapes
vary. These are conditional MP trees; their leaves are not asserted to be
primitive Frege axioms. They test occurrence bookkeeping and support independently
of source-leaf construction.

The compiled checks verify:

- Descendant closure of the enlarged survivor set and full-syntax sharing only
  among those survivors.
- Removal-time ancestor and retained-axiom freshness for 116 added root cuts,
  plus absence of their variables from the relevant input tuples.
- Intact consequent proper families and every retained OR subtree at each step.
- Literal agreement for all 84 ordinary MP comparisons.
- Exact nonidentity witnesses for 140 new goal-input comparisons, including
  future ordinary interfaces and future MOD frontiers.
- Failure of the sufficient freshness condition after merging each selected
  private root with a retained same-syntax copy.

The PC degree proof reuses the existing 2L copy theorem. No new large PC trace
suite, arbitrary-proof compiler, or rendered-notebook check was run.

## Data and controls

`checks-02.jsonl` is the complete successful run. It records every physical node,
parent edge, origin leaf, coefficient-family tag, cut classification, live step,
input pairing, and field-assignment witness. The first line explains the model
encoding. Node kinds x,n,o,m mean proposition, negation, disjunction, and MOD.
The source OR syntax is binary; its value and input supports use the flattened
maximal non-OR children. Original variable labels, signs, and residues are kept.

For a nonidentity witness, every original proposition value is zero. All
coefficient values are zero except the first coefficient of the named future
family and, when present, one auxiliary family, which are one. The complete second
vector remains zero. The reported two input values differ modulo p. These points
satisfy the variable domains but do not impose companions; they demonstrate that
literal polynomial agreement cannot replace the copy lemma. Twenty-four
witnesses need an auxiliary coefficient.

`summary.json` collects the sixteen case ledgers and totals. The exact small
metadata-extraction command is preserved in the archived session journal. It
reads the final checker output and does not recompute the structural mathematics.
`provenance.json` records hashes of the checker, failed-run snapshot, complete
outputs, and summary.

## Failed attempts preserved

The first compilation failed because four statements triggered strict
misleading-indentation warnings. Splitting the statements corrected them.
The first execution then stopped in the fifth case: its attempted nonidentity
witness varied only one coefficient family, but the selected gate's inputs at
that point were all zero. This was a restricted witness-generator failure, not a
freshness or survivor-closure counterexample. The corrected search may vary one
auxiliary family as well, and all sixteen cases pass.

`checks-01.jsonl` preserves the entire first partial output. Its interrupted final
case is an unfinished JSON line; do not parse it as a successful complete suite.
`checker-first-run.cpp` is the exact executable source for that failed run and
can be compiled with the same flags. The first compile-warning source version
has no mathematical output; its full diagnostics remain in the session archive.

## Dependencies and timing

The inherited live-forest lemma, original hybrid sharing theorem, formula-copy
PC bound, and fresh-frontier corollary were read from the notebook and relevant
checker sources at parent checkpoint `3d124e1`. No new external source audit is
claimed. The working proof distinguishes its larger private-cut plan from the
earlier convention in which every OR below a MOD frame survived.

`timing.html` and
`research/provenance/session-records/mod_frontier_occurrences_20260911_27/`
preserve the measured interval and every command output, including both failures.
Initial cut-plan formulation was interleaved with targeted reading; later proof
writing, implementation, and checkpoint work were marked separately. The previous
checkpoint's archive and push are included. Final archival and Git work after
the snapshot are measured in the next continuous cycle.
