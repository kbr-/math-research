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
    matches = list(found)
    if len({m.group(1) for m in matches}) != len(matches):
        raise ValueError('Duplicate research article IDs')
    return {match.group(1): re.sub(r'</?a\b[^>]*>', '', match.group(0)) for match in matches}


def violations(base_body, current_body):
    base, current = entries(base_body), entries(current_body)
    missing = [name for name in base if name not in current]
    changed = [name for name in base if name in current and base[name] != current[name]]
    if [name for name in current if name in base] != [name for name in base if name in current]:
        changed.append('(historical entry order)')
    return missing, changed


def check(root, ref):
    from notebooks import paths
    root = Path(root)
    listing = subprocess.run(['git','ls-tree','-r','--name-only',ref],cwd=root,capture_output=True,text=True)
    if listing.returncode:
        return None
    before = [p for p in listing.stdout.splitlines() if p == 'notebook.html' or
              re.fullmatch(r'research/branches/[^/]+/notebook.html',p)]
    current = {p.relative_to(root).as_posix() for p in paths(root)}
    missing, changed = [], []
    for path in before:
        if path not in current or not (root/path).exists():
            missing.append(path + ' (notebook deleted or unregistered)'); continue
        shown = subprocess.check_output(['git','show',f'{ref}:{path}'],cwd=root,text=True)
        left,right = violations(shown,(root/path).read_text())
        missing.extend(path+'#'+x for x in left)
        changed.extend(path+'#'+x for x in right)
    return missing, changed


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
