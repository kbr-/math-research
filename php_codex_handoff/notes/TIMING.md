# Observable timing protocol

The user requested timing of every research turn, including tools, computation, retries, and reading separately. The provided logger measures observable wall-clock intervals, not hidden cognitive processes.

Start a fresh session before reading/research:

```bash
python tools/timing.py start turn001
python tools/timing.py phase turn001 reading --note "Read Chapters 7--9"
```

When leaving a reading window:

```bash
python tools/timing.py phase turn001 reasoning_writing
```

Measure computation, including process startup and unsuccessful attempts:

```bash
python tools/timing.py run turn001 --category computation --timeout 180 -- python tools/run_check.py --suite A11 --workers 4
```

Bracket an external browsing call with phase changes:

```bash
python tools/timing.py phase turn001 network_tool --note "Primary-source lookup"
# Invoke the available browsing tool here.
python tools/timing.py phase turn001 reading --note "Review returned source"
```

A local download/import can be measured directly:

```bash
python tools/timing.py run turn001 --category network_tool --timeout 180 -- python tools/import_references.py --fetch --extract
```

At the last possible point before the final reply:

```bash
python tools/timing.py report turn001 --stop
```

Report the total, marked reading/review, computation, external-tool/network windows, failures and retries, and any unclassified/mixed residual. The report's categories are exclusive wall-clock intervals. Concurrent child workers are not added. The per-command output and return code are retained, including timeout and failure.

## Limits that must be stated

- “Reading” is an intentionally marked review interval, including interpretation, not a measurement of reading independent of thinking.
- “Reasoning/writing” is a designated phase. Do not claim it measures pure internal reasoning.
- A network-tool interval includes DNS, service/server processing, transport, and tool orchestration. Pure network latency is generally unavailable.
- Before the initial timestamp and after the final snapshot, generation, delivery, and tiny log writes are outside the measured interval. Do not claim a user-interface end-to-end timer.
- Copying a historical report does not rerun a computation. Never add historical test runtimes to the current turn.
- A subprocess can fail or time out; its elapsed time remains part of the turn. Do not report only the successful final run.

The export's own measurement has these same limitations. Files in `provenance/` identify which intervals were actually instrumented.
