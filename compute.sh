#!/usr/bin/env python3
"""Protected computation and observable timing in one executable (Python shebang).

  ./compute.sh python3 calculation.py
  ./compute.sh start turn001
  ./compute.sh phase turn001 reading --note "Read a proof"
  ./compute.sh run turn001 --threads 1 -- python3 calculation.py
  ./compute.sh report turn001 --stop
"""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import html
import json
import math
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parent
LOGS = ROOT / 'research/logs'
SLICE = 'mathcompute.slice'
WATCHDOG = 'mathcompute-watchdog.service'
MAX_MEMORY = MAX_SWAP = 10_000_000_000
MAX_CPUS = set(range(14))
PHASES = ('reading', 'mathematics', 'coding', 'preparation', 'overhead',
          'reasoning_writing', 'external_tool', 'network_tool', 'other')
RUNS = ('computation', 'network_tool', 'external_tool', 'local_processing')


def boot_id():
    return Path('/proc/sys/kernel/random/boot_id').read_text().strip()


def session_path(name):
    if not re.fullmatch(r'[A-Za-z0-9_.-]+', name) or name in ('.', '..'):
        raise ValueError('Use a simple session name: letters, digits, _, -, .')
    LOGS.mkdir(parents=True, exist_ok=True)
    return LOGS / (name + '.jsonl')


@contextmanager
def locked(path):
    with path.with_suffix('.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        yield


def read_events(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def add_event(path, event, **values):
    record = dict(event=event, monotonic_s=time.monotonic(), unix_s=time.time(), **values)
    with path.open('a') as stream:
        stream.write(json.dumps(record, ensure_ascii=False) + '\n')
    return record


def ensure_active(events):
    if any(e['event'] == 'stop' for e in events):
        raise ValueError('Session already stopped; start a new session')
    first = next(e for e in events if e['event'] == 'start')
    if first.get('boot_id', boot_id()) != boot_id():
        raise ValueError('Session predates this boot; start a new session')


def start_session(name):
    path = session_path(name)
    with locked(path):
        if path.exists():
            raise ValueError('Session exists; choose a new name')
        add_event(path, 'start', boot_id=boot_id())
    return path


def check_limits():
    result = subprocess.run(
        ["systemctl", "--user", "show", SLICE, "--property=ControlGroup", "--value"],
        capture_output=True, text=True, check=True,
    )
    group = result.stdout.strip()
    if not group.startswith("/user.slice/") or not group.endswith("/" + SLICE):
        raise RuntimeError("The shared computation slice is not active")
    path = Path("/sys/fs/cgroup" + group)
    memory = int((path / "memory.max").read_text())
    swap = int((path / "memory.swap.max").read_text())
    # Kernel limits are rounded to pages. Permit only rounding of this cap.
    page = os.sysconf("SC_PAGE_SIZE")
    if not 0 < memory <= ((MAX_MEMORY + page - 1) // page) * page:
        raise RuntimeError(f"Unsafe memory limit: {memory}")
    if not 0 <= swap <= ((MAX_SWAP + page - 1) // page) * page:
        raise RuntimeError("Missing swap backstop")
    watchdog = subprocess.run(
        ["systemctl", "--user", "show", WATCHDOG,
         "--property=ActiveState", "--property=SubState"],
        capture_output=True, text=True, check=True,
    ).stdout.splitlines()
    if "ActiveState=active" not in watchdog or "SubState=running" not in watchdog:
        raise RuntimeError("The combined RAM+swap watchdog is not running")
    # Ubuntu's user manager may delegate only memory and pids, not cpu/cpuset.
    # CPUAffinity= is enforced at service launch independently of delegation.
    # Verify that affinity inside the service before executing the workload.
    return path, memory

def summary(events:list[dict],end:float)->dict:
    begin=next(e['monotonic_s'] for e in events if e['event']=='start')
    phases=[(begin,'preparation')]+[(e['monotonic_s'],e['category']) for e in events if e['event']=='phase']
    phases=sorted((max(begin,min(end,t)),c) for t,c in phases)
    segments=[]
    for i,(a,c) in enumerate(phases):
        b=phases[i+1][0] if i+1<len(phases) else end
        if b>a:segments.append((a,b,c,False))
    runs={};failures=[]
    for e in events:
        if e['event']=='run_start':runs[e['id']]=e
        elif e['event']=='run_end' and e['id'] in runs:
            a=runs[e['id']]
            segments.append((a['monotonic_s'],min(e['monotonic_s'],end),a['category'],True))
            if e.get('returncode')!=0:failures.append(e)
    finished={e['id'] for e in events if e['event']=='run_end'}
    for rid,a in runs.items():
        if rid not in finished:segments.append((a['monotonic_s'],end,a['category'],True))
    cuts=sorted({begin,end}|{max(begin,min(end,x)) for a,b,_,_ in segments for x in (a,b)})
    totals={}
    for a,b in zip(cuts,cuts[1:]):
        if b<=a:continue
        mid=(a+b)/2;active=[s for s in segments if s[0]<=mid<s[1]]
        timed=[s for s in active if s[3]]
        if timed:
            cats={s[2] for s in timed};cat=next(iter(cats)) if len(cats)==1 else 'overlapping_tool_categories'
        else:cat=active[-1][2] if active else 'unclassified'
        totals[cat]=totals.get(cat,0.0)+(b-a)
    return {'total_instrumented_s':end-begin,'exclusive_categories_s':totals,'command_runs':len(runs),'failed_or_timed_out_commands':len(failures),
      'unfinished_commands':len(set(runs)-finished),
      'scope':'Phases label observed work windows, not internal cognition or pure latency. Unexpected interruptions may remain mixed with the active phase. Tool windows include service overhead; overlapping intervals count once. Work after the final snapshot is excluded.'}


def timing_html(data, session):
    """Format measured, exclusive intervals without inventing missing categories."""
    total = float(data['total_instrumented_s'])
    categories = {key: float(value) for key, value in data['exclusive_categories_s'].items()}
    if any(not math.isfinite(value) or value < 0 for value in [total, *categories.values()]):
        raise ValueError('Timing values must be finite and nonnegative')
    if not math.isclose(sum(categories.values()), total, rel_tol=1e-9, abs_tol=1e-6):
        raise ValueError('Exclusive timing categories do not sum to the measured total')

    def elapsed(value):
        minutes, remainder = divmod(round(value * 100), 6000)
        seconds, hundredths = divmod(remainder, 100)
        return (f'{minutes} min ' if minutes else '') + f'{seconds}.{hundredths:02d} s'

    labels = [
        ('reading', 'Marked reading and review windows'),
        ('mathematics', 'Mathematical reasoning and proof writing'),
        ('coding', 'Computation design and coding'),
        ('preparation', 'Preparation and checkpoint work'),
        ('overhead', 'Marked overhead and interruptions'),
        ('network_tool', 'Dedicated web and download-attempt windows'),
        ('external_tool', 'Other external-tool windows'),
        ('computation', 'Individually measured computation'),
        ('local_processing', 'Individually measured conversion, checks, and local processing'),
        ('overlapping_tool_categories', 'Overlapping tool categories, counted once'),
        ('reasoning_writing', 'Mixed reasoning and writing (legacy phase)'),
    ]
    rows = []
    used = set()
    for key, label in labels:
        used.add(key)
        if categories.get(key, 0) > 0:
            rows.append((label, categories[key]))
    residual = sum(value for key, value in categories.items() if key not in used)
    if residual > 0:
        rows.append(('Unseparated overhead and other unclassified time', residual))
    result = [f'<div class="timing-report" data-session="{html.escape(session, quote=True)}">',
              '<table class="timing-table">', '<caption>Measured timing</caption>',
              '<thead><tr><th scope="col">Measured category</th><th scope="col">Elapsed</th></tr></thead>',
              '<tbody>', '<tr><th scope="row">Total instrumented interval</th>'
              f'<td class="elapsed"><strong>{elapsed(total)}</strong></td></tr>']
    result += [f'<tr><td>{html.escape(label)}</td><td class="elapsed">{elapsed(value)}</td></tr>'
               for label, value in rows]
    note = 'Through final snapshot; overlapping time counted once.'
    if data['failed_or_timed_out_commands']:
        note += f" Failed/timed-out commands: {int(data['failed_or_timed_out_commands'])}."
    if data['unfinished_commands']:
        note += f" Unfinished commands: {int(data['unfinished_commands'])}."
    result += ['</tbody></table>', f'<p class="timing-note">{note}</p>', '</div>']
    return '\n'.join(result) + '\n'


def show_status():
    group, _ = check_limits()
    ram = int((group / 'memory.current').read_text())
    swap = int((group / 'memory.swap.current').read_text())
    print(f'Cgroup: {group}')
    print('Budget: 10 GB combined RAM + swap; unrestricted split; watchdog active')
    print(f'Workload usage: {ram:,} RAM + {swap:,} swap = {ram+swap:,} bytes')
    print('CPU affinity: 0-13, checked inside every job; watchdog polls every 2 ms')


def execute_inside(command):
    group, _ = check_limits()
    own = next(line[3:] for line in Path('/proc/self/cgroup').read_text().splitlines()
               if line.startswith('0::'))
    expected = str(group).removeprefix('/sys/fs/cgroup')
    cpus = os.sched_getaffinity(0)
    if not own.startswith(expected + '/') or not cpus or not cpus <= MAX_CPUS:
        raise RuntimeError('Refusing to execute: wrong cgroup or CPU affinity')
    os.execvp(command[0], command)


def invocation(command, threads, timeout, unit):
    check_limits()
    executable = shutil.which(command[0])
    if executable is None:
        raise FileNotFoundError(f'Command not found: {command[0]}')
    # abspath preserves virtualenv symlinks; resolve() would bypass the venv.
    command = [os.path.abspath(executable), *command[1:]]
    args = ['systemd-run', '--user', '--quiet', '--wait', '--pipe', '--collect',
            f'--unit={unit}', f'--slice={SLICE}', '--property=OOMPolicy=kill',
            '--property=KillMode=control-group', '--property=CPUAffinity=0-13',
            f'--property=BindsTo={WATCHDOG}', f'--property=After={WATCHDOG}',
            '--property=TimeoutStopSec=1s', '--property=KillSignal=SIGKILL',
            '--property=SendSIGKILL=yes', f'--property=RuntimeMaxSec={timeout}s',
            f'--working-directory={Path.cwd()}']
    for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
                'BLIS_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS',
                'NUMBA_NUM_THREADS'):
        args.append(f'--setenv={key}={threads}')
    args += ['--setenv=OMP_MAX_ACTIVE_LEVELS=1', '--setenv=MKL_DYNAMIC=FALSE']
    for key in ('PATH', 'VIRTUAL_ENV', 'PYTHONPATH', 'LANG', 'LC_ALL',
                'SSL_CERT_FILE', 'SSL_CERT_DIR', 'REQUESTS_CA_BUNDLE', 'CURL_CA_BUNDLE'):
        if key in os.environ:
            args.append(f'--setenv={key}={os.environ[key]}')
    return args + ['--', sys.executable, str(Path(__file__).resolve()), '--inside', '--', *command]


def terminate_job(unit, process, output):
    # Stop the service cgroup, not only systemd-run's process group.
    result = subprocess.run(['systemctl', '--user', 'stop', unit],
                            stdout=output, stderr=subprocess.STDOUT, timeout=10)
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
    # RuntimeMaxSec remains a kernel-service-manager backstop if stop failed.
    if result.returncode:
        output.write('Service stop returned nonzero; check the unit if cleanup is uncertain.\n')


def run_job(args, command):
    automatic = args.session is None
    name = args.session or ('run_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
                            + '_' + uuid.uuid4().hex[:8])
    path = start_session(name) if automatic else session_path(name)
    rid = uuid.uuid4().hex[:10]
    unit = f'mathcompute-job-{uuid.uuid4().hex}.service'
    log = LOGS / f'{name}-{rid}.output.txt'
    with locked(path):
        ensure_active(read_events(path))
        add_event(path, 'run_start', id=rid, category=args.category, command=command,
                  output=str(log.relative_to(ROOT / 'research')), cwd=str(Path.cwd()),
                  systemd_unit=unit, threads=args.threads, timeout_s=args.timeout)
    rc, timed_out, interrupted = 1, False, False
    process = None
    previous_term = signal.signal(signal.SIGTERM, lambda *_: (_ for _ in ()).throw(KeyboardInterrupt()))
    try:
        with log.open('w', buffering=1) as output:
            try:
                args_list = invocation(command, args.threads, args.timeout, unit)
                process = subprocess.Popen(args_list, stdout=output, stderr=subprocess.STDOUT)
                try:
                    rc = process.wait(timeout=args.timeout)
                except subprocess.TimeoutExpired:
                    timed_out = True
                    terminate_job(unit, process, output)
                    rc = 124
                except KeyboardInterrupt:
                    interrupted = True
                    terminate_job(unit, process, output)
                    rc = 130
            except Exception as error:
                output.write(f'Runner error: {error}\n')
                rc = 1
    except KeyboardInterrupt:
        interrupted = True
        rc = 130
        if process is not None and process.poll() is None:
            with log.open('a') as output:
                terminate_job(unit, process, output)
    finally:
        signal.signal(signal.SIGTERM, previous_term)
        with locked(path):
            add_event(path, 'run_end', id=rid, returncode=rc,
                      timed_out=timed_out, interrupted=interrupted)
            if automatic:
                stop = add_event(path, 'stop')
                data = summary(read_events(path), stop['monotonic_s'])
                path.with_suffix('.summary.json').write_text(json.dumps(data, indent=2) + '\n')
    if args.tail_bytes:
        with log.open('rb') as output:
            size = output.seek(0, os.SEEK_END)
            output.seek(max(0, size - args.tail_bytes))
            tail = output.read().decode('utf-8', errors='replace')
        if size > args.tail_bytes:
            print(f'[Showing last {args.tail_bytes} bytes; full output is saved.]')
        print(tail, end='' if tail.endswith('\n') or not tail else '\n')
    print(f'Exit {rc}; log: {log.relative_to(ROOT)}')
    return rc if rc >= 0 else 128 - rc


def run_options(parser):
    parser.add_argument('--threads', type=int, default=14)
    parser.add_argument('--timeout', type=float, default=180)
    parser.add_argument('--category', choices=RUNS, default='computation')
    parser.add_argument('--tail-bytes', type=int, default=8000,
                        help='Maximum output displayed; full output is always logged')


def main():
    raw = sys.argv[1:]
    if raw and raw[0] == '--inside':
        command = raw[1:]
        if command and command[0] == '--': command = command[1:]
        if not command: raise ValueError('Missing internal command')
        execute_inside(command)
    if raw in (['status'], ['--status']):
        show_status()
        return 0
    if raw and raw[0] in ('start', 'phase', 'report', 'run'):
        action = raw.pop(0)
        parser = argparse.ArgumentParser(prog=f'./compute.sh {action}')
        parser.add_argument('session')
        if action == 'phase':
            parser.add_argument('category', choices=PHASES)
            parser.add_argument('--note', default='')
        if action == 'report':
            parser.add_argument('--stop', action='store_true')
            parser.add_argument('--html-out', type=Path,
                                help='Write a notebook timing-table fragment for a completed session')
        if action == 'run':
            run_options(parser)
            # Explicit separator prevents options belonging to the command from
            # being interpreted as runner options.
            if '--' not in raw: parser.error('Use -- before the command')
            index = raw.index('--')
            command, raw = raw[index+1:], raw[:index]
        args = parser.parse_args(raw)
        if action == 'start':
            print(start_session(args.session).relative_to(ROOT))
            return 0
        if action != 'run':
            path = session_path(args.session)
            with locked(path):
                events = read_events(path)
                if action == 'phase':
                    ensure_active(events)
                    add_event(path, 'phase', category=args.category, note=args.note)
                else:
                    stop = next((e for e in events if e['event'] == 'stop'), None)
                    if stop is None: ensure_active(events)
                    if args.stop and stop is None:
                        started = {e['id'] for e in events if e['event'] == 'run_start'}
                        finished = {e['id'] for e in events if e['event'] == 'run_end'}
                        if started - finished: raise ValueError('Jobs are still running; cannot stop timing')
                        stop = add_event(path, 'stop')
                        events = read_events(path)
                    if args.html_out and stop is None:
                        raise ValueError('Use --stop to finalize the session before exporting its timing table')
                    data = summary(events, stop['monotonic_s'] if stop else time.monotonic())
                    path.with_suffix('.summary.json').write_text(json.dumps(data, indent=2) + '\n')
                    if args.html_out:
                        args.html_out.parent.mkdir(parents=True, exist_ok=True)
                        args.html_out.write_text(timing_html(data, args.session))
                    print(json.dumps(data, indent=2))
            return 0
    else:
        parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument('--session', help='Attach to a named session; otherwise log a standalone run')
        run_options(parser)
        parser.add_argument('command', nargs=argparse.REMAINDER)
        args = parser.parse_args(raw)
        command = args.command
        if command and command[0] == '--': command = command[1:]
    if not command: parser.error('Provide a command to execute')
    if not 1 <= args.threads <= 14: parser.error('--threads must be between 1 and 14')
    if not 0 < args.timeout < float('inf'): parser.error('--timeout must be finite and positive')
    if args.tail_bytes < 0: parser.error('--tail-bytes cannot be negative')
    return run_job(args, command)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f'compute.sh: {error}', file=sys.stderr)
        sys.exit(1)
