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
slowest tests are listed, with the CPU time the run used itself and what was certainly other work on the
machine meanwhile. An overrun on a busy machine by a run whose own CPU time is as when it runs alone is called
that, "TOO SLOW (machine busy)", and still fails unless --excuse-busy is given. Skipped tests are listed with
their reasons.

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
    parser.add_argument('--busy-share', type=float, default=BUSY_SHARE,
                        help='share of the processors busy elsewhere from which an overrun is the machine\'s')
    parser.add_argument('--own-cpu-limit', type=float, default=OWN_CPU_LIMIT_S,
                        help='CPU seconds of the run itself above which an overrun is its own whatever else ran')
    parser.add_argument('--excuse-busy', action='store_true',
                        help='do not fail a run whose overrun is a busy machine\'s (default: it fails, and says so)')
    parser.add_argument('--cpu', action='store_true',
                        help='always print the CPU used by the run and elsewhere on the machine')
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


SLICE = 'mathcompute.slice'


def group_usage(directory):
    """CPU seconds used so far in one control group; None if unreadable."""
    try:
        lines = (directory / 'cpu.stat').read_text().splitlines()
        return int(next(line.split()[1] for line in lines if line.startswith('usage_usec'))) / 1e6
    except (OSError, ValueError, IndexError, StopIteration):
        return None


def own_seconds(group=Path('/proc/self/cgroup'), groups=Path('/sys/fs/cgroup')):
    """The CPU time used in this process's own control group: under the launcher that is this run's job alone,
    its workers and browsers with it, and not the other jobs of the computation slice.  None if unreadable."""
    try:
        return group_usage(groups / group.read_text().strip().split('::', 1)[1].lstrip('/'))
    except (OSError, IndexError):
        return None


def other_jobs(group=Path('/proc/self/cgroup'), groups=Path('/sys/fs/cgroup')):
    """CPU seconds used so far by each other job now in the computation slice, by its group's name; {} outside
    the slice or where it cannot be read.  Taken before and after a run, the growth of the jobs present at both
    is work that was certainly not this run's: the launcher services the run's own tests start are born during
    the run and are left out, and so is any other session's job that started or ended meanwhile."""
    try:
        parts = group.read_text().strip().split('::', 1)[1].split('/')
        at = parts.index(SLICE)
        mine = parts[at + 1] if len(parts) > at + 1 else None
        found = {}
        for child in (groups / '/'.join(parts[:at + 1]).lstrip('/')).iterdir():
            used = group_usage(child) if child.is_dir() and child.name != mine else None
            if used is not None:
                found[child.name] = used
        return found
    except (OSError, ValueError, IndexError):
        return {}


def jobs_growth(before, after):
    return sum(max(0.0, after[name] - before[name]) for name in before if name in after)


# Measured on 11 October 2026 on the project machine, 928 to 930 tests: alone, 8.2 and 8.3 s with 93 and 94 s
# of CPU in the run's own group; beside a job loading 14 CPUs, 13.6 and 14.8 s with 90 s of its own.  The suite's
# own CPU time did not grow under the load while its wall time grew by 64 to 80%, so the two readings tell a
# slower suite from a busier machine.  Beside a job loading 4 CPUs it took 10.4 s with 97 s of its own and 31% of
# the processors busy with other work, the one measurement behind the quarter below.
BUSY_SHARE = 0.25
OWN_CPU_LIMIT_S = 125.0
BUSY_CAP = 2.0


def elsewhere(machine, shared, jobs, own, elapsed, cores):
    """(share of the machine's processors kept busy during the run by work that was certainly not the run's,
    the line saying so, the run's own CPU seconds); (None, None, None) where a reading is missing.  `machine`,
    `shared` and `own` are (before, after) readings of the whole machine, of cpu_seconds' group and of the
    run's own group; `jobs` is jobs_growth of the other jobs present throughout."""
    if None in machine + shared + own or elapsed <= 0:
        return None, None, None
    mine = own[1] - own[0]
    programs = max(0.0, (machine[1] - machine[0]) - (shared[1] - shared[0]))   # outside the slice, or the group
    share = (programs + jobs) / (cores * elapsed)
    return share, (f'CPU during the run: {mine:.0f} s in its own control group; elsewhere {jobs:.0f} s in other jobs of '
                   f'the computation slice that ran throughout and {programs:.0f} s in other programs, {share:.0%} of '
                   f'the {cores} processors (jobs that started or ended meanwhile are not counted).'), mine


def verdict(elapsed, limit, share, own, busy_share=BUSY_SHARE, own_limit=OWN_CPU_LIMIT_S, cap=BUSY_CAP):
    """'ok' within the limit; 'busy' for an overrun of at most `cap` times the limit while other work held
    `busy_share` of the processors and the run's own CPU time stayed within `own_limit`; else 'slow'."""
    if elapsed <= limit:
        return 'ok'
    if share is not None and share >= busy_share and own <= own_limit and elapsed <= cap * limit:
        return 'busy'
    return 'slow'


def measured_group(group=Path('/proc/self/cgroup')):
    """What cpu_seconds counts as the run's own: inside the computation slice it is the whole slice, which
    every session's jobs share, so that figure cannot tell this run from another session's computation."""
    try:
        shared = 'mathcompute.slice' in group.read_text().strip().split('::', 1)[1].split('/')
    except (OSError, IndexError):
        shared = False
    return ('the shared computation slice (this run and any other session\'s jobs in it)' if shared
            else 'the run\'s own control group')


def outside_load(before, after, elapsed, cores, group=Path('/proc/self/cgroup')):
    """The line a slow run prints about what else the machine did meanwhile, or None where it was not read."""
    if None in before + after:
        return None
    machine, own = after[0] - before[0], after[1] - before[1]
    return (f'CPU during the run: {own:.0f} s in {measured_group(group)}, {max(0.0, machine - own):.0f} s by '
            f'other programs; the machine\'s {cores} processors were busy for {machine:.0f} s of {elapsed * cores:.0f}.')


def timed_run(args, found, broken):
    used = cpu_seconds()
    mine, jobs = own_seconds(), other_jobs()
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
    after = cpu_seconds()
    share, line, own = elsewhere((used[0], after[0]), (used[1], after[1]), jobs_growth(jobs, other_jobs()),
                                 (mine, own_seconds()), elapsed, os.cpu_count())
    outcome = verdict(elapsed, args.limit, share, own, args.busy_share, args.own_cpu_limit)
    slow = outcome != 'ok'
    if slow:
        print(f'Over the {args.limit:g} s limit (AGENTS.md). Slowest tests:')
        for test_id, _, _, _, seconds, _ in sorted(results, key=lambda r: -r[4])[:10]:
            print(f'  {seconds:6.2f} s  {test_id}')
        load = outside_load(used, after, elapsed, os.cpu_count())
        if load:
            print(load)
    if line and (slow or args.cpu):
        print(line)
    if outcome == 'busy':
        # Other work held the processors and the suite's own CPU time is as when it runs alone.
        print('Busy machine: the overrun is not shown to be the suite\'s; time it again alone.')
        slow = not args.excuse_busy
    skipped = sorted(skip for r in results for skip in r[5])
    for test_id, reason in skipped:
        print(f'Skipped {test_id}: {reason}')
    print(f'Ran {sum(r[1] for r in results)} tests in {elapsed:.1f}s: '
          + (f'FAILED ({len(failed)})' if failed else 'OK')
          + (', TOO SLOW' + (' (machine busy)' if outcome == 'busy' else '') if slow else '')
          + (f', {len(skipped)} skipped' if skipped else ''))
    return 1 if failed or slow else 0


if __name__ == '__main__':
    sys.exit(main())
