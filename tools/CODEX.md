# Codex framework hooks

`.codex/hooks.json` registers one ordered command handler per event. Review and trust these
hooks through the normal Codex CLI before treating them as active; project trust alone does
not trust a changed hook definition. Missing scripts emit a visible, nonblocking warning.
The installed hooks can be inspected through the native `hooks/list` interface.

At startup, resume and compaction, supported tool calls are gated on restoration. Run
`python3 tools/resume.py` and read every listed part with default output allowances, including
any outer code-mode wrapper. Receipts compare the full UTF-8 payload to its cached manifest;
truncation, another bundle and an omitted part cannot clear the gate. A receipt proves delivery
to the tool caller, not model comprehension or rendering by an outer program. Retry missing
parts without preparing a new bundle. Root and child actors have separate locked state under
ignored `.codex/framework/`; no runtime identity is committed. There is no age-only deletion
of another live actor's state.

The command checks reuse the existing full-output and dependent-heredoc guards. Post-commit
feedback reports local-upstream lag as context, preserving the actual command's result.
Native hooks do not cover every hosted tool or an already-running `write_stdin` session;
these protections supplement the rules in AGENTS.md rather than supersede them.

Codex temporary files belong under ignored `research/tmp/codex/`, in the directory printed by
`python3 tools/codex_state.py scratch`. Configuration directories such as `.codex` are read-only
in an ordinary workspace-write sandbox and cannot hold agent-written scratch.
The startup/child hook supplies the same owner path. The finisher refuses more than 500 MB of
logical bytes, unreadable scratch, or symlinks in that tree or its runtime ancestors. It never
deletes files. Other actors and durable results are excluded; legacy Claude scratch lookup
continues to use the existing Claude locations.

`python3 tools/register_codex.py` registers the checkout's present `skills/*/SKILL.md` sources
through relative links. The launcher runs it before startup/resume. Missing sources are removed
only if their generated descriptors still match the managed manifest; unrelated or edited files
are preserved with an error. Nothing is installed globally. Commit canonical relative links with their source branch so phone-created sessions and fresh
clones discover them without a launcher. The verifier admits only links to that checkout's
`skills/NAME/SKILL.md`; the runtime ownership manifest remains ignored. Keep private links and
skill text on their private branch.

Use `python3 tools/codex_reviewer.py --handle NAME --brief FILE` for a fresh reviewer.
The helper uses the running authenticated daemon and the installed `websockets` package;
it never starts or reconfigures the daemon. Run inference through `compute.sh`. The native
root session has medium effort, read-only filesystem access and no approval escalation;
its effective policy is checked before sending the brief. Its instructions come from the
body of `.claude/agents/medium-reviewer.md`, not the parent conversation. Native child agents
inherit the parent's live permission overrides, so a custom child profile alone does not
provide this isolation. Reuse the handle only for a concrete correction to the same review;
`--close` archives that owned session. An interrupted review keeps its local handle for
recovery. Reviewer handles never replace `.codex-session-id`.

`./start-session.sh [--new|--resume] [--detached] [--worktree NAME] [--base BRANCH]`
starts/reuses the existing daemon, selects a persistent Git worktree and registers its skills.
An existing linked worktree is retained and must have a local upstream. A shared checkout uses
`.codex/worktrees/codex-BASE` by default. Folder and hook trust are separate: startup refuses
missing, disabled, duplicate or untrusted framework hooks. Run the normal CLI **from the target
directory with `-C` naming that directory**, review the displayed hook source through `/hooks`,
and retry; remote startup otherwise can use the daemon's default directory for initial UI state.
Never bypass trust or edit its saved decisions by hand.

The external launcher serializes startup, creates the native root with workspace-write and
automatic approval review, materializes an initialization record without inference, then binds
its exact ID before requesting restoration. A failed restoration request preserves that binding
for retry. A creation interrupted before binding retains its pending ID; retry attempts that ID
and reports failure rather than creating a replacement. `--new` deliberately creates a new
session. Detached mode returns after native acceptance; it does not claim restoration is already
finished. Normal mode attaches the terminal. Resume checks the saved working directory and does
not override permissions. Run launchers outside agent shells: agent and worker invocations cannot
replace the main binding. `remember-codex-session.py` now only verifies the externally saved ID.

## Background monitoring

In the functions.exec harness, evaluate tools/codex_monitor.js and call the returned function
with tools, notify, yield_control, the absolute checkout root, a started timing session, and
compute.sh arguments as a string array:

```javascript
const source = await tools.exec_command({cmd: "cat tools/codex_monitor.js", workdir: root});
const monitor = eval(source.output);
text(await monitor({tools, notify, yield_control, root, session,
  args: ["--threads", "1", "--timeout", "180", "--", "python3", "calculation.py"]}));
```

The helper arms watch_run.py before releasing the protected job, yields the cell, and forwards
its five-minute decision point, completion, and full controller output through notify. Continue
independent work while the cell runs; reap it with functions.wait when complete. The launcher
rejects long native runs without a live owned watcher and refuses duplicate run IDs.

To cancel, run `python3 tools/watch_run.py --cancel RUN_ID` from the same checkout/thread,
using the ID printed in WATCH_READY. This stops the recorded protected service and its children.
Cancel before terminating or abandoning a cell: terminating JavaScript alone is not a service
cancellation operation. Keep the cell alive until completion; delivery after session termination
is not guaranteed. Operational state is ignored under research/logs/codex-watchers. These
harness primitives do not create another agent, resume the owner, or inject synthetic user turns.

## Branch-local Stop judging

The shared Stop registration calls tools/hooks/codex_unchecked_claim.py in the active worktree
when that optional private handler exists. Main contains no private predicate or prompt.
The handler can call tools/codex_judge.py with a JSON object containing prompt and schema on
stdin. It returns result or a visible error category, without forwarding daemon diagnostics.
Use a 4.5-second subprocess timeout within the five-second hook budget.

Inference uses the existing login/daemon in a fresh ephemeral gpt-6-luna thread at low effort,
read-only/no-approval, with no environments, project instructions, shell, web, apps or hooks.
It interrupts timed-out inference and unsubscribes the owned thread. No Claude fallback or
additional login is used. Host-side validation of the returned schema and quoted evidence is
the handler's responsibility; a structured model response alone does not establish correctness.
