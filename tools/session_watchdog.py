#!/usr/bin/env python3
"""Session watchdog: find looping sessions of this repository that stalled, or wait at a prompt.

Two faults were measured on 17 October 2026 (times UTC). In each, a session with an active /goal
ended a turn (its last assistant message has stop_reason end_turn) and then nothing ran: no Stop
hook (no stop_hook_summary record), no goal evaluation (no goal_status), no turn_duration, and no
user input. The Common multiplier session (354c41d4) stalled so from 08:12:07, the Talagrand
session (c0de408b) from 06:49:07. The framework's Stop hook cannot see such a stop, since it never
runs; this watchdog reads the transcripts from outside. Separately, a session waiting at a
permission prompt has a main-chain tool_use with no tool_result; Talagrand waited so from 21:25:07
on 16 October for 95 minutes and from 02:39 on 17 October for 48 minutes.

Classification, from the tail of the main-chain records (records with isSidechain are ignored):
- stall: the last assistant record has stop_reason end_turn; after it there is no
  stop_hook_summary, turn_duration, goal record or user record; the job has no task in flight; the
  goal is active (the latest goal_status attachment or /goal command output says so); and at
  least STALL_S seconds have passed. Action: wake (stop the session, then resume it from its own
  directory with a prompt that says the watchdog sent it).
- permission_wait: a tool_use of the last assistant message has no tool_result, no task is in
  flight, and the call has outlived both PROMPT_S and its own run bound (a foreground Bash call
  cannot outlive its timeout, so silence beyond it is not a running command). A pending
  AskUserQuestion or ExitPlanMode is a question_wait. Action: notify. A tool with no run bound (a
  foreground Agent) is a long_call and gets nothing.
- otherwise nothing.

Only sessions with a live process (a pid in `claude agents --json`) are acted on, so a session the
user stopped or the daemon retired is never woken. A stall is woken at most once; a second stall on
the same anchor, a stall with no work done since the last wake, or a wake that leaves no watchdog
prompt in the transcript within WAKE_CHECK_S, is notified instead. Notifications go to a phone
push only, through one notifier session with Remote Control, woken by the same route with a prompt
to wait 75 s (the tool refuses a push within 60 s of an interaction with the session) and then call
PushNotification; the push result it records is logged, only "Mobile push requested" counts as
requested, and any other result is retried every RETRY_S seconds while the condition holds. This
is not a working alert channel yet: on 17 October 2026 a push the tool reported as "Mobile push
requested" did not reach the user's phone, so delivery is unverified; the log is the record. Every decision is logged under
research/logs/session-watchdog/ of the main checkout. Actions are off unless asked for: `--wake`
enables wakes and `--notify` pushes; without them a poll only logs what it would do.

Usage:
  session_watchdog.py poll [--wake] [--notify] [--notifier SESSION]   one pass over the sessions
  session_watchdog.py run [--interval 45] [--wake] [--notify] ...     poll until stopped
  session_watchdog.py replay TRANSCRIPT [--out FILE]                  detections over a whole file
  session_watchdog.py extract --window TRANSCRIPT FROM TO OUT ...     slim events, for tests
"""
import argparse
import datetime as dt
import glob
import json
import os
import subprocess
import sys
import time
from pathlib import Path

STALL_S = 300
PROMPT_S = 300
BOUND_GRACE_S = 120
WAKE_CHECK_S = 180
RETRY_S = 600
PUSH_CHECK_S = 420
# The PushNotification tool's text for a sent push (Claude Code 2.1.302); any other result is retried.
PUSH_SENT = 'Mobile push requested'
TAIL_START = 1 << 20
TAIL_MAX = 32 << 20
QUESTION_TOOLS = {'AskUserQuestion', 'ExitPlanMode'}
UNBOUNDED_TOOLS = {'Agent', 'Task'}
DEFAULT_BOUND_S = 300
PROMPT_TAG = '[session watchdog]'
WAKE_PROMPT = (PROMPT_TAG + ' Your last turn ended without its stop checks or goal evaluation (a Claude '
               'Code fault). Continue the Spin from your last reply.')
NOTIFIER_NAME = 'Session watchdog notifier'
HOME = Path.home()


def epoch(ts):
    return dt.datetime.fromisoformat(ts.replace('Z', '+00:00')).timestamp()


def iso(t):
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'


def goal_text_state(content):
    """Goal state named by a /goal command's output, or None for other local commands."""
    if not isinstance(content, str) or '<local-command-stdout>' not in content:
        return None
    body = content.split('<local-command-stdout>', 1)[1]
    if body.startswith('Goal set:') or body.startswith('Goal active:'):
        return True
    if body.startswith('Goal cleared') or body.startswith('No goal set'):
        return False
    return None


def tool_bound(name, inputs):
    """Seconds a foreground call of this tool can run before it must have returned; None if unbounded."""
    inputs = inputs if isinstance(inputs, dict) else {}
    if name in UNBOUNDED_TOOLS and not inputs.get('run_in_background'):
        return None
    if name == 'Bash':
        if inputs.get('run_in_background'):
            return 60
        timeout = inputs.get('timeout')
        return min(600, max(1, (timeout if isinstance(timeout, (int, float)) else 120000) / 1000))
    return DEFAULT_BOUND_S


def slim(record):
    """The fields the classifier reads, from one transcript record; None for records it ignores."""
    if not isinstance(record, dict) or record.get('isSidechain') or not record.get('timestamp'):
        return None
    t, typ = record['timestamp'], record.get('type')
    if typ == 'assistant':
        msg = record.get('message') or {}
        tools = [dict(id=c.get('id'), name=c.get('name'), bound=tool_bound(c.get('name'), c.get('input')))
                 for c in msg.get('content') or [] if isinstance(c, dict) and c.get('type') == 'tool_use']
        return dict(t=t, k='assistant', stop=msg.get('stop_reason'), mid=msg.get('id'),
                    uuid=record.get('uuid'), tools=tools)
    if typ == 'user':
        content = (record.get('message') or {}).get('content')
        ids = [c.get('tool_use_id') for c in content or [] if isinstance(c, dict) and c.get('type') == 'tool_result'] \
            if isinstance(content, list) else []
        if ids:
            return dict(t=t, k='result', ids=ids)
        text = content if isinstance(content, str) else ' '.join(
            c.get('text', '') for c in content or [] if isinstance(c, dict))
        return dict(t=t, k='input', watchdog=PROMPT_TAG in text,
                    feedback=text.lstrip().startswith('Stop hook feedback'))
    if typ == 'system':
        sub = record.get('subtype')
        if sub == 'stop_hook_summary':
            return dict(t=t, k='hook')
        if sub == 'turn_duration':
            return dict(t=t, k='duration')
        if sub == 'local_command':
            state = goal_text_state(record.get('content'))
            return None if state is None else dict(t=t, k='goal', active=state, source='command')
        return None
    if typ == 'attachment':
        a = record.get('attachment') or {}
        if a.get('type') == 'goal_status':
            return dict(t=t, k='goal', active=not a.get('met'), source='status')
    return None


def goal_active(events, initial=None):
    state = initial
    for e in events:
        if e['k'] == 'goal':
            state = e['active']
    return bool(state)


def classify(events, now, in_flight=0, goal=None):
    """Verdict dict(kind, since, anchor, detail) for slim events (oldest first) at time `now`.

    `goal` is the goal state before the first event (None if unknown); `in_flight` the job's
    count of running tasks (0 when unknown, as in a replay).
    """
    none = dict(kind='none', since=None, anchor=None, detail='')
    last = next((i for i in range(len(events) - 1, -1, -1) if events[i]['k'] == 'assistant'), None)
    if last is None:
        return dict(none, detail='no assistant record')
    a, after = events[last], events[last + 1:]
    closing = [e for e in after if e['k'] in ('hook', 'duration', 'input', 'goal')]
    if a['stop'] == 'end_turn':
        if closing:
            return dict(none, detail='turn closed by ' + closing[0]['k'])
        if in_flight:
            return dict(none, detail=f'{in_flight} tasks in flight')
        if not goal_active(events, goal):
            return dict(none, detail='no active goal')
        since = epoch(a['t'])
        if now - since < STALL_S:
            return dict(none, detail='turn ended recently')
        return dict(kind='stall', since=a['t'], anchor=a['uuid'] or a['mid'], needed=STALL_S,
                    detail=f'end_turn at {a["t"]} with no stop hook, goal evaluation or input since')
    if a['stop'] != 'tool_use':
        return dict(none, detail=f'stop_reason {a["stop"]}')
    first = next(i for i, e in enumerate(events) if e['k'] == 'assistant' and e['mid'] == a['mid'])
    tools = [(e['t'], tool) for e in events[first:] if e['k'] == 'assistant' and e['mid'] == a['mid']
             for tool in e['tools']]
    answered = {i for e in events[first:] if e['k'] == 'result' for i in e['ids']}
    pending = [(t, tool) for t, tool in tools if tool['id'] not in answered]
    if not pending:
        return dict(none, detail='tool calls answered')
    if closing:
        return dict(none, detail='turn closed by ' + closing[0]['k'])
    if in_flight:
        return dict(none, detail=f'{in_flight} tasks in flight')
    t, tool = pending[0]
    waited = now - epoch(t)
    if tool['name'] in QUESTION_TOOLS:
        kind, needed = 'question_wait', PROMPT_S
    elif tool['bound'] is None:
        return dict(none, detail=f'long {tool["name"]} call')
    else:
        kind, needed = 'permission_wait', max(PROMPT_S, tool['bound'] + BOUND_GRACE_S)
    if waited < needed:
        return dict(none, detail=f'{tool["name"]} call pending {waited:.0f} s of {needed:.0f} s')
    return dict(kind=kind, since=t, anchor=tool['id'], needed=needed,
                detail=f'{tool["name"]} call {tool["id"]} pending since {t}, bound {tool["bound"]} s')


# Transcript reading ----------------------------------------------------------------------------

def parse_lines(data):
    out = []
    for line in data.split(b'\n'):
        if line.strip():
            try:
                out.append(json.loads(line))
            except ValueError:
                pass
    return out


def read_tail(path, start=TAIL_START, limit=TAIL_MAX):
    """Slim events of the file's tail, long enough to hold its last main-chain assistant record."""
    size = os.path.getsize(path)
    n = start
    with open(path, 'rb') as f:
        while True:
            off = max(0, size - n)
            f.seek(off)
            data = f.read(size - off)
            if off:
                data = data[data.find(b'\n') + 1:]
            events = [e for e in map(slim, parse_lines(data)) if e]
            if any(e['k'] == 'assistant' for e in events) or off == 0 or n >= limit:
                return events, off
            n *= 2


GOAL_MARKS = (b'"type":"goal_status"', b'"subtype":"local_command"')


def line_at(f, pos, size):
    """The whole line holding byte `pos`."""
    lo = pos
    while lo > 0:
        step = min(lo, 65536)
        f.seek(lo - step)
        chunk = f.read(step)
        i = chunk.rfind(b'\n')
        if i >= 0:
            lo = lo - step + i + 1
            break
        lo -= step
    f.seek(lo)
    return f.readline()


def scan_goal(path, lo=0, hi=None, chunk=8 << 20):
    """Goal state from the last goal record in bytes [lo, hi), searched backwards; None if none."""
    size = os.path.getsize(path)
    hi = size if hi is None else hi
    with open(path, 'rb') as f:
        end = hi
        while end > lo:
            start = max(lo, end - chunk)
            f.seek(start)
            data = f.read(end - start + 64)
            cut = end - start + 64
            while True:
                pos = max(data.rfind(m, 0, cut) for m in GOAL_MARKS)
                if pos < 0:
                    break
                if start + pos >= hi:
                    cut = pos
                    continue
                e = slim(next(iter(parse_lines(line_at(f, start + pos, size))), None))
                if e and e['k'] == 'goal':
                    return e['active']
                cut = pos
            end = start
    return None


# Sessions and actions --------------------------------------------------------------------------

def git_common(path):
    try:
        out = subprocess.run(['git', '-C', str(path), 'rev-parse', '--path-format=absolute', '--git-common-dir'],
                             capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return os.path.realpath(out.stdout.strip()) if out.returncode == 0 else None


def main_checkout():
    common = git_common(Path(__file__).resolve().parent)
    return Path(common).parent if common else Path(__file__).resolve().parent.parent


def claude(*args, cwd=None, timeout=60):
    return subprocess.run(['claude', *args], capture_output=True, text=True, timeout=timeout, cwd=cwd)


def list_sessions():
    out = claude('agents', '--json')
    if out.returncode:
        raise RuntimeError('claude agents --json failed: ' + out.stderr.strip()[:300])
    return json.loads(out.stdout)


def job_state(short):
    try:
        return json.loads((HOME / '.claude' / 'jobs' / short / 'state.json').read_text())
    except (OSError, ValueError, TypeError):
        return {}


def transcript_path(session, state):
    p = state.get('linkScanPath')
    if p and os.path.exists(p) and session['sessionId'] in p:
        return p
    hits = glob.glob(str(HOME / '.claude' / 'projects' / '*' / (session['sessionId'] + '.jsonl')))
    return hits[0] if hits else None


class Watchdog:
    def __init__(self, root, wake=False, notify=False, notifier=None, now=time.time):
        self.root = Path(root)
        self.common = git_common(self.root)
        self.dir = self.root / 'research' / 'logs' / 'session-watchdog'
        self.dir.mkdir(parents=True, exist_ok=True)
        self.state_path = self.dir / 'state.json'
        try:
            self.state = json.loads(self.state_path.read_text())
        except (OSError, ValueError):
            self.state = {}
        self.state.setdefault('wakes', {})
        self.state.setdefault('alerts', {})
        self.state.setdefault('goals', {})
        if notifier:
            self.state['notifier'] = notifier
        self.do_wake, self.do_notify, self.now = wake, notify, now

    def log(self, **entry):
        entry = dict(at=iso(self.now()), **entry)
        with open(self.dir / (entry['at'][:10] + '.jsonl'), 'a') as f:
            f.write(json.dumps(entry) + '\n')

    def save(self):
        tmp = self.state_path.with_suffix('.new')
        tmp.write_text(json.dumps(self.state, indent=1))
        tmp.replace(self.state_path)

    def goal(self, path, offset):
        """Goal state before byte `offset`, from a cached backward scan extended to the new bytes."""
        st = os.stat(path)
        cache = self.state['goals'].get(path)
        if cache and cache['inode'] == st.st_ino and cache['scanned'] <= offset:
            found = scan_goal(path, cache['scanned'], offset)
            state = cache['state'] if found is None else found
        else:
            state = scan_goal(path, 0, offset)
        self.state['goals'][path] = dict(inode=st.st_ino, scanned=offset, state=state)
        return state

    def ours(self, session):
        return session.get('cwd') and git_common(session['cwd']) == self.common

    def poll(self):
        verdicts = []
        for s in list_sessions():
            if not self.ours(s) or s.get('sessionId') == (self.state.get('notifier') or {}).get('sessionId'):
                continue
            job = job_state(s['id']) if s.get('id') else {}
            path = transcript_path(s, job)
            if not path:
                continue
            events, offset = read_tail(path)
            in_flight = (job.get('inFlight') or {}).get('tasks', 0)
            v = classify(events, self.now(), in_flight=in_flight, goal=self.goal(path, offset))
            v.update(session=s.get('id') or s.get('sessionId'), name=s.get('name'), alive=bool(s.get('pid')))
            verdicts.append(v)
            self.check_wake(s, events)
            if v['kind'] != 'none':
                self.act(s, v, events)
        self.read_notifier()
        # A heartbeat in the state file every poll; a log line when the verdicts change, so that a
        # quiet watchdog is seen to be polling without a line per poll.
        summary = sorted([v['session'], v['name'], v['alive'], v['kind']] for v in verdicts)
        if summary != self.state.get('last_summary'):
            self.log(event='poll', sessions=summary)
            self.state['last_summary'] = summary
        self.state['last_poll'] = iso(self.now())
        self.save()
        return verdicts

    def check_wake(self, s, events):
        w = self.state['wakes'].get(s.get('sessionId'))
        if not w or w.get('verified') is not None:
            return
        seen = any(e['k'] == 'input' and e.get('watchdog') and epoch(e['t']) >= w['at'] - 5 for e in events)
        if seen or self.now() - w['at'] > WAKE_CHECK_S:
            w['verified'] = seen
            self.log(event='wake-check', session=s.get('id'), name=s.get('name'), delivered=seen)
            if not seen:
                self.alert(s, f'wake of {s.get("name")} delivered no prompt', ('wake-failed', w['anchor']))

    def act(self, s, v, events):
        key = (v['kind'], v['anchor'])
        if v['kind'] != 'stall':
            self.log(event='detected', session=s.get('id'), name=s.get('name'), verdict=v)
            self.alert(s, f'{s.get("name")}: {v["kind"].replace("_", " ")} since {v["since"]}', key)
            return
        w = self.state['wakes'].get(s['sessionId'])
        worked = w and any(e['k'] == 'result' and epoch(e['t']) > w['at'] for e in events)
        if not s.get('pid') or s.get('kind') != 'background':
            reason = 'no live background process'
        elif w and (w['anchor'] == v['anchor'] or not worked):
            reason = 'stalled again without progress since the last wake'
        else:
            reason = None
        if reason:
            self.log(event='detected', session=s.get('id'), name=s.get('name'), verdict=v, wake=False, reason=reason)
            if s.get('pid'):
                self.alert(s, f'{s.get("name")} stalled since {v["since"]}; {reason}', key)
            return
        self.log(event='detected', session=s['id'], name=s.get('name'), verdict=v, wake=self.do_wake)
        if self.do_wake:
            ok, detail = wake_session(s, WAKE_PROMPT)
            self.state['wakes'][s['sessionId']] = dict(at=self.now(), anchor=v['anchor'], ok=ok, verified=None if ok else False)
            self.log(event='wake', session=s['id'], name=s.get('name'), ok=ok, detail=detail)
            if not ok:
                self.alert(s, f'wake of {s.get("name")} failed: {detail[:120]}', ('wake-failed', v['anchor']))

    def alert(self, s, message, key):
        k = json.dumps([s.get('sessionId'), *key])
        a = self.state['alerts'].setdefault(k, dict(message=message, first=self.now(), attempts=0,
                                                    last=None, delivered=False, results=[]))
        if a['delivered'] or (a['last'] and self.now() - a['last'] < RETRY_S):
            return
        if not self.do_notify:
            self.log(event='alert', key=k, message=message, sent=False, reason='notify off')
            a['last'] = self.now()
            return
        if self.state.get('pending_push'):
            return
        ok, detail = self.push(message)
        a['attempts'] += 1
        a['last'] = self.now()
        self.state['pending_push'] = dict(key=k, at=self.now()) if ok else None
        self.log(event='alert', key=k, message=message, sent=ok, detail=detail)

    def push(self, message):
        prompt = (f'{PROMPT_TAG} First wait 75 seconds: arm the Monitor tool on the command '
                  '"sleep 75; echo done" with a 120000 ms timeout and wait for its event (a push is refused '
                  'within 60 s of an interaction). Then load the PushNotification tool with ToolSearch if '
                  f'needed and call it with exactly this message: {json.dumps(message)}. End your turn with '
                  'the tool\'s result quoted word for word. Do nothing else.')
        n = self.state.get('notifier')
        if not n:
            out = claude('--bg', '--remote-control', '-n', NOTIFIER_NAME, '--model', 'haiku', prompt,
                         cwd=str(self.root), timeout=120)
            if out.returncode:
                return False, 'creating the notifier failed: ' + out.stderr.strip()[:200]
            for s in list_sessions():
                if s.get('name') == NOTIFIER_NAME and s.get('pid'):
                    self.state['notifier'] = dict(id=s.get('id'), sessionId=s.get('sessionId'), cwd=s.get('cwd'))
                    return True, 'notifier created'
            return False, 'notifier created but not listed'
        session = next((s for s in list_sessions() if s.get('sessionId') == n.get('sessionId')), None)
        if not session:
            self.state['notifier'] = None
            return False, 'notifier session is gone; a new one is created at the next attempt'
        return wake_session(session, prompt)

    def read_notifier(self):
        p = self.state.get('pending_push')
        n = self.state.get('notifier')
        if not p or not n:
            return
        hits = glob.glob(str(HOME / '.claude' / 'projects' / '*' / (n['sessionId'] + '.jsonl')))
        result = push_result(hits[0], p['at']) if hits else None
        a = self.state['alerts'].get(p['key'])
        if result is None:
            if self.now() - p['at'] > PUSH_CHECK_S:
                self.log(event='push-result', key=p['key'], result=None, detail='no PushNotification result')
                self.state['pending_push'] = None
            return
        delivered = PUSH_SENT in result
        if a:
            a['results'].append(result[:300])
            a['delivered'] = delivered
        self.log(event='push-result', key=p['key'], result=result[:300], delivered=delivered)
        self.state['pending_push'] = None


def push_result(path, after):
    """Text of the first PushNotification result recorded after time `after`, or None."""
    events = parse_lines(open(path, 'rb').read()[-(4 << 20):])
    calls = set()
    for r in events:
        if r.get('isSidechain') or not r.get('timestamp') or epoch(r['timestamp']) < after - 5:
            continue
        content = (r.get('message') or {}).get('content')
        if not isinstance(content, list):
            continue
        for c in content:
            if not isinstance(c, dict):
                continue
            if c.get('type') == 'tool_use' and c.get('name') == 'PushNotification':
                calls.add(c.get('id'))
            if c.get('type') == 'tool_result' and c.get('tool_use_id') in calls:
                body = c.get('content')
                return body if isinstance(body, str) else ' '.join(x.get('text', '') for x in body or [] if isinstance(x, dict))
    return None


def wake_session(session, prompt):
    """Stop a background session, then resume it from its own directory with `prompt`, no flags.

    Resuming a session that still runs, or with flags, starts a copy instead; so stop first and
    wait until its process is gone.
    """
    short = session.get('id')
    out = claude('stop', short)
    if out.returncode:
        return False, 'claude stop: ' + (out.stderr or out.stdout).strip()[:200]
    for _ in range(30):
        if not any(s.get('id') == short and s.get('pid') for s in list_sessions()):
            break
        time.sleep(1)
    else:
        return False, 'session still running after claude stop'
    out = claude('--bg', '--resume', session['sessionId'], prompt, cwd=session['cwd'], timeout=120)
    if out.returncode:
        return False, 'claude --bg --resume: ' + (out.stderr or out.stdout).strip()[:200]
    return True, out.stdout.strip()[:200]


SESSION_UNIT = 'mathsession-watchdog.service'
STOPPED_FILE = 'mathsession-watchdog.stopped'


def service_notice(runtime, active=None):
    """A line for the agent when the service is down and the user has not stopped it, else None.

    `runtime` is the main checkout's .resource-runtime, where resource-controls/setup.py records a
    stop by the user; `active` overrides the systemctl query, for tests.
    """
    if (Path(runtime) / STOPPED_FILE).exists():
        return None
    if active is None:
        try:
            active = subprocess.run(['systemctl', '--user', 'is-active', SESSION_UNIT], capture_output=True,
                                    text=True, timeout=10).stdout.strip() == 'active'
        except (OSError, subprocess.TimeoutExpired):
            active = False
    if active:
        return None
    return (f'Session watchdog: {SESSION_UNIT} is not running (a reboot stops it); run python3 '
            'resource-controls/setup.py from the repository root, without asking, as for the memory controls '
            '(COMPUTATION_RULES.md, After reboot or session resume).')


# Replay and extraction --------------------------------------------------------------------------

def stream(path):
    with open(path, 'rb') as f:
        for line in f:
            try:
                e = slim(json.loads(line))
            except ValueError:
                continue
            if e:
                yield e


def replay(events, goal=None, stats=None, end=None):
    """Detections over a whole event stream: for each silence, the verdict just before it ended.

    Unknown here: tasks in flight (taken as 0) and process liveness. A detection is reported once
    per anchor, with the time it began to hold and when the silence ended. `stats`, a dict if
    given, receives the counts of turn ends, of Stop-hook blocks and of turn ends after a block,
    and the longest silence left unflagged with its verdict. `end`, an ISO time, closes the last
    silence there, for a window cut out of a longer stream.
    """
    if end is not None:
        events = list(events) + [dict(t=end, k='end')]
    out, seen, window, last = [], {}, [], None
    shortest = min(STALL_S, PROMPT_S)
    st = stats if stats is not None else {}
    st.update(end_turns=0, hook_blocks=0, ends_after_block=0, longest_unflagged=None)
    blocked, prev_end = False, None
    for e in events:
        t = epoch(e['t'])
        if e['k'] == 'input' and e.get('feedback'):
            st['hook_blocks'] += 1
            blocked = True
        if e['k'] == 'assistant' and e['stop'] == 'end_turn' and e['mid'] != prev_end:
            st['end_turns'] += 1
            st['ends_after_block'] += blocked
            blocked, prev_end = False, e['mid']
        if window and last is not None and t - last >= shortest:
            v = classify(window, t - 0.001, goal=goal)
            if v['kind'] == 'none' and (st['longest_unflagged'] is None or t - last > st['longest_unflagged'][0]):
                st['longest_unflagged'] = (round(t - last, 1), iso(last), v['detail'])
            if v['kind'] != 'none':
                key = (v['kind'], v['anchor'])
                if key not in seen:
                    seen[key] = dict(v, flagged=iso(epoch(v['since']) + v['needed']), ended=e['t'])
                    out.append(seen[key])
                else:
                    seen[key]['ended'] = e['t']
        if e['k'] == 'assistant' and window and not any(
                x['k'] == 'assistant' and x['mid'] == e['mid'] for x in window):
            # The classifier reads only the last message's records and what follows them, plus the
            # goal state, so the window restarts at each new message.
            goal = goal_active(window, goal)
            window = []
        window.append(e)
        last = max(last or t, t)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    for name in ('poll', 'run'):
        p = sub.add_parser(name)
        p.add_argument('--wake', action='store_true')
        p.add_argument('--notify', action='store_true')
        p.add_argument('--notifier', help='session ID of an existing notifier session')
        p.add_argument('--root', default=None)
        if name == 'run':
            p.add_argument('--interval', type=float, default=45)
    p = sub.add_parser('replay')
    p.add_argument('transcript')
    p.add_argument('--out')
    p = sub.add_parser('extract')
    p.add_argument('--window', nargs=4, action='append', required=True,
                   metavar=('TRANSCRIPT', 'FROM', 'TO', 'OUT'),
                   help='slim events of TRANSCRIPT between the times FROM and TO, written to OUT; '
                        'repeat for more windows (each transcript is read once)')
    a = ap.parse_args(argv)
    if a.cmd == 'replay':
        t0 = time.time()
        size = os.path.getsize(a.transcript)
        stats = {}
        found = replay(stream(a.transcript), stats=stats)
        print(f'{a.transcript}: {size / 1e6:.0f} MB read in {time.time() - t0:.1f} s; {len(found)} detections')
        print('counts:', json.dumps(stats))
        for v in found:
            print(v['kind'], 'since', v['since'], 'flagged', v['flagged'], 'ended', v['ended'], v['detail'][:100])
        if a.out:
            Path(a.out).write_text(json.dumps(dict(transcript=a.transcript, counts=stats, detections=found), indent=1))
        return 0
    if a.cmd == 'extract':
        by_file = {}
        for path, start, end, out in a.window:
            by_file.setdefault(path, []).append((start, end, out))
        for path, windows in by_file.items():
            files = {out: open(out, 'w') for _, _, out in windows}
            counts = dict.fromkeys(files, 0)
            for e in stream(path):
                for start, end, out in windows:
                    if start <= e['t'] <= end:
                        files[out].write(json.dumps(e) + '\n')
                        counts[out] += 1
            for out, f in files.items():
                f.close()
                print(f'{counts[out]} events written to {out}')
        return 0
    root = a.root or main_checkout()
    notifier = None
    if a.notifier:
        s = next((s for s in list_sessions() if s.get('sessionId') == a.notifier or s.get('id') == a.notifier), None)
        if not s:
            print(f'notifier {a.notifier} is not listed by claude agents', file=sys.stderr)
            return 2
        notifier = dict(id=s.get('id'), sessionId=s.get('sessionId'), cwd=s.get('cwd'))
    w = Watchdog(root, wake=a.wake, notify=a.notify, notifier=notifier)
    while True:
        t0 = time.time()
        try:
            verdicts = w.poll()
        except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired) as error:
            w.log(event='poll-error', error=str(error)[:300])
            verdicts = []
        if a.cmd == 'poll':
            for v in verdicts:
                print(v['session'], v['name'], 'alive' if v['alive'] else 'retired', v['kind'], v['detail'][:110])
            print(f'poll took {time.time() - t0:.2f} s over {len(verdicts)} sessions')
            return 0
        time.sleep(max(1, a.interval - (time.time() - t0)))


if __name__ == '__main__':
    sys.exit(main())
