#!/usr/bin/env python3
"""Audit the research record's open work (tools/record_audit.py).

Usage: tools/record-audit.py leads [--never] [--notebook PATH]
       tools/record-audit.py gaps [--notebook PATH]
       tools/record-audit.py not-run [--due YYYY-MM-DD] [--notebook PATH]

leads: each lead and bridge in the latest review's follow-up lists with its last real work;
       --never shows only those never worked on.
gaps:  entries whose remaining gap is open and which no later entry links, with the later entry
       the record search ranks first for the gap, which may have done the work without a link.
not-run: each review's leads and bridges whose test was not run, which no follow-up list carries,
       with the later entry the record search ranks first for the item's name; --due shows only
       items whose reason names a date on or before the one given, so date-gated items surface.
"""
import argparse
import datetime
from pathlib import Path
import sys

from record_audit import carried_items, not_run, open_gaps, reason_date

ROOT = Path(__file__).resolve().parents[1]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('report', choices=['leads', 'gaps', 'not-run'])
    parser.add_argument('--never', action='store_true', help='leads never worked on only')
    parser.add_argument('--due', type=datetime.date.fromisoformat,
                        help='not-run items whose reason names a date on or before this one only')
    parser.add_argument('--notebook', default=str(ROOT / 'notebook.html'))
    args = parser.parse_args(argv)
    text = Path(args.notebook).read_text()
    if args.report == 'leads':
        rows = carried_items(text)
        shown = [r for r in rows if not (args.never and r[3])]
        for kind, key, name, last in shown:
            print(f'{kind:6s} {key}  {name[:50]}\n        {last[:120] or "(never worked)"}')
        print(f'{len(shown)} of {len(rows)} carried items shown; '
              f'{sum(1 for r in rows if not r[3])} never worked.')
    elif args.report == 'not-run':
        rows = not_run(text)
        shown = [r for r in rows if args.due is None or (reason_date(r[3]) or datetime.date.max) <= args.due]
        for key, section, name, reason, later, naming in shown:
            dated = reason_date(reason)
            print(f'{key}  [{section}] {name[:60]}\n        {reason[:110]}' + (f'\n        dated: {dated}' if dated else '')
                  + f'\n        nearest later entry: {later or "(none)"}'
                  f'\n        later entries naming it: {", ".join(naming) or "(none)"}')
        print(f'{len(shown)} of {len(rows)} leads and bridges whose test was not run shown'
              + (f', those dated on or before {args.due}.' if args.due else '.'))
    else:
        rows = open_gaps(text)
        for anchor, gap, later in rows:
            print(f'{anchor}\n        gap: {gap[:150]}\n        nearest later entry: {later or "(none)"}')
        print(f'{len(rows)} open gaps no later entry links.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
