#!/usr/bin/env python3
"""Print Claude file rules for the shared run files in every registered worktree.

The user can run --apply to merge them into their own Claude settings. This tool never grants
Bash commands or whole-directory access. Re-run it after registering a worktree at a new path.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SHARED_FILES = ('user_requests', 'run_state')


def literal_pattern(path: str) -> str:
    return ''.join('\\' + char if char in '\\*?[]' else char for char in path)


def worktree_rules(porcelain: bytes) -> list[str]:
    roots = []
    for record in porcelain.strip().split(b'\n\n'):
        if not record:
            continue
        lines = record.splitlines()
        if not lines[0].startswith(b'worktree /') or any(
                not line.startswith((b'HEAD ', b'branch ', b'locked ', b'prunable '))
                and line not in (b'bare', b'detached', b'locked', b'prunable') for line in lines[1:]):
            raise ValueError('Ambiguous Git worktree inventory; no permissions were changed')
        roots.append(lines[0][len(b'worktree '):].decode())
    if not roots:
        raise ValueError('Git returned no worktrees; no permissions were changed')
    return list(dict.fromkeys(f'{tool}(/{literal_pattern(root)}/{name})'
                              for root in roots for name in SHARED_FILES for tool in ('Edit', 'Write')))


def merge_settings(path: Path, rules: list[str]) -> int:
    if path.is_symlink():
        path = path.resolve(strict=True)
    original = path.read_text()
    settings = json.loads(original)
    allowed = settings.setdefault('permissions', {}).setdefault('allow', [])
    if not isinstance(allowed, list) or not all(isinstance(rule, str) for rule in allowed):
        raise ValueError('permissions.allow must be a list of strings; no permissions were changed')
    added = [rule for rule in rules if rule not in allowed]
    if not added:
        return 0
    allowed.extend(added)
    backup = path.with_name(path.name + '.before-math-links')
    if not backup.exists():
        shutil.copy2(path, backup)
    with tempfile.NamedTemporaryFile('w', dir=path.parent, prefix='.math-links-', delete=False) as stream:
        temporary = Path(stream.name)
        json.dump(settings, stream, indent=2, ensure_ascii=False)
        stream.write('\n')
    try:
        shutil.copymode(path, temporary)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)
    return len(added)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='merge rules into your Claude user settings')
    parser.add_argument('--settings', type=Path, default=Path.home() / '.claude/settings.json')
    args = parser.parse_args()
    inventory = subprocess.check_output(['git', '-C', str(ROOT), 'worktree', 'list', '--porcelain'])
    rules = worktree_rules(inventory)
    if args.apply:
        print(f'Added {merge_settings(args.settings, rules)} rules to {args.settings}; existing settings retained.')
    else:
        print(json.dumps({'allow': rules}, indent=2))


if __name__ == '__main__':
    main()
