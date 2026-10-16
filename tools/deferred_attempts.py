#!/usr/bin/env python3
"""Find attempts owed on a queue item that entry after entry reports unmade.

Usage: tools/deferred_attempts.py [--carried] NOTEBOOK.html

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
sys.path.insert(0, str(Path(__file__).resolve().parent))
from notebook_math import strip_tags  # noqa: E402

ARTICLE = re.compile(r'<article\b([^>]*)>(.*?)</article>', re.S)
ITEM = re.compile(r'\bdata-(lead|bridge|idea|check|build)="([^"]+)"')
OWED = re.compile(r'<strong>Owed attempt\.</strong>((?:(?!</p>)(?!</li>).)*)', re.S)
UNMADE = re.compile(r'\bnot reached\b|\b(?:again |is |are )?not made\b|\bunmade\b|\bstays? owed\b|\bdeferred\b|'
                    r'\b(?:did|have) not read\b', re.I)
DENIED = re.compile(r'\b(?:none|nothing|no attempt)\b[^.]*?\b(?:unmade|owed|deferred)\b', re.I)
DROPPED = re.compile(r'\bdropped\b|\bwill not be made\b|\bis given up\b|\bno longer owed\b', re.I)


def owed_text(entry):
    return ' '.join(html.unescape(strip_tags(' '.join(OWED.findall(entry)))).split())


def defers(entry):
    """Whether an entry's Owed attempt paragraphs report an attempt unmade without dropping it."""
    text = DENIED.sub(' ', owed_text(entry))
    return bool(UNMADE.search(text)) and not DROPPED.search(text)


QUOTE = 8
IDENT = re.compile(r'\bentry-[\w-]+:s?\d+\b')


def handles(entry):
    """What the deferring sentences of an entry's Owed attempt paragraphs name their attempt by: the anchors
    they link, the queue identifiers they write, and their runs of QUOTE consecutive words."""
    raw = re.sub(r'<a\b[^>]*\bhref="#([^"]+)"[^>]*>', r' @\1 ', ' '.join(OWED.findall(entry)))
    text = ' '.join(html.unescape(strip_tags(raw)).split())
    found = set()
    for sentence in re.split(r'(?<=\.)\s+', text):
        if not UNMADE.search(DENIED.sub(' ', sentence)) or DROPPED.search(sentence):
            continue
        found.update(('link', anchor) for anchor in re.findall(r'@(\S+)', sentence))
        found.update(('item', ident) for ident in IDENT.findall(sentence))
        words = re.findall(r"[a-z0-9']+", IDENT.sub(' ', re.sub(r'@\S+', ' ', sentence)).lower())
        found.update(('words', ' '.join(words[at:at + QUOTE])) for at in range(len(words) - QUOTE + 1))
    return found


def carried(first, second):
    """The handles two entries' deferring sentences share: a way to tell that both defer one attempt."""
    return handles(first) & handles(second)


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


def survey_carried(text):
    """(entry, item, shared with the previous entry on the item, shared by that entry with the one before) for
    every third deferral in a row: whether links, identifiers or quotations identify one attempt in all three."""
    record = text[text.find('<section id="research-record"'):]
    entries, rows = ARTICLE.findall(record), []
    for index, (tag, body) in enumerate(entries):
        if not third_deferral(entries[:index], tag, body):
            continue
        item = item_of(tag)
        before, previous = [found for found_tag, found in entries[:index] if item_of(found_tag) == item][-2:]
        rows.append((re.search(r'\bid="([^"]+)"', tag).group(1), item[1],
                     carried(previous, body), carried(before, previous)))
    return rows


def kinds(shared):
    return ', '.join(sorted({kind for kind, _ in shared})) or 'nothing'


def main():
    if len(sys.argv) == 3 and sys.argv[1] == '--carried':
        rows = survey_carried(Path(sys.argv[2]).read_text())
        for ident, item, last, earlier in rows:
            print(f'{"one attempt" if last and earlier else "not identified"}\t{item}\t{ident}\t'
                  f'with the previous entry: {kinds(last)}; that entry with the one before: {kinds(earlier)}')
        print(f'{len(rows)} third deferrals in a row; in {sum(bool(a and b) for _, _, a, b in rows)} the deferring '
              'sentences of all three share a link, an identifier or a quotation.')
        return
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
