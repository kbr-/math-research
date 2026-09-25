# Computation rules

This is the authoritative policy for resource limits, protected execution,
numerical checks, timing tools, and computation outputs. It applies after reboot
and session resume. Research workflow, notebook editing, source audits, and
Git/publication rules belong in [AGENTS.md](AGENTS.md).

## CPU and memory budget

- Use at most **14 of the machine's 16 logical CPUs**, in total across all
  concurrent jobs and their child processes. The allowed CPUs are **0–13**.
- Use at most **10 GB total memory**, meaning **10,000,000,000 bytes of RAM plus
  swap combined**, shared across all computation jobs and their children.
  This is not a per-process allowance.
- **The RAM/swap split is unrestricted.** Leave placement to Linux. Do not
  disable system-wide swap or impose fixed shares such as 9 GB RAM plus 0.5 GB
  swap. Other applications also need the machine's resources.
- Kill computation jobs that exceed the combined memory budget. Brief overshoot
  before termination is acceptable (the user explicitly accepted approximately
  10.5 GB temporarily); it is not extra working capacity.
- Plan memory use below the limit, accounting for array copies, intermediate
  results, BLAS workspaces, and all parallel workers.

## Enforced execution

The launcher requires Linux, cgroup v2, and a working user systemd manager;
setup also needs the existing C compiler. Unsupported controls must fail closed.

Run computations, numerical checks, builds, and other potentially substantial
local workloads through the protected launcher:

```bash
./compute.sh python3 calculation.py
```

All launcher invocations share `mathcompute.slice`. Never bypass a failed limit
check, change CPU affinity from inside a workload, move a process out of the
group, or launch an unprotected job to work around the limits.

Each job receives kernel CPU affinity 0–13, inherited by its children and checked
before execution. On this host, CPU cgroup controllers are not delegated to user
systemd, so the configured slice CPU quota and cpuset are not active; per-job
affinity provides the restriction.

Cgroup v2 has no native combined RAM-plus-swap cap. A compiled C watchdog polls
the workload group's RAM and swap usage every 2 ms, includes its own memory use,
and writes `cgroup.kill` when the total exceeds 10 GB. Separate 10 GB RAM and
10 GB swap caps are only backstops, not permission to use 20 GB combined.

The launcher requires the watchdog to be running. Jobs depend on its lifetime;
if it stops, systemd stops dependent jobs and its stop handler kills the whole
computation group. Never compute without these protections. Polling and kernel
accounting can produce brief overshoot; no exact maximum overshoot or termination
latency is guaranteed.

The boundary covers protected computation jobs and their descendants. The agent,
the browser, the small control processes, unrelated applications, and commands
manually run outside the launcher are not inside the workload group.

## Efficient numerical implementation

- Computer algebra systems are installed (user installations, 23 and 25 September 2026):
  **Macaulay2** (`M2`), **Singular**, **msolve**, **GAP** (with HAP, GUAVA, design, GRAPE and
  the character-table library) and **PARI/GP**, with Normaliz, 4ti2, polymake and the XOR-aware
  SAT solver CryptoMiniSat (`cryptominisat5`). Run their scripts through `./compute.sh` (`.m2`,
  `.sing`, `.g` and `.gp` scripts are recognized). Their libraries cover far more than Gröbner
  bases: commutative algebra, modules and homology, combinatorics, representation theory of
  symmetric groups in positive characteristic, and linear algebra over finite fields. Consider
  them for every computation they could improve, and prefer them to a hand-built kernel unless
  the kernel is measured to be faster.
- Hand-written C/C++ kernels build their exact linear algebra on the installed libraries, not
  on hand-written elimination: **fflas-ffpack** (dense rank, echelon form, nullspace and products
  mod p at BLAS speed; `FFPACK::Rank`), **FLINT** (`nmod_mat`, polynomials), **LinBox** (sparse
  and black-box rank and solving), and **NTL**. On a 4000×4000 GF(3) matrix of rank 3100,
  fflas-ffpack took 0.2 s and FLINT 1.5 s, with equal ranks (25 September 2026). Link flags:
  fflas-ffpack `$(pkg-config --cflags fflas-ffpack) -lgivaro -lgmpxx -lgmp -lopenblas`; FLINT
  `-lflint -lgmp`; LinBox `$(pkg-config --cflags --libs linbox) -lopenblas`. Validate a
  kernel's ranks against a second library on small cases. `./compute.sh start` lists the systems
  and libraries it finds.
- Use compiled numerical libraries such as **NumPy, SciPy, and BLAS** for heavy
  computation, or appropriate compiled implementations in other languages.
- Do not write numerical inner loops or heavy computational logic in pure
  Python. Python is appropriate for orchestration and small control operations.
- Vectorize where appropriate. Use chunking when full vectorization would
  produce excessive temporary arrays or exceed the shared memory budget.
- When a computation is expected to be expensive or long, consider writing it in
  C++ with the installed `g++` (user suggestion, 23 September 2026). GPT-6 Astra
  wrote most of its checkers that way (`research/tools/*.cpp`, with shared headers
  such as `pc_boundary.hpp`), and they were consistently fast. A Python loop around
  compiled calls can still waste most of the time, for example by re-reducing a
  whole matrix for every chunk of new rows instead of reducing only the new rows
  against the existing basis.
  `compute.sh` requires `--kernel-reason` for a Python computation allowed more
  than 120 s: name the compiled kernel doing the heavy work (CLAUDE.md states the default).
  It also refuses such a run when its reachable Python nests loops three deep over
  non-literal ranges; vectorize them or move them into the kernel.
- Budget process counts and library threads together. Across concurrent work,
  keep worker count times threads per worker within 14; avoid nested thread
  pools and oversubscription.
- For 14 worker processes, use one numerical-library thread per worker:

```bash
./compute.sh --threads 1 python3 parallel_calculation.py
```

## Libraries and virtual environments

- **Install no libraries or dependencies without explicit user approval.**
- If a required library is missing, inform the user so they can install it or
  explicitly authorize installation.
- Create a project virtual environment only with approval. Use its interpreter
  through the same protected launcher:

```bash
./compute.sh .venv/bin/python calculation.py
```

## After reboot or session resume

From the project directory, recreate and verify the controls:

```bash
python3 resource-controls/setup.py
./compute.sh --status
```

`setup.py` is self-contained and rerunnable: it contains the watchdog source and
unit templates, compiles with the existing C compiler, recreates the systemd
resources, and checks readiness. It installs no packages. It refuses to
reconfigure while computation jobs are running.

Cgroups and running services disappear at shutdown. Project files and unit links
persist; the services are not enabled at boot. Rerun setup after reboot/login,
and check status when resuming. Codex needs the appropriate tool escalation to
access user systemd outside its sandbox; Claude Code needs no escalation.
The unit links are per-user. Setup run from a linked Git worktree builds in the
main checkout's `.resource-runtime/`, so all worktrees share one set of controls.

Resource-limit validation evidence and implementation details are recorded in
[resource-controls/README.md](resource-controls/README.md). Do not rerun the
resource stress tests merely to resume work; verify active controls with
`./compute.sh --status`.

## Unified execution and timing

`compute.sh` is one executable Python program with a shebang, containing both
resource enforcement and timing. Run it directly, not with `bash`.

From the repository root:

```bash
./compute.sh start turn001 --model "MODEL, reasoning setting"
./compute.sh phase turn001 reading --note "Read the relevant proof"
./compute.sh phase turn001 mathematics
./compute.sh phase turn001 coding --note "Design and implement a computation"
./compute.sh run turn001 --threads 1 -- python3 calculation.py
./compute.sh report turn001 --stop
```

`start` records the producing agent (detected, or `--agent NAME`), its model,
and the selected notebook (`--notebook NAME` overrides worktree selection).
The finisher refuses a different notebook; `--next` carries the notebook forward.
For Codex, `start` reads the current `CODEX_THREAD_ID`'s latest `turn_context`
under `CODEX_HOME/sessions` (default `~/.codex/sessions`) and records its `model`
and `effort`. These active-turn settings take precedence over supplied labels;
configuration defaults are not evidence of the active setting. Only the model
and reasoning setting enter the timing record, never the thread ID or transcript.
If that metadata is unavailable, supply `--model "MODEL, reasoning setting"` or
`MATH_AGENT_MODEL`; use `unknown` only for information you cannot establish.
Other agents, including Claude Code, retain their explicit-model/environment
behavior. `finish-turn.py --next` carries settings forward, with Codex metadata
refreshed at the next start, and `report` prints them.

Alternatively, use `./compute.sh --session turn001 --threads 1 python3 calculation.py`.
Without a session argument, execution gets an automatically named timing session.
Every executed workload uses the shared protected group, regardless of timing
category (`computation`, `local_processing`, `formal_verification`,
`network_tool`, or `external_tool`).
Metadata commands (`start`, `phase`, `report`, `--status`) are small control
operations outside computation services.

`tools/resume.py` marks `restoration` in an existing active cycle; ordinary phase
markers resume normal accounting. Silent [recovery evidence](tools/RECOVERY_EVIDENCE.md)
is preserved in timing summaries and their existing archives. Resuming alone starts
no research clock; ordinary notebook overview reads do not mark a resume.

The default timeout is 180 seconds; set `--timeout SECONDS` before `--` for longer
work. Timeouts and interrupts stop the actual service and its children, with a
systemd runtime limit as a backstop. Full output and timing records are saved in
`research/logs/`. Computation output is never displayed: the launcher prints only its own
lines (guard messages, timing, exit status) and the path and size of the saved log, which is
read from the file. Other categories can show a tail with `--tail-bytes N` (default none).
Jobs run as systemd services and do not inherit the caller's environment, apart from
the thread-count variables the launcher sets. Pass any other variable inside the
command, as in `./compute.sh run TURN -- env NAME=VALUE python3 script.py`; a prefix
before `./compute.sh` is silently dropped.

Mark `formalization` for translating statements into Lean, designing formal
proofs, writing tactics, and debugging formalization code. Use `mathematics`
when developing or revising the underlying mathematical argument, including an
alternative proof needed for formalization; switch phases as the work changes.
Run Lean builds and proof checks with `--category formal_verification`;
`formalization/verify.sh` selects this category automatically and accepts
`--session TURN` to include it in the same research cycle. Dependency downloads
remain `network_tool` or `local_processing` as appropriate. These categories
share the existing exclusive timing rules and do not require a separate cycle.

Mark `mathematics` for mathematical reasoning, proof review, and proof writing;
keep it active while drafting or correcting notebook mathematics. Use `coding` for
computation design and implementation, `preparation` for setup and checkpoint
work, and `overhead` for identifiable interruptions or overhead-only windows.
Mark the work phase before planning or drafting. Do not put a marker and a new
code/patch argument in the same tool call: that argument is drafted before the
marker executes. After each awaited source or web batch, explicitly set the
phase for interpreting its output in the same sequential tool call; mark any
source follow-up separately. Do the same after the final check or checkpoint.
Keep proof finalization in mathematics; switch back if checkpoint work uncovers
a substantive proof question.
Use `reading` for source review and `network_tool` before browsing, restoring the
work phase afterward. The table keeps these categories separate and omits empty
ones. The older mixed `reasoning_writing` phase remains readable for past sessions.
Command runs record their own category, status, and elapsed interval, including
failures and retries. AGENTS.md defines which turns require instrumentation.

Reports use exclusive wall-clock intervals; do not add overlapping worker times.
Reading includes interpretation and tool windows include service/orchestration
latency. Pure internal reasoning and pure network latency are not measurable.
Unexpected interruptions may remain mixed with the active phase; disclose material
mixing rather than retrospectively inventing a split or an overhead estimate.
Disclose mixed time, work before instrumentation, and final generation after the
snapshot. Start a fresh timing session after reboot. A session cannot be stopped
while command records remain unfinished.

## Numerical verification

- Use exact modular arithmetic for finite-field calculations, never floating-point
  rank; guard integer overflow in vectorized/compiled kernels.
- Match the intended field, encoding, parameters, and degree conventions. Use
  targeted checks capable of falsifying the claim, with nonvacuous cases and
  negative controls. Identify whether an instance is PHP, another unsatisfiable
  system, or a satisfiable finite domain.
- Report the scope of finite checks without treating them as universal proofs.
  Distinguish new runs from archived results; rerun only when the task requires it.
- Before launching an exhaustive enumeration, compute its size and expected time from
  the parameters, and shrink or skip cases beyond the budget; a checker should print the
  size and refuse oversized cases rather than let a run be discovered by its timeout.
  Extrapolate from the smaller runs you already have. Before a long run, apply the exact
  reductions available (quotients by monomial axioms, incremental reuse of nested results,
  narrow search brackets) and the parallel paths (OpenMP elimination, `--threads`).
  `compute.sh` enforces this: `--timeout` above 600 s needs `--expect SECONDS`, and a run
  expected to exceed 600 s on fewer than 4 threads needs `--serial-reason`; it prints
  expected against actual time. A run expected to exceed 600 s must also cite `--sized-by RUN_ID`,
  a completed run of the same program in the same session whose measured time the estimate
  extrapolates (user instruction, 24 September 2026, after unsized runs of 20+ minutes). Stop a superseded run as soon as its replacement is
  validated.
- **Run limit** (user instructions, 23 September 2026, after a cycle with 110 minutes
  of computation): a run may take at most 30 minutes. `compute.sh` refuses a `--timeout`
  above that unless the user's explicit approval is quoted in `--user-approved`. A cycle's
  total has no fixed cap, but keep it proportionate: 110 minutes was too much. Design tests
  to fit: the smallest informative size, symmetry classes instead of all cases, early exit
  (for example, stop a closure once 1 is in the span), and a sizing run before the full one.

## Persist computation outputs

Important computation output is research, not disposable logging. Scripts that
produce tables, group-element enumerations, proof certificates, matrices, search
results, or similar data should support `--out PATH` (or an equivalent explicit
destination) and write the complete result to a tracked location, normally
`research/results/`:

```bash
./compute.sh run turn001 --threads 1 -- python3 research/tools/calculation.py --out research/results/turn001/table.json
```

Large result files are acceptable when needed. Do not impose an arbitrary
output-size cutoff, silently truncate results, or leave their only copy in
ignored logs/tmp/runtime folders. The CLI's bounded output preview limits
context usage only; saved output is full. Include essential data with its
checkpoint under the Git rules in AGENTS.md.

A program without `--out` is saved with `tools/save-run-output.py SESSION RUN_ID OUT`, which copies
the run's complete log under its command line; the `compute.sh` display holds only the launcher's
own lines.

Reference output paths in the relevant notebook Research-record entry. Preserve
the generating command, parameters, random seed if applicable, data encoding or
schema, and verification/provenance (including hashes when useful). Use distinct
run paths to preserve accepted earlier results. Prefer structured formats suited
to the data, and stream/chunk generation, saving, copying, and hashing so a large
file does not require a correspondingly large RAM allocation. These operations
still obey the combined memory and CPU budget.
Use `tools/record-provenance.py --out MANIFEST FILE...` for shared path/size/hash
metadata; `--session TURN` records its timing-session label. It streams files,
rejects changing inputs, and refuses to replace an existing manifest.

## Timing export and evidence archival

Export a completed session as an HTML timing table:

```bash
./compute.sh report turn001 --stop --html-out research/results/turn001/timing.html
./tools/archive-session.py turn001
```

The export gives a **Measured category / Elapsed** table with the total
instrumented interval first. It verifies that exclusive categories sum to the
total and omits zero-duration categories. A stopped session must have no
unfinished commands. Do not invent categories or backfill unmeasured time.
Operations after the final snapshot are outside its measured interval.

Operational `research/logs/` are ignored. Archiving preserves the journal,
summary, and complete command outputs in `research/provenance/session-records/`.
Inspect the evidence for credentials and unrelated/private runtime state before
committing it. Promote any other essential scratch results to `research/results/`
or `research/provenance/`, using streaming I/O within the shared memory budget.
The notebook's entry, table-placement, and footnote rules are in AGENTS.md.

For new archives, a captured output identical to its declared `--out` report
under `research/results/` is stored once: the archive manifest's `canonical_path`
references that complete report relative to `research/`, with its SHA-256.
Commit the referenced report with the archive. Different outputs are preserved
separately, and existing archives are not rewritten. Missing or changed canonical
reports fail re-archival rather than silently losing evidence.
