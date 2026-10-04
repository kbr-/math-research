#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Ordered Codex command/restoration checks; one synchronous handler per event.

A receipt proves delivery of the complete tool response to its caller. It cannot prove
that an outer code-mode program displays it, or that the model reads it.
"""
import importlib.util
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from codex_state import actor_state, scratch_directory
from resume import read_part
import base_behind


def load_guard():
    spec = importlib.util.spec_from_file_location('guard_full_output', Path(__file__).with_name('guard-full-output.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


guard = load_guard()
CONTEXT = ('Restore context now: run python3 tools/resume.py bare, then read each listed part. '
           'Keep default output allowances, including the outer code-mode call, and display every '
           'part in full. Other supported tools remain blocked until all parts are delivered.')


def resume_call(command, root, cwd=None):
    """Recognize one literal repo resume invocation, optionally following a literal cd."""
    if any(x in command for x in ('$', '`', '\n', ';', '|', '>', '<')):
        return None
    try:
        words = shlex.split(command)
    except ValueError:
        return None
    cwd = Path(cwd or root)
    if '&&' in words:
        at = words.index('&&')
        if at != 2 or words[0] != 'cd':
            return None
        cwd = (cwd / words[1]).resolve()
        words = words[3:]
    if words and Path(words[0]).name in ('python', 'python3'):
        words.pop(0)
        if words and words[0] == '-u':
            words.pop(0)
    if not words or (cwd / words.pop(0)).resolve() != (Path(root) / 'tools/resume.py').resolve():
        return None
    if not words:
        return ('prepare', None, 1)
    if '--read' in words:
        if len(words) != 4 or set(words[::2]) != {'--read', '--part'}:
            return None
        args = dict(zip(words[::2], words[1::2]))
        if not re.fullmatch('[0-9a-f]{32}', args['--read']) or not args['--part'].isdigit():
            return None
        return ('read', args['--read'], int(args['--part']))
    # Preparation selectors are consumed by resume.py, not by a shell.
    i = 0
    while i < len(words):
        if words[i] == '--formalization':
            i += 1
        elif words[i] in ('--notebook', '--session', '--tail') and i + 1 < len(words):
            i += 2
        else:
            return None
    return ('prepare', None, 1)


def response_text(value):
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return '\n'.join(response_text(value[k]) for k in ('stdout', 'output', 'text', 'content') if k in value)
    if isinstance(value, list):
        return '\n'.join(map(response_text, value))
    return ''


def receipt(state, call, response, root):
    text = response_text(response)
    if re.search(r'(?:warning:.*truncat|tokens? truncated|output.*truncated)', text, re.I):
        return
    mode, key, number = call
    if mode == 'prepare':
        header = next((line for line in text.splitlines() if line.startswith('{"bundle":')), None)
        if not header:
            return
        meta = json.loads(header)
        key = meta.get('bundle')
    elif key != state.get('bundle'):
        return
    body, total = read_part(root, key, number)
    expected = f'RESUME PART {number}/{total} — {len(body.encode())} payload bytes\n{body}\nEND RESUME PART {number}/{total}'
    if expected not in text:
        return
    if mode == 'prepare':
        state.update(bundle=key, delivered=[])
    delivered = set(state.get('delivered', []))
    delivered.add(number)
    state['delivered'] = sorted(delivered)
    state['pending'] = delivered != set(range(1, total + 1))


def context(event, message):
    return {'hookSpecificOutput': {'hookEventName': event, 'additionalContext': message}}


def deny(message):
    return {'hookSpecificOutput': {'hookEventName': 'PreToolUse', 'permissionDecision': 'deny',
                                  'permissionDecisionReason': message}}


def dispatch(event, root):
    name = event.get('hook_event_name')
    if name == 'Stop':
        # The private branch owns its predicate and prompt; shared hooks resolve it there.
        path = Path(root) / 'tools/hooks/codex_unchecked_claim.py'
        if not path.is_file():
            return {}
        spec = importlib.util.spec_from_file_location('codex_unchecked_claim', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.check(event)
    command = (event.get('tool_input') or {}).get('command', '')
    if not isinstance(command, str):
        raise ValueError('Invalid command in Codex hook input')
    shell = event.get('tool_name') == 'Bash'
    # Stateless refusals run even when the session payload lacks an identity.
    if name == 'PreToolUse' and shell:
        reason = guard.blocked(command) or guard.unchained_heredoc(command)
        if reason:
            return deny('Refused: ' + reason + '. Run mandatory output bare and chain dependent commands.')
    if name == 'SessionStart':
        with actor_state(root, event) as state:
            state.update(pending=True, bundle=None, delivered=[])
        scratch = scratch_directory(root, event.get('agent_id') or event['session_id'], create=True)
        return context(name, CONTEXT + f" Put this thread's scratch in {scratch}.")
    if name == 'SubagentStart':
        scratch = scratch_directory(root, event['agent_id'], create=True)
        return context(name, f"Put this thread's scratch in {scratch}; never use another actor's directory.")
    if name in ('PreToolUse', 'PostToolUse'):
        call = resume_call(command, root, event.get('cwd')) if shell else None
        with actor_state(root, event) as state:
            if name == 'PreToolUse' and state.get('pending') and call is None:
                return deny(CONTEXT)
            if name == 'PreToolUse' and call is not None and call[0] == 'prepare' and state.get('pending'):
                state.update(bundle=None, delivered=[])
            if name == 'PostToolUse' and call is not None and state.get('pending'):
                receipt(state, call, event.get('tool_response'), root)
        if name == 'PostToolUse' and shell:
            message = base_behind.message(command, event.get('cwd', str(root)))
            if message:
                return context(name, message)
    return {}


def main():
    event = {}
    try:
        event = json.load(sys.stdin)
        if not isinstance(event, dict):
            event = {}
            raise ValueError('Expected a Codex hook object')
        result = subprocess.run(['git', 'rev-parse', '--show-toplevel'], cwd=event.get('cwd'),
                                capture_output=True, text=True, check=True)
        output = dispatch(event, Path(result.stdout.strip()))
    except (OSError, ValueError, TypeError, KeyError, AttributeError, subprocess.CalledProcessError) as error:
        message = 'Codex framework hook: ' + str(error)
        output = deny(message) if event.get('hook_event_name') == 'PreToolUse' else {'systemMessage': message}
    print(json.dumps(output))


if __name__ == '__main__':
    main()
