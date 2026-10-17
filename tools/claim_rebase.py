#!/usr/bin/env python3
"""Resolve the registry conflict of a rebase that replays a commit registering claims.

A worktree commit that registers a claim conflicts with its base whenever the base registered another claim in
between: both append to research/claims/index.json and to the generated views.  The resolution is always the
same, and on 11 October 2026 it was made by hand three times: keep the base's registry, rebuild the commit's
claims from their compact spec on top of it, render the views, stage, and recheck.  This tool does exactly
that, and refuses anything else.

Usage, from the worktree whose rebase or cherry-pick stopped:

    tools/claim_rebase.py --spec SPEC.json [--spec MORE.json]

It refuses when no rebase or cherry-pick is in progress, when a conflicted path is not a registry file (the
notebook's conflicts belong to tools/notebook_rebase.py), or when a spec's claim is already in the base's
registry.  It stages the registry files and runs the changed-claim and append-only checks against HEAD; it
does not continue the rebase, so its result is read first:  GIT_EDITOR=true git rebase --continue.
It prints what its work grew with: the claims rebuilt and the registry's size.
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = 'research/claims/index.json'
REGISTRY_PATHS = ('research/claims/', 'research/CLAIM_INDEX.md', 'research/ATTENTION.md')


def is_registry_path(path):
    return path.startswith(REGISTRY_PATHS[0]) or path in REGISTRY_PATHS[1:]


def foreign_conflicts(conflicted):
    """The conflicted paths this tool must not touch."""
    return sorted(p for p in conflicted if not is_registry_path(p))


def already_registered(registry, specs):
    """IDs of the specs' claims that the base's registry already holds."""
    have = {claim['id'] for claim in registry['claims']}
    return sorted(item['id'] for spec in specs for item in spec.get('claims', []) if item['id'] in have)


def git(*args, cwd, check=True):
    done = subprocess.run(['git', *args], cwd=cwd, text=True, capture_output=True)
    if check and done.returncode:
        raise SystemExit(f'git {" ".join(args)} failed: {done.stderr.strip()}')
    return done.stdout


def in_progress(cwd):
    for name in ('rebase-merge', 'rebase-apply', 'CHERRY_PICK_HEAD'):
        if Path(cwd, git('rev-parse', '--git-path', name, cwd=cwd).strip()).exists():
            return True
    return False


def run(command, cwd):
    done = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    if done.returncode:
        raise SystemExit(f'{" ".join(map(str, command))} failed:\n{done.stdout}{done.stderr}')
    return done.stdout


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('--spec', type=Path, action='append', required=True,
                        help='compact claim spec of the commit being replayed (repeatable)')
    parser.add_argument('--repo', type=Path, default=Path.cwd(), help='the worktree (default: here)')
    args = parser.parse_args(argv)
    cwd = args.repo
    if not in_progress(cwd):
        raise SystemExit('No rebase or cherry-pick is in progress here; nothing to resolve.')
    conflicted = [p for p in git('diff', '--name-only', '--diff-filter=U', cwd=cwd).split('\n') if p]
    if not conflicted:
        raise SystemExit('No conflicted path; continue the rebase.')
    other = foreign_conflicts(conflicted)
    if other:
        raise SystemExit('Conflicts outside the registry, resolve them first (the notebook with '
                         'tools/notebook_rebase.py --continue): ' + ', '.join(other))
    specs = [json.loads(path.read_text()) for path in args.spec]
    git('checkout', '--ours', '--', *conflicted, cwd=cwd)
    registry = json.loads(Path(cwd, REGISTRY).read_text())
    clash = already_registered(registry, specs)
    if clash:
        raise SystemExit('The base already registers ' + ', '.join(clash) + '; this is not the conflict this '
                         'tool resolves. The registry is left at the base\'s version.')
    tool = str(Path(cwd, 'tools/claim-index.py'))
    rebuilt = []
    with tempfile.TemporaryDirectory() as scratch:
        for number, path in enumerate(args.spec):
            proposal = Path(scratch, f'proposal{number}.json')
            run([sys.executable, tool, 'author', 'build', '--spec', str(path.resolve()),
                 '--out', str(Path(scratch, f'request{number}.json')), '--proposal', str(proposal),
                 '--report', str(Path(scratch, f'report{number}.txt')),
                 # the commit being replayed registered these summaries after comparing them with its entry; a
                 # rebuild on another base changes no text (16 October 2026: the check first broke this replay)
                 '--summaries-checked'], cwd)
            Path(cwd, REGISTRY).write_text(proposal.read_text())
            rebuilt += [item['id'] for item in specs[number].get('claims', [])]
    run([sys.executable, tool, 'render'], cwd)
    git('add', '--', *REGISTRY_PATHS, cwd=cwd)
    run([sys.executable, tool, 'changed', '--base', 'HEAD'], cwd)
    run([sys.executable, str(Path(cwd, 'tools/check-append-only.py')), '--base', 'HEAD'], cwd)
    size = Path(cwd, REGISTRY).stat().st_size / 1e6
    print(f'Rebuilt {len(rebuilt)} claim(s) on the base\'s registry ({size:.1f} MB): {", ".join(rebuilt)}.')
    print('Registry files staged; changed-claim and append-only checks pass against HEAD.')
    print('Next: GIT_EDITOR=true git rebase --continue, then tools/check-claims.py and tools/ff-base.sh.')
    unstaged_names = unstaged(cwd)
    if unstaged_names:
        print(unstaged_warning(unstaged_names))
    return 0


def unstaged(cwd):
    """Tracked files with changes not staged, which make git rebase --continue refuse."""
    return [name for name in git('diff', '--name-only', cwd=cwd).splitlines() if name]


def unstaged_warning(names):
    # 17 October 2026: git rebase --continue refused twice with only "You must edit all merge conflicts and then
    # mark them as resolved using git add", while no conflict was left, because two tool files had unstaged
    # edits; the cause was guessed as a commit hook and a hand commit put git's conflict comments in the message.
    return (f'Unstaged changes in {", ".join(names)}: git rebase --continue refuses with "You must edit all merge '
            'conflicts", though none is left. Set them aside (copy them out and git checkout -- them) and restore '
            'them after the rebase.')


if __name__ == '__main__':
    sys.exit(main())
