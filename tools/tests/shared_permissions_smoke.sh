#!/bin/sh
# Run through compute.sh from a linked worktree. No bytes are written to the shared files.
# This tests the native sandbox, not a model's report or a mock permission matcher.
set -eu
root=$(git rev-parse --show-toplevel)
common=$(git rev-parse --path-format=absolute --git-common-dir)
main=$(dirname "$common")
test "$root" != "$main" || { echo 'Run this check from a linked worktree.' >&2; exit 2; }
cd "$root"
codex sandbox -- sh -c '
    for name in user_requests run_state; do
        test -L "$name" && : >> "$name" || exit 1
    done
    test ! -w "$1/AGENTS.md" && test ! -w .git && test ! -w .codex
' sh "$main"
echo 'PASS: default project profile opens both links for writing; unrelated main files and metadata stay read-only.'
if codex sandbox -P :workspace -- sh -c ': >> user_requests'; then
    echo 'FAIL: control profile unexpectedly writes outside its workspace.' >&2
    exit 1
fi
echo 'PASS: built-in workspace control refuses the same linked-file write.'
