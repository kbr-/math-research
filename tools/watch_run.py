#!/usr/bin/env python3
"""Watch a session's running compute.sh jobs, for Claude Code's Monitor tool (COMPUTATION_RULES.md, long runs).

Prints one line per event and exits when every watched run has ended:
- when a run passes the decision point (default 300 s): its elapsed time and last output line, with the
  choice to make (user, 3 October 2026: a run past 5 minutes is a decision point, not a wait);
- when a run ends: its exit status.
Usage: watch_run.py [SESSION] [--at SECONDS] [--poll SECONDS]
Without SESSION it watches every timing journal in research/logs/ with an unfinished run."""
import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOGS = ROOT / 'research/logs'


def journals(session):
    if session:
        return [LOGS / f'{session}.jsonl']
    return sorted(LOGS.glob('*.jsonl'))


def unfinished(paths):
    """{run id: run_start event} for runs without run_end, and {run id: run_end event} for ended ones."""
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


def watch(session=None, at=300.0, poll=2.0, clock=time.time, sleep=time.sleep, out=sys.stdout):
    paths = journals(session)
    running, _ = unfinished(paths)
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
            running.setdefault(rid, event)
        if running:
            sleep(poll)
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('session', nargs='?')
    parser.add_argument('--at', type=float, default=300.0)
    parser.add_argument('--poll', type=float, default=2.0)
    args = parser.parse_args(argv)
    return watch(args.session, args.at, args.poll)


if __name__ == '__main__':
    sys.exit(main())
