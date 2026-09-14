#!/usr/bin/env bash
set -euo pipefail
compute_args=()
verify_args=()
while [[ $# -gt 0 ]]; do
    case "$1" in
        --session)
            if [[ $# -lt 2 || -z "$2" || "$2" == --* || ${#compute_args[@]} -ne 0 ]]; then
                echo 'Usage: verify.sh [--session TURN] [--out PATH]' >&2
                exit 2
            fi
            compute_args=(--session "$2")
            shift 2
            ;;
        --help|-h)
            echo 'Usage: verify.sh [--session TURN] [--out PATH]'
            echo 'Use an existing research timing session; save complete output to a new file.'
            exit 0
            ;;
        *) verify_args+=("$1"); shift ;;
    esac
done
repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -f "$HOME/.elan/env" ]]; then
    source "$HOME/.elan/env"
fi
cd "$repo_root"
exec ./compute.sh --threads 2 --timeout 600 --category formal_verification \
    "${compute_args[@]}" python3 formalization/verify.py "${verify_args[@]}"
