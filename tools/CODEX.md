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

Codex temporary files belong in the directory printed by `python3 tools/codex_state.py scratch`.
The startup/child hook supplies the same owner path. The finisher refuses more than 500 MB of
logical bytes, unreadable scratch, or symlinks in that tree or its runtime ancestors. It never
deletes files. Other actors and durable results are excluded; legacy Claude scratch lookup
continues to use the existing Claude locations.
