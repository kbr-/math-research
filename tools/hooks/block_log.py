"""The log of the times a hook blocked a call or a stop, with what the hook said, so the blocks of a
stretch of work can be counted and read.

record(HOOK) appends one line, time and hook name, to research/logs/hook-state/blocks.tsv, which git
ignores. It writes only inside a Claude Code session of this checkout (CLAUDE_PROJECT_DIR names the
directory this file lies in; a test run leaves it unset or names a directory of its own), and a
failure to write is never the hook's failure.
"""
from datetime import datetime
import os
from pathlib import Path

LOG = Path(__file__).resolve().parents[2] / 'research' / 'logs' / 'hook-state' / 'blocks.tsv'


def record(hook, log=None, now=None, what=''):
    """Append the block; `what`, the message the hook gave, follows on the same line, cut to 300 characters,
    so that a check's blocks can be read back and its wrong ones found."""
    # A session runs the hooks of its own project directory; a test that sets the variable names another.
    project = os.environ.get('CLAUDE_PROJECT_DIR')
    if log is None and not (project and Path(__file__).resolve().is_relative_to(Path(project).resolve())):
        return
    log = log or LOG
    try:
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open('a') as stream:
            said = ' '.join(str(what).split())[:300]
            stream.write(f"{(now or datetime.now()).isoformat(timespec='seconds')}\t{hook}" + (f'\t{said}' if said else '') + '\n')
    except OSError:
        pass
