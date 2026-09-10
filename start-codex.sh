#!/usr/bin/env bash
set -euo pipefail

# Edit these when you want a different context budget for the next launch.
readonly CONTEXT_WINDOW_TOKENS=600000
readonly AUTO_COMPACT_TOKENS=550000

cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
export VISUAL=vim
export EDITOR=vim

mode=auto
case "${1-}" in
  --new) mode=new; shift ;;
  --resume) mode=resume; shift ;;
  -h|--help)
    printf '%s\n' 'Usage: ./start-codex.sh [--new|--resume]' \
      'Default: resume the exact ID in .codex-session-id, or start fresh.' \
      '--new starts a fresh session and binds its ID to this checkout.'
    exit 0 ;;
esac
if (( $# )); then
  printf '%s\n' 'Unexpected arguments. Use ./start-codex.sh --help.' >&2
  exit 2
fi

options=(--approve-for-me
  -c "model_context_window=${CONTEXT_WINDOW_TOKENS}"
  -c "model_auto_compact_token_limit=${AUTO_COMPACT_TOKENS}")
if [[ "$mode" != new && -f .codex-session-id ]]; then
  session_id="$(cat .codex-session-id)"
  if [[ ! "$session_id" =~ ^[[:xdigit:]]{8}-[[:xdigit:]]{4}-[[:xdigit:]]{4}-[[:xdigit:]]{4}-[[:xdigit:]]{12}$ ]]; then
    printf '%s\n' 'Invalid .codex-session-id. Use --new to establish a fresh session.' >&2
    exit 1
  fi
  exec codex resume "$session_id" "${options[@]}"
fi
if [[ "$mode" == resume ]]; then
  printf '%s\n' 'No session ID is recorded for this checkout. Run without --resume to start fresh.' >&2
  exit 1
fi

bootstrap='Restore this repository research context. First run ./tools/remember-codex-session.py to save this main session ID for the launcher. Then read research/notes/RESUME.md fully and follow its restart checklist. Read the notebook living overview and load further sources only as needed; do not repeat the full handoff import. Summarize readiness without beginning a new research attempt.'
exec codex "${options[@]}" "$bootstrap"
