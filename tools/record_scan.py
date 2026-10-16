#!/usr/bin/env python3
"""Run a named text check of the framework over every record entry and print what it matches.

Usage: tools/record_scan.py CHECK [--notebook PATH] [--since YYYY-MM-DD] [--out FILE]
       tools/record_scan.py --list

A check that refuses text on its words is counted over the record's past entries before its commit,
so that its false refusals are counted, not only its catches (AGENTS.md, framework maintenance). Each
check is a function from an entry's plain text to the passages it matches; this tool applies it to
every article, prints each match with its anchor, then the count and how much it read.
"""
import argparse
import html
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
ARTICLE = re.compile(r'<article id="(entry-[^"]+)"(.*?)</article>', re.S)


def finisher():
    spec = importlib.util.spec_from_file_location('finish_turn', ROOT / 'tools/finish-turn.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def plain_text(fragment):
    from notebook_math import strip_tags
    return ' '.join(html.unescape(strip_tags(fragment)).split())


def matches_of(pattern):
    def check(plain, raw=None):
        return [plain[max(0, m.start() - 80):m.end() + 40] for m in pattern.finditer(plain)]
    return check


def checks():
    """Name to check function (plain text, raw HTML) -> matched passages, built lazily from the tools."""
    ft = finisher()
    found = {'planned-tense': matches_of(ft.LATER_TURN_DONE)}
    for name in getattr(ft, 'SCAN_CHECKS', {}):
        found[name] = ft.SCAN_CHECKS[name]
    return found


def scan(text, check, since=None):
    rows, entries = [], 0
    for anchor, body in ARTICLE.findall(text):
        date = anchor[len('entry-'):len('entry-') + 10]
        if since and date < since:
            continue
        entries += 1
        for passage in check(plain_text(body), body):
            rows.append((anchor, passage))
    return rows, entries


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('check', nargs='?')
    parser.add_argument('--list', action='store_true')
    parser.add_argument('--notebook', default=str(ROOT / 'notebook.html'))
    parser.add_argument('--since')
    parser.add_argument('--out')
    args = parser.parse_args(argv)
    available = checks()
    if args.list or not args.check:
        print('\n'.join(sorted(available)))
        return 0
    if args.check not in available:
        parser.error(f'unknown check {args.check}; --list shows them')
    from notebooks import notebook_file
    text = notebook_file(args.notebook).read_text(encoding='utf-8')
    rows, entries = scan(text, available[args.check], args.since)
    lines = [f'{anchor}\t{passage}' for anchor, passage in rows]
    lines.append(f'{len(rows)} matches of {args.check} in {entries} entries'
                 + (f' from {args.since}' if args.since else '') + f' ({len(text) / 1e6:.1f} MB read).')
    report = '\n'.join(lines) + '\n'
    if args.out:
        out = Path(args.out)
        if out.exists():
            parser.error(f'{out} exists')
        out.write_text(report)
    sys.stdout.write(report)
    return 0


if __name__ == '__main__':
    sys.exit(main())
