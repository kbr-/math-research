"""Tests for tools/pc_closure.py against tools/truncated_buchberger.py and closure invariants."""
import itertools
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import pc_closure as pc  # noqa: E402
import truncated_buchberger as tb  # noqa: E402


def to_exponents(poly, n):
    return {tuple(1 if m >> i & 1 else 0 for i in range(n)) for m in poly}


def php(m, n):
    v = lambda i, j: i * n + j
    axioms = []
    for i in range(m):
        p = {0}
        for j in range(n):
            p = pc.multiply(p, {0, 1 << v(i, j)})
        axioms.append(p)
    for j in range(n):
        for i, k in itertools.combinations(range(m), 2):
            axioms.append({(1 << v(i, j)) | (1 << v(k, j))})
    return axioms, m * n


class PCClosureTest(unittest.TestCase):
    def test_refutation_degree_agrees_with_truncated_buchberger(self):
        axioms, n = php(3, 2)
        ours = pc.refutation_degree(axioms, n, 4)
        theirs = tb.pc_degree([to_exponents(a, n) for a in axioms], n, 4)
        self.assertEqual(ours, theirs)
        self.assertEqual(ours, 3)
        rng = random.Random(7)
        for _ in range(6):
            n = 4
            axioms = [{rng.randrange(1 << n) for _ in range(rng.randint(1, 3))} for _ in range(rng.randint(1, 4))]
            axioms = [a for a in axioms if a]
            with self.subTest(axioms=axioms):
                self.assertEqual(pc.refutation_degree(axioms, n, 4),
                                 tb.pc_degree([to_exponents(a, n) for a in axioms], n, 4))

    def test_remainders_are_canonical_and_membership_is_closed_under_low_multiplication(self):
        axioms, n = php(3, 2)
        c = pc.Closure(axioms, n, 2)
        self.assertTrue(c.proper)
        members = [c.poly(row) for row in c.rows.values()]
        f = {0b11, 0b100, 0}
        for g in members:
            self.assertEqual(c.remainder(f ^ g), c.remainder(f))
            if pc.degree(g) < c.D:
                for x in range(n):
                    self.assertTrue(c.contains(pc.multiply(g, {1 << x})))

    def test_a_cancelling_top_term_member_is_multiplied(self):
        # x0 x1 and x0 x1 + x2 are degree-2 members whose sum x2 has degree 1 < D = 2, so x2 x3 must enter.
        c = pc.Closure([{0b11}, {0b11, 0b100}], 4, 2)
        self.assertTrue(c.contains({0b1100}))

    def test_a_monomial_above_the_degree_is_refused(self):
        c = pc.Closure([], 3, 1)
        with self.assertRaises(ValueError):
            c.contains({0b11})


if __name__ == '__main__':
    unittest.main()
