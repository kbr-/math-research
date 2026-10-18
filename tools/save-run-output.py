#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Kamil Braun
"""Save the full output of a ./compute.sh run as a result file, headed by its command line.

compute.sh does not display a computation's output, only the path of its saved log.
This compresses the complete log research/logs/SESSION-RUNID.output.txt to OUT.zst with zstd level 3, prefixed by two comment
lines naming the command (scratch-directory prefixes given with --strip are removed) and the run.
An OUT already ending in .zst keeps its name; read it with tools/evidence_io.py read or zstd -dc.
It refuses to overwrite OUT or OUT.zst, and OUT must lie inside the repository.
Usage: tools/save-run-output.py SESSION RUN_ID OUT [--strip PREFIX ...]
"""
import argparse
import json
import shutil
from pathlib import Path
from evidence_io import compressed_writer
from collections.abc import Sequence

ROOT = Path(__file__).resolve().parents[1]


def save(session: str, run_id: str, out: str | Path, strip: Sequence[str] = (), root: Path = ROOT) -> Path:
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
    if target.suffix != '.zst':
        target = target.with_name(target.name + '.zst')
    if target.exists():
        raise SystemExit(f'Refusing to overwrite {target}')
    words = []
    for word in command:
        for prefix in strip:
            word = word.replace(prefix, '')
        words.append(word)
    target.parent.mkdir(parents=True, exist_ok=True)
    with compressed_writer(target) as fh:
        fh.write(f'# command: {" ".join(words)}\n# run {run_id}, session {session}; full output\n'.encode())
        with log.open('rb') as source:
            shutil.copyfileobj(source, fh, length=1024 * 1024)
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
