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


def canonical_report(event):
    """A declared --out report may replace an identical captured output."""
    command = event.get('command', [])
    if '--out' not in command:
        return None
    position = command.index('--out') + 1
    if position >= len(command):
        return None
    candidate = Path(command[position])
    if not candidate.is_absolute():
        # Protected commands run from the checkout root. Never use a historical
        # machine's absolute cwd to locate evidence after moving a checkout.
        candidate = RESEARCH.parent / candidate
    candidate = candidate.resolve()
    if candidate.is_relative_to((RESEARCH / 'results').resolve()) and candidate.is_file():
        return candidate
    return None


def archive(path):
    events = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    if not any(e['event'] == 'stop' for e in events):
        return False
    target = DEST / path.stem
    sources = [(path, 'session.jsonl', None)]
    summary = path.with_suffix('.summary.json')
    if not summary.exists():
        raise RuntimeError(f'Missing summary: run ./compute.sh report {path.stem}')
    sources.append((summary, 'summary.json', None))
    for event in events:
        if event['event'] == 'run_start' and event.get('output'):
            output = (RESEARCH / event['output']).resolve()
            if not output.is_relative_to(LOGS.resolve()):
                raise RuntimeError(f'Unexpected output path in {path.name}')
            sources.append((output, 'outputs/' + output.name, canonical_report(event)))
    manifest = []
    index = target / 'manifest.json'
    previous = {entry['original_path']: entry for entry in json.loads(index.read_text())} \
        if index.exists() else {}
    exclusion_file = RESEARCH / 'provenance/archive-exclusions.json'
    exclusions = json.loads(exclusion_file.read_text()) if exclusion_file.exists() else {}
    for source, name, canonical in sources:
        source_hash = digest(source)
        original_path = str(source.relative_to(RESEARCH))
        prior = previous.get(original_path)
        if prior and prior['sha256'] != source_hash:
            raise RuntimeError(f'Archived evidence changed: {source}')
        if original_path in exclusions:
            manifest.append({'original_path': original_path, 'omitted': True,
                             'sha256': source_hash, 'reason': exclusions[original_path]})
            continue
        if prior and 'canonical_path' in prior:
            saved = (RESEARCH / prior['canonical_path']).resolve()
            if not saved.is_relative_to((RESEARCH / 'results').resolve()) \
                    or not saved.is_file() or digest(saved) != source_hash:
                raise RuntimeError(f'Canonical evidence missing or changed: {saved}')
            manifest.append(prior)
            continue
        # Preserve existing archive layouts. Deduplicate new outputs only, and
        # only by complete content equality; never truncate or omit diagnostics.
        if not prior and canonical and digest(canonical) == source_hash:
            target.mkdir(parents=True, exist_ok=True)
            manifest.append({'original_path': original_path,
                             'canonical_path': str(canonical.relative_to(RESEARCH)),
                             'sha256': source_hash})
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
