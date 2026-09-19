#!/usr/bin/env python3
"""Ranked search of research/CLAIM_INDEX.md by the content words of a statement.

A grep for one phrase misses a recorded claim that uses other words ("point-support lower bound"
was missed by "support size"). Give the statement's content words; rows are ranked by the rarity-
weighted number of distinct word stems they contain, so a row sharing several uncommon words with
the statement comes first whatever the phrasing.

Usage: tools/search-claims.py [-n ROWS] WORD [WORD ...]"""
import argparse
import math
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
STOP = set('a an and are as at be by for from has have in is it its no not of on or over that the this to '
           'with without every each any all at most least than then under into only which whose'.split())


def stem(word):
    word = word.lower()
    for suffix in ('ations', 'ation', 'ings', 'ing', 'ies', 'ed', 'es', 's'):
        if word.endswith(suffix) and len(word) - len(suffix) >= 4:
            return word[:len(word) - len(suffix)]
    return word


def stems(text):
    return {stem(w) for w in re.findall(r'[A-Za-z][A-Za-z0-9]+', text) if w.lower() not in STOP}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-n', type=int, default=12, help='rows to print')
    parser.add_argument('words', nargs='+')
    args = parser.parse_args()
    rows = [(number, line) for number, line in
            enumerate((ROOT / 'research/CLAIM_INDEX.md').read_text().splitlines(), 1) if line.startswith('| `')]
    row_stems = [stems(line.split('](')[0] if '](' in line else line) for _, line in rows]
    query = stems(' '.join(args.words))
    count = {q: sum(1 for s in row_stems if any(t.startswith(q) or q.startswith(t) for t in s)) for q in query}
    weight = {q: math.log((len(rows) + 1) / (c + 1)) for q, c in count.items()}
    scored = []
    for (number, line), s in zip(rows, row_stems):
        hit = [q for q in query if any(t.startswith(q) or q.startswith(t) for t in s)]
        if hit:
            scored.append((sum(weight[q] for q in hit), number, line, hit))
    scored.sort(key=lambda item: -item[0])
    for score, number, line, hit in scored[:args.n]:
        cells = [c.strip() for c in line.strip('|').split('|')]
        print(f'{score:5.1f}  line {number}  {cells[0]}  [{", ".join(sorted(hit))}]')
        print('       ' + cells[1][:230])


if __name__ == '__main__':
    main()
