#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
source ./start-codex.sh
export VISUAL=vim EDITOR=vim
case "${1-}" in
  -h|--help)
    printf '%s\n' 'Usage: ./start-session.sh [--new|--resume] [--detached] [--worktree NAME] [--base BRANCH]' \
      'Use one persistent Git worktree and externally bind its exact native session.' \
      'Resume preserves permissions. Detached startup returns after native acceptance.'
    exit 0 ;;
esac
if [[ -n "${CODEX_THREAD_ID-}" ]]; then
  printf '%s\n' 'Run the session launcher outside an agent; workers cannot replace session bindings.' >&2
  exit 1
fi
start_codex_daemon
exec python3 tools/codex_sessions.py --context "$CONTEXT_WINDOW_TOKENS" \
  --compact "$AUTO_COMPACT_TOKENS" "$@"
