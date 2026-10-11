#!/usr/bin/env python3
"""Find attempts owed on a queue item that entry after entry reports unmade.

Usage: tools/deferred_attempts.py NOTEBOOK.html

An entry on an item whose last entry named a next attempt says, after "Owed attempt.", what became of it.  An
attempt reported unmade in two entries in a row on one item is made or dropped in the next: a reading deferred
three times held a published form of a period's main result (11 October 2026).  The finisher prints a third
deferral; this lists, for a notebook's record, every entry that defers and those it would print, marked THIRD.

Words only.  Known misreadings: an entry that makes the attempt deferred twice and says so ("the attempt deferred
twice is made") counts as deferring; "dropped" anywhere in the paragraph counts as dropping; a denial ("nothing
... owed") hides a deferral later in its sentence; an entry tagged with two items is judged by the first."""
import html
import re
import sys
from pathlib import Path

ARTICLE = re.compile(r'<article\b([^>]*)>(.*?)</article>', re.S)
ITEM = re.compile(r'\bdata-(lead|bridge|idea|check|build)="([^"]+)"')
OWED = re.compile(r'<strong>Owed attempt\.</strong>((?:(?!</p>)(?!</li>).)*)', re.S)
UNMADE = re.compile(r'\bnot reached\b|\b(?:again |is |are )?not made\b|\bunmade\b|\bstays? owed\b|\bdeferred\b|'
                    r'\b(?:did|have) not read\b', re.I)
DENIED = re.compile(r'\b(?:none|nothing|no attempt)\b[^.]*?\b(?:unmade|owed|deferred)\b', re.I)
DROPPED = re.compile(r'\bdropped\b|\bwill not be made\b|\bis given up\b|\bno longer owed\b', re.I)


def owed_text(entry):
    return ' '.join(html.unescape(re.sub(r'<[^>]*>', ' ', ' '.join(OWED.findall(entry)))).split())


def defers(entry):
    """Whether an entry's Owed attempt paragraphs report an attempt unmade without dropping it."""
    text = DENIED.sub(' ', owed_text(entry))
    return bool(UNMADE.search(text)) and not DROPPED.search(text)


def item_of(tag):
    found = ITEM.search(tag)
    return found.groups() if found else None


def third_deferral(earlier, entry_tag, entry):
    """The anchors of the two previous entries on the entry's item, if both defer and the entry defers again.

    `earlier` is the record before the entry, as (tag, body) pairs in order."""
    item = item_of(entry_tag)
    if item is None or not defers(entry):
        return None
    same = [(tag, body) for tag, body in earlier if item_of(tag) == item][-2:]
    if len(same) == 2 and all(defers(body) for _, body in same):
        return [re.search(r'\bid="([^"]+)"', tag).group(1) if 'id="' in tag else '?' for tag, _ in same]
    return None


def survey(text):
    """(entry, item, defers, refused) for every entry on a queue item, in the record's order."""
    record = text[text.find('<section id="research-record"'):]
    entries, rows = ARTICLE.findall(record), []
    for index, (tag, body) in enumerate(entries):
        item = item_of(tag)
        if item is None:
            continue
        ident = re.search(r'\bid="([^"]+)"', tag)
        rows.append((ident.group(1) if ident else '?', item[1], defers(body),
                     bool(third_deferral(entries[:index], tag, body))))
    return rows


def main():
    if len(sys.argv) != 2 or sys.argv[1].startswith('-'):
        sys.exit(__doc__.split('\n\n')[1])
    rows = survey(Path(sys.argv[1]).read_text())
    for ident, item, deferring, refused in rows:
        if deferring:
            print(f'{"THIRD" if refused else "defers"}\t{item}\t{ident}')
    print(f'{len(rows)} entries on queue items; {sum(row[2] for row in rows)} defer an owed attempt; '
          f'{sum(row[3] for row in rows)} are a third deferral in a row on one item.')


if __name__ == '__main__':
    main()
