#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Worktree-local Codex actor state; runtime identities never enter tracked files."""
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import tempfile
import time


def actor_directory(root, event):
    session = event.get('session_id')
    agent = event.get('agent_id')
    if not isinstance(session, str) or not session or (agent is not None and not isinstance(agent, str)):
        raise ValueError('Codex hook has no valid session/agent identity')
    key = hashlib.sha256(json.dumps([session, agent], separators=(',', ':')).encode()).hexdigest()
    return Path(root) / '.codex/framework/actors' / key


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix='.write-')
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(value, stream)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


@contextmanager
def actor_state(root, event):
    directory = actor_directory(root, event)
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / 'lock').open('a') as lock:
        deadline = time.monotonic() + .2
        while True:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise ValueError('Codex actor state is busy; retry this tool call')
                time.sleep(.01)
        path = directory / 'state.json'
        state = json.loads(path.read_text()) if path.exists() else {'version': 1}
        if not isinstance(state, dict) or state.get('version') != 1:
            raise ValueError('Invalid Codex actor state; restore context before continuing')
        yield state
        atomic_json(path, state)


SCRATCH_CAP = 500 * 10**6


def scratch_directory(root, thread, create=False):
    """One thread's managed scratch, never a caller-selected path or a sanitized identity."""
    if not isinstance(thread, str) or not thread:
        raise ValueError('Codex scratch requires an actual thread identity')
    root = Path(root).resolve()
    key = hashlib.sha256(thread.encode()).hexdigest()
    path = root
    for part in ('.codex', 'framework', 'scratch', key):
        path = path / part
        if path.is_symlink():
            raise ValueError(f'Managed scratch path must not be a symlink: {path}')
    if create:
        path.mkdir(parents=True, exist_ok=True)
    return path


def check_owned_scratch(root, thread, cap=SCRATCH_CAP):
    """Count logical bytes without following links; a failed check never removes evidence."""
    directory = scratch_directory(root, thread)
    if not directory.exists():
        return
    total = 0
    pending = [directory]
    while pending:
        with os.scandir(pending.pop()) as entries:
            for entry in entries:
                if entry.is_symlink():
                    raise ValueError(f'Managed scratch contains a symlink: {entry.path}; '
                                     'move links outside the owned scratch tree before finalizing')
                if entry.is_dir(follow_symlinks=False):
                    pending.append(entry.path)
                elif entry.is_file(follow_symlinks=False):
                    total += entry.stat(follow_symlinks=False).st_size
    if total > cap:
        raise ValueError(f'The Codex scratch directory {directory} holds {total} logical bytes, '
                         f'over the {cap} byte cap. Promote needed evidence to research/results or '
                         'research/provenance, delete only your remaining scratch, and rerun.')


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Print/create this Codex thread\'s managed scratch directory.')
    parser.add_argument('action', choices=['scratch'])
    parser.parse_args()
    try:
        print(scratch_directory(Path(__file__).resolve().parents[1], os.environ.get('CODEX_THREAD_ID'), create=True))
    except (OSError, ValueError) as error:
        parser.exit(1, str(error) + '\n')


if __name__ == '__main__':
    main()
