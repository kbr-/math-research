# Agent cost and delegation report, 17 September 2026

A dated snapshot, not live guidance. It records what one long Claude Code session in this
repository cost, what a proof-delegation experiment showed, and the working conclusions.
Prices and plan limits change; check current sources before relying on the figures.

## Setting

- One Claude Code session on Claude Fable 5.1 (medium effort) under a Claude Max 20x
  subscription, about 1 h 45 min wall-clock and 35 min of API time.
- Work done in the session: adapting the repository for Claude Code, triaging preprint
  feedback, and three Lean formalization cycles (`cor:bit-PHP-exponential-parameter-bound`,
  `thm:generic-affine-subspace-consequence-transfer`, and the generic CNF bridge with
  `thm:generic-CNF-affine-DAG-subspace-criterion`).
- By the third cycle the session context had grown to roughly 250 thousand tokens.

## The delegation experiment

Idea tested: the main session (Fable) drafts the exact Lean statements, the dependency map and
the final review; a subagent on a cheaper model (Opus 5) writes the proofs.

Procedure for the generic CNF bridge cycle:

1. The main session wrote the statement file with placeholder proofs and checked that every
   statement elaborates.
2. A fresh Opus subagent was briefed with the task, the model proofs to generalize, the hard
   rules (no statement changes, no `sorry` or axioms, report instead of working around a
   problem), and the exact `compute.sh` command so its builds stayed inside the cycle's
   timing session.
3. The main session compared the verifier's printed theorem types with its drafted statements,
   then wrote the record.

Outcome: all four proofs were completed with no statement, import or helper changes, in two
substantive compile attempts and about six minutes. The first attempt failed on three
elaboration issues, none mathematical. The subagent reported its model as `claude-opus-5[1m]`.
The entry's status line names both producers.

## Measured usage

From the session's `/usage` report after the third cycle (API-equivalent list prices):

| Model | Input | Output | Cache read | Cache write | Cost |
|---|---|---|---|---|---|
| claude-fable-5-1 (main session and forks) | 19.8k | 138.8k | 40.6M | 568.7k | $27.08 |
| claude-opus-5 (proof subagent) | 9.6k | 28.6k | 3.3M | 123.0k | $3.20 |
| claude-haiku-4-5 (web-fetch summaries) | 196.0k | 8.4k | 104.9k | 20.4k | $0.27 |

Total $30.55. The subagent used 121,803 tokens over 38 tool calls. The same report attributed
76% of usage to requests above 150 thousand tokens of context, 7% to forks and 5% to the
general-purpose (Opus) subagent.

Plan limits after the whole session: 11% of the five-hour window, 6% of the weekly all-models
limit, 7% of the separate weekly Fable limit.

List prices per million tokens at the time
([pricing page](https://platform.claude.com/docs/en/about-claude/pricing)):

| Model | Input | Output | Cache read |
|---|---|---|---|
| Fable 5.1 | $10 | $50 | $0.25 |
| Opus 5 | $5 | $25 | $0.50 |
| Sonnet 5 | $2 | $10 | $0.20 |

## Analysis

- The subagent's $3.20 decomposes into about $1.65 of cache reads, $0.77 of cache writes and
  $0.72 of output. It spent much of its effort re-reading modules the main session had already
  read in order to draft the statements.
- The same proof work inside the main session is estimated, not measured, at $3.5 to $4.5:
  each of its tool calls re-reads about 250 thousand cached tokens (about $0.06 per call on
  Fable), while the fresh subagent averaged under 90 thousand (about $0.04 per call on Opus
  despite the higher cache-read price), and Fable output costs twice as much.
- Delegation was therefore roughly cost-neutral. A first assessment based on raw token counts
  called it "no saving"; pricing the tokens and accounting for context size reversed that.
- The cost driver is the main session's context size, not the model tier. Cache reads were
  about $10 and cache writes about $11 of the Fable total.
- Forks inherit the full parent context and model. Two quick side questions asked through
  forks cost more (7% of usage) than the entire delegated proof (5%).
- On this subscription the limits were far from binding, so none of this constrained the work.
  Opus usage counts against the all-models limit but not the separate Fable limit.

## Working conclusions

- Optimize for statement fidelity and the author's time, not tokens. Keep the strongest model
  for statements, proof design and the final type review.
- Start a fresh session (`./start-claude.sh --new`, then Resume) for each large task. Resume
  costs roughly 45 thousand tokens once; a 250-thousand-token session pays that on every call.
  The repository's file-based state makes this safe.
- Late in a large session, run long compile loops or batches of routine lemmas in a fresh
  subagent. Whether it uses Opus or Fable is a quality choice; the saving comes from the small
  context. In a freshly started session the advantage disappears.
- A delegated prover must be forbidden to change statements and told to report blockers; the
  main session must still review the printed theorem types, as `formalization/AGENTS.md`
  already requires.
- Ask short side questions in the main session rather than through a fork when the context is
  large.
- Unattended Spin is the case where limits could matter: usage scales with running time and
  with context size. This was not measured. See the next section.

## Compaction and unattended Spin

Decision: the settings stay as they are (auto-compaction at 550 thousand tokens for both
agents, `/loop` for Spin on Claude). The considerations below are recorded for a later review
after a first real Spin night on Claude.

- A compaction is cheap in tokens and slow in time. It is one model call that re-reads the
  context at the cache rate (about $0.14 at 550 thousand tokens) and writes a summary, followed
  by the Resume reading of roughly 45 thousand tokens; about $1.5 and a few minutes in total.
  These are estimates from list prices, not measurements.
- On cost alone a lower threshold looks attractive: per-call cost falls from about $0.14 at
  550 thousand tokens of context to about $0.06 at 250 thousand, and a cycle makes tens of
  calls. Below roughly 200 thousand the fixed cost and delay of each compaction dominate.
- Cost is the wrong criterion for research. Auto-compaction fires at a token count, not at a
  cycle boundary. The author's experience with long Codex cycles, some over an hour, is that a
  compaction in the middle of a cycle throws the agent off balance and can lose half-formed
  ideas that a length-limited summary does not keep. A lower threshold fires more often and
  almost always inside a cycle, so it would make this worse. The earlier suggestion to lower
  the threshold to 250 thousand is withdrawn.
- The sound reset point is the end of a cycle, when the result is in the notebook, evidence is
  archived and the checkpoint is committed. As far as this session could tell, the Claude agent
  has no tool to trigger compaction itself at that point (Codex was not checked), and `/loop`
  continues one growing session.
- A candidate design, not built: an external loop script that starts a fresh headless session
  per cycle (Resume, one Spin cycle, exit), with a stop file, an iteration cap, backoff after
  abnormal exits, and a log, keeping the 550-thousand threshold only as a safety net. It would
  never interrupt a cycle and would keep context small, at about $1 of Resume per cycle. Open
  risks: headless sessions cannot show permission or flagged-request prompts, so such a
  request ends that session's turn; and whether the notebook alone carries enough sense of what
  has been tried is an untested assumption. One night with the loop, followed by a check of
  the process assessments for repeated approaches, would test it.
- A cheap mitigation for either agent, also not adopted: during a long cycle, append
  intermediate findings and the current line of attack to a working file for the turn, so an
  unexpected compaction loses less.

## Limits of this report

One session, one delegated task, one subscription. The in-session cost of the delegated proof
is an estimate. No quality comparison between models was made beyond this single success, and
the per-model weighting of subscription limits is not documented in the sources consulted.
