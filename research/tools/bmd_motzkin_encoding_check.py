#!/usr/bin/env python3
"""Check the exact ternary pair/path encoding, not generic normality.

Exhaust every step word of lengths 0..6 and all nine (s,delta) in F3.
Compare weighted excursions with the quadratic recurrence and with the
original square-root coefficients through degree eight. Length three
already tests the essential cancellation; six also tests the next triple.
This is a bounded falsifying control on an all-length proof, not evidence
for any new dimension. Pure Python is confined to 1093 short step words.
"""
import argparse
import itertools
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    histograms = []
    words = 0
    for length in range(7):
        counts = {}
        for steps in itertools.product((-1, 0, 1), repeat=length):
            words += 1
            height = 0
            for step in steps:
                height += step
                if height < 0:
                    break
            else:
                if height == 0:
                    key = (steps.count(0), steps.count(-1))
                    counts[key] = counts.get(key, 0) + 1
        histograms.append(counts)
    rows = []
    for s, delta in itertools.product(range(3), repeat=2):
        v = (s * s - delta) % 3
        recurrence = [1]
        for length in range(1, 7):
            convolution = sum(
                recurrence[i] * recurrence[length - 2 - i]
                for i in range(length - 1)
            )
            recurrence.append((s * recurrence[-1] + delta * convolution) % 3)
        paths = [
            sum(count * s**h * delta**d for (h, d), count in hist.items()) % 3
            for hist in histograms
        ]
        assert paths == recurrence, (s, delta, paths, recurrence)
        root = [1]
        for degree in range(1, 9):
            target = s if degree == 1 else v if degree == 2 else 0
            convolution = sum(root[i] * root[degree - i] for i in range(1, degree))
            root.append((2 * (target - convolution)) % 3)
        expected = [1, (-s) % 3] + [(delta * q) % 3 for q in paths]
        assert root == expected, (s, delta, root, expected)
        rows.append({"s": s, "delta": delta, "v": v, "q": paths, "root": root})
    assert histograms[3] == {(3, 0): 1, (1, 1): 3}
    report = {
        "claim": "lem:cube-motzkin-pair-transfer",
        "scope": "All F3 parameter pairs, path lengths 0..6; not a normality test",
        "step_words_checked": words,
        "parameter_pairs_checked": len(rows),
        "length_three_histogram": [
            {"horizontal": h, "down": d, "multiplicity": count}
            for (h, d), count in sorted(histograms[3].items())
        ],
        "rows": rows,
        "passed": True,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"passed": True, "step_words": words, "parameter_pairs": len(rows)}))


if __name__ == "__main__":
    main()
