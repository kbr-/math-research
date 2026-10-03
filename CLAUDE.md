@AGENTS.md

# Claude-specific instructions

Shared research and framework rules are in AGENTS.md; computation policy is in
[COMPUTATION_RULES.md](COMPUTATION_RULES.md).

In a Spin loop driven by ScheduleWakeup, the delay is only a fallback re-entry
point. Continue work under AGENTS.md's Spin rules and re-arm with a short delay
(about 60 seconds). Use long delays only for genuinely blocked waits, such as a
running reviewer or background batch.

Background sessions work in one long-lived worktree under `.claude/worktrees/`, never the shared
checkout. Create a missing one from the base branch with
`git worktree add --track -b <name> .claude/worktrees/<name> main` and enter it by path; `--track`
makes `main` the new branch's upstream, git's record of its base (a worktree made without it gets
one with `git branch --set-upstream-to=main <name>`). The name is a convention only. After every
commit, with or without a push grant, since only pushes need one, run `tools/ff-base.sh`: it rebases
the worktree onto its upstream when that has moved and fast-forwards the local upstream branch,
never pushing (user, 3 October 2026). The `base_behind` hook reminds after any commit that leaves
the base behind, or when no upstream is set; `tools/checked-push.sh` fast-forwards the local branch
after a push.