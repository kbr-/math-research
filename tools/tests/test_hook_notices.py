import importlib.util
import shutil
import sys
import tempfile
import time
import types
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('hook_notices', ROOT / 'tools' / 'hook_notices.py')
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)

NOTICE = ('This commit resembles the queued build item spell-count of research/branches/x/notebook.html (0.4 of its '
          'words): read the item.\nThis commit resembles the queued build item other:s2 of notebook.html (0.5 of '
          'its words): read the item.')


class HookNoticesTest(unittest.TestCase):
    def test_a_notice_is_recorded_for_each_item_and_reported_until_answered(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(tool.report(tmp), [])                      # no log yet
            self.assertEqual(tool.record(tmp, 'Local main is not at this commit.', now=5), 0)
            self.assertEqual(tool.record(tmp, NOTICE, now=10), 2)
            tool.record(tmp, NOTICE.splitlines()[0], now=20)
            self.assertEqual(tool.unanswered(tmp), [('spell-count', 'research/branches/x/notebook.html', 2),
                                                    ('other:s2', 'notebook.html', 1)])
            lines = tool.report(tmp)
            self.assertIn('Hook notices not answered', lines[0])
            self.assertEqual(lines[1:], ['  spell-count of research/branches/x/notebook.html (2 notices)',
                                         '  other:s2 of notebook.html'])
            tool.answer(tmp, 'spell-count', 'Read: unrelated, it shares only the word finisher.', now=30)
            self.assertEqual([item for item, _, _ in tool.unanswered(tmp)], ['other:s2'])
            # A later notice of an answered item is open again; notices before `since` are not reported.
            tool.record(tmp, NOTICE.splitlines()[0], now=40)
            self.assertEqual([item for item, _, _ in tool.unanswered(tmp)], ['other:s2', 'spell-count'])
            self.assertEqual([item for item, _, _ in tool.unanswered(tmp, since=35)], ['spell-count'])

    def test_an_answer_needs_a_recorded_notice_and_a_note(self):
        with tempfile.TemporaryDirectory() as tmp:
            tool.record(tmp, NOTICE, now=10)
            with self.assertRaisesRegex(ValueError, 'twenty characters'):
                tool.answer(tmp, 'spell-count', 'read')
            with self.assertRaisesRegex(ValueError, 'no recorded notice names never-noticed'):
                tool.answer(tmp, 'never-noticed', 'Read: unrelated to this commit.')
            self.assertEqual(tool.main(['answer', 'spell-count', 'x'], root=tmp), 1)
            self.assertEqual(tool.main(['answer', 'spell-count', 'Read: unrelated to this commit.'], root=tmp), 0)
            self.assertEqual(tool.main(['list'], root=tmp), 0)
            self.assertEqual(tool.main(['other'], root=tmp), 1)


    def test_an_answer_quotes_the_items_text_when_the_item_is_found(self):
        # 17 October 2026: two notices were answered "Read the item" before their items were read.
        with tempfile.TemporaryDirectory() as tmp:
            notebook = Path(tmp) / 'research/branches/x/notebook.html'
            notebook.parent.mkdir(parents=True)
            notebook.write_text('<li data-build="spell-count" data-source="s">Make the finisher count the spell '
                                'of each item from its entries and refuse a fifth entry.<ul><li>sub</li></ul></li>')
            tool.record(tmp, NOTICE.splitlines()[0], now=10)
            with self.assertRaisesRegex(ValueError, 'quote at least 8'):
                tool.answer(tmp, 'spell-count', 'Read the item: the commit builds no part of it at all.')
            tool.answer(tmp, 'spell-count', 'It asks to "count the spell of each item from its entries"; the '
                        'commit builds no part of it.', now=20)
            self.assertEqual(tool.unanswered(tmp), [])


class HookAndFinisherTest(unittest.TestCase):
    def load(self, name, path):
        spec = importlib.util.spec_from_file_location(name, ROOT / path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_the_hook_records_the_notice_it_prints_and_the_finisher_lists_it(self):
        hook = self.load('base_behind_under_test', 'tools/hooks/base_behind.py')
        finisher = self.load('finish_turn_under_test', 'tools/finish-turn.py')
        with tempfile.TemporaryDirectory() as tmp:
            tools = Path(tmp) / 'tools'
            tools.mkdir()
            (tools / 'lead_queue.py').write_text('')
            shutil.copy(ROOT / 'tools' / 'hook_notices.py', tools / 'hook_notices.py')
            now = time.time()
            answers = {'rev-parse': tmp, 'log': str(int(now))}
            ran = types.SimpleNamespace(returncode=0, stdout=NOTICE + '\n')
            before = list(sys.path)
            try:
                with mock.patch.object(hook, 'git', lambda *args, cwd=None: answers[args[0]]), \
                        mock.patch.object(hook.subprocess, 'run', lambda *args, **kwargs: ran):
                    self.assertEqual(hook.built('git commit -q -F -', cwd=tmp), NOTICE)   # the text is unchanged
                    self.assertIsNone(hook.built('git status', cwd=tmp))                  # not a commit
                self.assertEqual([item for item, _, _ in tool.unanswered(tmp)], ['spell-count', 'other:s2'])
                lines = finisher.hook_notice_lines(tmp, now - 5)
                self.assertIn('Hook notices not answered', lines[0])
                self.assertEqual(len(lines), 3)
                self.assertEqual(finisher.hook_notice_lines(tmp, now + 60), [])           # before the session
                # A damaged log prints nothing and stops nothing.
                (Path(tmp) / tool.LOG).write_text('[1, 2]\nnot json\n"text"\n')
                self.assertEqual(finisher.hook_notice_lines(tmp, 0), [])
            finally:
                sys.path[:] = before
                sys.modules.pop('hook_notices', None)


if __name__ == '__main__':
    unittest.main()
