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
