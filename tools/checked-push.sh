#!/usr/bin/env bash
# Push the current branch only if the pre-publication checks pass (AGENTS.md, publication).
# The checks run in parallel; each one's exit status gates the push, and its output is shown
# in full, in order.
set -euo pipefail
branch="$(git rev-parse --abbrev-ref HEAD)"
git fetch -q origin
logs="$(mktemp -d)"
trap 'rm -rf "$logs"' EXIT
python3 tools/verify-checkout.py --public-history "$branch" > "$logs/1" 2>&1 & verify=$!
python3 tools/check-append-only.py --base "origin/$branch" > "$logs/2" 2>&1 & append=$!
python3 tools/notebook_context.py --all > "$logs/3" 2>&1 & context=$!
failed=0
for check in "1 $verify" "2 $append" "3 $context"; do
  set -- $check
  wait "$2" || failed=1
  cat "$logs/$1"
done
[ "$failed" = 0 ] || { echo "Not pushed: a pre-publication check failed." >&2; exit 1; }
git push -q origin "$branch"
git log --oneline -1
