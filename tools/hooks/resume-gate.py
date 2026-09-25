#!/usr/bin/env python3
"""Claude Code hooks that make the Resume protocol the first thing done after a compaction.

`start` (SessionStart, matcher compact) marks the session as needing restoration and tells the
agent so. `pre` (PreToolUse, every tool) then refuses each tool call except a run of
`tools/resume.py`, exiting with status 2 and the reason on stderr. `post` (PostToolUse, Bash)
clears the mark once a resume.py call has printed the bundle's last part. Marks live in the
ignored `.claude/resume-pending/`, one file per session ID, so parallel sessions in one checkout
do not block each other. Usage: resume-gate.py start|pre|post, with the hook JSON on stdin.
"""
import importlib.util
import json
import os
import re
import sys
import time
from pathlib import Path

_spec = importlib.util.spec_from_file_location('guard_full_output', Path(__file__).with_name('guard-full-output.py'))
_guard = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_guard)
# A resume.py run, by the output guard's notion of where a segment runs its program.
RESUME_RUN = re.compile(_guard.INVOKED + r"resume\.py\b")
CD = re.compile(r"^\s*cd(?:\s+\S+)?\s*$")
LAST_PART = 'END RESUME BUNDLE'
STALE_S = 7 * 24 * 3600
CONTEXT = ('Compaction happened. Immediately perform the Resume protocol before doing anything else: '
           'run python3 tools/resume.py and read every part it lists. Until the last part is read, '
           'every other tool call is refused.')


def runs_resume(command):
    """True if the command only runs tools/resume.py, optionally after cd: every segment between
    ;, &&, ||, | and newlines is a resume.py run or a cd, and no command substitution occurs."""
    if '$(' in command or '`' in command:
        return False
    segments = [s for s in re.split(r"\|\||&&|;|\n|\|", command) if s.strip()]
    return any(RESUME_RUN.search(s) for s in segments) and \
        all(RESUME_RUN.search(s) or CD.match(s) for s in segments)


def marks(root):
    return Path(root) / '.claude' / 'resume-pending'


def mark_path(root, session):
    return marks(root) / re.sub(r'[^A-Za-z0-9_.-]', '_', session)


def start(payload, root, now=time.time):
    directory = marks(root)
    directory.mkdir(parents=True, exist_ok=True)
    for old in directory.iterdir():
        if now() - old.stat().st_mtime > STALE_S:
            old.unlink(missing_ok=True)
    mark_path(root, payload['session_id']).write_text('compaction\n')
    print(json.dumps({'hookSpecificOutput': {'hookEventName': 'SessionStart', 'additionalContext': CONTEXT}}))
    return 0


def pre(payload, root):
    if not mark_path(root, payload['session_id']).exists():
        return 0
    command = (payload.get('tool_input') or {}).get('command') or ''
    if payload.get('tool_name') == 'Bash' and runs_resume(command):
        return 0
    print('Refused: this session was compacted and has not restored context. Perform the Resume protocol '
          'first: run python3 tools/resume.py bare and read every part it lists, then continue the task.',
          file=sys.stderr)
    return 2


def post(payload, root):
    command = (payload.get('tool_input') or {}).get('command') or ''
    if payload.get('tool_name') == 'Bash' and runs_resume(command) \
            and LAST_PART in json.dumps(payload.get('tool_response'), ensure_ascii=False):
        mark_path(root, payload['session_id']).unlink(missing_ok=True)
    return 0


def main(argv):
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    if len(argv) != 2 or argv[1] not in ('start', 'pre', 'post') or not payload.get('session_id'):
        return 0
    root = os.environ.get('CLAUDE_PROJECT_DIR') or payload.get('cwd') or '.'
    return {'start': start, 'pre': pre, 'post': post}[argv[1]](payload, root)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
