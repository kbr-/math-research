#!/usr/bin/env bash
# Push only if the pre-publication checks pass (AGENTS.md, publication).
# Usage: tools/checked-push.sh [TARGET]. Without TARGET the current branch is pushed to its
# namesake on origin. With TARGET (for example main, from a worktree branch) the checks run
# against origin/TARGET and HEAD is pushed to TARGET, only as a fast-forward.
# The checks run in parallel; each one's exit status gates the push, and its output is shown
# in full, in order. After the push, the branch is read back from the remote and compared with
# HEAD, so the output says what the remote holds.
set -euo pipefail
branch="${1:-$(git rev-parse --abbrev-ref HEAD)}"
git fetch -q origin
if git rev-parse -q --verify "origin/$branch" > /dev/null && ! git merge-base --is-ancestor "origin/$branch" HEAD; then
  echo "Not pushed: origin/$branch is not an ancestor of HEAD; rebase first." >&2
  exit 1
fi
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
git push -q origin "HEAD:refs/heads/$branch"
# The push's exit status says the update was accepted, not what the branch holds now.
remote_tip="$(git ls-remote origin "refs/heads/$branch" | cut -f1)"
if [ "$remote_tip" != "$(git rev-parse HEAD)" ]; then
  echo "Pushed, but origin/$branch is at ${remote_tip:-nothing}, not HEAD $(git rev-parse --short HEAD)." >&2
  exit 1
fi
echo "origin/$branch is at $(git log --oneline -1 HEAD), the local tip."
