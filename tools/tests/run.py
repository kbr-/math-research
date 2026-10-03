#!/usr/bin/env python3
"""Run the framework test suite: every test in this directory's test_*.py modules, in parallel.

Worker processes take tests one at a time from a shared queue, so the suite's wall time is set by the
total work divided among the workers rather than by the sum of all tests. The queue is ordered longest
first by the durations of the previous run, kept in the git-ignored DURATIONS beside this file, with tests
it has no time for first of all: in discovery order the browser tests, which sort last and take 6 s,
started 4.5 s into the run and set its end (3 October 2026: 10.9 s, and 7.5 s longest first). Workers default to the CPUs
this process may use. Each failure's traceback is printed; the exit status is nonzero if any test
fails or errors, or if the run takes longer than the limit (10 s, AGENTS.md), in which case the
slowest tests are listed. Skipped tests are listed with their reasons.

Usage: python3 tools/tests/run.py [-j WORKERS] [--limit SECONDS] [MODULE ...]
"""
import argparse
import io
import json
import multiprocessing
import os
from pathlib import Path
import sys
import time
import unittest

HERE = Path(__file__).resolve().parent
LIMIT_S = 10.0
DURATIONS = HERE / '.durations.json'


def tests(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from tests(item)
        else:
            yield item


def run(test, test_id):
    stream = io.StringIO()
    start = time.monotonic()
    result = unittest.TextTestRunner(stream=stream, verbosity=0).run(test)
    skipped = [(case.id(), reason) for case, reason in result.skipped]
    return test_id, result.testsRun, result.wasSuccessful(), stream.getvalue(), time.monotonic() - start, skipped


def run_one(test_id):
    return run(unittest.defaultTestLoader.loadTestsFromName(test_id), test_id)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-j', type=int, default=len(os.sched_getaffinity(0)), help='worker processes')
    parser.add_argument('--limit', type=float, default=LIMIT_S, help='wall-time limit in seconds')
    parser.add_argument('modules', nargs='*', help='module names (default: all test_*.py here)')
    args = parser.parse_args()
    os.chdir(HERE)
    sys.path.insert(0, str(HERE))
    loader = unittest.defaultTestLoader
    suite = loader.loadTestsFromNames(args.modules) if args.modules else loader.discover('.')
    found = list(tests(suite))
    # A module that fails to import is discovered as a placeholder test carrying its error; it can't be
    # reloaded by name in a worker, so it runs here and reports the real error.
    broken = [t for t in found if t.id().startswith('unittest.loader._FailedTest.')]
    start = time.monotonic()
    results = [run(t, t.id()) for t in broken]
    try:
        known = json.loads(DURATIONS.read_text())
    except (OSError, ValueError):
        known = {}
    queue = sorted((t.id() for t in found if t not in broken), key=lambda i: -known.get(i, float('inf')))
    with multiprocessing.get_context('fork').Pool(max(1, args.j)) as pool:
        results += pool.imap_unordered(run_one, queue)
    elapsed = time.monotonic() - start
    try:
        DURATIONS.write_text(json.dumps({**known, **{r[0]: round(r[4], 3) for r in results}}, sort_keys=True))
    except OSError:
        pass
    failed = [r for r in results if not r[2]]
    for test_id, _, _, output, _, _ in sorted(failed):
        print(f'===== {test_id} =====\n{output}')
    slow = elapsed > args.limit
    if slow:
        print(f'Over the {args.limit:g} s limit (AGENTS.md). Slowest tests:')
        for test_id, _, _, _, seconds, _ in sorted(results, key=lambda r: -r[4])[:10]:
            print(f'  {seconds:6.2f} s  {test_id}')
    skipped = sorted(skip for r in results for skip in r[5])
    for test_id, reason in skipped:
        print(f'Skipped {test_id}: {reason}')
    print(f'Ran {sum(r[1] for r in results)} tests in {elapsed:.1f}s: '
          + (f'FAILED ({len(failed)})' if failed else 'OK') + (', TOO SLOW' if slow else '')
          + (f', {len(skipped)} skipped' if skipped else ''))
    return 1 if failed or slow else 0


if __name__ == '__main__':
    sys.exit(main())
