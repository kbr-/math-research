#!/usr/bin/env bash
# Push only if the pre-publication checks pass (AGENTS.md, publication).
# Usage: tools/checked-push.sh [TARGET]. Without TARGET the current branch is pushed to its
# namesake on origin. With TARGET (for example main, from a worktree branch) the checks run
# against origin/TARGET and HEAD is pushed to TARGET, only as a fast-forward.
# The checks run in parallel; each one's exit status gates the push, and its output is shown
# in full, in order. The commit is fixed when the script starts, and if HEAD moves while the
# checks run, nothing is pushed. Before the push the script prints how many commits and bytes
# it sends; after it, the branch is read back from the remote and compared with that commit, so
# the output says what the remote holds.
set -euo pipefail
branch="${1:-$(git rev-parse --abbrev-ref HEAD)}"
commit="$(git rev-parse HEAD)"
git fetch -q origin
if git rev-parse -q --verify "origin/$branch" > /dev/null && ! git merge-base --is-ancestor "origin/$branch" "$commit"; then
  echo "Not pushed: origin/$branch is not an ancestor of HEAD; rebase first." >&2
  exit 1
fi
# Commit messages: every line at most 100 characters (AGENTS.md); checked on the commits to be pushed.
long=""
for c in $(git rev-list "$commit" --not --remotes=origin); do
  # Characters, not bytes: awk under LC_ALL=C counted an 88-character line with dashes as 154.
  long="$long$(git log -1 --format=%B "$c" | python3 -c '
import sys
ident = sys.argv[1]
for line in sys.stdin.buffer.read().decode("utf-8", "replace").splitlines():
    if len(line) > 100:
        print(ident + ": " + line[:60] + "...")' "$(git rev-parse --short "$c")")"
done
if [ -n "$long" ]; then
  printf 'Not pushed: commit message lines over 100 characters (AGENTS.md):\n%s\n' "$long" >&2
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
if [ "$(git rev-parse HEAD)" != "$commit" ]; then
  echo "Not pushed: HEAD moved from $(git rev-parse --short "$commit") while the checks ran; run it again." >&2
  exit 1
fi
# What the remote lacks, measured as the thin pack a push builds against its branches.
commits="$(git rev-list --count "$commit" --not --remotes=origin)"
bytes="$({ echo "$commit"; git for-each-ref --format='^%(objectname)' refs/remotes/origin; } \
  | git pack-objects --revs --thin --stdout -q | wc -c)"
echo "Pushing $commits commits, $(numfmt --to=iec --suffix=B "$bytes"), to origin/$branch."
git push -q origin "$commit:refs/heads/$branch"
# The push's exit status says the update was accepted, not what the branch holds now.
remote_tip="$(git ls-remote origin "refs/heads/$branch" | cut -f1)"
if [ "$remote_tip" != "$commit" ]; then
  echo "Pushed, but origin/$branch is at ${remote_tip:-nothing}, not $(git rev-parse --short "$commit")." >&2
  exit 1
fi
echo "origin/$branch is at $(git log --oneline -1 "$commit"), the commit pushed."

# Fast-forward the local branch of the same name to the pushed commit (ff-base.sh, which never pushes), so
# the base never lags its remote; a branch that cannot be fast-forwarded is reported, not a failed push.
tools/ff-base.sh --no-rebase "$branch" || true
