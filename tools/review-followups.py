#!/usr/bin/env python3
"""Print the Bridge follow-up and Lead follow-up sections a new route review needs.

Lists, with the finisher's own rule (finish-turn.py open_items), every passed Absurd bridge and passed
Outside lead of earlier reviews on ROUTE that no follow-up has closed, one <li data-bridge|data-lead>
per item. Each item gets the text given for it in --notes (a JSON object mapping "bridge:ID" or
"lead:ID" to HTML ending with its <strong>Follow-up.</strong> outcome), or else "No new work on this
item in this period." with "Continuing". Paste the output into the review before the Assessment.
"""
# Copyright (c) 2026 Kamil Braun. SPDX-License-Identifier: MIT

import argparse
import importlib.util
import json
from pathlib import Path
import sys

from notebooks import selected, ROOT

_spec = importlib.util.spec_from_file_location('finish_turn', Path(__file__).with_name('finish-turn.py'))
FT = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(FT)

NONE = 'No new work on this item in this period. <strong>Follow-up.</strong> Continuing.'


def followups(body, route, notes=None):
    """HTML of the two follow-up sections for a review appended at the end of the record."""
    notes = notes or {}
    record = body.find('<section id="research-record">')
    if record < 0:
        raise ValueError('research-record section missing')
    end = body.find('</section>', record)
    earlier = FT.route_articles(body, end, route)
    out, used = [], set()
    for _, section_re, followup_re, item_re, heading, attr in FT.FOLLOWUP_KINDS:
        kind = attr[len('data-'):]
        items = []
        for ident in FT.open_items(body, earlier, section_re, followup_re, item_re):
            key = f'{kind}:{ident}'
            text = notes.get(key, NONE)
            used.add(key)
            if not FT.FOLLOWUP_OUTCOME.search(text):
                raise ValueError(f'note for {key} lacks a <strong>Follow-up.</strong> outcome')
            items.append(f'<li {attr}="{ident}">{text}</li>')
        if items:
            out.append(f'<h4>{heading}</h4>\n<ul>\n' + '\n'.join(items) + '\n</ul>')
    unknown = sorted(set(notes) - used)
    if unknown:
        raise ValueError('notes name items that are not open: ' + ', '.join(unknown))
    return '\n'.join(out) + ('\n' if out else '')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('route', help='data-route of the review')
    parser.add_argument('--notebook')
    parser.add_argument('--notes', type=Path, help='JSON object {"bridge:ID"|"lead:ID": html}')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    body = (Path(ROOT) / selected(args.notebook)['source']).read_text()
    notes = json.loads(args.notes.read_text()) if args.notes else {}
    try:
        html = followups(body, args.route, notes)
    except ValueError as err:
        sys.exit(f'review-followups.py: {err}')
    if args.out:
        args.out.write_text(html)
        print(f'Wrote {args.out}')
    else:
        sys.stdout.write(html)


if __name__ == '__main__':
    main()
