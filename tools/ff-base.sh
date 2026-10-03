#!/usr/bin/env bash
# Keep a worktree's base branch level with it, without pushing (CLAUDE.md, background sessions).
# Usage: tools/ff-base.sh [--no-rebase] [BRANCH]
# BRANCH defaults to the current branch's upstream when that is a local branch (set it once with
# git branch --set-upstream-to=BASE), so nothing depends on how the worktree's branch is named.
# Rebases HEAD onto BRANCH when BRANCH has commits HEAD lacks, then fast-forwards the local BRANCH to HEAD:
# its ref when no worktree has it checked out, else that worktree, when it is clean. A conflict stops the
# rebase with git's own instructions. --no-rebase only fast-forwards, as tools/checked-push.sh does after a
# push. It never pushes. (Ported from the business framework, 3 October 2026, without its site-terms merge
# driver: main has no site registry.)
set -euo pipefail
rebase=1
if [ "${1:-}" = "--no-rebase" ]; then rebase=0; shift; fi
[ $# -le 1 ] || { echo "Usage: tools/ff-base.sh [--no-rebase] [BRANCH]" >&2; exit 2; }
if [ $# -eq 1 ]; then
  branch="$1"
else
  branch="$(git rev-parse -q --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || true)"
  if [ -z "$branch" ] || ! git show-ref -q --verify "refs/heads/$branch"; then
    echo "No BRANCH given and $(git rev-parse --abbrev-ref HEAD) has no local upstream: set one with" \
         "git branch --set-upstream-to=BASE, or name the branch." >&2
    exit 2
  fi
fi
if [ "$(git rev-parse --abbrev-ref HEAD)" = "$branch" ] || ! git show-ref -q --verify "refs/heads/$branch"; then
  exit 0
fi
if [ "$rebase" = 1 ] && ! git merge-base --is-ancestor "$branch" HEAD; then
  if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
    echo "Not rebased: the worktree has uncommitted changes; commit them first." >&2
    exit 1
  fi
  if ! git rebase -q "$branch"; then
    echo "Rebase onto $branch stopped on a conflict: resolve it, run git rebase --continue, then" \
         "tools/ff-base.sh $branch again." >&2
    exit 1
  fi
  echo "Rebased onto $branch."
fi
commit="$(git rev-parse HEAD)"
old="$(git rev-parse "refs/heads/$branch")"
if [ "$old" = "$commit" ]; then
  exit 0
elif ! git merge-base --is-ancestor "$old" "$commit"; then
  echo "Local $branch not fast-forwarded: it is not an ancestor of $(git rev-parse --short "$commit")." >&2
  exit 1
fi
where="$(git worktree list --porcelain | awk -v ref="branch refs/heads/$branch" '
  /^worktree / { path = substr($0, 10) } $0 == ref { print path }')"
if [ -z "$where" ]; then
  git update-ref "refs/heads/$branch" "$commit" "$old"
  echo "Local $branch fast-forwarded to $(git rev-parse --short "$commit")."
elif [ -z "$(git -C "$where" status --porcelain --untracked-files=no)" ]; then
  git -C "$where" merge -q --ff-only "$commit"
  echo "Local $branch fast-forwarded to $(git rev-parse --short "$commit") in $where."
else
  echo "Local $branch not fast-forwarded: $where has uncommitted changes." >&2
  echo "  Run: git -C '$where' merge --ff-only $commit" >&2
  exit 1
fi
