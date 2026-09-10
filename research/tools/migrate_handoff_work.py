"""One-time migration of session artifacts, restoring the original handoff ZIP."""
import hashlib
import json
from pathlib import Path
import shutil
from zipfile import ZipFile

WORKSPACE = Path(__file__).resolve().parents[2]
OLD = WORKSPACE / 'php_codex_handoff'
NEW = WORKSPACE / 'research'


def move(source, destination):
    if destination.exists():
        raise RuntimeError(f'Refusing to overwrite {destination}')
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(destination))


report = {'moved': [], 'restored': [], 'verified_original_files': 0}
with ZipFile(WORKSPACE / 'php_codex_handoff.zip') as archive:
    originals = {
        name.removeprefix('php_codex_handoff/'): name
        for name in archive.namelist()
        if name.startswith('php_codex_handoff/') and not name.endswith('/')
    }
    for path in sorted(OLD.rglob('*')):
        if not path.is_file():
            continue
        relative = path.relative_to(OLD)
        key = relative.as_posix()
        if key in originals:
            original = archive.read(originals[key])
            if path.read_bytes() == original:
                continue
            move(path, NEW / relative)
            path.write_bytes(original)
            report['restored'].append(key)
        else:
            if relative.parts[0] not in {'notes', 'logs', 'tools', 'references', 'tmp', 'cache'}:
                raise RuntimeError(f'Unexpected unarchived file: {key}')
            target = NEW / relative
            if relative.parts[0] == 'cache':
                target = NEW / 'references/user_supplied' / path.name
            move(path, target)
            report['moved'].append({'from': key, 'to': str(target.relative_to(NEW))})
    for relative, member in originals.items():
        path = OLD / relative
        if not path.is_file() or hashlib.sha256(path.read_bytes()).digest() != hashlib.sha256(archive.read(member)).digest():
            raise RuntimeError(f'Original package mismatch: {relative}')
        report['verified_original_files'] += 1

# These unchanged tools can operate in research/ without writing in the archive.
for relative in ('tools/import_references.py', 'references/manifest.json', 'references/references.bib'):
    destination = NEW / relative
    if destination.exists():
        raise RuntimeError(f'Refusing to overwrite helper: {destination}')
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(OLD / relative, destination)

for path in sorted(OLD.rglob('*'), key=lambda p: len(p.parts), reverse=True):
    if path.is_dir() and not any(path.iterdir()):
        path.rmdir()
(NEW / 'provenance').mkdir(exist_ok=True)
(NEW / 'provenance/handoff_restoration.json').write_text(json.dumps(report, indent=2) + '\n')
print(f"Moved {len(report['moved'])} new files; restored {len(report['restored'])} modified files.")
print(f"Verified all {report['verified_original_files']} original package files against php_codex_handoff.zip.")
