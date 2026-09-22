#!/usr/bin/env bash
set -euo pipefail

# Edit this when you want a different auto-compaction budget for the next launch.
# Claude Code accepts 100k-1M here and has no separate context-window cap below the
# model's own window. start-codex.sh keeps its own AUTO_COMPACT_TOKENS.
readonly AUTO_COMPACT_TOKENS=800000

cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
export VISUAL=vim
export EDITOR=vim

mode=auto
attach=1
while (( $# )); do
  case "$1" in
    --new) mode=new ;;
    --resume) mode=resume ;;
    --detached) attach=0 ;;
    -h|--help)
      printf '%s\n' 'Usage: ./start-claude.sh [--new|--resume] [--detached]' \
        'Run the session as a background session and attach this terminal to it.' \
        'Closing the terminal only detaches; the session keeps running and stays' \
        'reachable from the Claude app through Remote Control.' \
        'Default: attach to the running session in .claude-session-id, or resume it' \
        'in the background first, or start fresh when no ID is recorded.' \
        '--new starts a fresh session and binds its ID to this checkout.' \
        '--detached starts or reuses the background session without attaching.'
      exit 0 ;;
    *)
      printf '%s\n' 'Unexpected arguments. Use ./start-claude.sh --help.' >&2
      exit 2 ;;
  esac
  shift
done

# Short id of the running background session with this full session ID, if any.
running_background() {
  claude agents --json | python3 -c '
import json, sys
wanted = sys.argv[1]
for agent in json.load(sys.stdin):
    if agent.get("kind") == "background" and agent.get("sessionId") == wanted:
        print(agent["id"]); break
' "$1"
}

# Short id of any background session, running or stopped, with this full session ID.
known_background() {
  claude agents --json --all | python3 -c '
import json, sys
wanted = sys.argv[1]
for agent in json.load(sys.stdin):
    if agent.get("kind") == "background" and agent.get("sessionId") == wanted:
        print(agent["id"]); break
' "$1"
}

open_session() {
  local session_id=$1 short='' tries
  # claude --bg returns at once; give the new session a moment to register.
  for tries in 1 2 3 4 5 6 7 8 9 10; do
    short="$(running_background "$session_id")"
    [[ -n "$short" ]] && break
    sleep 0.5
  done
  if [[ -z "$short" ]]; then
    printf '%s\n' 'Background session did not start; see claude agents --all.' >&2
    exit 1
  fi
  if (( attach )); then
    exec claude attach "$short"
  fi
  printf 'Background session %s is running; attach with: claude attach %s\n' "$short" "$short"
}

# These options are saved with a session when it first runs in the background and apply to
# every later resume. --remote-control takes an optional name, so keep another flag after it.
options=(--bg --remote-control --permission-mode auto --autocompact "${AUTO_COMPACT_TOKENS}")
if [[ "$mode" != new && -f .claude-session-id ]]; then
  session_id="$(cat .claude-session-id)"
  if [[ ! "$session_id" =~ ^[[:xdigit:]]{8}-[[:xdigit:]]{4}-[[:xdigit:]]{4}-[[:xdigit:]]{4}-[[:xdigit:]]{12}$ ]]; then
    printf '%s\n' 'Invalid .claude-session-id. Use --new to establish a fresh session.' >&2
    exit 1
  fi
  # Never start a second copy of a session that is already running in the background.
  # A known background session keeps the options it was first started with, and any flag
  # passed on resume starts a copy under a new ID, so resume it with --bg alone.
  if [[ -z "$(running_background "$session_id")" ]]; then
    if [[ -n "$(known_background "$session_id")" ]]; then
      claude --bg --resume "$session_id" >/dev/null
    else
      claude --resume "$session_id" "${options[@]}" >/dev/null
    fi
  fi
  open_session "$session_id"
  exit 0
fi
if [[ "$mode" == resume ]]; then
  printf '%s\n' 'No session ID is recorded for this checkout. Run without --resume to start fresh.' >&2
  exit 1
fi

# Claude Code accepts the session ID at launch, so the launcher binds it directly.
session_id="$(python3 -c 'import uuid; print(uuid.uuid4())')"
printf '%s\n' "$session_id" > .claude-session-id

bootstrap='Restore this repository research context. Run python3 tools/resume.py and read every listed part with separate bounded outputs. Retry missing parts without preparing another resume. Follow its included restart guide without rereading bundled files; load further sources only as needed; do not repeat the full handoff import. Summarize readiness without beginning a new research attempt.'
claude --session-id "$session_id" "${options[@]}" "$bootstrap" >/dev/null
open_session "$session_id"
