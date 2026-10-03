#!/usr/bin/env python3
"""PostToolUse hook for Bash: after a git commit, report when the branch's base is not at the new commit, so the
session runs tools/ff-base.sh (CLAUDE.md, background sessions).

The base is git's own record of it, the branch's upstream, when that is a local branch: whatever the session named
its worktree's branch (user, 3 October 2026: "The hook should be generic over how the session named its
worktree"). A linked worktree whose branch has no upstream gets a reminder to set one; the main checkout, and a
branch tracking only a remote branch, are left alone.

A session stopped fast-forwarding its base when its push grant was withdrawn, though the withdrawal covered pushes
only, and the base fell 380 commits behind (user, 3 October 2026: "I thought you were always rebasing and
fast-forwarding business to business-work after every git commit?").  Ported to main
from the business framework the same day."""
import json
import os
import re
import subprocess
import sys


def git(*args, cwd=None):
    result = subprocess.run(['git', *args], cwd=cwd, capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else None


def base_of(cwd=None):
    """(branch, local upstream branch or None, linked worktree?), or None outside a branch."""
    branch = git('symbolic-ref', '-q', '--short', 'HEAD', cwd=cwd)
    if not branch:
        return None
    upstream = git('rev-parse', '--abbrev-ref', '--symbolic-full-name', '@{upstream}', cwd=cwd)
    local = upstream if upstream and git('show-ref', '-q', '--verify', f'refs/heads/{upstream}', cwd=cwd) is not None \
        else None
    git_dir, common = git('rev-parse', '--git-dir', cwd=cwd), git('rev-parse', '--git-common-dir', cwd=cwd)
    linked = bool(git_dir and common) and os.path.realpath(os.path.join(cwd or '.', git_dir)) != \
        os.path.realpath(os.path.join(cwd or '.', common))
    return branch, local, linked


def message(command, cwd=None):
    """The reminder for this command, or None."""
    if not re.search(r'\bgit\s+(?:-c\s+\S+\s+)*commit\b', command) or '--dry-run' in command:
        return None
    found = base_of(cwd)
    if not found:
        return None
    branch, base, linked = found
    if base is None:
        if not linked or git('rev-parse', '--abbrev-ref', '--symbolic-full-name', '@{upstream}', cwd=cwd):
            return None
        return (f'Branch {branch} has no upstream, so its base cannot be kept level: set it once with git branch '
                f'--set-upstream-to=<base> {branch}, then run tools/ff-base.sh (CLAUDE.md, background sessions).')
    if git('rev-parse', f'refs/heads/{base}', cwd=cwd) == git('rev-parse', 'HEAD', cwd=cwd):
        return None
    return (f'Local {base}, the upstream of {branch}, is not at this commit: run tools/ff-base.sh now, which rebases '
            f'onto {base} if needed and fast-forwards it without pushing (CLAUDE.md, background sessions).')


def main():
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return 0
    text = message(event.get('tool_input', {}).get('command', ''), event.get('cwd'))
    if text:
        print(json.dumps({'decision': 'block', 'reason': text}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
