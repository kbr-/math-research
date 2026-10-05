import importlib.util
import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
spec = importlib.util.spec_from_file_location('ft_research_leads', TOOLS / 'finish-turn.py')
FT = importlib.util.module_from_spec(spec)
spec.loader.exec_module(FT)

ITEM = '<li>A lead. <strong>Answers.</strong> It would. <strong>Test.</strong> Passed: yes.</li>'


def body(leads=(), bridges=()):
    sections = ''
    if leads:
        sections += '<h4>Outside leads</h4><ul>' + ''.join(leads) + '</ul>'
    if bridges:
        sections += '<h4>Absurd bridges</h4><ul>' + ''.join(bridges) + '</ul>'
    text = ('<li data-route-item="step">x</li><section id="research-record"><article id="e" data-kind="research" '
            'data-route="step">' + sections + '</article></section>')
    start = text.index('<article')
    return text, start, text.index('</article>', start)


class ResearchLeadsTest(unittest.TestCase):
    """Research entries carry no Outside leads or Absurd bridges (user, 9 October 2026)."""

    def test_any_lead_or_bridge_is_refused(self):
        FT.validate_leads(*body())
        for case in (body([ITEM]), body((), [ITEM]), body([ITEM], [ITEM])):
            with self.assertRaises(ValueError):
                FT.validate_leads(*case)


OK = ' <strong>Answers.</strong> It would. <strong>Test.</strong> '
OBSTACLE = ('<h4>Obstacle</h4><p>No recorded mechanism bounds the residual regularity uniformly in the degree, '
            'which the first step needs.</p>')


def review(leads, bridges):
    """A route review whose items are (outcome, picked) pairs."""
    li = lambda items: ''.join(f'<li{" data-pick" if pick else ""}>x{OK}{outcome}.</li>' for outcome, pick in items)
    text = ('<li data-route-item="step">x</li><section id="research-record"><article id="r" data-kind="review" '
            'data-route="step">' + OBSTACLE + '<h4>Outside leads</h4><ul>' + li(leads) + '</ul><h4>Absurd bridges'
            '</h4><ul>' + li(bridges) + '</ul></article></section>')
    start = text.index('<article')
    return text, start, text.index('</article>', start)


class ReviewPicksTest(unittest.TestCase):
    """Outside draining a review selects three passed leads and two bridges; draining selects none."""

    P, F = 'Passed', 'Falsified'

    def test_exact_picks_are_accepted(self):
        P, F = self.P, self.F
        FT.validate_leads(*review([(P, 1), (P, 1), (P, 1), (P, 0)], [(P, 1), (P, 1), (P, 0)]))
        FT.validate_leads(*review([(P, 1), (F, 0), (F, 0)], [(F, 0), (F, 0)]))     # fewer passed, fewer picks

    def test_wrong_picks_are_refused(self):
        P, F = self.P, self.F
        for leads, bridges in (([(P, 0), (P, 0), (P, 0)], [(P, 1), (F, 0)]),       # no lead picked
                               ([(P, 1), (P, 0), (P, 1)], [(P, 1), (P, 1)]),       # old two-lead quota
                               ([(P, 1), (P, 1), (P, 1)], [(P, 1), (P, 0)]),       # old one-bridge quota
                               ([(P, 1), (F, 1), (F, 0)], [(P, 1), (F, 0)]),       # a falsified item picked
                               ([(P, 1), (P, 1), (F, 0)], [(P, 0), (F, 0)])):      # passed bridge not picked
            with self.assertRaises(ValueError):
                FT.validate_leads(*review(leads, bridges))


class AuditLeadsTest(unittest.TestCase):
    """A queue audit lists recovered ideas without caps, each naming an earlier source entry."""

    def audit(self, sources):
        items = ''.join(f'<li data-source="{s}">Idea.</li>' for s in sources)
        text = ('<li data-route-item="step">x</li><section id="research-record"><article id="old" data-kind="review" '
                'data-route="step"></article><article id="a" data-kind="audit" data-route="step"><h4>Outside leads'
                '</h4><ul>' + items + '</ul></article></section>')
        start = text.index('<article id="a"')
        return text, start, text.index('</article>', start)

    def test_sources_are_required_and_must_be_earlier_entries(self):
        FT.validate_leads(*self.audit(['old', 'old', 'old']))       # no cap, no Test or Answers needed
        for sources in (['old', 'later'], ['a'], ['']):            # unknown, itself, missing
            with self.assertRaises(ValueError):
                FT.validate_leads(*self.audit(sources))

    def test_audit_entries_need_no_route_review_cadence(self):
        text, start, _ = self.audit(['old'])
        FT.validate_route(text, start)


if __name__ == '__main__':
    unittest.main()
