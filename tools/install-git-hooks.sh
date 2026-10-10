#!/bin/sh
# Link this workspace's git hooks into each given repository (default: this one).
# Usage: ./tools/install-git-hooks.sh [REPO ...]
# A worktree shares its main clone's hooks, so installing into the clone covers its worktrees.
# An existing hook that isn't already this link is left alone and reported.
set -eu
here=$(cd "$(dirname "$0")/git-hooks" && pwd)
[ $# -gt 0 ] || set -- "$(cd "$(dirname "$0")/.." && pwd)"
status=0
for repo in "$@"; do
    dir=$(git -C "$repo" rev-parse --path-format=absolute --git-common-dir)/hooks
    if [ -n "$(git -C "$repo" config --get core.hooksPath || true)" ]; then
        echo "$repo: core.hooksPath is set; add the hooks there by hand" >&2; status=1; continue
    fi
    for hook in "$here"/*; do
        target="$dir/$(basename "$hook")"
        if [ -L "$target" ] && [ "$(readlink "$target")" = "$hook" ]; then
            echo "$repo: $(basename "$hook") already installed"
        elif [ -e "$target" ]; then
            echo "$repo: $(basename "$hook") exists and differs; left alone" >&2; status=1
        else
            ln -s "$hook" "$target" && echo "$repo: $(basename "$hook") installed"
        fi
    done
done
exit $status
