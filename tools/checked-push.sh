#!/usr/bin/env bash
# Push the current branch only if the pre-publication checks pass (AGENTS.md, publication).
# Each check's own exit status gates the push; output is shown in full.
set -euo pipefail
branch="$(git rev-parse --abbrev-ref HEAD)"
git fetch -q origin
python3 tools/verify-checkout.py --public-history "$branch"
python3 tools/check-append-only.py --base "origin/$branch"
python3 tools/notebook_context.py --all
git push -q origin "$branch"
git log --oneline -1
