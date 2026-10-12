"""Measurements of the finisher's check that an entry links the earlier entries on its item
and quotes them (tools/lead_queue.py: unread_item_entries, item_entries, descendant_entries).

No statement tested: counts and timings of a framework tool on recorded data, for its entry.

Usage: measure.py NOTEBOOK [ENTRY_ANCHOR]
Without ENTRY_ANCHOR: for every top-level queued item and sub-idea, the number of earlier entries the check would
ask a new entry on it to link (its own entries and those on sub-ideas they listed), and how many items fall at or
under the limit.  With ENTRY_ANCHOR: the record cut after that entry, and what the check reports for it.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, 'tools')
import lead_queue as lq                                               # noqa: E402


def wanted_for(articles, item):
    return lq.item_entries(articles, item)


def main(notebook, entry=None):
    body = Path(notebook).read_text()
    articles = lq.record_articles(body)
    start = time.time()
    if entry:
        position = next(i for i, (tag, _) in enumerate(articles) if f'id="{entry}"' in tag)
        cut = articles[:position + 1]
        work = lq.developed_by(*cut[-1])
        own, below = wanted_for(cut[:-1], work[0])
        print(f'entry {entry} develops {work[0][0]}:{work[0][1]}')
        print('earlier entries on the item:', ', '.join(own) or 'none')
        print('entries on sub-ideas they listed:', ', '.join(below) or 'none')
        lacking = lq.unread_item_entries(cut, work[0])
        print('lacking in the entry:', ', '.join(f'{anchor} ({what})' for anchor, what in lacking) or 'none')
    else:
        nodes = lq.parse_tree(body)[1]
        items = [node for top in nodes for node in [top] + top.children]
        counts = []
        for node in items:
            own, below = wanted_for(articles, node.item)
            counts.append(len(own) + len(below))
            if below:
                print(f'{node.ident}: {len(own)} own, {len(below)} on sub-ideas they listed')
        within = sum(1 for count in counts if 1 <= count <= lq.READ_ALL_LIMIT)
        print(f'{len(items)} queued items and sub-ideas; {counts.count(0)} with no earlier entry, {within} with 1 to '
              f'{lq.READ_ALL_LIMIT}, {len(counts) - within - counts.count(0)} with more; the largest {max(counts)}')
    print(f'{len(articles)} articles; time {time.time() - start:.2f} s')


if __name__ == '__main__':
    main(*sys.argv[1:])
