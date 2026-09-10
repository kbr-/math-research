# Reproducible computation limits

After a reboot or a new login, run from the project directory:

```bash
python3 resource-controls/setup.py
```

`setup.py` is self-contained: its embedded C source and unit templates recreate
everything. It uses only Python's standard library, the existing C compiler, and
systemd. It builds files in `.resource-runtime/`, links two units into the user's
systemd configuration, starts the controls, and verifies readiness. It is safe to
rerun when no computation jobs are running; otherwise it refuses reconfiguration.
`setup.sh` is a convenience shim for the same script. No packages are installed.

Cgroups and running services disappear at shutdown. Generated files and unit
links persist, but services are not enabled at boot. Rerun setup to restore and
verify them. Codex needs escalation to reach user systemd outside its sandbox.

## Budget

- **10,000,000,000 bytes total (10 decimal GB), RAM plus swap, across all jobs.**
  There is no fixed division between RAM and swap; Linux chooses where pages live.
- Cgroup v2 has no native combined RAM-plus-swap cap. A small C watchdog reads
  the shared slice's `memory.current` and `memory.swap.current` every 2 ms and
  kills the entire computation subtree with `cgroup.kill` above 10 GB.
  The watchdog's own RAM and swap are included in this sum.
- Separate 10 GB RAM and 10 GB swap limits are backstops, NOT the combined limit.
  The launcher refuses work without the active watchdog. Jobs bind to its
  lifetime; its `ExecStopPost` kills the computation group if it stops.
  systemd also monitors the watchdog's heartbeat.
- Polling and kernel accounting are not atomic, so brief overshoot is possible.
  There is no guarantee that overshoot stays below 0.5 GB or lasts at most 2 ms.
  The user accepts brief overshoot. Plan allocations and temporaries below the
  threshold rather than depending on the kill mechanism.
- Each job is restricted to **logical CPUs 0-13**, inherited by children and
  checked before workload execution. This host delegates only memory/pids to
  user systemd. The slice CPU quota and cpuset are configured but not active;
  per-service kernel CPU affinity provides the restriction. Workloads must not
  reset affinity or move outside the computation group.

## Run work

`compute.sh` combines resource enforcement with timing. It has a Python shebang
and is directly executable. Standalone commands get automatic timing logs. For
a research turn, use `./compute.sh start NAME`, `phase NAME CATEGORY`,
`run NAME -- COMMAND ...`, and `report NAME --stop`; see COMPUTATION_RULES.md.
The default per-command timeout is 180 seconds (`--timeout` changes it). Full
output stays on disk; only a bounded tail is displayed. Timeouts and interrupts
stop the service cgroup, including descendants.

```bash
./compute.sh --status
./compute.sh python3 calculation.py
./compute.sh --threads 1 python3 parallel_calculation.py
./compute.sh .venv/bin/python calculation.py
```

Use `--threads` to budget compiled-library threads across worker processes.
For example, 14 workers should each use one BLAS thread. Concurrent launcher
invocations share the same memory budget and CPU set. Jobs run in the caller's
working directory with standard input/output forwarded. PATH and important
Python environment variables are forwarded; arbitrary shell variables are not.

This boundary covers computation jobs and their descendants, not the browser,
Codex, unrelated processes, or commands manually run outside the launcher.

## Verification

```bash
./compute.sh --threads 1 python3 resource-controls/verify.py
./compute.sh --threads 1 python3 resource-controls/test_watchdog.py
```

The first checks affinity, cgroup backstops, thread settings, and a tiny compiled
BLAS operation. The second uses a temporary 64 MiB combined budget: one 40 MiB
worker survives; adding another triggers SIGKILL for the whole test group.
It checks that no kernel OOM occurred, confirming the watchdog killed the jobs.
Test resources are cleaned up afterward. It does not stress RAM or force swapping.

Full-size checks (the memory test may use swap and kills all computation jobs):

```bash
./compute.sh --threads 1 cc -O2 -std=c11 -Wall -Wextra -Werror -pthread resource-controls/stress.c -o .resource-runtime/stress
./compute.sh --threads 1 .resource-runtime/stress cpu
python3 resource-controls/test_11gb.py
```

Verified on this machine: 15 busy workers ran exclusively on CPUs 0-13,
averaging 13.965 occupied CPUs over 4 seconds. An allocator attempting to touch
11,000,000,000 bytes was killed when the watchdog observed 10,000,871,424 bytes
combined. RAM and swap were both in use. The test checks the enforced boundary
and empty workload group, not a particular systemd-run exit-code convention.
The memory test's small recording process stays outside the computation group;
the actual allocator uses the protected launcher. Its measurements are saved in
`.resource-runtime/11gb-result.json`.

The initial validated 11 GB result and its original output are also preserved in
`research/provenance/resource-validation/`, so the evidence survives cloning
without the ignored runtime directory. Reproducibility data for the historical
handoff lives in `research/provenance/handoff-files.json`; its outer ZIP is not
required in the repository.

See the [Linux cgroup documentation](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html).
