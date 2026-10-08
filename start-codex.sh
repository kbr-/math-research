#!/usr/bin/env bash
set -euo pipefail

start_codex_daemon() {
  # Managed startup reuses a running daemon and enables remote control.
  # Never restart here: another terminal or the phone may be using it.
  codex remote-control start
}

# The session launcher sources this function without starting any process.
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  case "${1-}" in
    -h|--help)
      printf '%s\n' 'Usage: ./start-codex.sh' \
        'Start or reuse the background Codex daemon with remote control enabled.' \
        'Use ./start-session.sh [--new|--resume] to open the terminal session.'
      exit 0 ;;
  esac
  if (( $# )); then
    printf '%s\n' 'Unexpected arguments. Session options belong to ./start-session.sh.' >&2
    exit 2
  fi
  cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
  export VISUAL=vim EDITOR=vim
  start_codex_daemon
fi
