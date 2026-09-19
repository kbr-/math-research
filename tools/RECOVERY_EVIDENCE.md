# Automatic recovery evidence

The existing tools collect a baseline before we decide whether interruption notes
would pay for themselves. One explicit resume preparation collects the required
files; bounded reads deliver them without oversized tool responses. Other hooks
add no routine console output or agent steps.
This measures observable proxies, not forgotten ideas, and never scans transcripts.

- `python3 tools/resume.py` explicitly marks restoration and saves the required
  guide, instructions, living sections and compact TOC in ignored runtime storage.
  Preparation immediately emits part 1 with a compact ID/count header; subsequent
  `--read ID --part N` calls emit at most 16,000 UTF-8 payload bytes plus small
  delimiters and the next command. There is no manifest-only round trip. Read all parts,
  never concatenate them into one oversized response. This is not proof that
  compaction occurred: restoration may follow a restart or fresh session. Ordinary
  `notebook-excerpt.py --current` calls never start/reset a recovery window. Repeated
  explicit preparations censor the earlier window rather than inventing a duration.
  Part reads/retries do not start a new resume or reset timing. Only emitted parts
  are logged as reads; saving the bundle is not falsely counted as loaded context.
  The command finds the identified stream's active timing session, or accepts
  `--session TURN`; it marks a **Context restoration** phase there. No session is
  started for a restoration-only request. `--formalization` includes the extra
  instructions only for an assigned formalization task.
- Existing `compute.sh phase` markers for mathematics, coding, formalization or
  legacy reasoning/writing end the window. A job categorized computation or formal
  verification also ends it. This is time until an observed work marker, not a
  semantic detector of substantive progress. Idle time is included; the largest
  observation gap is reported. Reads before the resume marker are outside the window.
  Timing tables retain ordinary exclusive phase/tool accounting: the restoration
  row is not added on top of time already charged elsewhere.
- Notebook excerpts/TOC, claim search/list/exact lookup and claim packets silently
  record output fingerprints and bytes. Repeats require the same tool, selector and
  unchanged output. Saved-only operations are distinguished from emitted output.
  Bundle separators are excluded from payload counts. Captured/truncated output is not necessarily delivered to the agent; byte counts
  are neither tokens nor proof that the agent read the text. Arbitrary shell `cat`,
  `rg`, editor reads and internal reasoning are not observable through these hooks.
- Protected job starts/completions record whether the identical command previously
  succeeded in the same identified stream. Inputs may have changed, rerunning may
  be warranted, and tests may capture other tools' output. Treat these as possible
  repeats to inspect against the existing timing journals, never automatically as
  duplicated work. Job records distinguish the recovery window from later jobs.
- Reboot, checkpoint without a work marker, and unclosed windows retain explicit
  censored/open status with no made-up recovery duration. A stream with no reliable
  identity still records the explicit resume and unattributed operations, but no
  attributed recovery duration. An explicit active session still gets its timing phase.

## Storage, reports and privacy

Local state is in the already ignored `research/logs/recovery.sqlite`. It contains
no source text, query strings, raw command arguments or raw agent-session IDs.
Session identity is hashed only for local routing; neither that routing key nor
boot IDs are exported. Systemd children inherit an opaque routing key. Automatic
identity uses `CODEX_THREAD_ID` or `CLAUDE_SESSION_ID` when provided; other hosts can
provide `MATH_RECOVERY_STREAM`. Missing or shared identity limits attribution;
it must not be interpreted as evidence about an individual agent.

`research/logs/resume-bundles/` holds temporary delivery caches, not a second
research record or tracked historical snapshot. Each preparation saves one complete
UTF-8 file and byte-range/hash manifest. Reads use that fixed payload even if source
files subsequently change, verify part integrity, and never split a UTF-8 character.
Do not commit these caches. Their read fingerprints are chunk-based, so changing
source lengths can shift boundaries and conservatively reduce repeat detection.

Existing timing summaries acquire a `recovery_proxy` field for newly instrumented
sessions. Normal `compute.sh report` output and timing tables are unchanged; the
existing archive helper preserves the complete summary automatically. Snapshots
are frozen at their timing cutoff, and uninstrumented historical summaries are not
retrofitted. There is no retrospective baseline or transcript import.

Unbound resumes (restoration without a timing session) remain in local state.
To inspect/export all collected resumes, when requested:

```bash
./compute.sh --threads 1 --category local_processing \
  python3 tools/recovery_evidence.py --out /tmp/recovery-evidence.json
```

Use `--session TURN` for a selected timing session. Exports contain opaque episode
IDs, per-read fingerprints/counts and job IDs linking to timing records. They omit
source content and local routing identities. Inspect the evidence after several
resumptions before proposing any interruption-note requirement or claiming savings.
The full record, index and existing task plans remain the recovery sources.

Collection is best-effort: short SQLite lock timeouts cannot stall research.
Failures are recorded by exception type in an ignored error journal and exposed
in reports, without leaking exception paths/content. An unavailable collector is
reported as unavailable, never as zero overhead. `MATH_RECOVERY_DISABLED=1` opts out
(also useful for automated test suites); recorded summaries label that state.
This does not alter resource enforcement or the timing categories. The small
metadata hooks add local processing time, but no extra routine model interaction.
