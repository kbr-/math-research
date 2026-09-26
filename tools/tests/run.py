#!/usr/bin/env python3
"""Run the framework test suite: every test in this directory's test_*.py modules, in parallel.

Worker processes take tests one at a time from a shared queue, so the suite's wall time is set by the
total work divided among the workers rather than by the sum of all tests. Workers default to the CPUs
this process may use. Each failure's traceback is printed; the exit status is nonzero if any test
fails or errors, or if the run takes longer than the limit (10 s, AGENTS.md), in which case the
slowest tests are listed.

Usage: python3 tools/tests/run.py [-j WORKERS] [--limit SECONDS] [MODULE ...]
"""
import argparse
import io
import multiprocessing
import os
from pathlib import Path
import sys
import time
import unittest

HERE = Path(__file__).resolve().parent
LIMIT_S = 10.0


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
    return test_id, result.testsRun, result.wasSuccessful(), stream.getvalue(), time.monotonic() - start


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
    with multiprocessing.get_context('fork').Pool(max(1, args.j)) as pool:
        results += pool.imap_unordered(run_one, [t.id() for t in found if t not in broken])
    elapsed = time.monotonic() - start
    failed = [r for r in results if not r[2]]
    for test_id, _, _, output, _ in sorted(failed):
        print(f'===== {test_id} =====\n{output}')
    slow = elapsed > args.limit
    if slow:
        print(f'Over the {args.limit:g} s limit (AGENTS.md). Slowest tests:')
        for test_id, _, _, _, seconds in sorted(results, key=lambda r: -r[4])[:10]:
            print(f'  {seconds:6.2f} s  {test_id}')
    print(f'Ran {sum(r[1] for r in results)} tests in {elapsed:.1f}s: '
          + (f'FAILED ({len(failed)})' if failed else 'OK') + (', TOO SLOW' if slow else ''))
    return 1 if failed or slow else 0


if __name__ == '__main__':
    sys.exit(main())
