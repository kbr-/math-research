import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TurnGuidanceTest(unittest.TestCase):
    def setUp(self):
        self.guide = load('turn_guidance', 'tools/turn_guidance.py')
        self.ft = self.guide.finisher()

    def body(self, entries):
        route = '<section id="remaining-route"><li data-route-item="step">x</li></section>'
        arts = ''.join(f'<article data-kind="{kind}" data-route="step" data-claims="{claims}">'
                       f'<p class="entry-meta">{status}</p></article>' for kind, claims, status in entries)
        return route + '<section id="research-record">' + arts + '</section>'

    def notes(self, entries):
        return ' '.join(self.guide.guidance(self.body(entries), self.ft))

    def test_warns_after_finite_check(self):
        self.assertIn('will be rejected', self.notes([('research', 'ex:a', 'Finite check.')]))

    def test_no_warning_after_proof_or_review(self):
        self.assertNotIn('will be rejected', self.notes([('research', 'lem:a', 'Working proof.')]))
        self.assertNotIn('will be rejected', self.notes([('research', 'ex:a', 'Finite check.'),
                                                          ('review', 'none', 'Route review.')]))

    def test_review_period_warnings(self):
        five = [('research', 'lem:a', 'Working proof.')] * (self.ft.REVIEW_PERIOD - 1)
        self.assertIn('one more research entry is allowed', self.notes(five))
        six = five + [('research', 'lem:b', 'Working proof.')]
        self.assertIn('must be a route review', self.notes(six))

    def test_silent_without_route_items(self):
        self.assertEqual(self.guide.guidance('<section id="research-record"></section>', self.ft), [])


if __name__ == '__main__':
    unittest.main()
