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

    def test_goal_level_and_cadence_notes(self):
        research = ('research', 'lem:a', 'Working proof.')
        def with_review(after):
            body = self.body([('review', 'none', 'Route review.')] + [research] * after)
            return ' '.join(self.guide.guidance(body.replace('data-kind="review"',
                                                             'data-kind="review" data-open-items="3"'), self.ft))
        self.assertIn('declared 3 open items. If the review declares 3 or more, it must be goal-level',
                      with_review(self.ft.CONVERGENCE_SPAN))
        self.assertIn('must be an ordinary route review, not goal-level', with_review(self.ft.REVIEW_PERIOD))
        self.assertIn('the next review comes after', with_review(2))

    def test_route_notes_once_when_articles_carry_route_items(self):
        five = [('research', 'lem:a', 'Working proof.')] * (self.ft.REVIEW_PERIOD - 1)
        body = self.body(five).replace('data-route="step"', 'data-route="step" data-route-item="step"')
        notes = ' '.join(self.guide.guidance(body, self.ft))
        self.assertEqual(notes.count('one more research entry is allowed'), 1)

    def test_computation_and_generalization_notes(self):
        notes = self.notes([('research', 'lem:a', 'Working proof.')])
        self.assertIn('C or C++ kernels', notes)
        self.assertIn('propose a general statement and attempt to prove it', notes)
        self.assertIn(self.guide.CASES_PLEA, notes)

    def test_algebra_systems_note(self):
        body = self.body([('research', 'lem:a', 'Working proof.')])
        present = ' '.join(self.guide.guidance(body, self.ft, which=lambda b: '/usr/bin/' + b if b in ('M2', 'Singular') else None))
        self.assertIn('Macaulay2 (M2), Singular (Singular)', present)
        self.assertIn('far beyond Groebner bases', present)
        self.assertNotIn('msolve', present)
        absent = ' '.join(self.guide.guidance(body, self.ft, which=lambda b: None))
        self.assertNotIn('computer algebra', absent)

    def test_kernel_libraries_note(self):
        body = self.body([('research', 'lem:a', 'Working proof.')])
        present = ' '.join(self.guide.guidance(body, self.ft, has=lambda h: h.startswith('flint/')))
        self.assertIn('libraries for your own C/C++ kernels: FLINT (nmod_mat', present)
        self.assertIn('-lflint -lgmp', present)
        self.assertNotIn('LinBox', present)
        absent = ' '.join(self.guide.guidance(body, self.ft, has=lambda h: False))
        self.assertNotIn('C/C++ kernels:', absent)

    def test_silent_without_route_items(self):
        self.assertEqual(self.guide.guidance('<section id="research-record"></section>', self.ft), [])


if __name__ == '__main__':
    unittest.main()
