#!/usr/bin/env python3
"""Check that Git preserves the historical package, references, and restart tools."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, help='Also save the verification report')
    parser.add_argument('--public-history', help='Also check reachable paths in this public branch/ref')
    args = parser.parse_args()
    tracked = set(subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT, text=True).split('\0')) - {''}
    failures = []
    manifest = json.loads((ROOT / 'research/provenance/handoff-files.json').read_text())
    for entry in manifest['files']:
        path = ROOT / entry['path']
        if entry['path'] not in tracked or not path.is_file() or digest(path) != entry['sha256']:
            failures.append('Missing, untracked, or changed handoff file: ' + entry['path'])
    references = json.loads((ROOT / 'research/references/import_status.json').read_text())['references']
    policy = json.loads((ROOT / 'research/references/redistribution.json').read_text())
    local_sources = 0
    for key in ('BIKPRS', 'Razborov', 'Krajicek', 'Pebbling'):
        name = 'research/references/cache/' + key + '.pdf'
        text = 'research/references/extracted/' + key + '.txt'
        if key in policy['public']:
            if name not in tracked or not (ROOT / name).is_file() or digest(ROOT / name) != references[key]['sha256']:
                failures.append('Missing, untracked, or changed public reference: ' + key)
            if text not in tracked or not (ROOT / text).is_file():
                failures.append('Missing public extracted reference: ' + key)
        else:
            if name in tracked or text in tracked or ('research/references/user_supplied/' + key + '.pdf') in tracked:
                failures.append('Reference without redistribution clearance is tracked: ' + key)
            if (ROOT / name).is_file():
                local_sources += 1
                if digest(ROOT / name) != references[key]['sha256']:
                    failures.append('Local reference differs from the audited version: ' + key)
    required = ['notebook.html', 'index.html', 'server.py', 'AGENTS.md', 'COMPUTATION_RULES.md',
                'README.md', 'research/notes/RESUME.md', 'research/notes/SOURCE_AUDIT.md',
                'research/notes/RESEARCH_LOG.md', 'compute.sh', 'start-codex.sh',
                'resource-controls/setup.py', 'tools/remember-codex-session.py',
                'tools/archive-session.py', 'requirements-research.txt', 'LICENSE',
                'ATTRIBUTION.md', 'CITATION.cff', 'THIRD_PARTY_NOTICES.md']
    failures += ['Untracked essential file: ' + name for name in required if name not in tracked]
    forbidden = ['.codex-session-id', 'php_codex_handoff.zip']
    failures += ['Machine-local or redundant file tracked: ' + name for name in forbidden if name in tracked]
    for name in tracked:
        if name.startswith(('.resource-runtime/', '.codex/', '.agents/', 'research/tmp/', 'research/logs/', 'private/')) or '__pycache__/' in name:
            failures.append('Runtime or scratch file tracked: ' + name)
    modes = subprocess.check_output(['git', 'ls-files', '--stage', '-z'], cwd=ROOT, text=True).split('\0')
    mode_by_path = {line.split('\t', 1)[1]: line.split(' ', 1)[0] for line in modes if line}
    for name in ('compute.sh', 'start-codex.sh', 'tools/remember-codex-session.py', 'tools/archive-session.py'):
        if mode_by_path.get(name) != '100755':
            failures.append('Executable mode not tracked: ' + name)
    if args.public_history:
        objects = subprocess.check_output(['git', 'rev-list', '--objects', args.public_history],
                                          cwd=ROOT, text=True).splitlines()
        private_paths = set()
        for key in policy['local_only']:
            private_paths.update(('research/references/cache/' + key + '.pdf',
                                  'research/references/extracted/' + key + '.txt',
                                  'research/references/user_supplied/' + key + '.pdf'))
        excluded = json.loads((ROOT / 'research/provenance/archive-exclusions.json').read_text())
        excluded_names = {Path(name).name for name in excluded}
        for line in objects:
            _, separator, name = line.partition(' ')
            if not separator:
                continue
            if name in private_paths or name.startswith('private/') or Path(name).name in excluded_names:
                failures.append('Local-only material remains in public history: ' + name)
    report = {'tracked_files': len(tracked), 'historical_files_checked': len(manifest['files']),
              'public_reference_pdfs_checked': len(policy['public']),
              'local_only_references_available': local_sources,
              'public_history_checked': args.public_history, 'failures': failures}
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    return bool(failures)


if __name__ == '__main__':
    raise SystemExit(main())
