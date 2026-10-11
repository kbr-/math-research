#!/usr/bin/env python3
"""Checks that fire while a turn runs, since a long autonomous turn never reaches the Stop hook.

Usage (a PreToolUse hook; the tool call is on standard input):
  during_run.py commit    for Bash: before a `git commit`, the Stop hook's checks of a turn
                          (tools/hooks/stop_checks.py) run on what the assistant wrote since the last
                          commit this check saw: a promise about future behaviour or an admission
                          that implies one, a tool's fault worked around, a declared gap, and, by
                          its Haiku judge, an unchecked claim. The first one found blocks that
                          commit once, with the Stop hook's own request. The shell guard calls this
                          for a commit, so other commands pay nothing.

A blocked call exits 2 with the message on standard error. What was already said is kept per session
under research/logs/hook-state/, which git ignores.
"""
import json
import os
from pathlib import Path
import re
import sys

ROOT =Path(__file__).resolve().parents[2]
STATE = ROOT / 'research' / 'logs' / 'hook-state'
COMMIT = re.compile(r'(?:^|[;&|(]\s*|\s)git\b[^;&|]*\bcommit\b')


def load(session, directory=None):
    path = (directory or STATE) / f'{session or "unknown"}.json'
    try:
        return path, json.loads(path.read_text())
    except (OSError, ValueError):
        return path, {}


def save(path, state):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state))


def written_since(transcript, offset):
    """(the assistant's text and thinking blocks in the transcript's complete lines from byte
    `offset` on, the offset after the last complete line)."""
    with open(transcript, 'rb') as stream:
        if offset is None:
            # The first commit this check sees: what was written before it is not its to judge.
            return [], [], '', stream.seek(0, 2)
        stream.seek(offset)
        data = stream.read()
    end = data.rfind(b'\n') + 1
    calls, texts, said = [], [], []
    for line in data[:end].split(b'\n'):
        try:
            entry = json.loads(line)
            entry_calls, entry_texts = stop_checks.blocks_in(entry)
        except (ValueError, AttributeError):
            continue
        calls.extend(entry_calls)
        texts.extend(entry_texts)
        if entry_texts:
            # What the assistant said to the user, as opposed to what it thought.
            said.extend(block.get('text') or '' for block in entry['message']['content'] if block.get('type') == 'text')
    return calls, texts, '\n'.join(said), offset + end


def commit(data, directory=None):
    """The message that blocks this Bash call, or None."""
    if not COMMIT.search((data.get('tool_input') or {}).get('command') or ''):
        return None
    # Loaded for a commit alone: this hook runs before every shell command.
    global stop_checks
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import stop_checks
    path, state = load(data.get('session_id'), directory)
    try:
        calls, texts, said, offset = written_since(data.get('transcript_path') or '', state.get('offset'))
    except OSError:
        return None
    save(path, {**state, 'offset': offset})
    # The Stop hook's own checks of a turn, in its order.
    off = stop_checks.checks_off(stop_checks.ROOT)
    blocked = stop_checks.turn_block(texts, calls, said, off)
    if not blocked and said.strip() and 'judge' not in off:
        verdict = judge(said, calls)
        if verdict and 'error' not in verdict and not verdict['ok']:
            blocked = {'reason': (f"Unchecked claim: \"{verdict['quote']}\" {verdict['reason']} Check what the tool "
                                  'already offers (its documentation, --help, a scratch test) before building on it, '
                                  'and what the repository the change is for already has for the same concern (search '
                                  'it by the concern, not by the name you gave your own mechanism); if this turn '
                                  'already checked, say which search or run it was and what it found. A test of what '
                                  'you just built is no such check.')}
    if not blocked:
        return None
    return (f"Before this commit, in what was written since the last one: {blocked['reason']} Then commit again: this "
            'check has now seen that text.')


def judge(said, calls):
    """Haiku's verdict on an unchecked claim in `said`, as the Stop hook asks it; None where it gives none."""
    return stop_checks.judge(said, calls)





def main(argv):
    # A judge's own session (tools/haiku_judge.py sets this) is not checked.
    if os.environ.get('INSIDE_HAIKU_JUDGE') or argv != ['commit']:
        return 0
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return 0
    message = commit(data)
    if message:
        print(message, file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    status = main(sys.argv[1:])
    if status == 2:
        import block_log
        block_log.record('during_run')
    sys.exit(status)
