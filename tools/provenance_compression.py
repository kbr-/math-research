#!/usr/bin/env python3
"""Measure zstd archives and synthetic one-second telemetry without changing source data."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
from pathlib import Path
import random
import subprocess
import tarfile
import time
from typing import Any
from evidence_io import read_text


def durations(journal: Path) -> list[tuple[str, float]]:
    starts: dict[str, float] = {}
    runs = []
    if not journal.exists() and journal.suffix != '.zst':
        journal = journal.with_name(journal.name + '.zst')
    for line in read_text(journal).splitlines():
        row = json.loads(line)
        if row['event'] == 'run_start':
            starts[row['id']] = row['monotonic_s']
        elif row['event'] == 'run_end':
            runs.append((row['id'], row['monotonic_s'] - starts.pop(row['id'])))
    if starts:
        raise ValueError('Cannot estimate an unfinished run')
    return runs


def telemetry(runs: list[tuple[str, float]], seed: int = 17) -> bytes:
    """Synthetic varying readings, not reconstructed historical resource use."""
    rng = random.Random(seed)
    rows: list[dict[str, Any]] = []
    for run, seconds in runs:
        rows.append({'run': run, 'synthetic': True, 'duration_s': seconds,
                     'schema': 'elapsed_ms,cpu_usec,ram_bytes,swap_bytes,cores', 'seed': seed})
        cpu = 0
        previous = 0.0
        for at in [*range(math.ceil(seconds)), seconds]:
            delta = at - previous
            used = int(delta * rng.uniform(0, 14) * 1e6)
            cpu += used
            ram = rng.randrange(10_000_000, 8_000_000_000)
            rows.append({'run': run, 'elapsed_ms': round(at * 1000), 'cpu_usec': cpu,
                         'ram_bytes': ram, 'swap_bytes': rng.randrange(0, 10_000_000_000 - ram),
                         'cores': round(used / delta / 1e6, 3) if delta else 0})
            previous = at
        rows.append({'run': run, 'summary': {'cpu_seconds': cpu / 1e6,
                     'average_cores': cpu / seconds / 1e6 if seconds else 0, 'samples': math.ceil(seconds) + 1}})
    return ('\n'.join(json.dumps(row, separators=(',', ':')) for row in rows) + '\n').encode()


def compress(data: bytes, path: Path) -> dict[str, float | int]:
    started = time.perf_counter()
    subprocess.run(['zstd', '-q', '-3', '-T1', '-o', str(path)], input=data, check=True)
    elapsed = time.perf_counter() - started
    started = time.perf_counter()
    restored = subprocess.run(['zstd', '-q', '-d', '-c', str(path)], capture_output=True, check=True).stdout
    decoding = time.perf_counter() - started
    if restored != data:
        raise ValueError(f'{path}: decompression changed bytes')
    return {'raw_bytes': len(data), 'compressed_bytes': path.stat().st_size,
            'compressed_disk_bytes': path.stat().st_blocks * 512,
            'compress_seconds': elapsed, 'decompress_seconds': decoding}


def sample(root: Path, name: str, out: Path) -> dict[str, Any]:
    roots = [root / 'research/provenance/session-records' / name, root / 'research/results' / name]
    source_bytes = disk_bytes = 0
    files: dict[str, str] = {}
    tar_bytes = io.BytesIO()
    with tarfile.open(fileobj=tar_bytes, mode='w', format=tarfile.PAX_FORMAT) as archive:
        for folder in roots:
            if not folder.is_dir():
                raise ValueError(f'Missing sample directory: {folder}')
            for path in [folder, *sorted(folder.rglob('*'))]:
                if path.is_symlink():
                    raise ValueError(f'Sample contains a symlink: {path}')
                disk_bytes += path.stat().st_blocks * 512
                if path.is_file():
                    content = path.read_bytes()
                    source_bytes += len(content)
                    relative = str(path.relative_to(root))
                    files[relative] = hashlib.sha256(content).hexdigest()
                    info = tarfile.TarInfo(relative)
                    info.size = len(content)
                    info.mode = path.stat().st_mode & 0o777
                    archive.addfile(info, io.BytesIO(content))
    packed = tar_bytes.getvalue()
    # Check both the zstd round trip and the archive's member inventory and contents.
    with tarfile.open(fileobj=io.BytesIO(packed)) as archive:
        restored = {}
        for member in archive:
            stream = archive.extractfile(member)
            if stream is None:
                raise ValueError(f'Unexpected archive member: {member.name}')
            restored[member.name] = hashlib.sha256(stream.read()).hexdigest()
        if restored != files:
            raise ValueError('Archive differs from source inventory')
    stored = compress(packed, out / f'{name}.tar.zst')
    stored.update(source_bytes=source_bytes, source_disk_bytes=disk_bytes, files=len(files))
    runs = durations(roots[0] / 'session.jsonl')
    addition = compress(telemetry(runs), out / f'{name}.telemetry.jsonl.zst')
    addition['estimated_uncompressed_disk_bytes'] = math.ceil(int(addition['raw_bytes']) / 4096) * 4096
    return {'sample': name, 'runs': len(runs), 'run_seconds': sum(seconds for _, seconds in runs),
            'stored': stored, 'synthetic_addition': addition, 'source_hashes': files}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('samples', nargs='+')
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        parser.error('--out must be a new directory')
    args.out.mkdir(parents=True)
    rows = [sample(args.root.resolve(), name, args.out) for name in args.samples]
    report = {'codec': subprocess.check_output(['zstd', '--version'], text=True).strip(),
              'level': 3, 'threads': 1, 'telemetry': 'Synthetic varying values, seed 17; not measured historical utilization.',
              'samples': rows}
    (args.out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({**report, 'samples': [{key: value for key, value in row.items() if key != 'source_hashes'}
                                          for row in rows]}, indent=2))


if __name__ == '__main__':
    main()
