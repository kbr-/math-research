# PHP research notebook

A portable workspace for research on superpolynomial ordinary-PHP lower bounds
in fixed-depth AC⁰[p]-Frege.

**[Read the rendered research notebook](https://kbr-.github.io/math-research/).**
Its initial sections describe the current state, remaining obstacles, and proposed
next step. The research record preserves results, proofs, unsuccessful attempts,
and measured timing. The lower-bound goal remains open.

The research began in Claude, continued in ChatGPT, and moved to Codex. The
[pre-handoff research compendium](php_codex_handoff/php_extension_research_compendium.pdf)
and historical manuscript preserve the earlier development.

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

The [published notebook](https://kbr-.github.io/math-research/) is built by
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
and commit complete checkpoints locally. Public publication is handled by the
repository maintainer.

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
