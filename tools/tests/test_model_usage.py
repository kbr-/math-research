"""tools/model_usage.py on transcripts shaped as Claude Code and Codex write them (their record types and
fields as read on this machine, 17 October 2026), with expected figures worked out by hand."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import model_usage as mu

T = 1792200000.0          # the cycle's start
END = T + 60              # its stop
OAUTH = ['claude-code-20250219', 'oauth-2025-04-20']


def at(seconds):
    return mu.iso(T + seconds)


def write(path, lines):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(''.join(json.dumps(line) + '\n' for line in lines))


def request(seconds, effort, betas=OAUTH):
    return {'type': 'api-request', 'timestamp': at(seconds),
            'params': {'model': 'claude-opus-5-5', 'betas': betas, 'output_config': {'effort': effort}}}


def message(seconds, ident, model, usage):
    return {'parentUuid': 'x', 'type': 'assistant', 'timestamp': at(seconds),
            'message': {'id': ident, 'model': model, 'usage': usage}}


def journal(agent):
    return [{'event': 'start', 'unix_s': T, 'agent': agent, 'model': 'm'}, {'event': 'stop', 'unix_s': END}]


class Fixture(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)
        self.root, self.logs = self.dir / 'repo', self.dir / 'usage-logs'
        self.root.mkdir()
        self.prices = mu.load_prices()


class ClaudeCycleTest(Fixture):
    S, OTHER, KEYED = 'session-s', 'session-o', 'session-k'

    def build(self):
        projects = self.dir / 'claude' / 'projects' / 'project'
        opus = 'claude-opus-5-5'
        first = message(10, 'm1', opus, {'input_tokens': 10, 'cache_creation_input_tokens': 1000,
                                         'cache_creation': {'ephemeral_1h_input_tokens': 1000,
                                                            'ephemeral_5m_input_tokens': 0},
                                         'cache_read_input_tokens': 100000, 'output_tokens': 500})
        write(projects / f'{self.S}.jsonl', [
            request(-2000, 'high'),
            # filler: the file outgrows one search block, so the request above is found by searching back
            *({'type': 'progress', 'timestamp': at(-1990 + i), 'pad': 'x' * 300} for i in range(400)),
            message(-10, 'm0', opus, {'input_tokens': 999999, 'output_tokens': 999999}),   # before the start
            first, first,                                                                   # one message, two records
            request(20, 'medium'),
            message(30, 'm2', 'claude-haiku-4-5-20251001', {'input_tokens': 2000, 'cache_creation_input_tokens': 400,
                                                             'cache_read_input_tokens': 0, 'output_tokens': 100}),
            message(40, 'm3', 'mystery-model', {'input_tokens': 5, 'output_tokens': 5}),
            # a record that states its effort (as every assistant record does now) is taken at its word
            {**message(50, 'm4', opus, {'input_tokens': 0, 'cache_read_input_tokens': 1000000, 'output_tokens': 0,
                                        'speed': 'fast'}), 'effort': 'xhigh'},
            message(60 + mu.LATE_S + 5, 'm5', opus, {'input_tokens': 999999, 'output_tokens': 0}),  # after the stop
        ])
        write(projects / self.S / 'subagents' / 'agent-1.jsonl', [
            request(55, 'low'), message(58, 's1', opus, {'input_tokens': 100, 'output_tokens': 100})])
        write(projects / f'{self.OTHER}.jsonl', [
            request(1, 'medium'), message(20, 'o1', opus, {'input_tokens': 0, 'cache_read_input_tokens': 4000000,
                                                           'output_tokens': 0})])
        # a fork of the other session copies its message under the same id: counted once on the machine
        write(projects / 'session-fork.jsonl', [
            request(2, 'medium'), message(20, 'o1', opus, {'input_tokens': 0, 'cache_read_input_tokens': 4000000,
                                                           'output_tokens': 0})])
        write(projects / f'{self.KEYED}.jsonl', [
            request(1, 'medium', betas=['claude-code-20250219']),
            message(20, 'k1', opus, {'input_tokens': 50000000, 'output_tokens': 0})])
        write(self.root / 'research' / 'logs' / 'model-usage.jsonl', [
            {'at': at(45), 'session': self.S, 'models': {'claude-haiku-4-5-20251001': {}},
             'usage': {'input_tokens': 9, 'cache_creation_input_tokens': 6985, 'cache_read_input_tokens': 0,
                       'output_tokens': 71, 'cache_creation': {'ephemeral_1h_input_tokens': 6985,
                                                               'ephemeral_5m_input_tokens': 0}}},
            {'at': at(46), 'session': self.OTHER, 'models': {'claude-haiku-4-5-20251001': {}},
             'usage': {'input_tokens': 1000, 'output_tokens': 0}},
            {'at': at(400), 'session': self.S, 'models': {'claude-haiku-4-5-20251001': {}},
             'usage': {'input_tokens': 999999, 'output_tokens': 0}},                       # after the stop
        ])
        write(self.logs / 'claude.jsonl', [
            {'at': '2026-10-17T00:00:00+00:00', 'week': 40, 'week_resets_at': 1792500000},  # long before the start
            {'at': mu.datetime.fromtimestamp(END - 30, mu.timezone.utc).isoformat(), 'week': 43,
             'week_resets_at': 1792500000},
            {'at': mu.datetime.fromtimestamp(END - 20, mu.timezone.utc).isoformat(), 'week': 42,
             'week_resets_at': 1792500000},                                                  # an idle session's stale value
        ])
        (self.logs / 'plans.json').write_text(json.dumps({'claude': {'plan': 'Max 20x', 'usd_per_month': 200}}))
        return self.dir / 'claude'

    def run_cycle(self, env=None):
        home = self.build()
        env = {'CLAUDE_CODE_SESSION_ID': self.S, 'USAGE_LOG_DIR': str(self.logs)} if env is None else env
        return mu.cycle(journal('Claude Code'), root=self.root, env=env, prices=self.prices, claude=home)

    def test_tokens_and_costs_by_model_and_effort(self):
        use = self.run_cycle()
        rows = {(row['model'], row['effort']): row for row in use['rows']}
        # m1 at the effort of the request before the window: 10*4 + 1000*8 + 100000*0.2 + 500*20 per million.
        self.assertAlmostEqual(rows['claude-opus-5-5', 'high']['usd'], 0.03804)
        self.assertEqual(rows['claude-opus-5-5', 'high']['tokens']['cache_write_1h'], 1000)
        # m4, at the effort its record states, in fast mode, which doubles the cache read's 0.20: 1e6 * 0.4.
        self.assertAlmostEqual(rows['claude-opus-5-5', 'xhigh']['usd'], 0.4)
        # m2: 2000*1 + 400*1.25 + 100*5, its cache writes unsplit and so at the API's default 5-minute price.
        self.assertAlmostEqual(rows['claude-haiku-4-5-20251001', 'medium']['usd'], 0.003)
        self.assertEqual(rows['mystery-model', 'medium']['unpriced_tokens'], 10)
        self.assertEqual(use['unpriced_models'], ['mystery-model'])
        # the subagent's message at its own request's effort: 100*4 + 100*20.
        self.assertAlmostEqual(rows['claude-opus-5-5', 'low']['usd'], 0.0024)
        # the session's judge call, priced as Claude Code priced it (total_cost_usd 0.014334).
        self.assertAlmostEqual(rows['claude-haiku-4-5-20251001', 'judge']['usd'], 0.014334)
        self.assertAlmostEqual(use['usd'], 0.457774)
        self.assertEqual(use['billing'], 'plan')

    def test_share_of_the_weekly_limit(self):
        limit = self.run_cycle()['limit']
        # 40 at the start, 43 at the stop (the stale 42 ignored); the machine's plan use is this session's
        # 0.457774 plus the other session's 0.8 and its judge's 0.001; the API-key session's is not counted.
        self.assertEqual(limit['moved_percent'], 3.0)
        self.assertAlmostEqual(limit['fraction_of_machine_use'], 0.457774 / 1.258774, places=6)
        self.assertAlmostEqual(limit['share_percent'], 3 * 0.457774 / 1.258774, places=4)
        self.assertAlmostEqual(limit['usd'], 3 * 0.457774 / 1.258774 / 100 * 200 * 12 / 52, places=4)
        self.assertEqual(limit['plan'], 'Max 20x')
        self.assertNotIn('note', limit)

    def test_an_unreadable_transcript_of_another_session_is_left_out(self):
        home = self.build()
        locked = home / 'projects' / 'project' / 'session-locked.jsonl'
        write(locked, [message(20, 'x1', 'claude-opus-5-5', {'input_tokens': 1, 'output_tokens': 1})])
        locked.chmod(0)
        self.addCleanup(locked.chmod, 0o600)
        use = mu.cycle(journal('Claude Code'), root=self.root, prices=self.prices, claude=home,
                       env={'CLAUDE_CODE_SESSION_ID': self.S, 'USAGE_LOG_DIR': str(self.logs)})
        self.assertAlmostEqual(use['usd'], 0.457774)
        self.assertNotIn('unread_files', use)
        mine = home / 'projects' / 'project' / self.S / 'subagents' / 'agent-1.jsonl'
        mine.chmod(0)
        self.addCleanup(mine.chmod, 0o600)
        use = mu.cycle(journal('Claude Code'), root=self.root, prices=self.prices, claude=home,
                       env={'CLAUDE_CODE_SESSION_ID': self.S, 'USAGE_LOG_DIR': str(self.logs)})
        self.assertEqual(use['unread_files'], 1)   # its own unreadable subagent file is counted, not hidden

    def test_unmeasured_causes_are_named(self):
        self.assertIn('CLAUDE_CODE_SESSION_ID is not set', self.run_cycle(env={})['reason'])
        self.assertIn('no transcript', self.run_cycle(env={'CLAUDE_CODE_SESSION_ID': 'absent'})['reason'])
        other = mu.cycle(journal('Some agent'), root=self.root, env={}, prices=self.prices)
        self.assertFalse(other['measured'])
        self.assertIn('USAGE_LOG_DIR is not set',
                      self.run_cycle(env={'CLAUDE_CODE_SESSION_ID': self.S})['limit']['reason'])

    def test_an_api_key_session_is_billed_at_api_prices(self):
        self.build()
        use = mu.cycle(journal('Claude Code'), root=self.root, prices=self.prices, claude=self.dir / 'claude',
                       env={'CLAUDE_CODE_SESSION_ID': self.KEYED, 'USAGE_LOG_DIR': str(self.logs)})
        self.assertEqual(use['billing'], 'API key')
        self.assertFalse(use['limit']['measured'])
        self.assertEqual(mu.note_text(use), 'Model use billed to an API key at $200.00.')

    def test_a_session_without_request_records_uses_its_environment(self):
        # An interactive Claude Code session writes no api-request records (checked on this machine, 17 October
        # 2026): its effort is the session's setting and its billing is told by an API key in its environment.
        self.build()
        projects = self.dir / 'claude' / 'projects' / 'project'
        write(projects / 'session-i.jsonl', [message(20, 'i1', 'claude-opus-5-5', {'input_tokens': 1000,
                                                                                    'output_tokens': 0})])
        write(projects / 'session-j.jsonl', [message(20, 'j1', 'claude-opus-5-5', {'input_tokens': 1000,
                                                                                    'output_tokens': 0})])
        env = {'CLAUDE_CODE_SESSION_ID': 'session-i', 'USAGE_LOG_DIR': str(self.logs), 'CLAUDE_EFFORT': 'medium'}
        use = mu.cycle(journal('Claude Code'), root=self.root, env=env, prices=self.prices, claude=self.dir / 'claude')
        self.assertEqual([(row['model'], row['effort']) for row in use['rows']],
                         [('claude-opus-5-5', 'medium (session setting)')])
        self.assertEqual(use['billing'], 'plan')
        # another session without request records counts as plan use: 0.004 of S's 0.44344, the other
        # session's 0.8, the judges' 0.015334 and these two sessions' 0.004 each.
        self.assertAlmostEqual(use['limit']['fraction_of_machine_use'], 0.004 / 1.266774, places=6)
        for name in mu.API_BILLING:
            keyed = mu.cycle(journal('Claude Code'), root=self.root, env={**env, name: '1'},
                             prices=self.prices, claude=self.dir / 'claude')
            self.assertEqual(keyed['billing'], 'API key', name)

    def test_table_and_note(self):
        use = self.run_cycle()
        table = mu.table_html(use)
        self.assertIn('<caption>Model use (tokens)</caption>', table)
        self.assertIn('<th scope="col">Model and effort</th><th scope="col">Input</th><th scope="col">Cache writes, '
                      '5 min</th><th scope="col">Cache writes, 1 h</th><th scope="col">Cache reads</th>'
                      '<th scope="col">Output</th><th scope="col">All tokens</th><th scope="col">At API prices</th>', table)
        # m1: input 10, no 5-minute writes, 1000 one-hour writes, 100000 reads, 500 output; 101510 in all.
        self.assertIn('<td>claude-opus-5-5, high</td><td class="elapsed">10</td><td class="elapsed">0</td><td class="elapsed">1 k</td><td class="elapsed">100 k</td><td class="elapsed">500</td><td class="elapsed">102 k</td><td class="elapsed">$0.04</td>', table)
        self.assertIn('<td>claude-opus-5-5, xhigh</td><td class="elapsed">0</td><td class="elapsed">0</td><td class="elapsed">0</td><td class="elapsed">1.0 M</td><td class="elapsed">0</td><td class="elapsed">1.0 M</td><td class="elapsed">$0.40</td>', table)
        self.assertIn('<td>mystery-model, medium</td><td class="elapsed">5</td><td class="elapsed">0</td><td class="elapsed">0</td><td class="elapsed">0</td><td class="elapsed">5</td><td class="elapsed">10</td><td class="elapsed">unpriced</td>', table)
        self.assertEqual(mu.note_text(use), 'Model use: 1.09% of the weekly Claude Code limit (≈ $0.50 of Max 20x at '
                                            "$200 a month), its part by API prices of the limit's 3-point movement, "
                                            'read in whole points.')
        still = {**use, 'limit': {**use['limit'], 'moved_percent': 0.0, 'share_percent': 0.0, 'usd': 0.0}}
        self.assertEqual(mu.note_text(still), 'Model use: the weekly Claude Code limit, read in whole points, did '
                                              'not move during the cycle.')


class CodexCycleTest(Fixture):
    THREAD, OTHER = '01a00000-0000-7000-8000-000000000001', '01a00000-0000-7000-8000-000000000002'
    R1, R2 = 1792300000, 1792900000

    def count(self, seconds, total, last, used=None, resets=None):
        payload = {'type': 'token_count', 'info': {'total_token_usage': total, 'last_token_usage': last}}
        if used is not None:
            payload['rate_limits'] = {'primary': {'used_percent': used, 'window_minutes': 10080, 'resets_at': resets},
                                      'secondary': None, 'plan_type': 'pro'}
        return {'timestamp': at(seconds), 'type': 'event_msg', 'payload': payload}

    def context(self, seconds, model, effort):
        return {'timestamp': at(seconds), 'type': 'turn_context', 'payload': {'model': model, 'effort': effort}}

    def build(self):
        day = self.dir / 'codex' / 'sessions' / '2026' / '10' / '17'
        usage = lambda i, c, o: {'input_tokens': i, 'cached_input_tokens': c, 'output_tokens': o}
        write(day / f'rollout-2026-10-17T00-00-00-{self.THREAD}.jsonl', [
            {'timestamp': at(-300), 'type': 'session_meta', 'payload': {'id': self.THREAD}},
            self.context(-2000, 'gpt-6.1-sol', 'high'),
            *({'timestamp': at(-1990 + i), 'type': 'response_item', 'pad': 'x' * 300} for i in range(400)),
            self.count(-100, usage(1000, 800, 50), usage(1000, 800, 50), 20, self.R1),
            # 300000 input, 200000 cached, 1000 output in one request over 272K: long-context prices.
            self.count(10, usage(301000, 200800, 1050), usage(300000, 200000, 1000), 21, self.R1),
            self.context(20, 'gpt-6-astra', 'xhigh'),
            # the totals moved by more than the last request (two requests between events): the totals count.
            self.count(30, usage(311000, 208800, 1150), usage(9000, 8000, 90), 99, self.R1),
            self.count(40, usage(311100, 208800, 1160), usage(100, 0, 10), 3, self.R2),       # the week reset
            # totals lower than before (a new count): the event's own request counts.
            self.count(45, usage(50, 0, 5), usage(50, 0, 5)),
        ])
        # a thread on an API key (no plan in its rate limits) doesn't share the plan's limit.
        write(day / 'rollout-2026-10-17T00-00-03-01a00000-0000-7000-8000-000000000003.jsonl', [
            {'timestamp': at(-1), 'type': 'session_meta', 'payload': {'id': 'keyed'}},
            self.context(-1, 'gpt-6.1-sol', 'medium'),
            self.count(5, usage(1000000, 0, 0), usage(1000000, 0, 0)),
        ])
        write(day / 'rollout-2026-10-17T00-00-01-01a00000-0000-7000-8000-00000000000a.jsonl', [
            {'timestamp': at(-1), 'type': 'session_meta', 'payload': {'id': 'sub', 'session_id': self.THREAD}},
            self.context(-1, 'codex-auto-review', 'low'),
            self.count(15, usage(1000, 0, 10), usage(1000, 0, 10)),
        ])
        write(day / f'rollout-2026-10-17T00-00-02-{self.OTHER}.jsonl', [
            {'timestamp': at(-1), 'type': 'session_meta', 'payload': {'id': self.OTHER}},
            self.context(-1, 'gpt-6.1-sol', 'medium'),
            self.count(5, usage(100000, 0, 0), usage(100000, 0, 0), 20, self.R1),
        ])
        write(self.root / 'research' / 'logs' / 'model-usage.jsonl', [
            {'at': at(45), 'session': self.THREAD, 'models': {'claude-haiku-4-5-20251001': {}},
             'usage': {'input_tokens': 1000, 'output_tokens': 0}}])
        (self.logs).mkdir(parents=True, exist_ok=True)
        (self.logs / 'plans.json').write_text(json.dumps({'codex': {'plan': 'Pro', 'usd_per_month': 200}}))
        return self.dir / 'codex'

    def test_tokens_costs_and_share(self):
        home = self.build()
        use = mu.cycle(journal('Codex'), root=self.root, prices=self.prices, codex=home,
                       env={'CODEX_THREAD_ID': self.THREAD, 'USAGE_LOG_DIR': str(self.logs)})
        rows = {(row['model'], row['effort']): row for row in use['rows']}
        # long context: 100000 uncached * 4 + 200000 cached * 0.2 + 1000 * 15, per million.
        self.assertAlmostEqual(rows['gpt-6.1-sol', 'high']['usd'], 0.455)
        self.assertEqual(rows['gpt-6.1-sol', 'high']['tokens'], {'input': 100000, 'cache_write_5m': 0,
                                                                 'cache_write_1h': 0, 'cache_read': 200000,
                                                                 'output': 1000})
        # short context: 2000*10 + 8000*1 + 100*50, then 100*10 + 10*50, then 50*10 + 5*50.
        self.assertAlmostEqual(rows['gpt-6-astra', 'xhigh']['usd'], 0.03525)
        self.assertEqual(rows['codex-auto-review', 'low']['unpriced_tokens'], 1010)
        # its judge call is listed, but bills Claude's plan, so it stays out of the Codex share below.
        self.assertAlmostEqual(rows['claude-haiku-4-5-20251001', 'judge']['usd'], 0.001)
        self.assertEqual(use['billing'], 'plan')
        limit = use['limit']
        # 20 at the start; the old week ends at 99 and the new one stands at 3: (99 - 20) + 3.
        self.assertEqual(limit['moved_percent'], 82.0)
        # this thread's 0.49025 of the plan's 0.49025 + 0.2; the API-key thread's $2 is left out.
        self.assertAlmostEqual(limit['fraction_of_machine_use'], 0.49025 / 0.69025, places=6)
        self.assertAlmostEqual(limit['usd'], 82 * 0.49025 / 0.69025 / 100 * 200 * 12 / 52, places=4)


class ReadingTest(unittest.TestCase):
    def test_records_in_a_large_file_match_a_full_scan(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'large.jsonl'
            lines = [{'type': 'assistant', 'timestamp': at(second - 10000), 'n': second, 'pad': 'x' * 200}
                     for second in range(20000)]   # 5 MB: many search blocks
            write(path, lines)
            got = [r['n'] for r in mu.records(path, at(0), at(10), (mu.ASSISTANT,)) if not r.get('_before')]
            want = [line['n'] for line in lines
                    if at(-mu.MARGIN_S) <= line['timestamp'] <= at(10 + mu.LATE_S)]
            self.assertEqual(got, want)
            self.assertEqual(len(got), mu.MARGIN_S + 10 + mu.LATE_S + 1)

    def test_the_last_line_before_crosses_read_blocks(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'blocks.jsonl'
            path.write_bytes(b'{"marker": 1}\n' + b'x' * (3 << 20) + b'\n{"other": 1}\n')
            with open(path, 'rb') as stream:
                found = mu.last_line_before(stream, path.stat().st_size, mu.re.compile(b'marker'))
                self.assertEqual(found, b'{"marker": 1}')
                self.assertIsNone(mu.last_line_before(stream, path.stat().st_size, mu.re.compile(b'absent')))

    def test_a_stale_lower_reading_does_not_lower_the_limit(self):
        readings = [(100.0, 50.0, 9000), (150.0, 49.0, 9000), (160.0, 51.0, 9000), (170.0, 50.0, 9000)]
        self.assertEqual(mu.reading_at(readings, 175.0), 51.0)
        self.assertEqual(mu.reading_at(readings, 400.0), 51.0)   # use within a window only grows
        self.assertIsNone(mu.reading_at(readings, 50.0))
        # an idle session's stale 74 three seconds after 75, long before the cycle: no movement
        self.assertEqual(mu.movement([(1.0, 75.0, 9000), (4.0, 74.0, 9000), (500.0, 75.0, 9000)], 200.0, 1000.0),
                         (0.0, None))
        # after a weekly reset an idle session still reports the old window: no reset inside a later cycle
        stale = [(0.0, 90.0, 9000), (10.0, 2.0, 700000), (20.0, 90.0, 9000), (4000.0, 5.0, 700000)]
        self.assertEqual(mu.movement(stale, 3600.0, 7200.0), (3.0, None))
        # a reset inside the cycle: the old window's rise, then the new window's level
        self.assertEqual(mu.movement([(0.0, 40.0, 9000), (50.0, 45.0, 9000), (60.0, 1.0, 700000)], 10.0, 100.0),
                         (6.0, None))

    def test_a_request_record_longer_than_a_search_block_still_sets_the_effort(self):
        # Request records average about 119 KB: the search lands inside one, which must not be read as a record.
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'session.jsonl'
            long_request = {**request(-2000, 'high'), 'messages': 'x' * 300000}
            filler = [{'type': 'progress', 'timestamp': at(-5000 + i), 'pad': 'x' * 300} for i in range(800)]
            write(path, [*filler, long_request,
                         message(10, 'm', 'claude-opus-5-5', {'input_tokens': 1, 'output_tokens': 1})])
            data = path.read_bytes()
            with open(path, 'rb') as stream:   # the search returns a line's start, never a point inside one
                offset = mu.seek_time(stream, len(data), at(-mu.MARGIN_S))
            self.assertEqual(data[offset - 1:offset], b'\n')
            messages, oauth = mu.claude_file(path, at(0), at(60))
            self.assertEqual([m[2] for m in messages], ['high'])
            self.assertTrue(oauth)

    def test_leading_records_stamped_late_do_not_end_the_read(self):
        # A resumed transcript begins with snapshot records stamped later than the messages after them.
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'resumed.jsonl'
            write(path, [{'type': 'file-history-snapshot', 'timestamp': at(9000)},
                         message(10, 'm', 'claude-opus-5-5', {'input_tokens': 1, 'output_tokens': 1})])
            self.assertEqual(len(mu.claude_file(path, at(0), at(60))[0]), 1)

    def test_a_late_first_reading_is_said(self):
        moved, note = mu.movement([(120.0, 10.0, 9000), (190.0, 12.0, 9000)], 100.0, 200.0)
        self.assertEqual((moved, note), (2.0, 'its first limit reading came after the cycle began'))
        self.assertEqual(mu.movement([], 100.0, 200.0), (None, 'no limit reading before the cycle ended'))


if __name__ == '__main__':
    unittest.main()
