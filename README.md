# Noemesis: a framework for autonomous mathematical research

Noemesis runs an AI agent on an open mathematical problem for weeks at a time and keeps the result
inspectable: every claim has a status, every argument is reviewed by a second agent, selected
results are verified in Lean, and the rules the agent works under are enforced by programs rather
than by its good intentions.

It is a repository, not a service. The research record, the claim registry, the tools and the rules
are ordinary files in Git; the agent is Codex CLI or Claude Code.

**[Read the research online](https://kbr.is-a.dev/math-research/)** · [What it has
produced](#what-it-has-produced) · [How it keeps the record honest](#how-it-keeps-the-record-honest)
· [Limits](#limits) · [Run it](#run-it)

[![Selected notebook excerpts showing the research agenda, a working proof, exact finite checks, and
measured timing.](docs/assets/notebook-preview.png)](https://kbr.is-a.dev/math-research/)

*Selected excerpts from the 13 September 2026 notebook checkpoint, arranged side by side.*

## What it has produced

**A theorem, with a machine-checked proof.** [An exponential lower bound for the bit pigeonhole
principle in resolution over parities](https://arxiv.org/abs/2609.23015) (arXiv:2609.23015, 19
September 2026): a proof-size lower bound for the bit pigeonhole principle in unrestricted DAG-like
Res(⊕), with no regularity or depth restriction. As the paper's abstract states, superpolynomial
size lower bounds were previously known only for restricted refutations (tree-like, regular,
bounded-depth). The main results and their dependencies are formalized in Lean 4; the paper includes
the verification map and reproduction instructions, and the [TeX
sources](publications/bit-php-resolution-over-parities/) and the [formalized
theorem](https://kbr.is-a.dev/math-research/#lean-publication-bit-PHP-superpolynomial) are in this
repository.

The paper's abstract states that the proof "was developed with substantial AI assistance within an
open research framework": this one. By the author's [own
account](publications/bit-php-resolution-over-parities/DEVELOPMENT_HISTORY.md), GPT-6 Astra, working
in Noemesis under a standing goal, was the main contributor to the mathematical development and
drafting; the author's contribution was the design, direction and refinement of the framework. Lean
verification was added because the author could not check the mathematics himself.

**A record you can audit.** As of 11 October 2026, counted from the repository:

| | |
| --- | --- |
| Research-record entries | 2,959 across six notebooks, each dated, with its status, its measured time and the model that produced it |
| Registered claims | 4,382: 3,118 working proofs, 525 finite checks, 277 conjectures, 163 refutations, 121 conditional results, 102 established (imported) results, 59 context items, 17 retractions |
| Claims verified in Lean | 98 complete, 3 partial, in 106 Lean files with pinned Lean and Mathlib |
| Commits | 3,630 since 10 September 2026 |

A *working proof* is an argument written out in full and reviewed inside the workflow. It is not a
formal proof and not a peer-reviewed one; the registry keeps the three apart, and a claim counts as
formalized only when its full statement and every proof dependency is verified.

**The main goal is open.** The first case study asks for superpolynomial proof-size lower bounds for
the pigeonhole principle in fixed-depth AC⁰[p]-Frege systems. The
[notebook](https://kbr.is-a.dev/math-research/) states what is proved, what is not, and what the
next step is. Failed attempts, obstructions and retractions stay in the record.

## How it keeps the record honest

An agent left alone for a day will overstate a result, grow a list of cases in place of a proof,
close a question on a remark, and forget what it promised. The mechanisms below were added as such
failures were observed, and each is a check that runs, not a guideline.

| Risk | What stops it |
| --- | --- |
| A wrong proof is recorded as proved | Near the end of every cycle a [fresh-context reviewer](.claude/agents/medium-reviewer.md) gets only the stable drafts and their dependencies, and tries to break them. An entry whose review is incomplete is recorded as conditional. |
| The agent's account of its own work is not what happened | A second reviewer with no memory of the session reads what the agent wrote while working and lists what the maintainer would object to, each objection with a quote. The next entry must answer each one ([stand_in_review.py](tools/stand_in_review.py)). |
| Entries overstate | The [finisher](tools/finish-turn.py) rejects an entry that does not declare whether the goal advanced, cite the claim that advanced it, or say what the result gives at the goal's own parameters after repeated cycles without progress. |
| Case lists stand in for a general statement | Each entry cites its all-parameter claim. Two finite-check-only entries in a row on a route are rejected, as is a fourth in any five; a finite check needs a paragraph showing it could have failed. The [launcher](compute.sh) refuses a fifth argument list for one program. |
| A line of attack continues from habit | After six research entries a route review is due, and nothing else is accepted. It states the obstacle and names a decisive test the next cycle has to report. Unless the queue of leads is already full, it must bring at least three leads from other areas and two deliberately remote ones, each with a test and that test's outcome. |
| A lead is dropped after one objection | Picked leads wait in a [queue](tools/lead_queue.py) and are developed one at a time. Closing one requires the reason, what a yes and a no would each have given, and which statements of each source were read; a closure resting on an abstract is refused. |
| A result is rediscovered or contradicted unnoticed | Claims live in a [structured registry](research/claims/README.md) with typed relationships (depends on, refines, corrects, supersedes, obstructs). [Search](tools/search-claims.py) is ranked and shows newer versions; registration refuses a new claim that resembles an existing one unless it says how they relate. |
| History is quietly rewritten | The record is append-only: [check-append-only.py](tools/check-append-only.py) compares every earlier entry with the base revision, in the finisher and before a push. Corrections are new dated entries. |
| A computation proves less than it seems | Runs go through [compute.sh](compute.sh): enforced CPU and memory limits, a 30-minute cap, full output saved to disk with its command line, and an estimate required before a long run. The [computation policy](COMPUTATION_RULES.md) requires exact arithmetic for finite-field work and a statement of what a check could have falsified. |
| Context is lost at compaction | After a compaction every tool call is refused until the agent has read the whole [resume bundle](tools/resume.py), delivered in bounded parts. Nothing is kept in machine-local agent memory; a hook refuses such writes. |
| The agent promises to do better | A reply that admits a mistake is sent back until it says what prevents the class of mistake. A promise about future behaviour is sent back too: nothing said in a turn survives compaction, only the framework does. |
| The rules rot | [AGENTS.md](AGENTS.md) holds only rules that apply to every notebook, and a test fails when goal-specific vocabulary enters it. The framework's own suite, 86 test files, has to finish in 10 seconds or it fails. |

These checks have known gaps, listed under [Limits](#limits).

## How a research cycle works

**Restore context → name the open statement → investigate → review → record → answer the reviewers →
assess the process → commit → repeat**

- **Restore.** The agent reads the living sections of the notebook: where the work stands, the open
  statements whose conjunction gives the goal, the remaining route with the highest risk first, and
  the proposed next step.
- **Name the obligation.** A cycle opens by stating the missing implication it attacks, how the work
  tests it, and what evidence would end the test. Before proposing a lemma the agent searches the
  registry for it, under its synonyms and its dual formulation.
- **Investigate.** Proof attempts, and computations under the protected launcher. Installed algebra
  systems (Macaulay2, Singular, msolve, GAP, PARI/GP, SageMath and others) and exact linear-algebra
  libraries are preferred to hand-written kernels.
- **Review.** One fresh-context reviewer per cycle, at a fixed reasoning effort, checks correctness,
  then proposes a way past the cycle's open point and audits how the work was done. Its suggestions
  are recorded as unverified leads.
- **Record.** A dated entry with assumptions, the precise claim, the complete argument,
  dependencies, checks and measured time, including when the outcome is an obstruction or nothing at
  all.
- **Assess the process.** Each cycle says what cost time or went wrong and what now prevents it.
  Framework fixes are committed separately from the research.

The [Spin prompt](PROMPTS.md#spin) runs this loop under [AGENTS.md](AGENTS.md) until the notebook
records the goal as proved. A checkpoint is never a stopping point, and the next step is always
research: the loop may not park the goal or wait for the maintainer.

### Formalization

Formalization is requested, never automatic. On request the agent maps a claim's statement and
dependencies, writes per-claim Lean files, and verifies them: an incremental build with warnings as
errors, each declaration's type and axioms checked, only `propext`, `Classical.choice` and
`Quot.sound` allowed, no `sorry`, never `native_decide`. Large computations enter as certificates
checked in the kernel. Formalization feeds back: the notebook's [Gaps identified by
formalization](https://kbr.is-a.dev/math-research/#formalization-gaps) lists missing hypotheses and
wrong statements it exposed. See the [formalization rules](formalization/AGENTS.md) and
[guide](formalization/README.md).

## It changes through use

The framework's rules were not designed up front. Each one records a correction, with its date and
often the maintainer's words, and the correction is turned into a program where one can exist. In
the four weeks after 13 September 2026 the framework itself received 474 commits: the tools grew
from 7 to 75, the test files from a handful to 86, and the hooks from none to 11.

Three examples of a correction becoming a check:

- Runs of 20 minutes and more were started without an estimate. The launcher now requires an
  expected time for a long run and a measured smaller run of the same program to extrapolate from.
- A required route review went unnoticed because a tool's output was truncated. A hook now refuses
  to pipe or filter the output of the commands whose guidance must be read in full.
- Rules about one research goal accumulated in the general rules file. A test now fails on such
  vocabulary, and each notebook carries its own route decisions.

## Limits

- **The main goal is open**, and most of the record is working proofs: reviewed inside the workflow,
  not formalized and not peer reviewed. Treat an unformalized claim as a careful draft.
- **The reviewers are models.** They miss things, and they share blind spots with the agent they
  review. Checked against two days of the maintainer's own corrections, the second reviewer made the
  same point for 4 of 18 in one session and 2 of 12 in another, and those figures are upper bounds.
  Of ten of its other objections sampled in each session and checked against the record, seven and
  eight held, and one or two misread the text.
- **A finite check is a finite check.** The registry keeps them apart from proofs, and the rules
  above exist because the pull toward more cases is constant.
- **The checks enforce form, not truth.** The finisher verifies that an entry declares its progress
  and cites its claim; whether the assessment is right is for the reviewers and the reader.
- **One environment.** The protected launcher needs Linux with cgroup v2 and a user systemd manager.
  Its resource profile (CPUs 0–13, 10 GB) is fixed in the code for the 16-CPU machine its controls
  were validated on; another machine needs those constants changed. The framework has been used with
  Codex CLI and Claude Code only.
- **Cost.** Long autonomous runs are expensive; see the [agent cost
  report](docs/agent-cost-report-2026-09-17.md).

## Read the research

The **[published notebook](https://kbr.is-a.dev/math-research/)** needs no setup or account. Start
with its living overview, then follow claim links into the full record and the evidence. Side
notebooks, each with its own goal and record and sharing the claim registry, are listed on every
page.

### Browse locally

```bash
git clone https://github.com/kbr-/math-research.git
cd math-research
python3 server.py
```

Open **http://localhost:8000** (`--port 8001` if it is occupied). MathJax loads from a CDN, so the
browser needs internet access. When the notebook's source changes, the page offers a reload.

Mathematics is rendered near the viewport only, and off-screen entries defer layout while staying
available to browser search and anchor links; see the [performance
measurements](research/results/notebook_performance_20260920/README.md). **Search notebook** (or
`/`) searches all prose and the original TeX, in this notebook or all of them, including equations
not yet rendered. It is literal search with whitespace normalized, not symbolic equivalence; **Match
case** distinguishes `\Gamma` from `\gamma`.

The published site is built by GitHub Actions when notebook or site-tooling changes reach `main`.

## Run it

Clone the repository, install and authenticate Codex CLI or Claude Code, and initialize the
[computation controls](#computation). Browsing the notebook needs none of this.

Research with this framework has been run with **GPT-6 Astra** in Codex and **Claude Opus 5 and
5.5** and **Claude Fable 5.1** in Claude Code, at various reasoning settings. Each entry credits the
model and setting that produced it.

### Sessions

```bash
./start-session.sh        # Codex
./start-claude.sh         # Claude Code
```

Both launchers start or reuse a background session, attach the terminal to it, and leave it running
when the terminal closes. On a fresh clone the session restores its context from the committed
files; later launches resume the session recorded locally. `--new` starts and binds a fresh session,
`--resume` requires an existing one, `--detached` does not attach. Session IDs, chat history and
credentials are never committed.

- **Codex.** `start-session.sh` works in a persistent Git worktree (`--worktree NAME`, `--base
  BRANCH`), attaches over the daemon's Unix socket, and refuses to start when the framework's hooks
  are missing or untrusted. `start-codex.sh` starts the daemon alone. For phone access, run `codex
  remote-control pair`. Details are in the [Codex guide](tools/CODEX.md).
- **Claude Code.** `start-claude.sh` runs the session in the background with Remote Control, so the
  terminal and the Claude app can use it at once. [CLAUDE.md](CLAUDE.md) imports
  [AGENTS.md](AGENTS.md); the tracked [.claude/settings.json](.claude/settings.json) registers the
  hooks and pre-approves routine framework commands.

Context and auto-compaction budgets come from each harness's own settings.

### Automatic research

A goal keeps the agent working across turns. After restoring context:

```text
/goal Execute the Spin prompt in ./PROMPTS.md until the notebook's goal is proved or I say stop; a commit or push is never completion.
```

State when the loop ends: Claude Code's `/goal` judges the condition from each turn's last message,
and a bare `/goal Spin` was once judged achieved after a checkpoint report. In Claude Code, `/loop
Execute the Spin prompt in ./PROMPTS.md.` is an alternative.

Publishing is by explicit grant only. For local work, append: "Stay on the current branch, commit
locally, and do not push."

### Named prompts

[PROMPTS.md](PROMPTS.md) defines **Resume** and **Dump** (restore and save context), **Spin** (the
research loop), **Branch** (open a [side notebook](tools/SIDE_NOTEBOOKS.md) with its own goal),
**Formalize**, **Spin-formalize** and **Spin-formalize-parallel** (one claim, a set of claims, or a
large theorem split across worktrees), and **Fossick** ([screen the record](tools/FOSSICK.md) for
results worth publishing).

```text
Execute the Formalize prompt in ./PROMPTS.md against claim lem:mp-telescoping.
```

## Computation

Python 3.10+ is required. The notebook server, resource controller and timing tools use only the
standard library; the browser tests need Node with Playwright, and the Codex runtime client needs
`websockets`. [requirements-research.txt](requirements-research.txt) records the numerical libraries
used. An agent installs nothing without approval.

The protected launcher requires **Linux, cgroup v2, a user systemd manager and a C compiler**. Its
profile is CPUs 0–13 and 10 GB of RAM plus swap combined, shared by all jobs; a watchdog kills the
group above that, and unsupported controls fail closed ([details](resource-controls/README.md)).

```bash
python3 resource-controls/setup.py      # after reboot or login; installs no packages
./compute.sh --status

./compute.sh start turn001              # prints what this cycle's entry must contain
./compute.sh run turn001 --threads 1 -- python3 calculation.py
./tools/finish-turn.py turn001          # after drafting the entry with <!-- TIMING turn001 -->
```

`start` prints the cycle's guidance: the review that is due, the queue's head, the installed algebra
systems. `run` saves the full output and prints only its path; a run that may take over a minute
goes to the background under a [watcher](tools/watch_run.py) that reports at five minutes and at the
end. The finisher runs the entry's checks, exports the timing table, archives the evidence and runs
the second reviewer. Substantial results belong in `research/results/` with their commands;
completed sessions are archived in `research/provenance/`.

## Tools

| Task | Tools |
| --- | --- |
| Restore context | [resume.py](tools/resume.py), [notebook-excerpt.py](tools/notebook-excerpt.py) (by anchor, with backlinks), [notebook_context.py](tools/notebook_context.py) (word budgets for the living sections) |
| Find and relate results | [search-claims.py](tools/search-claims.py), [claim-index.py](tools/claim-index.py) (render, graph queries, authoring), [claim-dependencies.py](tools/claim-dependencies.py), [search-record.py](tools/search-record.py), [record-audit.py](tools/record-audit.py) |
| Write the record | [notebook-append.py](tools/notebook-append.py), [lead_queue.py](tools/lead_queue.py), [finish-turn.py](tools/finish-turn.py), [check-append-only.py](tools/check-append-only.py), [check_records.py](tools/check_records.py) |
| Review | [medium-reviewer](.claude/agents/medium-reviewer.md), [stand_in_review.py](tools/stand_in_review.py), [blind_copy.py](tools/blind_copy.py) (a copy of the repository without its history) |
| Compute and measure | [compute.sh](compute.sh), [watch_run.py](tools/watch_run.py), [save-run-output.py](tools/save-run-output.py), [record-provenance.py](tools/record-provenance.py), [archive-session.py](tools/archive-session.py) |
| Guard the session | [tools/hooks/](tools/hooks/): shell guard, resume gate, monitor gate, memory gate, reviewer-brief guard, stop checks; [git hooks](tools/install-git-hooks.sh) |
| Formalize | [formalization/verify.sh](formalization/verify.sh), the [Lean project](formalization/README.md) |
| Branch, merge, publish | [branch.py](tools/branch.py), [ff-base.sh](tools/ff-base.sh), [notebook_rebase.py](tools/notebook_rebase.py), [checked-push.sh](tools/checked-push.sh), [verify-checkout.py](tools/verify-checkout.py), [build_pages.py](tools/build_pages.py) |
| Test the framework | `./compute.sh --threads 1 --timeout 60 python3 tools/tests/run.py` |

## Repository contents

- `notebook.html`: the main notebook: current state, working context and the append-only record.
  `research/branches/`: side notebooks.
- `research/claims/`: the claim registry; `research/CLAIM_INDEX.md` is generated from it.
- `research/results/`, `research/provenance/`: computation outputs, timing and execution evidence.
- `research/references/`: bibliography, source audits and papers cleared for redistribution
  ([guide](research/references/README.md)).
- `formalization/`: the Lean project. `publications/`: manuscripts with TeX sources.
- `AGENTS.md`, `COMPUTATION_RULES.md`, `PROMPTS.md`: the rules, the computation policy and the named
  prompts.
- `tools/`, `compute.sh`, `resource-controls/`: the framework's code and its tests.
- `php_codex_handoff/`: the unchanged historical package from before the framework, with the
  [pre-handoff compendium](php_codex_handoff/php_extension_research_compendium.pdf). The research
  began in Claude, continued in ChatGPT and moved to Codex.

Verify historical-file integrity and the essential tools with `./compute.sh --threads 1 python3
tools/verify-checkout.py`.

## About the name

Noemesis (noh-EM-uh-sis) is a coined name inspired by *noema*, the philosophical term for the
content of thought.

## License and credit

Original software is MIT-licensed; original research writing and other covered non-software material
use CC BY 4.0. Forks and further research are welcome. Preserve the attribution notices and cite the
results or tools your work relies on: see [LICENSE](LICENSE), [ATTRIBUTION.md](ATTRIBUTION.md) and
[CITATION.cff](CITATION.cff). Mathematical facts and ideas are not claimed as copyright property;
scholarly attribution remains an ethical expectation.

Third-party materials retain their own rights; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
