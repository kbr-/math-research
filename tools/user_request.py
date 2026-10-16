#!/usr/bin/env python3
"""Append a request to the user to the main checkout's user_requests file, wrapped like the rest of it.

    python3 tools/user_request.py add "TEXT"     append TEXT as a new paragraph
    python3 tools/user_request.py path           print the file's path

AGENTS.md sends every request to the user into the Git-ignored user_requests file of the main checkout,
which a worktree reaches through a link. A shell append to that link writes outside the worktree, and in
auto mode Claude Code held such a write at a permission prompt for 95 minutes (16 October 2026); the
project's allow rule for python3 tools/ covers this tool, and tools/hooks/bash_guard.py refuses the shell
forms. The text is wrapped at 100 columns, as tools/rewrap_md.py wraps prose.
"""
import argparse
import subprocess
import sys
import textwrap
from pathlib import Path

WIDTH = 100


def requests_path(cwd='.'):
    common = subprocess.run(['git', 'rev-parse', '--path-format=absolute', '--git-common-dir'], cwd=cwd,
                            capture_output=True, text=True, check=True).stdout.strip()
    return Path(common).parent / 'user_requests'


def paragraph(text):
    words = ' '.join(text.split())
    if not words:
        raise SystemExit('user_request.py: empty request')
    return textwrap.fill(words, WIDTH, break_long_words=False, break_on_hyphens=False)


def add(path, text):
    body = path.read_text() if path.exists() else ''
    sep = '' if not body else ('\n' if body.endswith('\n') else '\n\n')
    if body.endswith('\n') and not body.endswith('\n\n'):
        sep = '\n'
    path.write_text(body + sep + paragraph(text) + '\n')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('path')
    added = sub.add_parser('add')
    added.add_argument('text')
    args = parser.parse_args(argv)
    path = requests_path()
    if args.command == 'path':
        print(path)
        return 0
    add(path, args.text)
    print(f'Added a request of {len(args.text.split())} words to {path}.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
