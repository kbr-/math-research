"""Tests of tools/session_watchdog.py: the classifier on slim windows of two real transcripts, its
boundaries, goal scanning, tail reading, the wake and alert decisions, and mutants of the classifier.

The fixtures under fixtures/session_watchdog/ are slim events (types, times, ids, tool names and
bounds, no content) cut by `session_watchdog.py extract` from the Common multiplier (354c41d4) and
Talagrand (c0de408b) transcripts of 16 and 17 October 2026.
"""
import importlib.machinery
import importlib.util
import json
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parent.parent
FIX = Path(__file__).resolve().parent / 'fixtures' / 'session_watchdog'
SOURCE = (TOOLS / 'session_watchdog.py').read_text()


def load(source=SOURCE, name='session_watchdog'):
    mod = types.ModuleType(name)
    mod.__file__ = str(TOOLS / 'session_watchdog.py')
    exec(compile(source, mod.__file__, 'exec'), mod.__dict__)
    return mod


sw = load()


def fixture(name):
    return [json.loads(line) for line in (FIX / name).read_text().splitlines()]


# Window ends, as cut by the extraction, and the detections each window must give.
WINDOWS = {
    'multiplier-stall.jsonl': ('2026-10-17T08:20:00Z', [('stall', '2026-10-17T08:12:07.855Z')]),
    'talagrand-stall.jsonl': ('2026-10-17T07:14:00Z', [('stall', '2026-10-17T06:49:07.737Z')]),
    'talagrand-permission-1.jsonl': ('2026-10-16T23:01:00Z', [('permission_wait', '2026-10-16T21:25:07.711Z')]),
    'talagrand-permission-2.jsonl': ('2026-10-17T03:28:00Z', [('permission_wait', '2026-10-17T02:39:36.304Z')]),
    # The longest silences the full replays left unflagged: 433 s and 642 s with every call answered.
    'multiplier-long-silence.jsonl': ('2026-10-17T05:50:00Z', []),
    'talagrand-long-silence.jsonl': ('2026-10-16T18:32:00Z', []),
}


def ev(t, k, **kw):
    return dict(t=t, k=k, **kw)


def asst(t, stop, mid='m1', tools=(), uuid=None):
    return ev(t, 'assistant', stop=stop, mid=mid, uuid=uuid or mid + t, tools=list(tools))


def bash(i, timeout=None, background=False, mod=sw):
    inputs = {'command': 'x'}
    if timeout is not None:
        inputs['timeout'] = timeout
    if background:
        inputs['run_in_background'] = True
    return dict(id=i, name='Bash', bound=mod.tool_bound('Bash', inputs))


T0 = '2026-10-17T08:00:00.000Z'


def at(seconds):
    return sw.epoch(T0) + seconds


def expectations(mod):
    """Failures of `mod` against every behaviour the watchdog promises; empty for a correct module."""
    bad = []
    for name, (end, want) in WINDOWS.items():
        got = [(v['kind'], v['since']) for v in mod.replay(fixture(name), goal=True, end=end)]
        if got != want:
            bad.append(f'{name}: {got} != {want}')
    stall = [asst(T0, 'end_turn')]
    cases = [
        ('stall at 5 min', mod.classify(stall, at(300), goal=True)['kind'], 'stall'),
        ('no stall at 4 min', mod.classify(stall, at(240), goal=True)['kind'], 'none'),
        ('no stall without goal', mod.classify(stall, at(900), goal=False)['kind'], 'none'),
        ('no stall after goal cleared', mod.classify(
            [ev('2026-10-17T07:00:00Z', 'goal', active=False, source='command')] + stall, at(900), goal=True)['kind'], 'none'),
        ('stall from goal set in window', mod.classify(
            [ev('2026-10-17T07:00:00Z', 'goal', active=True, source='command')] + stall, at(900))['kind'], 'stall'),
        ('no stall with a task in flight', mod.classify(stall, at(900), in_flight=1, goal=True)['kind'], 'none'),
        ('no stall after a stop hook', mod.classify(stall + [ev(T0, 'hook')], at(900), goal=True)['kind'], 'none'),
        ('no stall after turn_duration', mod.classify(stall + [ev(T0, 'duration')], at(900), goal=True)['kind'], 'none'),
        ('no stall after input', mod.classify(stall + [ev(T0, 'input', watchdog=False, feedback=False)], at(900),
                                              goal=True)['kind'], 'none'),
        ('no stall after goal evaluation', mod.classify(stall + [ev(T0, 'goal', active=True, source='status')], at(900),
                                                        goal=True)['kind'], 'none'),
    ]
    pend = lambda tool, s: mod.classify([asst(T0, 'tool_use', tools=[tool])], at(s), goal=True)['kind']
    cases += [
        ('default Bash waits at 5 min', pend(bash('a'), 300), 'permission_wait'),
        ('default Bash not at 4 min', pend(bash('a'), 240), 'none'),
        ('long Bash timeout is running at 650 s', pend(bash('a', 600000, mod=mod), 650), 'none'),
        ('long Bash timeout waits at 730 s', pend(bash('a', 600000, mod=mod), 730), 'permission_wait'),
        ('background Bash waits at 5 min', pend(bash('a', 600000, True, mod=mod), 300), 'permission_wait'),
        ('foreground Agent is a long call', pend(dict(id='a', name='Agent', bound=mod.tool_bound('Agent', {})), 7200),
         'none'),
        ('background Agent waits', pend(dict(id='a', name='Agent', bound=mod.tool_bound(
            'Agent', {'run_in_background': True})), 600), 'permission_wait'),
        ('question waits', pend(dict(id='a', name='AskUserQuestion', bound=300), 300), 'question_wait'),
        ('answered call is no wait', mod.classify([asst(T0, 'tool_use', tools=[bash('a')]), ev(T0, 'result', ids=['a'])],
                                                  at(900), goal=True)['kind'], 'none'),
        ('one of two parallel calls pending', mod.classify(
            [asst(T0, 'tool_use', tools=[bash('a')]), asst(T0, 'tool_use', tools=[bash('b')]),
             ev(T0, 'result', ids=['a'])], at(900), goal=True)['anchor'], 'b'),
        ('pending call with a task in flight', mod.classify([asst(T0, 'tool_use', tools=[bash('a')])], at(900),
                                                            in_flight=2, goal=True)['kind'], 'none'),
    ]
    side = dict(type='assistant', isSidechain=True, timestamp='2026-10-17T08:01:00Z',
                message=dict(id='s', stop_reason='tool_use', content=[]))
    cases += [('sidechain records ignored', mod.slim(side), None),
              ('goal_status read', mod.slim(dict(type='attachment', timestamp=T0,
                                                 attachment=dict(type='goal_status', met=False)))['active'], True),
              ('goal met read', mod.slim(dict(type='attachment', timestamp=T0,
                                              attachment=dict(type='goal_status', met=True)))['active'], False),
              ('goal cleared read', mod.slim(dict(type='system', subtype='local_command', timestamp=T0,
                                                  content='<local-command-stdout>Goal cleared: x</local-command-stdout>'))['active'], False)]
    bad += [f'{name}: {got!r} != {want!r}' for name, got, want in cases if got != want]
    return bad


class Classifier(unittest.TestCase):
    def test_expectations(self):
        self.assertEqual(expectations(sw), [])

    def test_flag_times(self):
        found = sw.replay(fixture('multiplier-stall.jsonl'), goal=True, end='2026-10-17T08:20:00Z')
        self.assertEqual(found[0]['flagged'], '2026-10-17T08:17:07.855Z')
        found = sw.replay(fixture('talagrand-permission-1.jsonl'), goal=True, end='2026-10-16T23:01:00Z')
        self.assertEqual(found[0]['flagged'], '2026-10-16T21:30:07.711Z')
        self.assertEqual(found[0]['ended'], '2026-10-16T22:59:50.221Z')

    def test_replay_counts_blocks(self):
        stats = {}
        sw.replay(fixture('talagrand-stall.jsonl'), goal=True, stats=stats, end='2026-10-17T07:14:00Z')
        self.assertEqual(stats['hook_blocks'], 2)
        self.assertGreaterEqual(stats['ends_after_block'], 1)


class Mutants(unittest.TestCase):
    """Each mutant breaks one promise, and the expectations must catch it."""
    MUTANTS = [
        ("closing = [e for e in after if e['k'] in ('hook', 'duration', 'input', 'goal')]",
         "closing = [e for e in after if e['k'] in ('duration', 'input', 'goal')]"),
        ("closing = [e for e in after if e['k'] in ('hook', 'duration', 'input', 'goal')]",
         "closing = [e for e in after if e['k'] in ('hook', 'input', 'goal')]"),
        ("closing = [e for e in after if e['k'] in ('hook', 'duration', 'input', 'goal')]",
         "closing = [e for e in after if e['k'] in ('hook', 'duration', 'goal')]"),
        ("closing = [e for e in after if e['k'] in ('hook', 'duration', 'input', 'goal')]",
         "closing = [e for e in after if e['k'] in ('hook', 'duration', 'input')]"),
        ("        if not goal_active(events, goal):\n            return dict(none, detail='no active goal')",
         "        if False:\n            return dict(none, detail='no active goal')"),
        ("        if in_flight:\n            return dict(none, detail=f'{in_flight} tasks in flight')\n        if not goal",
         "        if False:\n            return dict(none, detail=f'{in_flight} tasks in flight')\n        if not goal"),
        ("STALL_S = 300", "STALL_S = 200"),
        ("PROMPT_S = 300", "PROMPT_S = 200"),
        ("max(PROMPT_S, tool['bound'] + BOUND_GRACE_S)", "max(PROMPT_S, tool['bound'])"),
        ("QUESTION_TOOLS = {'AskUserQuestion', 'ExitPlanMode'}", "QUESTION_TOOLS = set()"),
        ("UNBOUNDED_TOOLS = {'Agent', 'Task'}", "UNBOUNDED_TOOLS = set()"),
        ("if not isinstance(record, dict) or record.get('isSidechain') or not record.get('timestamp'):",
         "if not isinstance(record, dict) or not record.get('timestamp'):"),
        ("        if inputs.get('run_in_background'):\n            return 60",
         "        if False:\n            return 60"),
        ("    pending = [(t, tool) for t, tool in tools if tool['id'] not in answered]",
         "    pending = [(t, tool) for t, tool in tools[:1] if tool['id'] not in answered]"),
        ("    if a['stop'] == 'end_turn':\n        if closing:",
         "    if a['stop'] == 'end_turn':\n        if closing and False:"),
        ("            return dict(t=t, k='goal', active=not a.get('met'), source='status')",
         "            return dict(t=t, k='goal', active=True, source='status')"),
        ("    if body.startswith('Goal cleared') or body.startswith('No goal set'):\n        return False",
         "    if body.startswith('No goal set'):\n        return False"),
    ]

    def test_each_mutant_is_caught(self):
        for old, new in self.MUTANTS:
            with self.subTest(mutant=new[:70]):
                self.assertEqual(SOURCE.count(old), 1, old)
                try:
                    failures = expectations(load(SOURCE.replace(old, new), 'mutant'))
                except Exception as error:  # a crash on a promised case catches the mutant too
                    failures = [repr(error)]
                self.assertNotEqual(failures, [])


class Reading(unittest.TestCase):
    def write(self, records):
        f = tempfile.NamedTemporaryFile('w', suffix='.jsonl', delete=False)
        for r in records:
            f.write((r if isinstance(r, str) else json.dumps(r, separators=(',', ':'))) + '\n')
        f.close()
        self.addCleanup(Path(f.name).unlink)
        return f.name

    def test_scan_goal_takes_the_last_record_and_ignores_quoted_markers(self):
        quoted = dict(type='user', timestamp=T0, message=dict(content=[dict(
            type='tool_result', tool_use_id='q', content='{"type":"goal_status","met":true}')]))
        path = self.write([
            dict(type='system', subtype='local_command', timestamp=T0,
                 content='<local-command-stdout>Goal set: Spin</local-command-stdout>'),
            dict(type='attachment', timestamp=T0, attachment=dict(type='goal_status', met=False)),
            dict(type='system', subtype='local_command', timestamp=T0,
                 content='<local-command-stdout>Set model to haiku</local-command-stdout>'),
            quoted])
        self.assertIs(sw.scan_goal(path), True)
        self.assertIs(sw.scan_goal(path, chunk=40), True)
        path = self.write([dict(type='attachment', timestamp=T0, attachment=dict(type='goal_status', met=False)),
                           dict(type='system', subtype='local_command', timestamp=T0,
                                content='<local-command-stdout>Goal cleared: Spin</local-command-stdout>')])
        self.assertIs(sw.scan_goal(path), False)
        self.assertIsNone(sw.scan_goal(self.write([quoted])))

    def test_scan_goal_bounds(self):
        first = json.dumps(dict(type='attachment', timestamp=T0, attachment=dict(type='goal_status', met=False)),
                           separators=(',', ':'))
        path = self.write([first, dict(type='attachment', timestamp=T0,
                                       attachment=dict(type='goal_status', met=True))])
        self.assertIs(sw.scan_goal(path, 0, len(first) + 1), True)
        self.assertIs(sw.scan_goal(path, len(first) + 1), False)

    def test_read_tail_grows_until_an_assistant_record(self):
        filler = [dict(type='attachment', timestamp=T0, attachment=dict(type='x', pad='p' * 1000))] * 300
        path = self.write([dict(type='assistant', timestamp=T0, uuid='u',
                                message=dict(id='m', stop_reason='end_turn', content=[]))] + filler)
        events, off = sw.read_tail(path, start=4096)
        self.assertEqual(events[0]['k'], 'assistant')
        self.assertEqual(off, 0)


class Service(unittest.TestCase):
    def test_notice_when_down_unless_stopped_by_the_user(self):
        runtime = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: __import__('shutil').rmtree(runtime))
        self.assertIsNone(sw.service_notice(runtime, active=True))
        notice = sw.service_notice(runtime, active=False)
        self.assertIn('run python3 resource-controls/setup.py from the repository root, without asking', notice)
        (runtime / sw.STOPPED_FILE).write_text('2026-10-17 13:40\n')
        self.assertIsNone(sw.service_notice(runtime, active=False))

    def test_setup_unit_text(self):
        spec = importlib.util.spec_from_file_location('rc_setup', TOOLS.parent / 'resource-controls' / 'setup.py')
        setup = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(setup)
        self.assertEqual((setup.SESSION_UNIT, setup.STOPPED_FILE), (sw.SESSION_UNIT, sw.STOPPED_FILE))
        spec = importlib.util.spec_from_loader('compute_cli', importlib.machinery.SourceFileLoader(
            'compute_cli', str(TOOLS.parent / 'compute.sh')))
        compute = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(compute)
        self.assertEqual((compute.SESSION_WATCHDOG, compute.SESSION_WATCHDOG_STOPPED),
                         (setup.SESSION_UNIT, setup.STOPPED_FILE))
        text = setup.session_watchdog_unit(Path('/repo'), '/home/u/.local/bin/claude', ['notify', 'wake'])
        self.assertIn('/repo/tools/session_watchdog.py" run --interval 45 --notify --wake\n', text)
        self.assertIn('PATH=/home/u/.local/bin:', text)
        self.assertIn('\nWorkingDirectory=/repo\n', text)  # systemd rejects a quoted path here
        with self.assertRaises(RuntimeError):
            setup.session_watchdog_unit(Path('/my repo'), '/c/claude', [])

    def test_setup_starts_by_default_and_respects_a_stop(self):
        spec = importlib.util.spec_from_file_location('rc_setup2', TOOLS.parent / 'resource-controls' / 'setup.py')
        setup = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(setup)
        build = Path(tempfile.mkdtemp()) / '.resource-runtime'
        build.mkdir()
        self.addCleanup(lambda: __import__('shutil').rmtree(build.parent))
        calls = []

        def fake_run(*args, capture=False):
            calls.append(args)
            return types.SimpleNamespace(stdout='ActiveState=active\n')
        with mock.patch.object(setup, 'run', fake_run), \
                mock.patch.object(setup.shutil, 'which', return_value='/u/bin/claude'):
            setup.install_session_watchdog(build)
            self.assertIn(('systemctl', '--user', 'restart', setup.SESSION_UNIT), calls)
            self.assertIn('--notify --wake', (build / setup.SESSION_UNIT).read_text())
            calls.clear()
            setup.install_session_watchdog(build, stop=True)
            self.assertTrue((build / setup.STOPPED_FILE).exists())
            calls.clear()
            setup.install_session_watchdog(build)
            self.assertNotIn(('systemctl', '--user', 'restart', setup.SESSION_UNIT), calls)
            setup.install_session_watchdog(build, actions=[], start=True)
            self.assertFalse((build / setup.STOPPED_FILE).exists())
            self.assertIn(('systemctl', '--user', 'restart', setup.SESSION_UNIT), calls)
            self.assertIn('run --interval 45\n', (build / setup.SESSION_UNIT).read_text())
            setup.install_session_watchdog(build)
            self.assertIn('run --interval 45\n', (build / setup.SESSION_UNIT).read_text())

    def test_systemd_accepts_the_unit(self):
        """The unit text is read by systemd's own verifier, not only matched as text (a quoted
        WorkingDirectory= passed the text checks and made systemd reject the unit)."""
        import shutil
        import subprocess
        if not shutil.which('systemd-analyze'):
            self.skipTest('systemd-analyze not installed')
        spec = importlib.util.spec_from_file_location('rc_setup', TOOLS.parent / 'resource-controls' / 'setup.py')
        setup = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(setup)
        d = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: shutil.rmtree(d))
        unit = d / setup.SESSION_UNIT
        unit.write_text(setup.session_watchdog_unit(TOOLS.parent, shutil.which('true'), ['notify']))
        out = subprocess.run(['systemd-analyze', '--user', 'verify', str(unit)], capture_output=True, text=True,
                             timeout=20)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn('run --interval 45\n', setup.session_watchdog_unit(Path('/repo'), '/c/claude', []))


class Actions(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: __import__('shutil').rmtree(self.root))
        self.clock = [at(1000)]
        with mock.patch.object(sw, 'git_common', return_value='/repo/.git'):
            self.w = sw.Watchdog(self.root, wake=True, notify=False, now=lambda: self.clock[0])
        self.s = dict(id='abc', sessionId='abc-1', name='S', pid=7, kind='background', cwd='/repo')
        self.v = dict(kind='stall', since=T0, anchor='u1', detail='', needed=300)

    def logged(self):
        return [json.loads(line) for f in sorted((self.root / 'research/logs/session-watchdog').glob('*.jsonl'))
                for line in f.read_text().splitlines()]

    def test_poll_logs_changes_and_keeps_a_heartbeat(self):
        with mock.patch.object(sw, 'list_sessions', return_value=[]):
            self.w.poll()
            self.clock[0] += 45
            self.w.poll()
        self.assertEqual([e['event'] for e in self.logged()], ['poll'])
        self.assertEqual(self.w.state['last_poll'], sw.iso(self.clock[0]))

    def test_wakes_once_then_alerts(self):
        with mock.patch.object(sw, 'wake_session', return_value=(True, 'ok')) as wake:
            self.w.act(self.s, self.v, [])
            self.w.act(self.s, self.v, [])
        self.assertEqual(wake.call_count, 1)
        alerts = [e for e in self.logged() if e['event'] == 'alert']
        self.assertEqual(len(alerts), 1)
        self.assertIn('stalled again without progress', alerts[0]['message'])

    def test_new_stall_after_work_is_woken(self):
        with mock.patch.object(sw, 'wake_session', return_value=(True, 'ok')) as wake:
            self.w.act(self.s, self.v, [])
            self.clock[0] += 600
            later = sw.iso(self.clock[0] - 100)
            self.w.act(self.s, dict(self.v, anchor='u2'), [ev(later, 'result', ids=['x'])])
        self.assertEqual(wake.call_count, 2)

    def test_no_wake_without_live_process_or_without_flag(self):
        with mock.patch.object(sw, 'wake_session', return_value=(True, 'ok')) as wake:
            self.w.act(dict(self.s, pid=None), self.v, [])
            self.w.do_wake = False
            self.w.act(dict(self.s, sessionId='other'), self.v, [])
        wake.assert_not_called()
        self.assertEqual([e['wake'] for e in self.logged() if e['event'] == 'detected'], [False, False])

    def test_failed_wake_alerts_and_unseen_prompt_fails_its_check(self):
        with mock.patch.object(sw, 'wake_session', return_value=(False, 'claude stop: no such session')):
            self.w.act(self.s, self.v, [])
        self.assertTrue(any(e['event'] == 'alert' and 'failed' in e['message'] for e in self.logged()))
        w = self.w.state['wakes']['abc-1']
        self.assertIs(w['verified'], False)
        self.w.state['wakes']['abc-1'] = dict(at=self.clock[0], anchor='u1', ok=True, verified=None)
        self.clock[0] += sw.WAKE_CHECK_S + 1
        self.w.check_wake(self.s, [])
        self.assertIs(self.w.state['wakes']['abc-1']['verified'], False)
        self.w.state['wakes']['abc-1'] = dict(at=self.clock[0], anchor='u1', ok=True, verified=None)
        self.w.check_wake(self.s, [ev(sw.iso(self.clock[0] + 2), 'input', watchdog=True, feedback=False)])
        self.assertIs(self.w.state['wakes']['abc-1']['verified'], True)

    def test_alert_retried_until_requested(self):
        self.w.do_notify = True
        with mock.patch.object(self.w, 'push', return_value=(True, 'woken')) as push:
            self.w.alert(self.s, 'm', ('permission_wait', 'a'))
            key = self.w.state['pending_push']['key']
            with mock.patch.object(sw, 'push_result', return_value='Not sent — this terminal is active'), \
                    mock.patch.object(sw.glob, 'glob', return_value=['t']):
                self.w.state['notifier'] = dict(sessionId='n')
                self.w.read_notifier()
            self.assertFalse(self.w.state['alerts'][key]['delivered'])
            self.w.alert(self.s, 'm', ('permission_wait', 'a'))
            self.assertEqual(push.call_count, 1)
            self.clock[0] += sw.RETRY_S
            self.w.alert(self.s, 'm', ('permission_wait', 'a'))
            self.assertEqual(push.call_count, 2)
            with mock.patch.object(sw, 'push_result', return_value='Terminal notification sent. Mobile push requested.'), \
                    mock.patch.object(sw.glob, 'glob', return_value=['t']):
                self.w.read_notifier()
            self.assertTrue(self.w.state['alerts'][key]['delivered'])
            self.clock[0] += sw.RETRY_S
            self.w.alert(self.s, 'm', ('permission_wait', 'a'))
            self.assertEqual(push.call_count, 2)


if __name__ == '__main__':
    unittest.main()
