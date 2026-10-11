import sys
import unittest
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import staged_claims  # noqa: E402


class StagedClaimsTest(unittest.TestCase):
    """The commit check reads the claims declared by the articles a staged change adds, and refuses the commit
    when the registry marks a review of one of them stale."""

    def test_labels_come_from_added_article_tags_only(self):
        diff = ('+<article id="a" data-kind="research" data-claims="lem:one prop:two">\n'
                '-<article id="b" data-claims="lem:removed">\n'
                ' <article id="c" data-claims="lem:context">\n'
                '+<p>mentions data-claims="lem:in-prose" outside a tag</p>\n'
                '+<article id="d" data-claims="none" data-claim-note="x">\n')
        self.assertEqual(staged_claims.staged_labels(diff), ['lem:one', 'prop:two'])

    def test_no_declared_claims_checks_nothing(self):
        with mock.patch.object(staged_claims.subprocess, 'run') as run, \
                mock.patch.object(staged_claims, 'stale') as stale:
            run.return_value.stdout = '+<p>text</p>\n'
            self.assertEqual(staged_claims.main(), 0)
            stale.assert_not_called()

    def test_a_stale_declared_claim_refuses_the_commit(self):
        with mock.patch.object(staged_claims.subprocess, 'run') as run, \
                mock.patch.object(staged_claims, 'stale', return_value=[('lem:one', 'topics', ['source changed: x'])]):
            run.return_value.stdout = '+<article id="a" data-claims="lem:one">\n'
            self.assertEqual(staged_claims.main(), 1)

    def test_current_claims_pass(self):
        with mock.patch.object(staged_claims.subprocess, 'run') as run, \
                mock.patch.object(staged_claims, 'stale', return_value=[]):
            run.return_value.stdout = '+<article id="a" data-claims="lem:one">\n'
            self.assertEqual(staged_claims.main(), 0)


if __name__ == '__main__':
    unittest.main()
