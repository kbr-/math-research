"""The log of the times a hook blocked a call or a stop, with what the hook said, so the blocks of a
stretch of work can be counted and read.

record(HOOK) appends one line, time and hook name, to research/logs/hook-state/blocks.tsv, which git
ignores. It writes only inside a Claude Code session of this checkout (CLAUDE_PROJECT_DIR names the
directory this file lies in; a test run leaves it unset or names a directory of its own), and a
failure to write is never the hook's failure. A block may also keep the files the refused call named
by full path, in a last field "paths=PATH PATH", which blocks() reads back: a refused command that was
to write a file left that file as it was.
"""
from datetime import datetime
import os
from pathlib import Path
import re

LOG = Path(__file__).resolve().parents[2] / 'research' / 'logs' / 'hook-state' / 'blocks.tsv'

# A file named by its full path: /dir/.../name.ext.
FULL_PATH = re.compile(r'(?<![\w.~*-])(/(?:[\w.+-]+/)+[\w+-][\w.+-]*\.[A-Za-z0-9]{1,5})(?![\w/*])')


ASSIGNMENT = re.compile(r'(?<![\w$])([A-Za-z_]\w*)=(/[^\s;&|\'"]+)')


def paths_in(text):
    """The files `text` names by full path, in order, each once; a shell variable assigned a full path in the
    text (T=/scratch && ... $T/spec.json) is expanded first, since on 16 October 2026 a refused command named
    the files it was to write only as $T/... and the block log kept none of them."""
    text, values, expanded, start = text or '', {}, [], 0
    # Each use takes the value of the latest assignment before it (T=/a ... T=/b ... $T/x reads /b).
    for match in list(ASSIGNMENT.finditer(text)) + [None]:
        end = match.start() if match else len(text)
        segment = text[start:end]
        for name, value in values.items():
            segment = re.sub(r'\$\{?' + name + r'\}?(?=/)', lambda _: value.rstrip('/'), segment)
        expanded.append(segment)
        if match:
            values[match.group(1)] = match.group(2)
            start = match.start()
    return list(dict.fromkeys(FULL_PATH.findall(''.join(expanded))))


def record(hook, log=None, now=None, what='', paths=()):
    """Append the block; `what`, the message the hook gave, follows on the same line, cut to 300 characters,
    so that a check's blocks can be read back and its wrong ones found; `paths`, the files the refused call
    named, close the line."""
    # A session runs the hooks of its own project directory; a test that sets the variable names another.
    project = os.environ.get('CLAUDE_PROJECT_DIR')
    if log is None and not (project and Path(__file__).resolve().is_relative_to(Path(project).resolve())):
        return
    log = log or LOG
    try:
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open('a') as stream:
            said = ' '.join(str(what).split())[:300]
            named = ' '.join(p for p in paths if '\t' not in p and ' ' not in p)
            stream.write(f"{(now or datetime.now()).isoformat(timespec='seconds')}\t{hook}" + (f'\t{said}' if said else '')
                         + (f'\tpaths={named}' if named else '') + '\n')
    except OSError:
        pass


def blocks(log=None):
    """The logged blocks, oldest first, as (time, hook, paths) with paths a list."""
    try:
        lines = Path(log or LOG).read_text(errors='replace').splitlines()
    except OSError:
        return []
    found = []
    for line in lines:
        fields = line.split('\t')
        try:
            when = datetime.fromisoformat(fields[0])
        except ValueError:
            continue
        named = next((f[len('paths='):].split() for f in fields[2:] if f.startswith('paths=')), [])
        found.append((when, fields[1] if len(fields) > 1 else '', named))
    return found
