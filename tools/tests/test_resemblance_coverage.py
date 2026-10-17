"""A Record comparison names the registered claims nearest the entry's declared claims, or relates them."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import resemblance_coverage as rc

# Summaries share words so that the nearest claim is the one meant; scores come from claim_authoring.
CLAIMS = [
    {'id': 'lem:old-occupancy', 'summary': 'Old occupancy: the coset count of an edge set with exposed vertices'},
    {'id': 'cor:star-closure', 'summary': 'Star closure ratio: closing the edge set by vertex stars keeps the '
                                          'tuple ratio of exposed vertices'},
    {'id': 'thm:far', 'summary': 'Unrelated certificate depth of a modular simulation'},
    {'id': 'cor:new-ratio', 'summary': 'New ratio: the tuple ratio of an edge set with exposed vertices without '
                                       'closing it by stars'},
]


def article(comparison, claims='cor:new-ratio'):
    return (f'<article id="entry-x" data-kind="research" data-claims="{claims}">'
            f'<p><strong>Best outcome.</strong> cor:star-closure gives it inside the window.</p>'
            f'<p><strong>Record comparison.</strong> {comparison}</p></article>')


def edge(source, kind, target):
    return {'source': {'id': source}, 'target': {'id': target}, 'type': kind}


class ResemblanceCoverageTest(unittest.TestCase):
    def test_the_exposing_case_a_nearest_claim_cited_elsewhere_but_not_compared(self):
        # 17 October 2026: the Best outcome cited cor:star-closure-ratio, the comparison passed over it.
        gaps = rc.missing(article('lem:old-occupancy is the template.'), CLAIMS, at=0.1)
        self.assertIn('cor:star-closure', [other for _, _, other in gaps])
        self.assertNotIn('thm:far', [other for _, _, other in gaps])

    def test_naming_each_or_relating_it_passes(self):
        self.assertEqual(rc.missing(article('lem:old-occupancy and cor:star-closure, neither more general.'),
                                    CLAIMS, at=0.1), [])
        related = [edge('cor:new-ratio', 'refines', 'cor:star-closure')]
        self.assertEqual(rc.missing(article('lem:old-occupancy is the template.'), CLAIMS, at=0.1,
                                    relationships=related), [])

    def test_a_cites_edge_alone_does_not_pass(self):
        # Its reviewer, 17 October 2026: one spec line of "cites" would pass without the comparison.
        cites = [edge('cor:new-ratio', 'cites', 'cor:star-closure')]
        gaps = rc.missing(article('lem:old-occupancy is the template.'), CLAIMS, at=0.1, relationships=cites)
        self.assertIn('cor:star-closure', [other for _, _, other in gaps])

    def test_an_entry_with_claims_but_no_comparison_is_refused(self):
        bare = ('<article id="entry-x" data-kind="research" data-claims="cor:new-ratio">'
                '<p><strong>Best outcome.</strong> cor:star-closure.</p></article>')
        with self.assertRaisesRegex(ValueError, 'needs a <p><strong>Record comparison'):
            rc.validate(bare)

    def test_a_named_newer_version_covers_the_older(self):
        claims = CLAIMS + [{'id': 'cor:star-closure-two', 'summary': 'Star closure ratio refined'}]
        refined = [edge('cor:star-closure-two', 'refines', 'cor:star-closure')]
        self.assertEqual(rc.missing(article('lem:old-occupancy; cor:star-closure-two refines the closure.'),
                                    claims, at=0.1, relationships=refined), [])

    def test_only_claims_registered_before_the_entrys_own_are_compared(self):
        later = CLAIMS + [{'id': 'cor:later-ratio', 'summary': 'Later ratio: the tuple ratio of exposed vertices '
                                                                  'of an edge set'}]
        gaps = rc.missing(article('lem:old-occupancy and cor:star-closure.'), later, at=0.1)
        self.assertEqual(gaps, [])

    def test_entries_without_claims_or_without_the_paragraph_are_not_checked(self):
        self.assertEqual(rc.missing(article('Nothing.', claims='none'), CLAIMS, at=0.1), [])
        self.assertEqual(rc.comparison_ids('<p><strong>Record search.</strong> cor:star-closure</p>'), set())
        self.assertEqual(rc.comparison_ids('<p class="x"><strong>Record comparison.</strong> cor:star-closure</p>'),
                         {'cor:star-closure'})


if __name__ == '__main__':
    unittest.main()
