#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Register this checkout's existing skills; never install global files.

Relative skill links may be committed on the branch owning their sources. Their authoritative content
remains in skills/, including private branches' additions.
"""
import fcntl
import json
import os
from pathlib import Path
import re
import sys
import tempfile

from codex_state import atomic_json

ROOT = Path(__file__).resolve().parents[1]


def desired(root):
    result = {}
    for source in sorted((root/'skills').glob('*/SKILL.md')):
        name = source.parent.name
        if not re.fullmatch(r'[A-Za-z0-9_-]+', name):
            raise ValueError(f'Invalid skill directory name: {name}')
        target = root/'.agents/skills'/name
        result[str(target.relative_to(root))] = {'link': os.path.relpath(source.parent, target.parent)}
    return result


def target_path(root, name):
    if not re.fullmatch(r'\.agents/skills/[A-Za-z0-9_-]+', name):
        raise ValueError(f'Invalid managed Codex descriptor: {name}')
    path = root/name
    if not path.parent.resolve().is_relative_to(root):
        raise ValueError(f'Descriptor directory escapes this checkout: {name}')
    return path


def contents(path):
    if path.is_symlink():
        return {'link': os.readlink(path)}
    if path.is_file():
        return {'text': path.read_text()}
    if path.exists():
        raise ValueError(f'Registration target is not a file/link: {path}')
    return None


def register(root):
    root = Path(root).resolve()
    directory = root/'.codex/framework'
    if not directory.resolve().is_relative_to(root):
        raise ValueError('Codex runtime directory escapes this checkout')
    directory.mkdir(parents=True, exist_ok=True)
    manifest = directory/'registrations.json'
    if manifest.is_symlink():
        raise ValueError('Codex registration manifest must not be a symlink')
    with (directory/'registration.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        old = json.loads(manifest.read_text()) if manifest.exists() else {}
        new = desired(root)
        # Validate every target before changing any descriptor.
        current = {name: contents(target_path(root, name)) for name in old.keys() | new.keys()}
        for name, value in current.items():
            if value is not None and value not in (old.get(name), new.get(name)):
                raise ValueError(f'Unmanaged/edited Codex descriptor preserved: {name}; reconcile it before registration')
        changed = 0
        for name in sorted(current):
            value = new.get(name)
            if value == current[name]:
                continue
            path = target_path(root, name)
            if value is None:
                path.unlink(missing_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                fd, temporary = tempfile.mkstemp(dir=path.parent, prefix='.register-')
                os.close(fd)
                temporary = Path(temporary)
                try:
                    temporary.unlink()
                    temporary.symlink_to(value['link'])
                    temporary.replace(path)
                finally:
                    temporary.unlink(missing_ok=True)
            changed += 1
        if old != new:
            atomic_json(manifest, new)
        for name, value in new.items():
            if contents(target_path(root, name)) != value:
                raise ValueError(f'Codex registration did not persist: {name}')
        return {'skills': len(new), 'changed': changed}


def main():
    try:
        print(json.dumps(register(ROOT)))
    except (OSError, ValueError, TypeError, AttributeError) as error:
        print('Codex registration: ' + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
