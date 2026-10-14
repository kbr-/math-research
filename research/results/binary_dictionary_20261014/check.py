"""Exhaustive rule control on all nonempty 2-uniform dictionaries on four bits.

Prediction: deletion families with forbidden pairwise intersection at most r-2
have monotone paths and largest basis-free support at most r. The constructive
path is compared with an independent breadth-first search on the actual graph.
Control: two separated retained supports have small basis-free support but no
path; deleting the path requirement must therefore change an asserted outcome.
Refuted by: a failed path, excessive basis-free support, or graph disagreement.
Possible because: every dictionary is enumerated without imposing the prediction.
This is a bounded combinatorial control, not a hard-system lower-bound test.
"""
import argparse
from collections import deque
from itertools import combinations
import json
from pathlib import Path
import time


def graph_path(dictionary, source, target):
    queue = deque([source])
    distance = {source: 0}
    while queue:
        current = queue.popleft()
        if current == target:
            return distance[current]
        for candidate in dictionary:
            if candidate not in distance and len(current - candidate) == 1:
                distance[candidate] = distance[current] + 1
                queue.append(candidate)
    return None


def deletion_path(dictionary, source, target):
    """The theorem's fixed-removal, available-target insertion construction."""
    path = [source]
    current = source
    while current != target:
        removed = min(current - target)
        candidates = [(current - {removed}) | {added}
                      for added in sorted(target - current)]
        available = [candidate for candidate in candidates if candidate in dictionary]
        if not available:
            return None
        current = available[0]
        path.append(current)
    return path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    started = time.monotonic()
    vertices = frozenset(range(4))
    r = 2
    layer = tuple(map(frozenset, combinations(vertices, r)))
    supports = tuple(frozenset(c) for size in range(5)
                     for c in combinations(vertices, size))
    # Refuse expansion: this control answers the four-coordinate rule question.
    assert len(layer) == 6 and len(supports) == 16
    rows = []
    pair_checks = 0
    applicable = 0
    nonempty_deletions = 0
    for mask in range(1, 1 << len(layer)):
        dictionary = frozenset(s for i, s in enumerate(layer) if mask & (1 << i))
        forbidden = frozenset(layer) - dictionary
        sparse = all(len(a & b) <= r - 2 for a, b in combinations(forbidden, 2))
        basis_free = [u for u in supports if not any(s <= u for s in dictionary)]
        q = max(map(len, basis_free))
        monotone = True
        greedy_success = True
        for source in dictionary:
            for target in dictionary:
                minimum = graph_path(dictionary, source, target)
                monotone &= minimum == len(source - target)
                path = deletion_path(dictionary, source, target)
                if sparse:
                    assert path is not None
                    assert len(path) - 1 == len(source - target) == minimum
                    assert all(s in dictionary for s in path)
                    assert all(len(path[i] - target) == len(source - target) - i
                               for i in range(len(path)))
                    pair_checks += 1
                greedy_success &= path is not None
        if sparse:
            assert q <= r
            assert monotone
            applicable += 1
            nonempty_deletions += bool(forbidden)
        rows.append({'mask': mask, 'retained': [sorted(s) for s in sorted(dictionary, key=sorted)],
                     'q': q, 'sparse_deletion': sparse, 'monotone': monotone,
                     'greedy_success': greedy_success})
    separated = frozenset((frozenset((0, 1)), frozenset((2, 3))))
    control = next(row for row in rows
                   if frozenset(map(frozenset, row['retained'])) == separated)
    assert control['q'] == 2 * r - 2 and not control['monotone']
    assert not control['sparse_deletion']
    # This is the positive falsifier of deleting the path hypothesis.
    assert control['q'] <= r and graph_path(separated, *tuple(separated)) is None
    result = {'parameters': {'v': 4, 'r': r, 'dictionaries': len(rows)},
              'applicable_dictionaries': applicable,
              'nonempty_deletion_dictionaries': nonempty_deletions,
              'applicable_ordered_pairs': pair_checks,
              'disconnected_control': control,
              'elapsed_s': time.monotonic() - started, 'rows': rows}
    target = Path(args.out)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('x') as handle:
        json.dump(result, handle, indent=2)
        handle.write('\n')
    print('RESULT ' + json.dumps({key: value for key, value in result.items() if key != 'rows'}))


if __name__ == '__main__':
    main()
