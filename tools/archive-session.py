#!/usr/bin/env python3
"""Preserve completed timing sessions and their outputs as durable evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / 'research'
LOGS = RESEARCH / 'logs'
DEST = RESEARCH / 'provenance/session-records'


def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(chunk)
    return result.hexdigest()


def archive(path):
    events = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    if not any(e['event'] == 'stop' for e in events):
        return False
    target = DEST / path.stem
    sources = [(path, 'session.jsonl')]
    summary = path.with_suffix('.summary.json')
    if not summary.exists():
        raise RuntimeError(f'Missing summary: run ./compute.sh report {path.stem}')
    sources.append((summary, 'summary.json'))
    for event in events:
        if event['event'] == 'run_start' and event.get('output'):
            output = (RESEARCH / event['output']).resolve()
            if not output.is_relative_to(LOGS.resolve()):
                raise RuntimeError(f'Unexpected output path in {path.name}')
            sources.append((output, 'outputs/' + output.name))
    manifest = []
    exclusion_file = RESEARCH / 'provenance/archive-exclusions.json'
    exclusions = json.loads(exclusion_file.read_text()) if exclusion_file.exists() else {}
    for source, name in sources:
        source_hash = digest(source)
        original_path = str(source.relative_to(RESEARCH))
        if original_path in exclusions:
            manifest.append({'original_path': original_path, 'omitted': True,
                             'sha256': source_hash, 'reason': exclusions[original_path]})
            continue
        destination = target / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists() and digest(destination) != source_hash:
            raise RuntimeError(f'Refusing to overwrite different archived evidence: {destination}')
        if not destination.exists():
            temporary = destination.with_name(destination.name + '.part')
            with source.open('rb') as src, temporary.open('wb') as dst:
                shutil.copyfileobj(src, dst, length=1024 * 1024)
            if digest(temporary) != source_hash:
                raise RuntimeError(f'Source changed during archival: {source}')
            temporary.replace(destination)
        manifest.append({'original_path': original_path,
                         'archived_path': name, 'sha256': source_hash})
    index = target / 'manifest.json'
    data = json.dumps(manifest, indent=2).encode() + b'\n'
    if index.exists() and index.read_bytes() != data:
        raise RuntimeError(f'Archive manifest changed: {index}')
    index.write_bytes(data)
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('sessions', nargs='*')
    parser.add_argument('--all-completed', action='store_true')
    args = parser.parse_args()
    if args.all_completed:
        paths = [p for p in sorted(LOGS.glob('*.jsonl')) if not p.name.startswith('cli_test_')]
    else:
        if not args.sessions:
            parser.error('Provide session names or --all-completed')
        paths = []
        for name in args.sessions:
            if Path(name).name != name or name in ('.', '..'):
                parser.error('Use session names, not paths')
            paths.append(LOGS / (name + '.jsonl'))
    count = sum(archive(path) for path in paths)
    print(f'Preserved {count} completed sessions in research/provenance/session-records/.')


if __name__ == '__main__':
    main()
