#!/usr/bin/env python3
"""Watch a session's running compute.sh jobs, for native background notifications (COMPUTATION_RULES.md, long runs).

Prints one line per event and exits when every watched run has ended:
- when a run passes the decision point (default 300 s): its elapsed time and last output line, with the
  choice to make (user, 3 October 2026: a run past 5 minutes is a decision point, not a wait);
- when a run ends: its exit status.
Usage: watch_run.py [SESSION] [--at SECONDS] [--poll SECONDS]
Without SESSION it watches every timing journal in research/logs/ with an unfinished run."""
import argparse
import json
import os
import re
import fcntl
import subprocess
import uuid
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOGS = ROOT / 'research/logs'


def journals(session):
    if session:
        return [LOGS / f'{session}.jsonl']
    return sorted(LOGS.glob('*.jsonl'))


def records(paths):
    """Return run_start and run_end events, each indexed by run ID."""
    started, ended = {}, {}
    for path in paths:
        if not path.exists():
            continue
        for line in path.read_text().splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get('event') == 'run_start':
                started[event['id']] = event
            elif event.get('event') == 'run_end':
                ended[event['id']] = event
    return started, ended


def unfinished(paths):
    started, ended = records(paths)
    return {k: v for k, v in started.items() if k not in ended}, ended


def last_line(event):
    path = ROOT / 'research' / event.get('output', '')
    try:
        with path.open('rb') as handle:
            handle.seek(max(0, handle.seek(0, 2) - 4096))
            lines = [x for x in handle.read().decode('utf-8', 'replace').splitlines() if x.strip()]
        return lines[-1][:200] if lines else '(no output yet)'
    except OSError:
        return '(no output file)'


def watch(session=None, at=300.0, poll=2.0, clock=time.time, sleep=time.sleep, out=sys.stdout, grace=15.0, expected=None):
    paths = journals(session)
    running, _ = unfinished(paths)
    if expected is not None:
        running = {expected: records(paths)[0][expected]}
    if not running:
        print(f'No unfinished compute.sh run in {session or "research/logs"}.', file=out, flush=True)
        return 0
    announced = set()
    while running:
        now = clock()
        current, ended = unfinished(paths)
        for rid, event in list(running.items()):
            if rid in ended:
                end = ended[rid]
                state = 'timed out' if end.get('timed_out') else 'interrupted' if end.get('interrupted') else \
                    f'exit {end.get("returncode")}'
                print(f'Run {rid} ended after {end.get("unix_s", now) - event["unix_s"]:.0f} s: {state}. '
                      f'Log: research/{event.get("output")}', file=out, flush=True)
                del running[rid]
            elif rid not in announced and now - event['unix_s'] >= at:
                announced.add(rid)
                print(f'Run {rid} still running after {now - event["unix_s"]:.0f} s (decision point). Last output: '
                      f'{last_line(event)}. Find what it is doing; keep it only if its measured progress justifies '
                      f'the rest, otherwise stop it with systemctl --user stop {event.get("systemd_unit")} and '
                      f'optimize (COMPUTATION_RULES.md, long runs).', file=out, flush=True)
        for rid, event in current.items():   # runs started after the watch began
            if expected is None or rid == expected:
                running.setdefault(rid, event)
        if not running:   # a chain (a && b) starts its next run a moment later: wait a grace period for it
            quiet_since = clock()
            while not running and clock() - quiet_since < grace:
                sleep(poll)
                running.update(unfinished(paths)[0])
        if running:
            sleep(poll)
    return 0


def native_path(root, run):
    if not re.fullmatch(r'[0-9a-f]{32}', run or ''):
        raise ValueError('Use the run ID returned by the armed watcher')
    return Path(root)/'research/logs/codex-watchers'/(run+'.json')


def native_ready(root, session, run, owner):
    try:
        path = native_path(root, run)
        state = json.loads(path.read_text())
        if state['owner'] != owner or state['session'] != session or path.with_suffix('.cancel').exists():
            return False
        with path.with_suffix('.lock').open('rb') as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return True
        return False
    except (OSError, ValueError, KeyError):
        return False


def arm(session, at=300.0, poll=2.0, wait=30.0):
    from codex_state import atomic_json
    owner = os.environ.get('CODEX_THREAD_ID')
    if not owner or not session or not re.fullmatch(r'[A-Za-z0-9_.-]+', session) or session in ('.','..'):
        raise ValueError('Native arming needs CODEX_THREAD_ID and a named timing session')
    if not 0 < at <= 300:
        raise ValueError('The decision point must be positive and no later than 300 seconds')
    run = uuid.uuid4().hex
    path = native_path(ROOT, run)
    state = {'owner': owner, 'session': session}
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.with_suffix('.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        atomic_json(path, state)
        print('WATCH_READY '+json.dumps({'run_id': run}), flush=True)
        deadline = time.monotonic()+wait
        while run not in records(journals(session))[0]:
            if path.with_suffix('.cancel').exists():
                print('Watcher cancelled before run start.', flush=True)
                return 1
            if time.monotonic() >= deadline:
                print('No matching run started; watcher disarmed.', flush=True)
                return 1
            time.sleep(min(poll, .1))
        return watch(session, at, poll, out=sys.stdout, grace=0, expected=run)


def cancel(run):
    path = native_path(ROOT, run)
    if not path.exists():
        return 0
    state = json.loads(path.read_text())
    if state['owner'] != os.environ.get('CODEX_THREAD_ID'):
        raise ValueError('This watcher belongs to another thread')
    path.with_suffix('.cancel').write_text('Cancellation requested\n')
    started, ended = records(journals(state['session']))
    if run in started and run not in ended:
        unit = started[run]['systemd_unit']
        if not re.fullmatch(r'mathcompute-job-[0-9a-f]+\.service', unit):
            raise ValueError('Invalid protected service identity')
        subprocess.run(['systemctl','--user','stop',unit], check=True, timeout=10)
    print('Watcher cancellation requested; any recorded live protected service was stopped.', flush=True)
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('session', nargs='?')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--arm', action='store_true', help='Arm a native harness watcher before releasing its run')
    mode.add_argument('--cancel', metavar='RUN_ID', help="Stop this thread's watcher and protected service")
    parser.add_argument('--at', type=float, default=300.0)
    parser.add_argument('--poll', type=float, default=2.0)
    parser.add_argument('--grace', type=float, default=15.0, help='seconds to wait for the next run of a chain')
    args = parser.parse_args(argv)
    try:
        if args.cancel:
            return cancel(args.cancel)
        if args.arm:
            return arm(args.session, args.at, args.poll)
        return watch(args.session, args.at, args.poll, grace=args.grace)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print('Watcher: '+str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
