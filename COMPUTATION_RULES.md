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
access user systemd outside its sandbox.

Resource-limit validation evidence and implementation details are recorded in
[resource-controls/README.md](resource-controls/README.md). Do not rerun the
resource stress tests merely to resume work; verify active controls with
`./compute.sh --status`.

## Unified execution and timing

`compute.sh` is one executable Python program with a shebang, containing both
resource enforcement and timing. Run it directly, not with `bash`.

From the repository root:

```bash
./compute.sh start turn001
./compute.sh phase turn001 reading --note "Read the relevant proof"
./compute.sh phase turn001 mathematics
./compute.sh phase turn001 coding --note "Design and implement a computation"
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

Mark `mathematics` for mathematical reasoning, proof review, and proof writing;
keep it active while drafting or correcting notebook mathematics. Use `coding` for
computation design and implementation, `preparation` for setup and checkpoint
work, and `overhead` for identifiable interruptions or overhead-only windows.
Mark the work phase before planning or drafting. Do not put a marker and a new
code/patch argument in the same tool call: that argument is drafted before the
marker executes. For a planned transition after an awaited check or checkpoint,
issue the next marker in the same sequential tool call before returning its
output for interpretation. Keep proof finalization in mathematics; switch back
if checkpoint work uncovers a substantive proof question.
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

Reference output paths in the research log and relevant notebook entry. Preserve
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
