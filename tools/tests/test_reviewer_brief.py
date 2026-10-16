import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest import mock

spec = importlib.util.spec_from_file_location('reviewer_brief', Path(__file__).resolve().parents[1] / 'hooks/reviewer_brief.py')
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)


def call(prompt, agent='medium-reviewer', tool='Agent'):
    return {'tool_name': tool, 'tool_input': {'subagent_type': agent, 'prompt': prompt}}


class ReviewerBriefTest(unittest.TestCase):
    def run_hook(self, payload):
        err = io.StringIO()
        with mock.patch('sys.stdin', io.StringIO(json.dumps(payload))), redirect_stderr(err):
            return hook.main(), err.getvalue()

    def test_a_brief_that_hands_over_a_whole_document_is_refused(self):
        for prompt in ('Read the file, then read the whole Path section of PLAN.md once.',
                       'Audit the rows against the entire theory.',
                       'Read notes/x/PLAN.md in full before you start.',
                       'First read all of the notebook.'):
            with self.subTest(prompt=prompt):
                status, err = self.run_hook(call(prompt))
                self.assertEqual(status, 2)
                self.assertIn('tools/notebook-excerpt.py ANCHOR --out FILE', err)
        status, err = self.run_hook(call('Read the whole Path.'))
        self.assertIn('("whole Path")', err)

    def test_a_narrow_brief_other_agents_and_other_tools_pass(self):
        narrow = (f'Audit every row in {Path(__file__).resolve()}; read that file in full first. It holds the increments '
                  'the rows cite. Search PLAN.md only for a clause you challenge.')
        for payload in (call(narrow), call('Read the whole Path.', agent='Explore'),
                        call('Read the whole Path.', tool='Bash'), {'tool_name': 'Agent'}):
            with self.subTest(payload=payload):
                self.assertEqual(self.run_hook(payload), (0, ''))

    def test_the_refusal_names_a_further_tool_only_where_the_branch_s_own_module_does(self):
        with tempfile.TemporaryDirectory() as without, tempfile.TemporaryDirectory() as tools:
            there = hook.refusal(call('Read the whole notebook.'), tools=Path(without))
            (Path(tools) / 'branch_own.py').write_text('EXCERPT_TOOL = "`tools/rows.py --brief` for a table or "\n')
            here = hook.refusal(call('Read the whole notebook.'), tools=Path(tools))
        self.assertIn('built with `tools/rows.py --brief` for a table or `tools/notebook-excerpt.py ANCHOR --out FILE` '
                      'for the notebook', here)
        self.assertNotIn('rows.py', there)
        self.assertIn('built with `tools/notebook-excerpt.py ANCHOR --out FILE` for the notebook', there)

    def test_an_entry_draft_needs_its_commit_message_in_the_brief(self):
        with tempfile.TemporaryDirectory() as folder:
            draft, message = Path(folder) / 'entry_x.html', Path(folder) / 'commit_x.txt'
            draft.write_text('<article></article>')
            message.write_text('Main: x')
            refused = hook.refusal(call(f'Review the draft {draft} with excerpts.'))
            self.assertIn('no drafted commit message', refused)
            self.assertIsNone(hook.refusal(call(f'Review the draft {draft} and the commit message {message}.')))
            # A brief without an entry draft (a blind stage, a tool review) needs none.
            notes = Path(folder) / 'blind.md'
            notes.write_text('goal')
            self.assertIsNone(hook.refusal(call(f'Read {notes} only.')))
            # A tracked page named in a layout review is not a draft; a test file is not a commit message.
            page = Path(__file__).resolve().parents[2] / 'index.html'
            self.assertIsNone(hook.refusal(call(f'Check the layout of {page}.')))
            stray = Path(folder) / 'test_commit_hook.py'
            stray.write_text('')
            self.assertIn('no drafted commit message', hook.refusal(call(f'Review {draft} and {stray}.')))

    def test_input_that_is_not_json_passes(self):
        with mock.patch('sys.stdin', io.StringIO('not json')):
            self.assertEqual(hook.main(), 0)




class MissingBriefFileTest(unittest.TestCase):
    def test_a_brief_naming_a_file_that_is_not_there_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            there = Path(tmp) / 'brief.txt'
            there.write_text('x')
            self.assertIsNone(hook.refusal(call(f'Read only {there} and answer.')))
            reason = hook.refusal(call(f'Read only {tmp}/absent.txt and {there}.'))
            self.assertIn(f'{tmp}/absent.txt', reason)
            self.assertNotIn(str(there) + ',', reason)
            # A directory, a relative path, a pattern and another agent's brief are left alone.
            self.assertIsNone(hook.refusal(call(f'Work from {tmp}/nowhere and save to research/results/x/review.txt; '
                                                f'run tools/tests/run.py; see {tmp}/*.txt')))
            self.assertIsNone(hook.refusal(call(f'Read {tmp}/absent.txt', agent='general-purpose')))

    def test_files_named_inside_the_brief_and_in_a_follow_up_must_exist(self):
        # 16 October 2026: the brief file existed, the excerpt it named did not.
        with tempfile.TemporaryDirectory() as tmp:
            brief = Path(tmp) / 'brief.md'
            brief.write_text(f'Draft: {tmp}/draft.html\nDependencies: {tmp}/deps.md\n')
            (Path(tmp) / 'draft.html').write_text('x')
            reason = hook.refusal(call(f'Read the brief at {brief} and only the files it names.'))
            self.assertIn(f'{tmp}/deps.md', reason)
            (Path(tmp) / 'deps.md').write_text('x')
            self.assertIsNone(hook.refusal(call(f'Read the brief at {brief} and only the files it names.')))
            follow = {'tool_name': 'SendMessage', 'tool_input': {'to': 'a1', 'message': f'Check {tmp}/draft2.html.'}}
            self.assertIn('draft2.html', hook.refusal(follow))
            (Path(tmp) / 'draft2.html').write_text('x')
            self.assertIsNone(hook.refusal(follow, log=Path(tmp) / 'none.tsv'))

    def test_a_follow_up_claiming_an_update_its_refused_command_was_to_write_is_refused(self):
        # 16 October 2026: the command writing the spec was refused, and the follow-up said it was updated.
        with tempfile.TemporaryDirectory() as tmp:
            spec, excerpts = Path(tmp) / 'spec.json', Path(tmp) / 'deps.md'
            spec.write_text('{}')
            excerpts.write_text('x')
            written = hook.datetime.fromtimestamp(spec.stat().st_mtime)
            log = Path(tmp) / 'blocks.tsv'
            blocked = written + hook.timedelta(seconds=30)
            hook.block_log.record('bash_guard', log, blocked, what='Refused: a script replaces text', paths=[str(spec)])
            now = blocked + hook.timedelta(seconds=60)

            def send(text, when=now):
                return hook.refusal({'tool_name': 'SendMessage', 'tool_input': {'message': text}}, log=log, now=when)

            words = ('updated', 'rewritten', 'rewrote', 'now written', 'corrected', 'revised')
            for word in words:
                self.assertIn('spec.json', send(f'The spec {spec} is {word} as described.'), word)
                # The same word in a legitimate sentence passes: about a file the refused call did not name.
                self.assertIsNone(send(f'The excerpts {excerpts} are {word} as described.'), word)
            # A file named beside the updated one is not refused for it; the stale one alone is named.
            both = send(f'The spec {spec} is updated; the excerpts are at {excerpts}.')
            self.assertIn('spec.json', both)
            self.assertNotIn('deps.md', both)
            # The file read back, a refusal older than the window, no file named: all pass.
            self.assertIsNone(send(f'The spec {spec} is updated, checked on disk.'))
            self.assertIsNone(send(f'The spec {spec} is updated.', blocked + hook.timedelta(seconds=900)))
            self.assertIsNone(send('The corrected lemma now holds for every t.'))
            # An unrelated refusal, naming no file or another one, does not refuse the message.
            log.write_text('')
            hook.block_log.record('bash_guard', log, blocked, what='Refused: a pipe')
            hook.block_log.record('bash_guard', log, blocked, paths=[str(excerpts)])
            self.assertIsNone(send(f'The spec {spec} is updated.'))
            # A refusal older than the file's last write passes: the update was written after it.
            log.write_text('')
            hook.block_log.record('bash_guard', log, written - hook.timedelta(seconds=30), paths=[str(spec)])
            self.assertIsNone(send(f'The spec {spec} is updated.'))


if __name__ == '__main__':
    unittest.main()
