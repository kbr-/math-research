#!/usr/bin/env python3
"""A copy of a repository's files for a reviewer who must not see its history.

Usage: tools/blind_copy.py REPOSITORY TIP DESTINATION [--base BASE]

A reviewer given a worktree of the repository can read every branch's commit messages with
`git log --all`, and so learns what the change it reviews was meant to do. This writes DESTINATION, a new
repository holding the files of TIP and nothing else of REPOSITORY: no remote, no other branch, no tag, no
commit message, author or date of its own. With --base its history is two commits, the files of BASE and
then those of TIP, named "base" and "change", so `git diff HEAD~1` is the change under review; without it,
one commit named "snapshot". Files git ignores and uncommitted work are not copied. DESTINATION must not
exist. Prints what the copy holds, read back from it.
"""
import argparse
import subprocess
import sys
from pathlib import Path

WHO = {'GIT_AUTHOR_NAME': 'copy', 'GIT_AUTHOR_EMAIL': 'copy@example.invalid', 'GIT_COMMITTER_NAME': 'copy',
       'GIT_COMMITTER_EMAIL': 'copy@example.invalid', 'GIT_AUTHOR_DATE': '2000-01-01T00:00:00+0000',
       'GIT_COMMITTER_DATE': '2000-01-01T00:00:00+0000'}


def git(directory, *arguments, data=None, env=None):
    done = subprocess.run(['git', '-C', str(directory), *arguments], input=data, capture_output=True,
                          env=None if env is None else {**__import__('os').environ, **env})
    if done.returncode:
        raise SystemExit(f'git {" ".join(arguments[:3])} failed in {directory}: {done.stderr.decode(errors="replace").strip()}')
    return done.stdout


def snapshot(repository, revision, destination, message):
    """Commit the files of `revision` in `destination`, replacing what is there, and return their tree's id."""
    git(destination, 'rm', '-r', '-q', '--ignore-unmatch', '.')
    archive = git(repository, 'archive', '--format=tar', revision)
    subprocess.run(['tar', '-x', '-C', str(destination)], input=archive, check=True)
    git(destination, 'add', '-A')
    git(destination, '-c', 'core.hooksPath=/dev/null', 'commit', '-q', '--allow-empty', '-m', message, env=WHO)
    return git(destination, 'rev-parse', 'HEAD^{tree}').decode().strip()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('repository', type=Path)
    parser.add_argument('tip')
    parser.add_argument('destination', type=Path)
    parser.add_argument('--base', help='a revision whose files become the first commit')
    args = parser.parse_args(argv)
    if args.destination.exists():
        print(f'{args.destination} exists: give a path that does not', file=sys.stderr)
        return 2
    wanted = {name: git(args.repository, 'rev-parse', f'{revision}^{{tree}}').decode().strip()
              for name, revision in (('base', args.base), ('tip', args.tip)) if revision}
    args.destination.mkdir(parents=True)
    git(args.destination, 'init', '-q', '-b', 'review')
    made = {}
    if args.base:
        made['base'] = snapshot(args.repository, args.base, args.destination, 'base')
    made['tip'] = snapshot(args.repository, args.tip, args.destination, 'change' if args.base else 'snapshot')
    # A file export-ignore leaves out of an archive is in the revision's tree and not in the copy.
    differing = [name for name in made if made[name] != wanted[name]]
    log = git(args.destination, 'log', '--all', '--format=%s').decode().split()
    refs = git(args.destination, 'for-each-ref', '--format=%(refname)').decode().split()
    remotes = git(args.destination, 'remote').decode().split()
    print(f'{args.destination}: commits {log[::-1]}, refs {refs}, remotes {remotes}')
    if differing:
        print(f'The copy\'s files differ from the revision\'s for: {", ".join(differing)} (an export-ignore attribute leaves '
              'files out of an archive)', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
