#!/usr/bin/env python3
"""Keep the post-commit hook's notices that a commit resembles a queued build item, and what was done about each.

Usage: tools/hook_notices.py list
       tools/hook_notices.py answer IDENT NOTE

The hook prints such a notice once, after the commit, where it is easily passed over: on 11 October 2026 two were,
their items unread.  The hook now records each notice in research/logs/hook-notices.jsonl, which Git ignores;
`answer` records, for an item, what reading it found (built by the commit, part of it, or unrelated), in at
least twenty characters; `list` prints the notices no answer followed, as the finisher does at each checkpoint.
It reports and refuses nothing: an answer is a note, and nothing can tell whether the item was read."""
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = 'research/logs/hook-notices.jsonl'
NOTICE = re.compile(r'resembles the queued build item (\S+) of (\S+)')


def rows(root):
    path = Path(root) / LOG
    found = []
    for line in path.read_text().splitlines() if path.exists() else ():
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if isinstance(row, dict):      # a damaged line must not stop the finisher that reads this log
            found.append(row)
    return found


def append(root, row):
    path = Path(root) / LOG
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a') as log:
        log.write(json.dumps(row) + '\n')


def record(root, text, now=None):
    """Record one row for each item a notice names; return how many."""
    named = NOTICE.findall(text or '')
    for ident, notebook in named:
        append(root, {'unix_s': now if now is not None else time.time(), 'kind': 'notice', 'item': ident,
                      'notebook': notebook})
    return len(named)


def answer(root, ident, note, now=None):
    if len(' '.join(note.split())) < 20:
        raise ValueError('say what reading the item found, in at least twenty characters')
    if not any(row.get('kind') == 'notice' and row.get('item') == ident for row in rows(root)):
        raise ValueError(f'no recorded notice names {ident}')
    append(root, {'unix_s': now if now is not None else time.time(), 'kind': 'answer', 'item': ident, 'note': note})


def unanswered(root, since=0):
    """(item, notebook, times noticed) for the items noticed at or after `since` with no later answer."""
    last, count, where = {}, {}, {}
    for row in rows(root):
        ident = row.get('item')
        if row.get('kind') == 'notice' and row.get('unix_s', 0) >= since:
            last[ident] = max(last.get(ident, 0), row.get('unix_s', 0))
            count[ident] = count.get(ident, 0) + 1
            where[ident] = row.get('notebook', '')
        elif row.get('kind') == 'answer' and ident in last and row.get('unix_s', 0) >= last[ident]:
            del last[ident], count[ident], where[ident]
    return [(ident, where[ident], count[ident]) for ident in last]


def report(root, since=0):
    """Lines for the finisher to print, or none."""
    open_ = unanswered(root, since)
    if not open_:
        return []
    return (['Hook notices not answered: a commit of this session resembled these queued build items; read each '
             'and record what you found with tools/hook_notices.py answer IDENT NOTE:']
            + [f'  {ident} of {notebook}' + (f' ({times} notices)' if times > 1 else '')
               for ident, notebook, times in open_])


def main(argv=None, root=ROOT):
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ['list'] and len(argv) == 1:
        print('\n'.join(report(root)) or 'No hook notice is unanswered.')
        return 0
    if argv[:1] == ['answer'] and len(argv) == 3:
        try:
            answer(root, argv[1], argv[2])
        except ValueError as error:
            print(f'hook_notices.py: {error}', file=sys.stderr)
            return 1
        print(f'Answered {argv[1]}.')
        return 0
    print(__doc__.split('\n\n')[1], file=sys.stderr)
    return 1


if __name__ == '__main__':
    sys.exit(main())
