#!/usr/bin/env python3
"""Check that Research-record entries of a base revision are unchanged: the notebook is append-only.

Every <article id=...> of BASE:notebook.html must reappear in the working notebook with the same
text. Only link repairs are tolerated, as AGENTS.md allows: <a ...> and </a> tags are ignored.
Usage: check-append-only.py [--base REF]   (default origin/main; exit 1 on any changed or missing entry)"""
import argparse
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def entries(body):
    record = body.find('<section id="research-record">')
    found = re.finditer(r'<article\b[^>]*\bid="([^"]+)"[^>]*>.*?</article>', body[max(record, 0):], re.S)
    return {match.group(1): re.sub(r'</?a\b[^>]*>', '', match.group(0)) for match in found}


def violations(base_body, current_body):
    base, current = entries(base_body), entries(current_body)
    missing = [name for name in base if name not in current]
    changed = [name for name in base if name in current and base[name] != current[name]]
    return missing, changed


def check(root, ref):
    shown = subprocess.run(['git', 'show', f'{ref}:notebook.html'], cwd=root, capture_output=True, text=True)
    if shown.returncode != 0:
        return None   # no such revision (fresh clone without the remote, or not a repository)
    return violations(shown.stdout, (root / 'notebook.html').read_text())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', default='origin/main')
    args = parser.parse_args()
    result = check(ROOT, args.base)
    if result is None:
        print(f'check-append-only.py: cannot read {args.base}:notebook.html; nothing checked')
        return 0
    missing, changed = result
    for name in missing:
        print(f'MISSING entry {name}')
    for name in changed:
        print(f'CHANGED entry {name}')
    if missing or changed:
        print('The notebook is append-only: restore these entries and put corrections in a new dated entry.')
        return 1
    print(f'Entries of {args.base} are unchanged.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
