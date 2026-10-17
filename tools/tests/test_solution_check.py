import contextlib
import io
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import solution_check as sc


def run(*arguments):
    said = io.StringIO()
    with contextlib.redirect_stdout(said):
        status = sc.main(list(arguments))
    return status, said.getvalue()


class SolutionCheckTest(unittest.TestCase):
    def test_the_case_that_exposed_it_is_refuted_in_characteristic_3(self):
        status, said = run('--pigeons', '4', '--holes', '8', '--prime', '3', 'x00*x11 + x00*x11*x22 + x00*x11*x33')
        self.assertEqual(status, 1)
        self.assertIn('nonzero mod 3', said)

    def test_the_first_family_product_passes_in_characteristic_3_and_fails_in_2(self):
        # x00*x11*(1 + x00 + x11) = 3*x00*x11 multilinearly: zero in characteristic 3, not in 2
        family_one = 'x00*x11 + x00*x11 + x00*x11'
        status, said = run('--pigeons', '4', '--holes', '8', '--prime', '3', family_one)
        self.assertEqual(status, 0)
        self.assertIn('membership is not shown', said)
        self.assertEqual(run('--pigeons', '4', '--holes', '8', '--prime', '2', family_one)[0], 1)

    def test_the_exposing_product_fails_in_characteristic_2_at_another_solution(self):
        # 1 + 1 + 0 = 0 at 2->2, 3->4, but 2->5 gives 1: the refutation holds in every characteristic
        self.assertEqual(run('--pigeons', '4', '--holes', '8', '--prime', '2', 'x00*x11 + x00*x11*x22 + x00*x11*x33')[0], 1)

    def test_a_true_member_is_not_refuted(self):
        # x00 * (pigeon axiom of pigeon 0) reduces to members of the hole and functionality span
        axiom = '1 - x00 - x01 - x02 - x03'
        status, _ = run('--pigeons', '3', '--holes', '4', '--prime', '5', axiom)
        self.assertEqual(status, 0)

    def test_functionality_and_hole_monomials_vanish(self):
        self.assertEqual(run('--pigeons', '3', '--holes', '4', '--prime', '3', 'x00*x01 + 2*x10*x20')[0], 0)

    def test_more_pigeons_than_holes_decides_nothing(self):
        self.assertEqual(run('--pigeons', '4', '--holes', '3', '--prime', '3', 'x00')[0], 2)

    def test_parsing(self):
        self.assertEqual(sc.parse('2*x01*x12 - x3_10 + 1'), [(2, [(0, 1), (1, 2)]), (-1, [(3, 10)]), (1, [])])
        with self.assertRaises(ValueError):
            sc.parse('y00')

    def test_sampling_when_the_board_is_large(self):
        witness, count = sc.check(6, 12, 3, 'x00', limit=50)
        self.assertIsNotNone(witness)
        self.assertLessEqual(count, 50)


if __name__ == '__main__':
    unittest.main()
