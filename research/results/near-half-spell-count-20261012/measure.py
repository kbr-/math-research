#!/usr/bin/env python3
"""How a notebook's research entries group into spells, as the queue tool counts them (tools/lead_queue.py:
group_of, spell_entries), and what a count over a window of recent entries would give instead.

No statement tested: a measurement of a framework tool on the notebook's own record, for the build item
spell-by-top-level-item.

Usage: measure.py NOTEBOOK [WINDOW]
Prints: the number of research entries that develop a queue item; how many of them the tool groups under an
item other than the one they name (a sub-idea counted for its parent); how many name an item that is neither
queued nor grouped under a queued item; for each group the number of entries in all and the longest run of
consecutive entries; and, for WINDOW (default 8), the largest number of entries of one group among any WINDOW
consecutive item entries.
"""
import collections
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'tools'))
import lead_queue as lq  # noqa: E402


def main():
    start = time.time()
    body = Path(sys.argv[1]).read_text()
    window = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    found = lq.parse_tree(body)
    nodes = found[1] if found else []
    top = {node.item for node in nodes}
    articles = lq.record_articles(body)
    groups, own, regrouped, loose = [], 0, 0, 0
    for position, (tag, text) in enumerate(articles):
        if not lq.counted(tag, text):
            continue
        try:
            work = lq.developed_by(tag, text)
        except ValueError:
            continue
        if not work:
            continue
        group = lq.group_of(body, nodes, work[0], position)
        groups.append(group)
        own += group == work[0]
        regrouped += group != work[0]
        loose += group not in top
    print(f'{len(articles)} articles; {len(groups)} entries develop a queue item; {own} counted under the item they '
          f'name, {regrouped} under another (a parent); {loose} under an item no longer queued at the top level')
    total = collections.Counter(groups)
    longest, run, last = collections.Counter(), 0, None
    for group in groups:
        run = run + 1 if group == last else 1
        last = group
        longest[group] = max(longest[group], run)
    most = collections.Counter()
    for i in range(len(groups)):
        for group, count in collections.Counter(groups[max(0, i - window + 1):i + 1]).items():
            most[group] = max(most[group], count)
    print(f'groups: {len(total)}; with more than {lq.SPELL} entries in all: '
          f'{sum(1 for g in total if total[g] > lq.SPELL)}; with a run of more than {lq.SPELL} consecutive entries: '
          f'{sum(1 for g in total if longest[g] > lq.SPELL)}; with more than {lq.SPELL} among some {window} '
          f'consecutive item entries: {sum(1 for g in total if most[g] > lq.SPELL)}')
    for group, count in total.most_common(8):
        print(f'  {group[0]}:{group[1]}: {count} entries, longest run {longest[group]}, most in {window}: {most[group]}')
    print(f'time {time.time() - start:.2f} s')
    if hasattr(lq, 'window_count'):     # the option built on 12 October 2026: the tool's own count, on the record's end
        start = time.time()
        counts = [(lq.window_count(body, node.item, nodes, window), node.ident) for node in nodes]
        over = [(count, ident) for count, ident in counts if count >= lq.SPELL]
        print(f'window_count over {len(nodes)} queued top-level items, window {window}: {len(over)} at or above '
              f'{lq.SPELL} now ({", ".join(f"{i} {c}" for c, i in sorted(over, reverse=True)) or "none"}); '
              f'time {time.time() - start:.2f} s')


if __name__ == '__main__':
    main()
