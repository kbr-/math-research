"""The log of the times a hook blocked a call or a stop, which tools/cycle_numbers.py counts per cycle.

record(HOOK) appends one line, time and hook name, to research/logs/hook-state/blocks.tsv, which git
ignores. It writes only inside a Claude Code session of this checkout (CLAUDE_PROJECT_DIR names the
directory this file lies in; a test run leaves it unset or names a directory of its own), and a
failure to write is never the hook's failure.
"""
from datetime import datetime
import os
from pathlib import Path

LOG = Path(__file__).resolve().parents[2] / 'research' / 'logs' / 'hook-state' / 'blocks.tsv'


def record(hook, log=None, now=None):
    # A session runs the hooks of its own project directory; a test that sets the variable names another.
    project = os.environ.get('CLAUDE_PROJECT_DIR')
    if log is None and not (project and Path(__file__).resolve().is_relative_to(Path(project).resolve())):
        return
    log = log or LOG
    try:
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open('a') as stream:
            stream.write(f"{(now or datetime.now()).isoformat(timespec='seconds')}\t{hook}\n")
    except OSError:
        pass
