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
    """Research entries may carry one Outside lead and one Absurd bridge (user, 3 October 2026)."""

    def test_one_of_each_is_allowed(self):
        FT.validate_leads(*body([ITEM], [ITEM]))
        FT.validate_leads(*body())

    def test_more_than_one_is_refused(self):
        for case in (body([ITEM, ITEM]), body((), [ITEM, ITEM])):
            with self.assertRaises(ValueError):
                FT.validate_leads(*case)

    def test_items_still_answer_and_test(self):
        with self.assertRaises(ValueError):
            FT.validate_leads(*body(['<li>A lead. <strong>Test.</strong> Passed.</li>']))


if __name__ == '__main__':
    unittest.main()
