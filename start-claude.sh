#!/usr/bin/env bash
set -euo pipefail

# Edit this when you want a different auto-compaction budget for the next launch.
# It mirrors AUTO_COMPACT_TOKENS in start-codex.sh; Claude Code has no separate
# context-window cap below the model's own window.
readonly AUTO_COMPACT_TOKENS=550000

cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
export VISUAL=vim
export EDITOR=vim

mode=auto
case "${1-}" in
  --new) mode=new; shift ;;
  --resume) mode=resume; shift ;;
  -h|--help)
    printf '%s\n' 'Usage: ./start-claude.sh [--new|--resume]' \
      'Default: resume the exact ID in .claude-session-id, or start fresh.' \
      '--new starts a fresh session and binds its ID to this checkout.'
    exit 0 ;;
esac
if (( $# )); then
  printf '%s\n' 'Unexpected arguments. Use ./start-claude.sh --help.' >&2
  exit 2
fi

options=(--permission-mode auto --autocompact "${AUTO_COMPACT_TOKENS}")
if [[ "$mode" != new && -f .claude-session-id ]]; then
  session_id="$(cat .claude-session-id)"
  if [[ ! "$session_id" =~ ^[[:xdigit:]]{8}-[[:xdigit:]]{4}-[[:xdigit:]]{4}-[[:xdigit:]]{4}-[[:xdigit:]]{12}$ ]]; then
    printf '%s\n' 'Invalid .claude-session-id. Use --new to establish a fresh session.' >&2
    exit 1
  fi
  exec claude --resume "$session_id" "${options[@]}"
fi
if [[ "$mode" == resume ]]; then
  printf '%s\n' 'No session ID is recorded for this checkout. Run without --resume to start fresh.' >&2
  exit 1
fi

# Claude Code accepts the session ID at launch, so the launcher binds it directly.
session_id="$(python3 -c 'import uuid; print(uuid.uuid4())')"
printf '%s\n' "$session_id" > .claude-session-id

bootstrap='Restore this repository research context. Read research/notes/RESUME.md fully and follow its restart checklist. Read the notebook living overview and load further sources only as needed; do not repeat the full handoff import. Summarize readiness without beginning a new research attempt.'
exec claude --session-id "$session_id" "${options[@]}" "$bootstrap"
