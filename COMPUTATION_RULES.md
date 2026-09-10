# Computation rules

These rules apply to computations in this workspace and continue to apply after
rebooting the laptop or resuming the session.

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

The boundary covers protected computation jobs and their descendants. Codex,
the browser, the small control processes, unrelated applications, and commands
manually run outside the launcher are not inside the workload group.

## Efficient numerical implementation

- Use compiled numerical libraries such as **NumPy, SciPy, and BLAS** for heavy
  computation, or appropriate compiled implementations in other languages.
- Do not write numerical inner loops or heavy computational logic in pure
  Python. Python is appropriate for orchestration and small control operations.
- Vectorize where appropriate. Use chunking when full vectorization would
  produce excessive temporary arrays or exceed the shared memory budget.
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
- A project virtual environment may be used once approved. It has not yet been
  created. Use its interpreter through the same protected launcher:

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
access user systemd outside its sandbox.

## Verification already performed

- An allocator attempting to write **11 GB** was killed when the watchdog
  observed **10,000,871,424 bytes** combined RAM and swap. Both RAM and swap were
  in use, and no test processes remained afterward.
- **15 busy CPU workers** ran exclusively on CPUs **0–13**, averaging **13.97
  occupied CPUs** over approximately four seconds.
- A smaller test confirmed aggregate enforcement: one 40 MiB worker fit under
  a temporary 64 MiB budget; adding a second caused the entire test group to be
  killed.
- Repeated setup and a small compiled BLAS calculation were verified. Success
  means the resource boundary is enforced, not a particular wrapper exit code.

Implementation details and test commands are in
[resource-controls/README.md](resource-controls/README.md).

## Unified execution and timing

`compute.sh` is one executable Python program with a shebang, containing both
resource enforcement and timing. Run it directly, not with `bash`.
It replaces compute.py and research/tools/timing.py.

From the repository root:

```bash
./compute.sh start turn001
./compute.sh phase turn001 reading --note "Read the relevant proof"
./compute.sh phase turn001 reasoning_writing
./compute.sh run turn001 --threads 1 -- python3 calculation.py
./compute.sh report turn001 --stop
```

Alternatively, use `./compute.sh --session turn001 --threads 1 python3 calculation.py`.
Without a session argument, execution gets an automatically named timing session.
Every executed workload uses the shared protected group, regardless of timing
category (`computation`, `local_processing`, `network_tool`, or `external_tool`).
Metadata commands (`start`, `phase`, `report`, `--status`) are small control
operations outside computation services.

The default timeout is 180 seconds; set `--timeout SECONDS` before `--` for longer
work. Timeouts and interrupts stop the actual service and its children, with a
systemd runtime limit as a backstop. Full output and timing records are saved in
`research/logs/`. Only the last 8,000 output bytes are displayed by default;
`--tail-bytes N` changes that without losing the saved log.

Measure every research turn, including failures/retries, from as early as practical.
Mark reading/review, preparation, reasoning/writing, and external-tool phases.
For browsing, mark `network_tool` before the call and restore the phase afterward.
Command runs log their own category, status, and elapsed interval automatically.

Reports use exclusive wall-clock intervals; do not add overlapping worker times.
Reading includes interpretation and tool windows include service/orchestration
latency. Pure internal reasoning and pure network latency are not measurable.
Disclose mixed time, work before instrumentation, and final generation after the
snapshot. Start a fresh timing session after reboot. A session cannot be stopped
while command records remain unfinished.

## Evidence and reproducibility

- Keep `php_codex_handoff/` unchanged. New artifacts normally belong in `research/`;
  read `research/notes/RESUME.md` after compaction rather than reimporting everything.
- Match source versions, hypotheses, encodings, fields, and degree conventions.
  Keep dependencies and unresolved assumptions explicit.
- Separate working proofs, conditional claims, source statements, and finite tests.
  Do not treat finite checks as universal theorems, archived results as new runs,
  or failed retrievals as imported sources.
- Use exact modular arithmetic for finite-field calculations, never floating-point
  rank; guard integer overflow in vectorized/compiled kernels.
- Choose targeted tests capable of falsifying the claim, with nonvacuous cases and
  negative controls. State whether the test is actual PHP, a different unsatisfiable
  system, or a satisfiable finite domain. Do not rerun archives just to import context.
- Record the statement, proof attempt or obstruction, parameter/degree accounting,
  checks, timing, effect on the goal, and remaining gap in the research notes.

## Persistent research checkpoints

Every research turn must produce a notebook Research-record entry and a Git
commit, including turns with no useful result, an obstruction, or a failed proof
attempt. Preserve the question, attempted approach, actual outcome, and remaining
gap without inventing progress. Update the living overview and restart
notes, and include the relevant tools, source provenance, and result data.

Operational `research/logs/` and generated/scratch directories are ignored.
After `./compute.sh report TURN --stop`, run `./tools/archive-session.py TURN`
to preserve the journal, summary, and command outputs in
`research/provenance/session-records/`. Inspect the evidence before committing;
keep credentials and unrelated/private runtime state out of Git. Promote any
other substantial results to `research/results/` or `research/provenance/`.
The math record must not depend on an ignored file or on chat history alone.

Git commits are local checkpoints. Use descriptive messages and report failures
instead of claiming success. Preserve unrelated user edits and the historical
handoff. All current tools resolve paths from the checkout; no particular home
directory is required. The resource-control implementation requires Linux with
cgroup v2 and a working user systemd manager, and must fail closed if unavailable.

## Persist computation outputs

Important computation output is research, not disposable logging. Scripts that
produce tables, group-element enumerations, proof certificates, matrices, search
results, or similar data should support `--out PATH` (or an equivalent explicit
destination) and write the complete result to a tracked location, normally
`research/results/`:

```bash
./compute.sh run turn001 --threads 1 -- python3 research/tools/calculation.py --out research/results/turn001/table.json
```

Large result files are acceptable when needed and should be included in the
research-result commit. Do not impose an arbitrary output-size cutoff, silently
truncate results, or leave their only copy in ignored logs/tmp/runtime folders.
The CLI's bounded output preview limits context usage only; saved output is full.

Reference output paths in the research log and relevant notebook entry. Preserve
the generating command, parameters, random seed if applicable, data encoding or
schema, and verification/provenance (including hashes when useful). Use distinct
run paths to preserve accepted earlier results. Prefer structured formats suited
to the data, and stream/chunk generation, saving, copying, and hashing so a large
file does not require a correspondingly large RAM allocation. These operations
still obey the combined memory and CPU budget.

## Timing table in every research-turn entry

Every research turn, successful or not, ends with a dated notebook entry and a
**Measured category / Elapsed** table. Put the bold total instrumented interval
first, followed by the actual measured reading/review, web/download, other tool,
computation/local-processing, and drafting/preparation/unseparated categories
that occurred. Do not invent a breakdown merely to match an example table.
Count overlapping execution once and distinguish failed commands from failed
mathematical attempts. Keep the repeated footnote short, for example:
"Through final snapshot; overlapping time counted once." Add exceptional
failure/limitation details only when needed. Do not repeat the long methodology
disclaimer after every entry; its details are documented here. The first notebook
timing entry retains its original longer explanation as a reference.

Draft the entry and refresh the overview first. At the final snapshot:

```bash
./compute.sh report turn001 --stop --html-out research/results/turn001/timing.html
```

Embed that generated HTML fragment at the end of the notebook entry, archive the
session, and commit both the entry and its timing/evidence artifacts. Final entry
publication, archiving, Git operations, and response delivery after the snapshot
are excluded from the table and must not be presented as measured within it.
The export requires a completed session and checks that exclusive categories
sum to the measured total. Zero-duration categories are omitted; full raw timing
remains in the archived journal and summary. No retrospective timing is fabricated.
