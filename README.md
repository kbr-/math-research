# PHP research notebook

A portable workspace for research on superpolynomial ordinary-PHP lower bounds
in fixed-depth AC⁰[p]-Frege. The goal remains open. Start with
[research/notes/RESUME.md](research/notes/RESUME.md) for a reading guide to the
authoritative checkpoint in the initial sections of [notebook.html](notebook.html).

## License and credit

Original software is MIT-licensed; original research writing and other covered
non-software material use CC BY 4.0. Forks and further research are welcome.
Preserve the applicable attribution notices and cite the results or tools your
research relies on. See [LICENSE](LICENSE), [ATTRIBUTION.md](ATTRIBUTION.md), and
[CITATION.cff](CITATION.cff). Mathematical facts and ideas are not claimed as
copyright property; scholarly attribution remains an ethical expectation.

Third-party materials retain their own rights. See
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) before redistributing sources.

## Clone and continue

```bash
git clone <repository-url> math
cd math
./start-codex.sh
```

On a fresh clone, the launcher starts a new Codex session and asks it to load
RESUME.md, inspect the notebook overview, and record its session ID. On this
machine it resumes the exact ID in `.codex-session-id`, so another unrelated
conversation does not change which session is resumed. Use `--new` to establish
and bind a fresh session, or `--resume` to require an existing local binding.
If the recorded session has been removed from Codex, use `--new`.

The session-ID file is deliberately ignored: Codex chat history, authentication,
and user-global settings do not travel with a Git clone. Research continuity
comes from the committed files. You can also tell a fresh session explicitly:

> Read research/notes/RESUME.md fully and follow its restart checklist. Load
> other sources only as needed; do not repeat the full manuscript import.

The launcher selects Vim for Ctrl+G and automatic approval review. Context and
auto-compaction budgets are editable constants at the top of `start-codex.sh`.
Install and sign in to a Codex CLI version supporting these options before using it.

## Local services and computations

From the checkout root, after reboot/login:

```bash
python3 resource-controls/setup.py
./compute.sh --status
```

Setup rebuilds all runtime resource controls from source; it installs no packages.
It requires **Linux, cgroup v2, a user systemd manager, and a C compiler**.
The profile allows at most 14 logical CPUs and 10 GB combined RAM plus swap,
with no fixed RAM/swap split. Unsupported controls must fail closed; do not
bypass them on a different platform. See [COMPUTATION_RULES.md](COMPUTATION_RULES.md).

In another terminal, run the live notebook:

```bash
python3 server.py
```

Open **http://localhost:8000**. Editing [notebook.html](notebook.html) refreshes
its rendered mathematics automatically. MathJax 4.0.0 loads from a CDN, so the
browser needs internet access. `index.html` contains layout and rendering logic.
Use `python3 server.py --port 8001` if the default port is occupied.

## Public notebook on GitHub Pages

The deployment workflow publishes the rendered notebook at
**https://kbr-.github.io/math-research/** once Pages is enabled.

One-time activation:

1. Open the repository's **Settings → Pages**.
2. Under **Build and deployment**, choose **GitHub Actions** as the source.
3. Push the workflow and notebook changes with `git push origin main`.
   If already pushed, run **Publish research notebook** manually from the
   repository's Actions tab, selecting `main`.

Subsequent pushes changing the notebook HTML, its template, or the site builder
automatically rebuild and deploy the site. An open published tab checks for a
new revision every 30 seconds; deployment and CDN propagation can add delay.
The published page does not require the Python server or your laptop to stay on.

The workflow builds only `index.html`, `revision.json`, and `.nojekyll` in `_site/`;
it does not upload the repository, private caches, PDFs, or Git history. It runs
only for `main`, including manual deployment. The page retains attribution and
the interface's MIT notice. Supporting source/data links should point to the
public repository unless explicitly added to the site artifact.

Build locally, without installing additional packages:

```bash
./compute.sh --threads 1 python3 tools/build_pages.py --out _site
```

`_site/` is generated and ignored. GitHub's hosted workflow uses Python's standard
library and built-in JavaScript tests; it does not run numerical research jobs.

Run and time a research turn:

```bash
./compute.sh start turn001
./compute.sh phase turn001 reading
./compute.sh run turn001 --threads 1 -- python3 calculation.py
./compute.sh report turn001 --stop --html-out research/results/turn001/timing.html
./tools/archive-session.py turn001
```

`compute.sh` has a Python shebang: execute it directly, not with `bash`.
Python 3.10+ is required for the complete toolset. The notebook server, resource
controller, and timing tools use the standard library. NumPy/SciPy/SymPy versions
from the working environment are listed in [requirements-research.txt](requirements-research.txt).
A virtual environment can be created and these packages installed **only with
explicit user approval**. Numba is additionally needed by historical suite A01;
it is not currently installed and no full archive rerun is required for setup.

## What is preserved

- `notebook.html`: authoritative current state, working mathematical context, and
  append-only mathematical Research record.
- `research/notes/`: restart navigation, proofs, source audits, historical import
  snapshots, and supporting research log.
- `research/references/`: bibliography and audit metadata for all four papers,
  plus the CC BY 4.0 Krajíček PDF and its extracted text. The other three papers
  and their full-text copies are local-only and excluded from public Git history.
- `research/provenance/`: durable timing, execution evidence, and resource tests.
- `resource-controls/`, `tools/`, `compute.sh`: reproducible execution and setup code.
- `php_codex_handoff/`: the **complete, unchanged historical package**, including
  the manuscript, original TeX, eleven historical check archives, and reports.
  The directory also contains the separately supplied
  [pre-handoff research compendium](php_codex_handoff/php_extension_research_compendium.pdf),
  generated by ChatGPT before the handoff package.
  The redundant outer `php_codex_handoff.zip` is intentionally not tracked.

Runtime binaries, virtual environments, temporary renders, operational logs,
credentials, and local session state are ignored. Before committing a new result,
archive its completed timing session and move any essential scratch output into
`research/results/` or `research/provenance/`. Never leave substantial research
only in an ignored directory or in chat history.

Locally held source PDFs without established redistribution permission remain
at ignored reference-cache paths. They do not travel with a public clone. Obtain
authorized copies or transfer your private research copies separately as allowed;
do not publish `private/` or the private pre-publication Git bundle. The public
repository preserves our research, source locators, versions, and hashes.
The local `pre-publish` branch is a private backup containing excluded sources.
Publish **only `main`**; do not push `pre-publish`, `--all`, or `--mirror`.

After every research turn, including failed proof attempts and no-progress turns,
append a Research-record entry with the generated timing table, update the
overview and working context, and commit the complete checkpoint. RESUME.md is
a stable reading guide; change it only for navigation or workflow updates. Timing
rows must reflect actual measurements; the final publication/commit steps follow
the timing snapshot. See [AGENTS.md](AGENTS.md).

Verify a checkout's historical files, licensed public source PDF, and essential tracked
tools with `python3 tools/verify-checkout.py`. On a configured machine, run it
through `./compute.sh`. This does not need the redundant outer handoff ZIP.
Use `--public-history main` to also check that excluded source paths and
source-containing diagnostics are absent from the public branch's reachable history.
