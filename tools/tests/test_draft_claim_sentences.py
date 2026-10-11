"""Sentences of a draft that cite a claim are listed beside the claim's registered statement."""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import draft_claim_sentences as dcs

REGISTRY = {'claims': [
    {'id': 'lem:first', 'summary': 'First lemma: holds for original instances only.'},
    {'id': 'prop:second', 'summary': 'Second proposition, for balanced profiles.'},
]}

DRAFT = '''<article id="entry-x" data-claims="lem:new-one">
<h3>Title</h3>
<p><strong>New mathematics.</strong> <code>lem:new-one</code>: a bound \\(s&lt;n/2.5\\) holds. By <code>lem:first</code> every core is excluded. Nothing else.</p>
<h4>The count</h4>
<p>With <code>prop:second</code> and <code>lem:first</code> the budget is two-sided. See <code>cor:missing</code>.</p>
<ul><li>An item citing <code>lem:first</code> twice, <code>lem:first</code> again.</li></ul>
</article>'''


class DraftClaimSentences(unittest.TestCase):
    def test_sentences_are_listed_under_their_claim_with_labels(self):
        out, unregistered = dcs.report(DRAFT, REGISTRY, 0)
        self.assertIn('lem:first\n  REGISTERED: First lemma: holds for original instances only.', out)
        self.assertIn('  [New mathematics] By lem:first every core is excluded.', out)
        self.assertIn('  [The count] With prop:second and lem:first the budget is two-sided.', out)
        self.assertEqual(out.count('An item citing lem:first twice'), 1)
        self.assertEqual(unregistered, {'cor:missing'})

    def test_a_full_stop_inside_tex_does_not_split_a_sentence(self):
        found = dcs.citations(DRAFT)
        self.assertIn(('lem:new-one', 'New mathematics', 'New mathematics. lem:new-one: a bound \\(s<n/2.5\\) holds.'),
                      found)

    def test_declared_and_unregistered_claims_are_told_apart(self):
        out, _ = dcs.report(DRAFT, REGISTRY, 0)
        self.assertIn('lem:new-one\n  REGISTERED: (declared by this draft; not yet registered)', out)
        self.assertIn('cor:missing\n  REGISTERED: (NOT IN THE REGISTRY)', out)
        self.assertTrue(out.endswith('6 citing sentences, 4 claims, 1 unregistered.'))

    def test_width_cuts_long_lines(self):
        out, _ = dcs.report(DRAFT, REGISTRY, 20)
        self.assertIn('  REGISTERED: First lemma: holds f\n', out)


if __name__ == '__main__':
    unittest.main()
