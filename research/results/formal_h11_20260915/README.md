# H11 chessboard arithmetic formalization

Completed 15 September 2026 on formal-arithmetic. Target:
`third-party:chessboard-parameter-arithmetic`, extracted from H11 in
`formalization/BIT_PHP_FORMALIZATION_ROUTE.md`. The complete human-readable
statement/proof is in notebook entry
`entry-2026-09-15-lean-chessboard-arithmetic`, claim anchor
`chessboard-parameter-arithmetic`.

## Outcome and scope

`formalization/third-party-claims/ChessboardParameterArithmetic.lean` contains
13 verified theorem declarations under `MathResearch.ThirdParty`. Its only
import is `Lean.Elab.Tactic.Omega`. `chessboardNu` is an explicit natural-number
minimum. The intersection bound uses additive natural arithmetic and supplies
an integer reduced-degree corollary. The file also covers transposition,
induction decrease, zero/one-side boundaries, and the narrow stable range.
No chain/homology theorem is proved or assumed. H12/H13 remain separate.

The full audit passed: six proof files, one statement-only file (H), thirty
audited declarations. All axiom reports use only standard foundations. The
existing sixteen theorem declarations were rechecked under the repository's
full checkpoint policy, not presented as new results. The new thirteen plus
H's proposition give thirty audit entries.

`scope.md` records the target/dependency map before proof writing.
`lean-verification.txt` includes exact theorem types, axiom reports, pinned
versions, build and elaboration output. `provenance.json` hashes the source,
map, and verification report. Full protected command outputs and timing are
archived in `research/provenance/session-records/formal_h11_20260915/`.

## Reproduction

From the repository root, with its pinned toolchain and approved dependencies:

```bash
./compute.sh --threads 2 --category formal_verification bash -c 'source "$HOME/.elan/env"; cd formalization; lake env lean -DwarningAsError=true third-party-claims/ChessboardParameterArithmetic.lean'
./formalization/verify.sh --out /tmp/h11-verification.txt
```

The output destination must not already exist. During this research cycle,
these commands used `--session formal_h11_20260915`, and the full audit used
the committed `lean-verification.txt` destination. Both passed on the first
proof-check attempt. No finite numerical testing was needed for these
universally checked integer statements.

This worktree initially lacked `.lake/`. Protected targeted cache commands
restored the pinned dependencies without upgrades. The first cache request
included nonexistent `Mathlib.Tactic.Omega`; cache reported it and skipped it,
returning success. Lean's core omega import needed no Mathlib module. The
second cache command requested the existing per-claim source paths; their six
local modules have no upstream cache and were built locally by the audit.
These setup warnings are not failed mathematical arguments.

## Review and process

Reviewed the thirteen printed types against the complete notebook statement;
no hidden topological premise or strengthened arithmetic premise appears.
The restriction t<b intentionally selects nonempty intersection boards.
Natural subtraction is used for board sizes, integer subtraction for reduced
degrees. The proof explicitly handles negative required degree and nu=0/1.
The source argument is retained in human-readable form even though Lean's
arithmetic proof automation supplies its own proof terms. No mathematical
discrepancy was identified and no new framework rule was necessary.

Initial rules/source reading preceded instrumentation. The first post-start
resume-reading window used the default preparation phase; it is not backfilled
as separately measured reading. Cache/setup jobs and formal verification have
their own command categories. Final checkpoint work after the snapshot is
outside the instrumented interval.
