import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import staged_claims  # noqa: E402


def entry(ident, claims, body='text'):
    return f'<article id="{ident}" data-kind="research" data-claims="{claims}"><p>{body}</p></article>\n'


class ChangedLabelsTest(unittest.TestCase):
    def test_new_and_edited_articles_count_and_unchanged_ones_do_not(self):
        old = entry('a', 'lem:one') + entry('b', 'lem:two') + entry('c', 'none')
        new = entry('a', 'lem:one') + entry('b', 'lem:two', 'edited') + entry('c', 'none', 'edited') \
            + entry('d', 'prop:three ex:four')
        self.assertEqual(staged_claims.changed_labels(old, new), (3, ['ex:four', 'lem:two', 'prop:three'], []))

    def test_an_article_whose_tag_cannot_be_read_is_reported(self):
        bad = '<article data-note="a > b" id="x" data-claims="lem:one"><p>t</p></article>\n'
        count, labels, unread = staged_claims.changed_labels('', bad)
        self.assertEqual((count, labels), (1, []))
        self.assertEqual(len(unread), 1)


class RegistryAnswerTest(unittest.TestCase):
    """The registry's own answer, on a small registry: a stale review after its source changes, and a declared
    claim the registry does not hold."""

    def test_stale_and_missing_claims_are_told_apart(self):
        import json
        import claim_registry as cr
        import test_claim_registry as fixture
        from claim_reviews import Evidence, make_review
        data = cr.upgrade(cr.import_markdown(fixture.source()))
        claim = data['claims'][0]
        claim['mathematical_status'] = 'working_proof'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'research' / 'claims').mkdir(parents=True)
            page = root / 'notebook.html'
            page.write_text('<section><h4 id="proof">A</h4><p>Exact statement.</p></section>')
            claim['reviews']['mathematical_status'] = make_review(
                data, claim, 'mathematical_status', ['https://kbr.is-a.dev/math-research/#proof'],
                revision='a' * 40, date='2026-09-19', reviewer='Test', note='Read', evidence=Evidence(root))
            (root / staged_claims.REGISTRY).write_text(json.dumps(cr.validate(data)))
            self.assertEqual(staged_claims.stale([claim['id'], 'lem:absent'], root), ([], ['lem:absent']))
            page.write_text('<section><h4 id="proof">A</h4><p>Changed statement.</p></section>')
            rows, missing = staged_claims.stale([claim['id'], 'lem:absent'], root)
            self.assertEqual([(row[0], row[1]) for row in rows], [(claim['id'], 'mathematical_status')])
            self.assertEqual(missing, ['lem:absent'])


class StagedClaimsTest(unittest.TestCase):
    """In a real repository: the check takes the claims of staged articles that are new or changed against the
    base, refuses on stale or unregistered claims and on unstaged differences, and passes otherwise. The
    registry's coverage is replaced by a stand-in; its real answer is recorded with the build."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.git('init', '-q')
        self.git('config', 'user.email', 'x@example.invalid')
        self.git('config', 'user.name', 'x')
        (self.root / 'research' / 'claims').mkdir(parents=True)
        self.registry = self.root / staged_claims.REGISTRY
        self.registry.write_text('{}\n')
        self.nb = self.root / 'notebook.html'
        self.nb.write_text(entry('a', 'lem:one'))
        self.git('add', '.')
        self.git('commit', '-qm', 'start')

    def git(self, *args):
        return subprocess.run(['git', *args], cwd=self.root, check=True, capture_output=True, text=True)

    def run_check(self, rows=(), missing=(), base='HEAD'):
        with mock.patch.object(staged_claims, 'stale', return_value=(list(rows), list(missing))) as stale:
            return staged_claims.check(self.root, base), stale

    def test_nothing_declared_by_changed_articles_checks_nothing(self):
        self.nb.write_text(entry('a', 'lem:one') + entry('b', 'none'))
        self.git('add', 'notebook.html')
        messages, stale = self.run_check(rows=[('lem:one', 'topics', ['x'])])
        self.assertEqual(messages, [])
        stale.assert_not_called()

    def test_a_new_entry_with_a_stale_claim_is_refused(self):
        self.nb.write_text(entry('a', 'lem:one') + entry('b', 'lem:two'))
        self.git('add', 'notebook.html')
        messages, stale = self.run_check(rows=[('lem:two', 'topics', ['source changed: x'])])
        self.assertEqual(stale.call_args[0][0], ['lem:two'])
        self.assertIn('Commit refused', messages[-1])
        self.assertIn('lem:two: stale topics', messages[0])

    def test_an_edit_of_a_committed_entrys_body_is_checked(self):
        self.nb.write_text(entry('a', 'lem:one', 'edited'))
        self.git('add', 'notebook.html')
        messages, stale = self.run_check(rows=[('lem:one', 'topics', ['source changed: x'])])
        self.assertEqual(stale.call_args[0][0], ['lem:one'])
        self.assertTrue(messages)

    def test_an_amend_is_compared_with_the_parent(self):
        self.nb.write_text(entry('a', 'lem:one') + entry('b', 'lem:two'))
        self.git('add', 'notebook.html')
        self.git('commit', '-qm', 'entry')
        self.nb.write_text(entry('a', 'lem:one') + entry('b', 'lem:two', 'edited'))
        self.git('add', 'notebook.html')
        _, stale = self.run_check(base='HEAD^')
        self.assertEqual(stale.call_args[0][0], ['lem:two'])

    def test_an_unregistered_declared_claim_is_refused(self):
        self.nb.write_text(entry('a', 'lem:one') + entry('b', 'lem:new'))
        self.git('add', 'notebook.html')
        messages, _ = self.run_check(missing=['lem:new'])
        self.assertIn('lem:new: declared by a staged entry and not in the registry', messages[0])

    def test_a_draft_outside_a_notebook_is_not_read_as_an_entry(self):
        draft = self.root / 'research' / 'results' / 'cycle' / 'entry.html'
        draft.parent.mkdir(parents=True)
        draft.write_text(entry('b', 'lem:new'))
        self.git('add', '.')
        messages, stale = self.run_check(missing=['lem:new'])
        self.assertEqual(messages, [])
        stale.assert_not_called()
        side = self.root / 'research' / 'branches' / 'side' / 'notebook.html'
        side.parent.mkdir(parents=True)
        side.write_text(entry('c', 'lem:new'))
        self.git('add', '.')
        messages, _ = self.run_check(missing=['lem:new'])
        self.assertIn('lem:new: declared by a staged entry and not in the registry', messages[0])

    def test_an_unstaged_registry_or_notebook_is_refused_before_the_registry_is_read(self):
        self.nb.write_text(entry('a', 'lem:one') + entry('b', 'lem:two'))
        self.git('add', 'notebook.html')
        self.registry.write_text('{"rebuilt": true}\n')                 # rebuilt and not staged
        messages, stale = self.run_check()
        self.assertIn('research/claims/index.json', messages[0])
        stale.assert_not_called()
        self.git('add', str(self.registry))
        self.nb.write_text(entry('a', 'lem:one') + entry('b', 'lem:two', 'edited after staging'))
        messages, stale = self.run_check()
        self.assertIn('notebook.html', messages[0])
        stale.assert_not_called()

    def test_an_amend_that_stages_nothing_new_still_checks_the_amended_commit(self):
        self.nb.write_text(entry('a', 'lem:one') + entry('b', 'lem:two'))
        self.git('add', 'notebook.html')
        self.git('commit', '-qm', 'entry')
        _, stale = self.run_check(base='HEAD^')                         # nothing staged beyond HEAD
        self.assertEqual(stale.call_args[0][0], ['lem:two'])

    def test_an_unreadable_tag_is_refused(self):
        self.nb.write_text(entry('a', 'lem:one') + '<article data-x="a > b" id="z" data-claims="lem:q"></article>\n')
        self.git('add', 'notebook.html')
        messages, stale = self.run_check()
        self.assertIn('could not be read', messages[-1])
        stale.assert_not_called()

    def test_a_commit_already_made_can_be_audited(self):
        self.nb.write_text(entry('a', 'lem:one') + entry('b', 'lem:two'))
        self.git('add', 'notebook.html')
        self.git('commit', '-qm', 'entry')
        with mock.patch.object(staged_claims, 'stale', return_value=([], [])) as stale:
            self.assertEqual(staged_claims.check(self.root, 'HEAD^', 'HEAD'), [])
        self.assertEqual(stale.call_args[0][0], ['lem:two'])

    def test_current_claims_pass(self):
        self.nb.write_text(entry('a', 'lem:one') + entry('b', 'lem:two'))
        self.git('add', 'notebook.html')
        self.assertEqual(self.run_check()[0], [])

    def test_a_crash_refuses_with_a_message(self):
        with mock.patch.object(staged_claims, 'check', side_effect=ValueError('broken')):
            self.assertEqual(staged_claims.main([]), 1)


if __name__ == '__main__':
    unittest.main()
