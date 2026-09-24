#!/usr/bin/env python3
"""Append a drafted research-record entry and optionally replace the Proposed next step.

The entry file holds one <article> element. It is inserted after the last article of the
selected notebook's research record. With --next FILE, the body of the proposed-next-step
section is replaced by the file's HTML (the section heading is kept). Fails closed if the entry's
anchor already exists or the record or section is missing.
"""
# Copyright (c) 2026 Kamil Braun. SPDX-License-Identifier: MIT

import argparse
from pathlib import Path
import re
import sys
from notebooks import selected, ROOT

HEADING = '<h2>Proposed next step</h2>'


def append(source, entry, next_html=None):
    entry = entry.strip()
    m = re.match(r'<article id="([^"]+)"', entry)
    if not m or not entry.endswith('</article>'):
        raise ValueError('entry must be one <article id="..."> ... </article> element')
    if f'id="{m.group(1)}"' in source:
        raise ValueError(f'anchor already present: {m.group(1)}')
    start = source.find('<section id="research-record">')
    if start < 0:
        raise ValueError('research-record section missing')
    close = source.find('</section>', start)
    last = source.rfind('</article>', start, close)
    at = last + len('</article>') if last >= 0 else source.index('>', start) + 1
    source = source[:at] + '\n' + entry + source[at:]
    if next_html is not None:
        a = source.find('<section id="proposed-next-step">')
        if a < 0:
            raise ValueError('proposed-next-step section missing')
        b = source.index('</section>', a)
        body = source[a:b]
        if HEADING not in body:
            raise ValueError('proposed-next-step heading missing')
        head = body[:body.index(HEADING) + len(HEADING)]
        source = source[:a] + head + '\n' + next_html.strip() + '\n' + source[b:]
    return source


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('entry', type=Path)
    parser.add_argument('--next', type=Path, dest='next_file')
    parser.add_argument('--notebook')
    args = parser.parse_args()
    path = Path(ROOT) / selected(args.notebook)['source']
    nxt = args.next_file.read_text() if args.next_file else None
    try:
        path.write_text(append(path.read_text(), args.entry.read_text(), nxt))
    except ValueError as err:
        sys.exit(f'notebook-append.py: {err}')
    print(f'Appended to {path.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
