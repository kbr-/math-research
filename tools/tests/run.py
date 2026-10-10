#!/usr/bin/env python3
"""Run the framework test suite: every test in this directory's test_*.py modules, in parallel.

Worker processes take tests one at a time from a shared queue, so the suite's wall time is set by the
total work divided among the workers rather than by the sum of all tests. With no duration cache,
test classes can supply expected_seconds hints so known costly groups start first. The queue is ordered longest
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
import shutil
from pathlib import Path
import sys
import tempfile
import time
import unittest

HERE = Path(__file__).resolve().parent
LIMIT_S = 10.0
DURATIONS = HERE / '.durations.json'
MEMORY = Path('/dev/shm')


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
    scratch = memory_scratch(MEMORY)
    try:
        return timed_run(args, found, broken)
    finally:
        if scratch:
            shutil.rmtree(scratch, ignore_errors=True)


def memory_scratch(base):
    """Point the tests' temporary files at a new directory in memory and return it, or None where there
    is no memory filesystem to write to or TMPDIR already names a place. The tests wrote some 250 MB to the
    disk in each run, and about one run in six then stalled on its I/O for 3 to 4 s and took 15 to 18 s
    (10 October 2026); in memory a run writes 5 MB and none of that. The caller removes the directory,
    with whatever tests left in it."""
    if os.environ.get('TMPDIR') or not (base.is_dir() and os.access(base, os.W_OK | os.X_OK)):
        return None
    scratch = tempfile.mkdtemp(prefix='framework-tests-', dir=base)
    os.environ['TMPDIR'] = scratch
    tempfile.tempdir = None   # read again from the environment, here and in the workers forked later
    return scratch


def cpu_seconds(stat=Path('/proc/stat'), group=Path('/proc/self/cgroup'), groups=Path('/sys/fs/cgroup')):
    """(the CPU time every processor of the machine has spent busy, the CPU time used in the computation
    slice this process runs in, or in its own control group outside one), each in seconds since some start;
    None for one that cannot be read. Their growth over a run tells its own work from other programs'."""
    try:
        fields = [int(field) for field in stat.read_text().split('\n', 1)[0].split()[1:]]
        machine = (sum(fields[:8]) - fields[3] - fields[4]) / os.sysconf('SC_CLK_TCK')   # all but idle and iowait
    except (OSError, ValueError, IndexError):
        machine = None
    try:
        parts = group.read_text().strip().split('::', 1)[1].split('/')
        if 'mathcompute.slice' in parts:   # the tests' launcher calls start services beside the run's own
            parts = parts[:parts.index('mathcompute.slice') + 1]
        lines = (groups / '/'.join(parts).lstrip('/') / 'cpu.stat').read_text().splitlines()
        own = int(next(line.split()[1] for line in lines if line.startswith('usage_usec'))) / 1e6
    except (OSError, ValueError, IndexError, StopIteration):
        own = None
    return machine, own


def outside_load(before, after, elapsed, cores):
    """The line a slow run prints about what else the machine did meanwhile, or None where it was not read."""
    if None in before + after:
        return None
    machine, own = after[0] - before[0], after[1] - before[1]
    return (f'CPU during the run: {own:.0f} s in the run\'s own control group, {max(0.0, machine - own):.0f} s by '
            f'other programs; the machine\'s {cores} processors were busy for {machine:.0f} s of {elapsed * cores:.0f}.')


def timed_run(args, found, broken):
    used = cpu_seconds()
    start = time.monotonic()
    results = [run(t, t.id()) for t in broken]
    try:
        known = json.loads(DURATIONS.read_text())
    except (OSError, ValueError):
        known = {}
    queued = [t for t in found if t not in broken]
    queue = [t.id() for t in sorted(queued, key=lambda t: -known.get(
        t.id(), float('inf') if known else getattr(t, 'expected_seconds', 0.0)))]
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
        load = outside_load(used, cpu_seconds(), elapsed, os.cpu_count())
        if load:
            print(load)
    skipped = sorted(skip for r in results for skip in r[5])
    for test_id, reason in skipped:
        print(f'Skipped {test_id}: {reason}')
    print(f'Ran {sum(r[1] for r in results)} tests in {elapsed:.1f}s: '
          + (f'FAILED ({len(failed)})' if failed else 'OK') + (', TOO SLOW' if slow else '')
          + (f', {len(skipped)} skipped' if skipped else ''))
    return 1 if failed or slow else 0


if __name__ == '__main__':
    sys.exit(main())
