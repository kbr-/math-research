#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Kamil Braun
"""Save the full output of a ./compute.sh run as a result file, headed by its command line.

compute.sh does not display a computation's output, only the path of its saved log.
This copies the complete log research/logs/SESSION-RUNID.output.txt to OUT, prefixed by two comment
lines naming the command (scratch-directory prefixes given with --strip are removed) and the run.
It refuses to overwrite OUT, and OUT must lie inside the repository.
Usage: tools/save-run-output.py SESSION RUN_ID OUT [--strip PREFIX ...]
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def save(session, run_id, out, strip=(), root=ROOT):
    journal = root / 'research' / 'logs' / f'{session}.jsonl'
    log = root / 'research' / 'logs' / f'{session}-{run_id}.output.txt'
    command = None
    for line in journal.read_text().splitlines():
        event = json.loads(line)
        if event.get('event') == 'run_start' and event.get('id') == run_id:
            command = event['command']
    if command is None:
        raise SystemExit(f'No run {run_id} in {journal.relative_to(root)}')
    if not log.is_file():
        raise SystemExit(f'Missing log {log.relative_to(root)}')
    target = (root / out).resolve()
    target.relative_to(root.resolve())
    if target.exists():
        raise SystemExit(f'Refusing to overwrite {out}')
    words = []
    for word in command:
        for prefix in strip:
            word = word.replace(prefix, '')
        words.append(word)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('w') as fh:
        fh.write(f'# command: {" ".join(words)}\n# run {run_id}, session {session}; full output\n')
        fh.write(log.read_text())
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('session')
    parser.add_argument('run_id')
    parser.add_argument('out')
    parser.add_argument('--strip', action='append', default=[], help='Prefix to remove from command words')
    args = parser.parse_args()
    target = save(args.session, args.run_id, args.out, args.strip)
    print(f'Saved {target.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
