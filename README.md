# A Self-Improving Framework for Autonomous Mathematical Research

An open framework for autonomous mathematical research—with persistent memory,
reproducible evidence, and a workflow that improves through use.

- **Research that survives session boundaries.** Resume from durable findings,
  proofs, and context stored in the repository, including from a fresh session
  on another machine.
- **Autonomous investigation.** Pursue a goal through repeated cycles of
  reasoning, experimentation, and review, with explicit remaining obstacles
  and a concrete next step.
- **A workflow that improves through use.** After each autonomous research
  cycle, assess what helped, what wasted effort, and what made the mathematics
  difficult to check; make bounded improvements to tools and procedures.
- **Inspectable results.** Preserve arguments, assumptions, computational
  evidence, and failed approaches. Distinguish working proofs, conditional
  results, conjectures, and finite checks.
- **A live, versioned notebook.** Follow progress locally or online, with
  rendered mathematics and Git checkpoints preserving the research record,
  code, outputs, and provenance together.

The framework combines an explicit research protocol for AI agents with tools
for context recovery, protected computation, evidence archival, and publication.
Self-improvement means refining the research workflow and its tools; mathematical
arguments remain open to review, and recorded proofs are not automatically
formally verified.

## First ongoing case study: proof-complexity lower bounds

The first application investigates superpolynomial proof-size lower bounds for
the ordinary pigeonhole principle in fixed-depth AC⁰[p]-Frege systems: bounded-depth
propositional proof systems with modular counting gates. **The goal remains open.**

**[Read the live research notebook](https://kbr.is-a.dev/math-research/).**
Its initial sections describe the current state, remaining obstacles, and proposed
next step. The research record preserves results, proofs, unsuccessful attempts,
and measured timing, making the ongoing investigation available for inspection.

The research began in Claude, continued in ChatGPT, and moved to Codex. The
[pre-handoff research compendium](php_codex_handoff/php_extension_research_compendium.pdf)
and historical manuscript preserve the earlier development.

## Research workflow and evidence

The [research protocol](AGENTS.md) and supporting tools provide:

- **Focused context recovery.** A [restart guide](research/notes/RESUME.md)
  leads from concise living summaries to the exact sources needed for a task.
  The [excerpt tool](tools/notebook-excerpt.py) retrieves validated sections by
  stable anchor without loading the whole research history.
- **An indexed body of results.** The [claim index](research/CLAIM_INDEX.md)
  connects stable labels and explicit statuses to full statements and proofs.
  The protocol requires checking earlier work and recording dependencies,
  refinements, and rediscoveries.
- **A durable record of corrections and failed attempts.** Research entries
  are chronological and append-only. Corrections and retractions receive new
  dated entries, preserving the argument's history and the reasons a route failed.
- **Reproducible computational evidence.** Complete outputs accompany their
  generating commands and relevant parameters. [Provenance manifests](tools/record-provenance.py)
  record file hashes; [archival](tools/archive-session.py) preserves completed
  execution records and refuses to replace different evidence.
- **Measured research effort.** [Timing tools](COMPUTATION_RULES.md#unified-execution-and-timing)
  record work phases and command outcomes, count overlapping intervals once,
  and export per-turn timing tables. Measurements include unsuccessful commands
  and retries, with explicit limits on what the recorded intervals establish.
- **Resource-bounded execution.** The [computation launcher](compute.sh)
  applies shared CPU and memory controls, command timeouts, and full output
  logging. It refuses work when required protections are unavailable.
- **Complete checkpoints and controlled publication.** The
  [turn finalizer](tools/finish-turn.py) exports timing, archives evidence, and
  embeds the timing table before review and commit. Source licensing and
  [public-history checks](tools/verify-checkout.py) help keep known private
  materials out of publication; the static builder packages only the intended
  public site files.

The [Spin prompt](notes) specifies the autonomous research and process-improvement
loop. The agent follows that protocol, while the tools enforce specific execution
and evidence checks. The current launcher integrates with Codex CLI; the research
record itself lives in ordinary HTML, Markdown, code, and data files.

## Browse locally

```bash
git clone https://github.com/kbr-/math-research.git
cd math-research
python3 server.py
```

Open **http://localhost:8000**. Editing [notebook.html](notebook.html) refreshes
its rendered mathematics automatically. MathJax loads from a CDN, so the browser
needs internet access. `index.html` supplies the layout and rendering logic.
Use `python3 server.py --port 8001` if the default port is occupied.

The [published notebook](https://kbr.is-a.dev/math-research/) is built by
GitHub Actions when relevant notebook or site-tooling changes are pushed to
`main`. It is a standalone site and requires no local server.

## Continue the research

[research/notes/RESUME.md](research/notes/RESUME.md) is the reading guide for
restoring research context. It points to the notebook's authoritative initial
sections and selected supporting sources. The original handoff import is complete;
resuming work does not require repeating it.

With Codex CLI installed and authenticated, run:

```bash
./start-codex.sh
```

On a fresh clone, the launcher starts a session that restores context from the
committed files. Subsequent launches resume the session recorded locally in
`.codex-session-id`. Use `--new` to start and bind a fresh session, or `--resume`
to require an existing binding. Session IDs, chat history, and authentication
are not included in the repository.

The launcher selects Vim for Ctrl+G and automatic approval review. Context and
auto-compaction budgets are editable constants at the top of `start-codex.sh`.
A Codex CLI version supporting these options is required.

[AGENTS.md](AGENTS.md) describes the research workflow: maintain the notebook's
living sections, append each research attempt with its timing and evidence,
and commit complete checkpoints locally. Publishing requires authorization under
the repository's Git policy; research work alone does not authorize a push.

### Automatic research

Use a Codex **goal** to keep the agent working across successive turns without
prompting it after every checkpoint. The goal points to the **Spin:** prompt in
[`notes`](notes), which defines the research, process-improvement, and checkpoint
loop, including how to resume after context compaction.

After restoring context in the session for your chosen checkout:

- **Codex CLI:** enter `/goal <objective>` in the interactive session.
- **ChatGPT app:** open the remotely connected Codex session for that checkout,
  enter `/goal`, and supply the same objective in the goal interface.

For example, use this goal in the CLI, or paste the text after `/goal` into the
app's goal field:

```text
/goal Pursue the notebook's research objective and improve the research framework by following the "Spin:" prompt in ./notes. Continue the loop until I stop you. Follow AGENTS.md and COMPUTATION_RULES.md. Override Spin's publication instructions for this run: stay on the current branch, commit checkpoints locally, and do not push.
```

This example keeps checkpoints local and preserves the selected branch. If you
want automatic publication too, replace that override with your explicit branch
and push authorization under [the Git policy](AGENTS.md#portable-sessions-and-git-checkpoints).
The Spin prompt remains the authoritative loop; there is no need to paste its
full instructions into each goal.

In the CLI, `/goal` displays the current objective, `/goal edit` changes it,
`/goal pause` pauses it, `/goal resume` continues it, and `/goal clear` removes it.
The app also provides goal controls in its progress row. Keep the machine hosting
the remote session awake and connected while it works. See the official OpenAI
guides to [long-running work](https://learn.chatgpt.com/docs/long-running-work)
and [goal commands](https://learn.chatgpt.com/docs/developer-commands?surface=cli#set-or-view-a-task-goal-with-goal).

## Computation tools

Python 3.10+ is required for the complete toolset. The notebook server,
resource controller, and timing tools use the Python standard library.
[requirements-research.txt](requirements-research.txt) records numerical-library
versions used in the research environment; historical suite A01 also requires
Numba. Dependency installation by an agent requires explicit approval under
[COMPUTATION_RULES.md](COMPUTATION_RULES.md).

The protected computation launcher requires **Linux, cgroup v2, a user systemd
manager, and a C compiler**. Its resource profile uses CPUs 0–13 and a shared
10 GB combined RAM-plus-swap budget, with no fixed RAM/swap split. See
[resource-controls/README.md](resource-controls/README.md) for compatibility and
enforcement details. Unsupported controls fail closed.

Initialize the controls from the checkout root after reboot or login:

```bash
python3 resource-controls/setup.py
./compute.sh --status
```

Setup rebuilds runtime controls from source and installs no packages. Run
computations through `./compute.sh`; it combines resource enforcement, timing,
and full output logging. For example, with a research script `calculation.py`:

```bash
./compute.sh start turn001
./compute.sh phase turn001 reading
./compute.sh run turn001 --threads 1 -- python3 calculation.py
# After drafting the notebook entry with <!-- TIMING turn001 -->:
./tools/finish-turn.py turn001
```

The finalizer exports timing, archives evidence under the resource limits, and
fills the unique notebook placeholder. `--next turn002` also starts the next
cycle's clock immediately after the snapshot. Review and commit the checkpoint
afterward. The lower-level timing commands remain in COMPUTATION_RULES.md.

Substantial result files belong in `research/results/`, with their generating
commands and verification evidence. Completed timing sessions are archived in
`research/provenance/`; operational logs and scratch files are ignored.

Build a local static notebook artifact with:

```bash
./compute.sh --threads 1 python3 tools/build_pages.py --out _site
```

The generated `_site/` directory contains only the rendered page and revision
metadata. It is ignored by Git.

## Repository contents

- `notebook.html`: authoritative current state, working mathematical context,
  and append-only research record.
- `research/notes/`: restart navigation, proofs, source audits, historical import
  snapshots, and supporting research log.
- `research/results/`: complete computation outputs and timing tables.
- `research/references/`: bibliography and audit metadata for four papers,
  plus the CC BY 4.0 Krajíček PDF and its extracted text. Other papers and their
  full-text copies are not distributed; consult the
  [reference guide](research/references/README.md) to obtain authorized sources.
- `research/provenance/`: durable timing, execution evidence, and resource tests.
- `resource-controls/`, `tools/`, `compute.sh`: reproducible execution and setup code.
- `php_codex_handoff/`: the unchanged historical package, including the manuscript,
  original TeX, eleven check archives, and reports, plus the ChatGPT-generated
  [pre-handoff compendium](php_codex_handoff/php_extension_research_compendium.pdf).

Verify historical-file integrity, the licensed source PDF, and essential tools:

```bash
./compute.sh --threads 1 python3 tools/verify-checkout.py
```

Runtime binaries, virtual environments, temporary renders, operational logs,
credentials, and local session state are excluded from version control.

## License and credit

Original software is MIT-licensed; original research writing and other covered
non-software material use CC BY 4.0. Forks and further research are welcome.
Preserve the applicable attribution notices and cite the results or tools your
research relies on. See [LICENSE](LICENSE), [ATTRIBUTION.md](ATTRIBUTION.md), and
[CITATION.cff](CITATION.cff). Mathematical facts and ideas are not claimed as
copyright property; scholarly attribution remains an ethical expectation.

Third-party materials retain their own rights. See
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for source licensing and
redistribution details.
