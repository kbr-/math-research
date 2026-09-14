#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -f "$HOME/.elan/env" ]]; then
    source "$HOME/.elan/env"
fi
cd "$repo_root"
exec ./compute.sh --threads 2 --timeout 600 --category local_processing \
    python3 formalization/verify.py "$@"
