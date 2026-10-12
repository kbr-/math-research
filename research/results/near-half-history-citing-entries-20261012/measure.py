"""Measurements of the queue tool's listing of citing entries (tools/lead_queue.py: citing_entries).

No statement tested: timings and counts of a framework tool's output on recorded data, for its entry.

Usage: measure.py NOTEBOOK REGISTRY [ITEM]
With ITEM, the nearest claims by text and the two lists of citing entries for that item; without, the counts over
every top-level queued item of NOTEBOOK.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, 'tools')
import lead_queue as lq                                               # noqa: E402


def main(notebook, registry, item=None):
    body = Path(notebook).read_text()
    start = time.time()
    claims, edges = lq.registered(Path(registry))
    print(f'registry: {len(claims)} claims, {len(edges)} edges, read in {time.time() - start:.2f} s; '
          f'notebook {len(body) / 1e6:.1f} MB, {len(lq.record_articles(body))} articles')
    start = time.time()
    if item:
        print('nearest by text:', lq.claims_elsewhere(body, claims, item))
        rows = lq.citing_entries(body, edges, item)
        print('citing a claim of the queuing entry:')
        print('\n'.join(lq.citing_lines(rows, True)) or '  none')
        print('citing a claim of its own entries:')
        print('\n'.join(lq.citing_lines(rows, False)) or '  none')
    else:
        tops = lq.parse_tree(body)[1]
        queuing = own = with_queuing = with_any = longest = 0
        for node in tops:
            rows = lq.citing_entries(body, edges, lq.qualified(node))
            first, second = len(lq.citing_lines(rows, True)), len(lq.citing_lines(rows, False))
            queuing += first
            own += second
            with_queuing += bool(first)
            with_any += bool(rows)
            longest = max(longest, first)
            print(f'{node.ident}: {first} entries cite the queuing entry, {second} its own entries')
        print(f'{len(tops)} items; {with_any} with a line, {with_queuing} with a line for the queuing entry; '
              f'{queuing} lines for queuing entries, the longest list {longest}; {own} lines for own entries')
    print(f'listing time {time.time() - start:.2f} s')


if __name__ == '__main__':
    main(*sys.argv[1:])
