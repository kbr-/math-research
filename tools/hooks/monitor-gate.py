#!/usr/bin/env python3
"""Claude Code hooks that make arming a monitor the next step after a long background compute.sh run
(COMPUTATION_RULES.md, long runs; user, 3 October 2026: "I want you to arm the monitor, but can we
enforce arming the monitor?").

`post` (PostToolUse, Bash) marks the session when a compute.sh run expected over 60 s or allowed over
180 s (the thresholds of guard-full-output.py) was started with run_in_background.  `pre` (PreToolUse,
every tool) then refuses each tool call except ToolSearch and a Monitor whose command runs
tools/watch_run.py; that Monitor call clears the mark.  Marks live in the ignored
.claude/monitor-pending/, one file per session ID, holding the compute.sh session name.
Usage: monitor-gate.py pre|post, with the hook JSON on stdin."""
import importlib.util
import json
import os
import re
import shlex
import sys
from pathlib import Path

_spec = importlib.util.spec_from_file_location('guard_full_output', Path(__file__).with_name('guard-full-output.py'))
_guard = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_guard)


def mark_path(root, session):
    return Path(root) / '.claude' / 'monitor-pending' / re.sub(r'[^A-Za-z0-9_.-]', '_', session)


def long_run_session(command):
    """The compute.sh session name of a long run in the command ('' for a standalone run), or None."""
    for segment in _guard.SEPARATOR.split(command):
        options = _guard.launcher_options(segment)
        if options is None:
            continue
        def seconds(name):
            value = options.get(name, '')
            return int(value) if value.isdigit() else 0
        if seconds('--expect') <= _guard.FOREGROUND_EXPECT and seconds('--timeout') <= _guard.FOREGROUND_TIMEOUT:
            continue
        words = shlex.split(segment)
        at = next(i for i, w in enumerate(words) if w.endswith('compute.sh'))
        if len(words) > at + 2 and words[at + 1] == 'run':
            return words[at + 2]
        return options.get('--session', '')
    return None


def instruction(name):
    target = f' {name}' if name else ''
    return (f'arm the monitor on the background run first: Monitor with command '
            f'"python3 tools/watch_run.py{target}" and timeout_ms 1800000 (load its schema with ToolSearch '
            f'"select:Monitor" if needed). It reports the 5-minute decision point and the run\'s end '
            f'(COMPUTATION_RULES.md, long runs)')


def pre(payload, root):
    mark = mark_path(root, payload['session_id'])
    if not mark.exists():
        return 0
    tool, tool_input = payload.get('tool_name'), payload.get('tool_input') or {}
    if tool == 'ToolSearch':
        return 0
    if tool == 'Monitor' and 'watch_run.py' in (tool_input.get('command') or ''):
        mark.unlink(missing_ok=True)
        return 0
    name = mark.read_text().strip()
    print('Refused: ' + instruction(name), file=sys.stderr)
    return 2


def post(payload, root):
    tool_input = payload.get('tool_input') or {}
    if payload.get('tool_name') != 'Bash' or not tool_input.get('run_in_background'):
        return 0
    name = long_run_session(tool_input.get('command') or '')
    if name is None:
        return 0
    mark = mark_path(root, payload['session_id'])
    mark.parent.mkdir(parents=True, exist_ok=True)
    mark.write_text(name + '\n')
    return 0


def main(argv):
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    if len(argv) != 2 or argv[1] not in ('pre', 'post') or not payload.get('session_id'):
        return 0
    root = os.environ.get('CLAUDE_PROJECT_DIR') or payload.get('cwd') or '.'
    return {'pre': pre, 'post': post}[argv[1]](payload, root)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
