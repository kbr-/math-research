#!/usr/bin/env python3
"""Ranked search of a notebook's Research-record entries by content words.

Give the candidate's content words, including the deciding body and the document; entries
sharing several uncommon words come first whatever their phrasing (tools/record_search.py).

Usage: tools/search-record.py [-n ROWS] [--notebook PATH] WORD [WORD ...]
       tools/search-record.py --catalogue FILE [-n ROWS] [--notebook PATH]
       tools/search-record.py --phrase PHRASE [--phrase PHRASE ...] [-n ROWS]

--phrase lists the entries holding an exact phrase, whatever its case and spacing, with the count in
each, oldest first: the check that a lead, bridge or name is not already in the record.

A catalogue file holds one procedure per line, "NAME<TAB>WORDS", for screening a published list
(a tribunal's jurisdictions, an agency's adjudication schemes) against the record before a draw:
each row shows its best entries and how many of its words their titles share.
"""
import argparse
from pathlib import Path
import sys

from record_search import coverage, phrase_hits, search
from text_stems import stems

ROOT = Path(__file__).resolve().parents[1]
BODY_ROWS = 5


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('words', nargs='*')
    parser.add_argument('-n', type=int, default=None, help='rows to show (default 10; 2 per catalogue row)')
    parser.add_argument('--notebook', default=str(ROOT / 'notebook.html'))
    parser.add_argument('--catalogue', help='file of NAME<TAB>WORDS lines to screen against the record')
    parser.add_argument('--phrase', action='append', default=[], help='exact phrase to find; repeatable')
    args = parser.parse_args(argv)
    text = Path(args.notebook).read_text()
    if args.phrase:
        return show_phrases(text, args.phrase, args.n or 6)
    if args.catalogue:
        return show_catalogue(text, args.catalogue, args.n or 2)
    if not args.words:
        parser.error('give WORDS or --catalogue FILE')
    args.n = args.n or 10
    rows = search(text, args.words)
    for score, anchor, title, hits in rows[:args.n]:
        print(f'{score:6.2f}  {anchor}  [{" ".join(hits)}]\n        {title[:140]}')
    print(f'{len(rows)} entries share at least one word; {min(len(rows), args.n)} shown, ranked by '
          'the words their titles share, then by the whole-text score shown.')
    # A review holds many screened jobs under one generic title, so its matches rank far down by
    # title: a review that had falsified Entra secret expiry ranked about 144th for that job's own
    # words (notebook entry-2026-10-02-entra-expiry). The best whole-text matches are listed too.
    shown = {anchor for _, anchor, _, _ in rows[:args.n]}
    body = [row for row in sorted(rows, key=lambda r: -r[0]) if row[1] not in shown][:BODY_ROWS]
    if body:
        print('Best whole-text matches not shown above:')
        for score, anchor, title, hits in body:
            print(f'{score:6.2f}  {anchor}  [{" ".join(hits)}]\n        {title[:140]}')


def show_phrases(text, phrases, n):
    for phrase in phrases:
        hits = phrase_hits(text, phrase)
        print(f'"{phrase}": {sum(c for _, _, c in hits)} mentions in {len(hits)} entries')
        for anchor, title, count in hits[:n]:
            print(f'        {anchor}  ({count})  {title[:110]}')
    return 0


def show_catalogue(text, path, n):
    rows = []
    for number, line in enumerate(Path(path).read_text().splitlines(), 1):
        if not line.strip() or line.startswith('#'):
            continue
        name, sep, words = line.partition('\t')
        if not sep or not words.split():
            print(f'{path}:{number}: expected NAME<TAB>WORDS', file=sys.stderr)
            return 2
        rows.append((name.strip(), words.split()))
    for (name, words), (_, best) in zip(rows, coverage(text, rows, n)):
        top = max((shared for _, _, shared, _ in best), default=0)
        print(f'{name}  [best title shares {top} of {len(stems(" ".join(words)))} words]')
        for anchor, title, shared, total in best:
            print(f'        {anchor}  ({shared}/{total})  {title[:110]}')
        if not best:
            print('        no entry shares a word')
    return 0


if __name__ == '__main__':
    sys.exit(main())
