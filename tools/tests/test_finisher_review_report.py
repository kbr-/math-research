"""Regression tests for the fresh-context review of 3 October 2026 (finish-turn.py items 9-11)."""
import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
spec = importlib.util.spec_from_file_location('ft_review_report', TOOLS / 'finish-turn.py')
FT = importlib.util.module_from_spec(spec)
spec.loader.exec_module(FT)


def notebook(kinds):
    """A notebook whose record holds articles of the given kinds on route r ('untagged' has no tags); the last
    article is the one checked.  A kind 'review:N' declares data-open-items N."""
    parts = []
    for n, kind in enumerate(kinds):
        if kind == 'untagged':
            parts.append(f'<article id="a{n}"><p>x</p></article>')
            continue
        kind, _, items = kind.partition(':')
        extra = f' data-open-items="{items}"' if items else ''
        parts.append(f'<article id="a{n}" data-kind="{kind}" data-route="r"{extra}><p>x</p></article>')
    body = '<li data-route-item="r">r</li><section id="research-record">' + ''.join(parts) + '</section>'
    return body, body.rindex('<article')


class FinisherReviewReportTest(unittest.TestCase):
    def test_convergence_reference_passes_over_reviews_without_open_items(self):   # item 9
        body, last = notebook(['review:7'] + ['research'] * 3 + ['review'] + ['research'] * 10 + ['review:7'])
        self.assertEqual(FT.convergence_reference(body, last, 'r'), ('a0', 13, 7))

    def test_review_cadence_counts_across_untagged_entries(self):   # item 10
        body, last = notebook(['review', 'research', 'research', 'research', 'untagged', 'research', 'review'])
        with self.assertRaises(ValueError):
            FT.validate_route(body, last)
        body, last = notebook(['review'] + ['research'] * 6 + ['review'])
        FT.validate_route(body, last)

    def test_scratch_check_survives_a_vanishing_file(self):   # item 11
        with tempfile.TemporaryDirectory() as home:
            pad = Path(home) / '.claude/jobs/abcdef12/tmp'
            pad.mkdir(parents=True)
            (pad / 'kept').write_bytes(b'x' * 10)
            (pad / 'gone').write_bytes(b'x' * 10)
            real_stat = Path.stat
            calls = {'gone': 0}

            def stat(self, *args, **kwargs):
                if self.name == 'gone':
                    calls['gone'] += 1
                    if calls['gone'] > 1:   # present for is_file(), vanished for the size
                        raise FileNotFoundError(self)
                return real_stat(self, *args, **kwargs)
            with mock.patch.object(Path, 'stat', stat):
                FT.check_scratch({'CLAUDE_CODE_SESSION_ID': 'abcdef12-3456'}, Path(home), cap=1000)

    def test_validate_queue_end_to_end(self):
        """The finisher's queue check against HEAD's notebook through git, and a side notebook without route items."""
        import subprocess
        from test_lead_queue import review, research, notebook as qnotebook, PASS
        rev = review('r1', [PASS, PASS])
        q = [('lead', 'r1:1'), ('lead', 'r1:2')]
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            nb = root / 'research/branches/x/notebook.html'
            nb.parent.mkdir(parents=True)
            nb.write_text(qnotebook([rev], q))
            run = lambda *a: subprocess.run(['git', *a], cwd=root, check=True, capture_output=True)
            run('init', '-q')
            run('add', '.')
            run('-c', 'user.name=T', '-c', 'user.email=t@example.invalid', 'commit', '-qm', 'base')
            nb.write_text(qnotebook([rev, research(q[0], 'Closed')], q[1:]))
            FT.validate_queue(root, nb)
            nb.write_text(qnotebook([rev, research(q[1], 'Closed')], q[:1]))   # not the head
            with self.assertRaises(ValueError):
                FT.validate_queue(root, nb)
            side = root / 'research/branches/side/notebook.html'
            side.parent.mkdir(parents=True)
            side.write_text('<section id="research-record"><article data-kind="research"><p>x</p></article></section>')
            FT.validate_queue(root, side)   # no route items: no queue rules

    def test_finisher_fixtures_ignore_the_real_session(self):   # item 11
        from test_finish_turn import FinalizationTest
        with mock.patch.dict(os.environ, {'CLAUDE_CODE_SESSION_ID': 'real-session'}):
            case = FinalizationTest('test_incomplete_new_claim_is_rejected_before_clock_stops')
            case.setUp()
            try:
                self.assertNotIn('CLAUDE_CODE_SESSION_ID', os.environ)
                self.assertNotIn('CLAUDE_CODE_SESSION_ID', case.command_env)
            finally:
                case.doCleanups()
            self.assertEqual(os.environ.get('CLAUDE_CODE_SESSION_ID'), 'real-session')


if __name__ == '__main__':
    unittest.main()
