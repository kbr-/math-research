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
sys.path.insert(0, str(ROOT / 'tools'))
from recovery_evidence import observe as recovery_observe, snapshot as recovery_snapshot, stream as recovery_stream
LOGS = ROOT / 'research/logs'
SLICE = 'mathcompute.slice'
WATCHDOG = 'mathcompute-watchdog.service'
MAX_MEMORY = MAX_SWAP = 10_000_000_000
MAX_CPUS = set(range(14))
PHASES = ('restoration', 'reading', 'mathematics', 'formalization', 'coding', 'preparation', 'overhead',
          'reasoning_writing', 'external_tool', 'network_tool', 'other')
RUNS = ('computation', 'network_tool', 'external_tool', 'local_processing', 'formal_verification')


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


def detect_agent():
    if os.environ.get('MATH_AGENT'): return os.environ['MATH_AGENT']
    if os.environ.get('CLAUDECODE'): return 'Claude Code'
    if os.environ.get('CODEX_THREAD_ID'): return 'Codex'
    return 'unknown'


def codex_session_model():
    """Read only the active thread's latest turn settings; never persist its ID."""
    try:
        thread = str(uuid.UUID(os.environ.get('CODEX_THREAD_ID', '')))
        home = Path(os.environ.get('CODEX_HOME') or Path.home() / '.codex')
        paths = list((home / 'sessions').rglob(f'*-{thread}.jsonl'))
        if len(paths) != 1:
            return None
        latest = {}
        with paths[0].open() as stream:
            for line in stream:
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue  # The active log may end in a partially written line.
                if isinstance(event, dict) and event.get('type') == 'turn_context':
                    latest = event.get('payload') or {}
        if not isinstance(latest, dict):
            return None
        model, effort = latest.get('model'), latest.get('effort')
        if isinstance(model, str) and model and isinstance(effort, str) and effort:
            return f'{model}, {effort} reasoning'
    except (OSError, ValueError):
        pass
    return None


def session_model(agent=None, model=None):
    # Runtime turn metadata outranks a stale or guessed Codex label. Other
    # agents retain their existing explicit-model/environment precedence.
    if (agent or detect_agent()) == 'Codex':
        recorded = codex_session_model()
        if recorded:
            return recorded
    return model or os.environ.get('MATH_AGENT_MODEL')


def start_session(name, agent=None, model=None, notebook=None):
    from notebooks import selected
    notebook = selected(notebook, ROOT)["name"]
    # Record who produced the cycle; never a machine-local session ID.
    path = session_path(name)
    with locked(path):
        if path.exists():
            raise ValueError('Session exists; choose a new name')
        add_event(path, 'start', boot_id=boot_id(), agent=agent or detect_agent(),
                  model=session_model(agent, model) or 'unspecified', notebook=notebook)
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
    first=next(e for e in events if e['event']=='start')
    begin=first['monotonic_s']
    phases=[(begin,'preparation')]+[(e['monotonic_s'],e['category']) for e in events if e['event']=='phase']
    # Preserve event order at equal timestamps; an explicit phase overrides
    # the initial preparation phase rather than sorting by category name.
    phases=sorted(((max(begin,min(end,t)),c) for t,c in phases), key=lambda phase: phase[0])
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
    return {'agent':first.get('agent','unrecorded'),'model':first.get('model','unrecorded'),'total_instrumented_s':end-begin,'exclusive_categories_s':totals,'command_runs':len(runs),'failed_or_timed_out_commands':len(failures),
      'unfinished_commands':len(set(runs)-finished),
      'scope':'Phases label observed work windows, not internal cognition or pure latency. Unexpected interruptions may remain mixed with the active phase. Tool windows include service overhead; overlapping intervals count once. Work after the final snapshot is excluded.'}


def recovery_summary(data, path, cutoff):
    """Freeze portable evidence at the timing snapshot, without extra CLI output."""
    previous = path.with_suffix('.summary.json')
    saved = json.loads(previous.read_text()).get('recovery_proxy') if previous.exists() else None
    recovery = (saved if saved and saved.get('snapshot_unix_s') == cutoff
                 else recovery_snapshot(ROOT, path.stem, cutoff))
    # Do not retrofit old completed summaries: their archived bytes are immutable.
    if recovery.get('session_tracked') or saved or (not previous.exists() and recovery.get('collection') != 'available'):
        data['recovery_proxy'] = recovery
    return data


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
        ('restoration', 'Context restoration'),
        ('reading', 'Marked reading and review windows'),
        ('mathematics', 'Mathematical reasoning and proof writing'),
        ('formalization', 'Formal proof design and coding'),
        ('coding', 'Computation design and coding'),
        ('preparation', 'Preparation and checkpoint work'),
        ('overhead', 'Marked overhead and interruptions'),
        ('network_tool', 'Dedicated web and download-attempt windows'),
        ('external_tool', 'Other external-tool windows'),
        ('computation', 'Individually measured computation'),
        ('local_processing', 'Individually measured conversion, checks, and local processing'),
        ('formal_verification', 'Individually measured formal verification'),
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
                'SSL_CERT_FILE', 'SSL_CERT_DIR', 'REQUESTS_CA_BUNDLE', 'CURL_CA_BUNDLE',
                'MATH_RECOVERY_DISABLED'):
        if key in os.environ:
            args.append(f'--setenv={key}={os.environ[key]}')
    owner = recovery_stream()
    if owner:
        args.append(f'--setenv=MATH_RECOVERY_STREAM={owner}')
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
                  systemd_unit=unit, threads=args.threads, timeout_s=args.timeout,
                  expect_s=getattr(args, 'expect', None), serial_reason=getattr(args, 'serial_reason', ''),
                  kernel_reason=getattr(args, 'kernel_reason', ''),
                  user_approved=getattr(args, 'user_approved', ''))
    recovery_observe('job_start', root=ROOT, turn=name, job=rid, command=command, category=args.category)
    rc, timed_out, interrupted = 1, False, False
    started = time.monotonic()
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
            recovery_observe('job_end', root=ROOT, turn=name, job=rid, rc=rc)
            if automatic:
                stop = add_event(path, 'stop')
                data = summary(read_events(path), stop['monotonic_s'])
                recovery_summary(data, path, stop['unix_s'])
                path.with_suffix('.summary.json').write_text(json.dumps(data, indent=2) + '\n')
    if args.tail_bytes:
        with log.open('rb') as output:
            size = output.seek(0, os.SEEK_END)
            output.seek(max(0, size - args.tail_bytes))
            tail = output.read().decode('utf-8', errors='replace')
        if size > args.tail_bytes:
            print(f'[Showing last {args.tail_bytes} bytes; full output is saved.]')
        print(tail, end='' if tail.endswith('\n') or not tail else '\n')
    expect = getattr(args, 'expect', None)
    if expect:
        elapsed = time.monotonic() - started
        print(f'Expected {expect:g} s, took {elapsed:.0f} s.')
    print(f'Exit {rc}; log: {log.relative_to(ROOT)}')
    return rc if rc >= 0 else 128 - rc


LONG_RUN_S = 600
PARALLEL_THREADS = 4
# Hard run limit (user instructions, 23 September 2026: a cycle with 110 minutes of computation
# is too much; a single run may take up to 30 minutes, and a cycle's total is left to judgement).
# A run's --timeout may not exceed MAX_RUN_S unless the user's approval is quoted in --user-approved.
MAX_RUN_S = 1800
# Compiled-kernel default (user instruction, 23 September 2026, after repeated slow Python drivers): a Python
# command allowed more than KERNEL_RUN_S must state in --kernel-reason which compiled kernel does the heavy work
# and why the driver does not repeat it (for example one incremental elimination, not one per parameter).
KERNEL_RUN_S = 120
# Python loops (user instruction, 23 September 2026, after a driver built its matrices in four nested Python loops
# behind a --kernel-reason that named only the elimination kernel): the reason is a declaration the guard cannot
# verify, so a long Python computation is also scanned statically. Loop nesting of depth MAX_PY_LOOP_DEPTH or more
# (for/while statements and comprehension generators) in the script or in any local module it imports is refused;
# vectorize it (numpy index arithmetic) or move it into the compiled kernel. Only a quoted user approval overrides.
MAX_PY_LOOP_DEPTH = 3
# Parameter series (user instruction, 24 September 2026, after a driver refused by the loop guard was split into one
# invocation per parameter pair and looped from the shell; narrowed the same day at the user's request as too harsh):
# a series over parameters belongs in one run of one program (CLAUDE.md rules 3 to 5). Short Python computations
# (timeout <= KERNEL_RUN_S) escape the loop scan, so a Python script already run short in the session with
# MAX_SERIES_ARGSETS different argument lists is refused a further new one. Reruns, sizing and a few validation
# cases stay allowed. Only a quoted user approval overrides.
MAX_SERIES_ARGSETS = 6
# Sizing runs (user instruction, 24 September 2026, after two runs in one session were launched for 20+ minutes on an
# estimate that no measurement supported): a run expected to exceed LONG_RUN_S must cite, with --sized-by RUN_ID, a
# completed run of the same program in the same session, whose measured time the estimate extrapolates.


def python_loop_offenders(script, root=None):
    """(file, line, depth) of loops nested MAX_PY_LOOP_DEPTH deep in code the script can run: the whole script, and
    in each local module it imports the module-level statements plus the imported names and every top-level
    definition they reference, transitively (unused library functions are not scanned)."""
    import ast
    root = Path(root or Path(__file__).resolve().parent)
    trees, found, done = {}, set(), set()

    def tree(path):
        if path not in trees:
            try:
                trees[path] = ast.parse(path.read_text(), str(path))
            except (OSError, SyntaxError, UnicodeDecodeError):
                trees[path] = None
        return trees[path]

    def locate(name, near):
        for p in [near.parent / f'{name}.py'] + sorted((root / 'research' / 'results').glob(f'*/{name}.py')):
            if p.exists():
                return p.resolve()
        return None

    def small(it):                                    # a literal range or tuple of at most 64 constants is bounded work
        if isinstance(it, (ast.Tuple, ast.List, ast.Set)) and all(isinstance(e, ast.Constant) for e in it.elts):
            return len(it.elts) <= 64
        if (isinstance(it, ast.Call) and getattr(it.func, 'id', '') == 'range' and it.args
                and all(isinstance(e, ast.Constant) and isinstance(e.value, int) for e in it.args)):
            return len(range(*[e.value for e in it.args])) <= 64
        return False

    def loops(node, depth, path):
        loop = isinstance(node, (ast.For, ast.AsyncFor)) and not small(node.iter) or isinstance(node, ast.While)
        gens = (sum(not small(g.iter) for g in node.generators)
                if isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)) else 0)
        here = depth + (1 if loop else 0) + gens
        if (loop or gens) and here >= MAX_PY_LOOP_DEPTH:
            found.add((str(path), getattr(node, 'lineno', 0), here))
        for child in ast.iter_child_nodes(node):
            if not isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                loops(child, here, path)

    def visit(path, names):
        t = tree(path)
        if t is None:
            return
        defs = {n.name: n for n in t.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}
        main = lambda n: (isinstance(n, ast.If) and isinstance(n.test, ast.Compare)
                          and getattr(n.test.left, 'id', '') == '__name__')
        entry = names is None
        units = [n for n in t.body if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                 and (entry or not main(n))]
        wanted = set(defs) if entry else set(names or ())
        while True:                                   # close the wanted definitions under references
            refs = {n.id for u in units + [defs[w] for w in wanted if w in defs] for n in ast.walk(u)
                    if isinstance(n, ast.Name) and n.id in defs}
            if refs <= wanted:
                break
            wanted |= refs
        reach = units + [defs[w] for w in wanted if w in defs]
        used = {n.id for u in reach if not isinstance(u, (ast.Import, ast.ImportFrom)) for n in ast.walk(u)
                if isinstance(n, ast.Name)}
        for u in reach:
            key = (path, getattr(u, 'lineno', 0))
            if key in done:
                continue
            done.add(key)
            if isinstance(u, ast.ClassDef):
                for m in u.body:
                    loops(m, 0, path)
            elif isinstance(u, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for m in u.body:
                    loops(m, 0, path)
            else:
                loops(u, 0, path)
            for n in ast.walk(u):
                if isinstance(n, ast.ImportFrom) and n.module and not n.level:
                    p = locate(n.module.split('.')[0], path)
                    if p:
                        visit(p, [alias.name for alias in n.names if entry or (alias.asname or alias.name) in used])
                elif isinstance(n, ast.Import):
                    for alias in n.names:
                        p = locate(alias.name.split('.')[0], path)
                        if p:
                            visit(p, list({a.attr for a in ast.walk(t) if isinstance(a, ast.Attribute)
                                           and getattr(a.value, 'id', '') == (alias.asname or alias.name)}))

    visit(Path(script).resolve(), None)
    return sorted(found)


def program_key(command):
    """The program a command runs: its first script argument, else the executable's name."""
    script = next((c for c in command[1:] if Path(c).suffix in ('.py', '.sh', '.sing', '.g', '.m2')), None)
    return Path(script).name if script else Path(command[0]).name if command else ''


def series_error(events, command, timeout):
    """None unless `command`, a short Python computation (timeout <= KERNEL_RUN_S), would be a further new argument
    list for a script that `events` (the session journal) already ran short with MAX_SERIES_ARGSETS different
    argument lists; else the reason."""
    key = program_key(command)
    if not Path(command[0]).name.startswith('python') or not key.endswith('.py') or timeout > KERNEL_RUN_S:
        return None
    seen = {tuple(e['command'][1:]) for e in events if e['event'] == 'run_start'
            and e.get('category', 'computation') == 'computation' and program_key(e['command']) == key
            and Path(e['command'][0]).name.startswith('python') and (e.get('timeout_s') or 0) <= KERNEL_RUN_S}
    if tuple(command[1:]) in seen or len(seen) < MAX_SERIES_ARGSETS:
        return None
    return (f'{key} already ran short with {len(seen)} different argument lists in this session: a parameter series '
            'belongs in one run, with the loop in the compiled kernel, not in the shell or in repeated invocations '
            '(CLAUDE.md rules 3 to 5); only --user-approved overrides')


def sizing_error(events, sized_by, command, expect):
    """None if RUN_ID `sized_by` is a completed run of the same program in `events`; else the reason it is not.
    On success the second value is the sizing run's measured seconds."""
    start = next((e for e in events if e['event'] == 'run_start' and e.get('id') == sized_by), None)
    if start is None:
        return f'--sized-by {sized_by}: no run with that id in this session', None
    end = next((e for e in events if e['event'] == 'run_end' and e.get('id') == sized_by), None)
    if end is None or end.get('returncode') != 0 or end.get('timed_out') or end.get('interrupted'):
        return f'--sized-by {sized_by}: that run did not complete successfully', None
    if program_key(start['command']) != program_key(command):
        return (f'--sized-by {sized_by}: that run used {program_key(start["command"])}, not '
                f'{program_key(command)}'), None
    took = end['monotonic_s'] - start['monotonic_s']
    if expect < took:
        return f'--expect {expect:g} is below the sizing run\'s own {took:.0f} s', None
    return None, took


def run_options(parser):
    parser.add_argument('--threads', type=int, default=14)
    parser.add_argument('--timeout', type=float, default=180)
    parser.add_argument('--expect', type=float,
                        help='Estimated running time in seconds, from a count or a smaller run; '
                             f'required when --timeout exceeds {LONG_RUN_S:g}')
    parser.add_argument('--serial-reason', default='',
                        help='Why a run expected to exceed the long-run limit uses fewer than '
                             f'{PARALLEL_THREADS} threads')
    parser.add_argument('--kernel-reason', default='',
                        help=f'For a Python command with --timeout above {KERNEL_RUN_S} s: the compiled kernel (C/C++) '
                             'doing the heavy work and why nothing is recomputed')
    parser.add_argument('--sized-by', default='',
                        help=f'For --expect above {LONG_RUN_S:g} s: the id of a completed smaller run of the same '
                             'program in this session (the id in its log name SESSION-ID.output.txt)')
    parser.add_argument('--category', choices=RUNS, default='computation')
    parser.add_argument('--user-approved', default='',
                        help='Quote of the user\'s explicit approval for a run beyond MAX_RUN_S')
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
        if action == 'start':
            parser.add_argument('--notebook', help='Research thread; defaults to worktree selection or main')
            parser.add_argument('--agent', help='Default: detected from the environment or MATH_AGENT')
            parser.add_argument('--model', help='Model and reasoning setting; Codex uses active turn metadata when available, otherwise this value or MATH_AGENT_MODEL')
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
            if not session_model(args.agent, args.model):
                parser.error('State your model: --model "MODEL, reasoning setting" (or set MATH_AGENT_MODEL)')
            print(start_session(args.session, args.agent, args.model, args.notebook).relative_to(ROOT))
            recovery_observe('bind', root=ROOT, turn=args.session)
            try:   # advisory only: what finish-turn.py would reject, said before the work starts
                guide = subprocess.run([sys.executable, str(ROOT / 'tools/turn_guidance.py')]
                                       + ([args.notebook] if args.notebook else []),
                                       cwd=ROOT, capture_output=True, text=True, timeout=60)
                print(guide.stdout, end='')
            except (OSError, subprocess.SubprocessError):
                pass
            return 0
        if action != 'run':
            path = session_path(args.session)
            with locked(path):
                events = read_events(path)
                if action == 'phase':
                    ensure_active(events)
                    add_event(path, 'phase', category=args.category, note=args.note)
                    recovery_observe('phase', root=ROOT, turn=args.session, category=args.category)
                else:
                    stop = next((e for e in events if e['event'] == 'stop'), None)
                    if stop is None: ensure_active(events)
                    if args.stop and stop is None:
                        started = {e['id'] for e in events if e['event'] == 'run_start'}
                        finished = {e['id'] for e in events if e['event'] == 'run_end'}
                        if started - finished: raise ValueError('Jobs are still running; cannot stop timing')
                        stop = add_event(path, 'stop')
                        recovery_observe('stop', root=ROOT, turn=args.session, at=stop['unix_s'])
                        events = read_events(path)
                    if args.html_out and stop is None:
                        raise ValueError('Use --stop to finalize the session before exporting its timing table')
                    data = summary(events, stop['monotonic_s'] if stop else time.monotonic())
                    recovery_summary(data, path, stop['unix_s'] if stop else time.time())
                    path.with_suffix('.summary.json').write_text(json.dumps(data, indent=2) + '\n')
                    if args.html_out:
                        args.html_out.parent.mkdir(parents=True, exist_ok=True)
                        args.html_out.write_text(timing_html(data, args.session))
                    print(json.dumps({k:v for k,v in data.items() if k != 'recovery_proxy'}, indent=2))
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
    if args.timeout > LONG_RUN_S and args.expect is None:
        parser.error(f'--timeout above {LONG_RUN_S:g} s needs --expect SECONDS: estimate the running '
                     'time from a count or a smaller run first (COMPUTATION_RULES.md)')
    if args.timeout > MAX_RUN_S and not args.user_approved.strip():
        parser.error(f'--timeout above {MAX_RUN_S} s needs --user-approved "QUOTE": runs are limited to '
                     f'{MAX_RUN_S // 60} minutes unless the user explicitly approves more (COMPUTATION_RULES.md)')
    if args.expect is not None and not 0 < args.expect <= args.timeout:
        parser.error('--expect must be positive and at most --timeout')
    if (args.expect or 0) > LONG_RUN_S and args.threads < PARALLEL_THREADS and not args.serial_reason.strip():
        parser.error(f'a run expected to exceed {LONG_RUN_S:g} s on fewer than {PARALLEL_THREADS} threads '
                     'needs --serial-reason: use the parallel paths first (COMPUTATION_RULES.md)')
    if (args.expect or 0) > LONG_RUN_S and not args.user_approved.strip():
        if not args.sized_by or not getattr(args, 'session', None):
            parser.error(f'a run expected to exceed {LONG_RUN_S:g} s needs --session and --sized-by RUN_ID: first run '
                         'the same program at a smaller size in this session and extrapolate --expect from its '
                         'measured time (CLAUDE.md, COMPUTATION_RULES.md); only --user-approved overrides')
        journal = session_path(args.session)
        events = read_events(journal) if journal.exists() else []
        error, took = sizing_error(events, args.sized_by, command, args.expect)
        if error: parser.error(error + ' (CLAUDE.md, COMPUTATION_RULES.md)')
        print(f'Sized by run {args.sized_by}: took {took:.0f} s; expecting {args.expect:g} s.')
    if args.category == 'computation' and getattr(args, 'session', None) and not args.user_approved.strip():
        journal = session_path(args.session)
        error = series_error(read_events(journal) if journal.exists() else [], command, args.timeout)
        if error: parser.error(error)
    exe = Path(command[0]).name if command else ''
    if (exe.startswith('python') and args.timeout > KERNEL_RUN_S and args.category == 'computation'
            and len(args.kernel_reason.split()) < 6):
        parser.error(f'a Python computation allowed more than {KERNEL_RUN_S} s needs --kernel-reason "..." of at '
                     'least six words: name the compiled C/C++ kernel doing the heavy work (including product '
                     'or row generation) and the reuse (one incremental pass per series, shared prefixes '
                     'computed once and copied); never launch with known waste (CLAUDE.md)')
    if (exe.startswith('python') and args.timeout > KERNEL_RUN_S and args.category == 'computation'
            and not args.user_approved.strip()):
        script = next((c for c in command[1:] if c.endswith('.py')), None)
        offenders = python_loop_offenders(script) if script else []
        if offenders:
            shown = '; '.join(f'{Path(f).name}:{line} (depth {d})' for f, line, d in offenders[:6])
            parser.error(f'a Python computation allowed more than {KERNEL_RUN_S} s may not nest loops '
                         f'{MAX_PY_LOOP_DEPTH} deep in its script or local imports: {shown}. Vectorize or move them '
                         'into the compiled kernel (CLAUDE.md); only --user-approved overrides')
    return run_job(args, command)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f'compute.sh: {error}', file=sys.stderr)
        sys.exit(1)
