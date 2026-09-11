#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Kamil Braun
"""Record stable, streamed file hashes without copying source contents."""
import argparse
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def local_path(path):
    resolved = (ROOT / path).resolve()
    resolved.relative_to(ROOT)
    return resolved


def fingerprint(stat):
    return stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns


def file_record(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        before = os.fstat(stream.fileno())
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
        after = os.fstat(stream.fileno())
    if fingerprint(before) != fingerprint(after) or fingerprint(after) != fingerprint(path.stat()):
        raise RuntimeError(f'File changed while hashing: {path.relative_to(ROOT)}')
    return {'path': path.relative_to(ROOT).as_posix(),
            'bytes': after.st_size, 'sha256': digest.hexdigest()}


def record(paths, out, session=None):
    inputs = sorted({local_path(path) for path in paths})
    target = local_path(out)
    if not inputs or target in inputs:
        raise ValueError('Provide input files and a separate output manifest')
    report = {'schema': 1, 'files': [file_record(path) for path in inputs]}
    if session is not None:
        report['session'] = session
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(report, indent=2) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True, type=Path, help='New repository-local JSON manifest')
    parser.add_argument('--session', help='Optional computation-session label')
    parser.add_argument('files', nargs='+', type=Path, help='Repository-local source or result files')
    args = parser.parse_args()
    try:
        report = record(args.files, args.out, args.session)
    except (OSError, ValueError, RuntimeError) as error:
        parser.exit(1, f'{error}\n')
    print(f'Recorded {len(report["files"])} file hashes in {args.out}.')


if __name__ == '__main__':
    main()
