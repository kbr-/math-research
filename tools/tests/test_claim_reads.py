"""The finisher refuses a Record paragraph naming a claim whose statement the session did not print."""
from importlib.machinery import SourceFileLoader
from pathlib import Path
import sys
import tempfile
import time
import unittest

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import claim_reads  # noqa: E402

FT = SourceFileLoader('finish_turn_claim_reads', str(TOOLS / 'finish-turn.py')).load_module()

# The sentence that exposed the gap, 17 October 2026, as the draft had it.
EXPOSED = ('<article id="entry-x" data-claims="lem:extension-field-quotients"><p><strong>Follow-up.</strong> '
           'Continuing. <strong>Record search.</strong> For the next attempt, "quotient by z squared plus z" '
           'returned lem:quotient-restriction-data, prop:pair-merging-gap and thm:finite-algebra-evaluation, '
           'none giving a binary descent of such quotients or a hard one.</p></article>')


class ClaimReads(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='claim-reads-')
        self.root = Path(self.temporary.name)
        self.since = time.time() - 1
        from unittest import mock
        patcher = mock.patch.object(sys, 'argv', ['tools/notebook-excerpt.py'])   # the log's writers are the readers
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_only_the_reading_tools_write_the_log(self):
        # 17 October 2026: a scratch script that printed 300 characters of each summary logged its claims as read.
        from unittest import mock
        with mock.patch.object(sys, 'argv', ['/tmp/judge_pairs.py']):
            with self.assertRaisesRegex(ValueError, 'written only by notebook-excerpt.py, search-claims.py'):
                claim_reads.log(self.root, ['lem:x'])
        claim_reads.log(self.root, ['lem:x'])
        self.assertIn('lem:x', claim_reads.read_since(self.root, self.since))

    def tearDown(self):
        self.temporary.cleanup()

    def test_the_exposing_sentence_is_refused_until_its_claims_are_read(self):
        with self.assertRaisesRegex(ValueError, 'thm:finite-algebra-evaluation'):
            FT.validate_named_claims_read(EXPOSED, self.root, self.since)
        claim_reads.log(self.root, ['lem:quotient-restriction-data', 'prop:pair-merging-gap'])
        with self.assertRaisesRegex(ValueError, r'evaluation\. A search'):
            FT.validate_named_claims_read(EXPOSED, self.root, self.since)
        claim_reads.log(self.root, ['thm:finite-algebra-evaluation'])
        FT.validate_named_claims_read(EXPOSED, self.root, self.since)

    def test_a_read_before_the_session_does_not_count(self):
        claim_reads.log(self.root, ['lem:quotient-restriction-data', 'prop:pair-merging-gap',
                                    'thm:finite-algebra-evaluation'])
        with self.assertRaises(ValueError):
            FT.validate_named_claims_read(EXPOSED, self.root, time.time() + 1)

    def test_the_entry_s_own_claims_and_other_paragraphs_are_exempt(self):
        entry = ('<article id="e" data-claims="lem:new-thing"><p><strong>New mathematics.</strong> '
                 'lem:new-thing extends thm:older-thing.</p><p><strong>Record comparison.</strong> From the '
                 "record's side, lem:new-thing is beside nothing read.</p></article>")
        FT.validate_named_claims_read(entry, self.root, self.since)

    def test_the_same_dismissal_in_other_applying_paragraphs_is_refused(self):
        # The reviewer's unlike case: the dismissal moved out of the Record search.
        for label in ('Own statements', 'Bearing', 'Record'):
            entry = (f'<article id="e" data-claims="none"><p><strong>Follow-up.</strong> Continuing. '
                     f'<strong>{label}.</strong> thm:finite-algebra-evaluation decides nothing here.</p></article>')
            with self.assertRaisesRegex(ValueError, 'thm:finite-algebra-evaluation', msg=label):
                FT.validate_named_claims_read(entry, self.root, self.since)

    def test_a_comparison_ends_at_the_next_labelled_paragraph(self):
        text = ('<p><strong>Record comparison.</strong> cor:one-thing is related. <strong>Baseline.</strong> '
                'lem:not-a-record-claim.</p>')
        self.assertEqual(claim_reads.named(text), ['cor:one-thing'])

    def test_identifiers_are_registry_prefixes_only(self):
        self.assertEqual(claim_reads.CLAIM_ID.findall('see third-party:x-y, ex:z1 and data:abc, http://a:b'),
                         ['third-party:x-y', 'ex:z1'])
        # 17 October 2026: a registered ID with capitals was cut at them and refused though read.
        self.assertEqual(claim_reads.CLAIM_ID.findall('and imp:binary-algebraic-CNF-IPS-transfer, concern'),
                         ['imp:binary-algebraic-CNF-IPS-transfer'])

    def test_every_registered_identifier_matches_whole(self):
        # 17 October 2026: the prefix list was taken from a truncated listing and missed "draft"; a prefix the
        # registry gains later fails here, not in a finisher refusal of a read claim.
        import json
        registry = Path(__file__).resolve().parents[2] / 'research/claims/index.json'
        if not registry.exists():
            self.skipTest('no registry in this checkout')
        ids = [claim['id'] for claim in json.loads(registry.read_text())['claims']]
        self.assertEqual([i for i in ids if not claim_reads.CLAIM_ID.fullmatch(i)], [])


if __name__ == '__main__':
    unittest.main()
