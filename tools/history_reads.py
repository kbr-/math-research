#!/usr/bin/env python3
"""The earlier entries of the queue items a next step names that the session has not read.

A cycle that develops a queued item must link and quote each earlier entry on it (notebook-append.py), and on
16 October 2026 the error cube floor cycle learnt this only when the finisher refused its entry, after the
mathematics was written.  `compute.sh phase SESSION mathematics` runs this tool: it takes the items the
Proposed next step names, their earlier entries (notebook-append.py's item history) and the anchors that
tools/notebook-excerpt.py printed or saved since the session began (research/logs/excerpt-reads.jsonl), and
prints the entries not yet read, so that they are read before planning.  Advisory: it never refuses.

Usage: history_reads.py --since UNIX_S [--notebook NAME]
Prints how many entries and log lines it compared, which its work grows with.
"""
# Copyright (c) 2026 Kamil Braun. SPDX-License-Identifier: MIT
import argparse
import importlib.util
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
READ_LOG = ROOT / 'research' / 'logs' / 'excerpt-reads.jsonl'


def _append_tool():
    spec = importlib.util.spec_from_file_location('notebook_append', ROOT / 'tools' / 'notebook-append.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_anchors(lines, since, notebook):
    """The anchors read in `notebook` at or after `since`, from read-log lines."""
    read = set()
    for line in lines:
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if row.get('unix_s', 0) >= since and row.get('notebook') == notebook:
            read.update(row.get('anchors', []))
    return read


def unread_history(source, read, tool=None):
    """[(item label, [unread anchor, ...]), ...] for the items the notebook's Proposed next step names."""
    tool = tool or _append_tool()
    found = re.search(r'<section id="proposed-next-step">(.*?)</section>', source, re.S)
    if not found:
        return []
    out = []
    for ident, *_ in tool.named_items(source, found.group(1)) or []:
        missing = [anchor for anchor, _ in tool.item_history(source, ident) if anchor not in read]
        if missing:
            out.append((getattr(ident, 'label', str(ident)), missing))
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--since', type=float, required=True, help='session start, Unix seconds')
    parser.add_argument('--notebook', help='research thread name (default: the selected one)')
    args = parser.parse_args(argv)
    import notebooks
    item = notebooks.selected(args.notebook, ROOT)
    source = (ROOT / item['source']).read_text(encoding='utf-8')
    lines = READ_LOG.read_text().splitlines() if READ_LOG.exists() else []
    rows = unread_history(source, read_anchors(lines, args.since, item['name']))
    import lead_queue
    for label, missing in rows:
        print(f'Item history: {label} has {len(missing)} earlier entries not read this session; read them '
              f'(tools/notebook-excerpt.py ANCHOR --text) before planning, the latest first (with at most '
              f'{lead_queue.READ_ALL_LIMIT} in all the entry links and quotes each): '
              + ', '.join('#' + a for a in missing))
    if rows:
        print(f'Item history: compared {len(lines)} read-log lines.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
