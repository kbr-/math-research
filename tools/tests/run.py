#!/usr/bin/env python3
"""Run the framework test suite: every test in this directory's test_*.py modules, in parallel.

Worker processes take tests one at a time from a shared queue, so the suite's wall time is set by the
total work divided among the workers rather than by the sum of all tests. Workers default to the CPUs
this process may use. Each failure's traceback is printed; the exit status is nonzero if any test
fails or errors.

Usage: python3 tools/tests/run.py [-j WORKERS] [MODULE ...]
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


def tests(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from tests(item)
        else:
            yield item


def run(test, test_id):
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=0).run(test)
    return test_id, result.testsRun, result.wasSuccessful(), stream.getvalue()


def run_one(test_id):
    return run(unittest.defaultTestLoader.loadTestsFromName(test_id), test_id)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-j', type=int, default=len(os.sched_getaffinity(0)), help='worker processes')
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
    failed = [r for r in results if not r[2]]
    for test_id, _, _, output in sorted(failed):
        print(f'===== {test_id} =====\n{output}')
    print(f'Ran {sum(r[1] for r in results)} tests in {time.monotonic() - start:.1f}s: '
          + (f'FAILED ({len(failed)})' if failed else 'OK'))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
