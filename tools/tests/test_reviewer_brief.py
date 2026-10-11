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


if __name__ == '__main__':
    unittest.main()
