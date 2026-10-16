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
        # Random width-2 clause systems on 4 variables: seed 3 gives some refuted at degree 2 and some
        # never refuted, so agreement is tested on both outcomes (asserted below).
        rng = random.Random(3)
        degrees = []
        for _ in range(6):
            n = 4
            axioms = []
            for _ in range(rng.randint(6, 12)):
                p = {0}
                for v in rng.sample(range(n), 2):
                    p = pc.multiply(p, {1 << v} if rng.random() < 0.5 else {0, 1 << v})
                axioms.append(p)
            ours = pc.refutation_degree(axioms, n, 4)
            degrees.append(ours)
            with self.subTest(axioms=axioms):
                self.assertEqual(ours, tb.pc_degree([to_exponents(a, n) for a in axioms], n, 4))
        self.assertTrue(any(d is not None and d >= 2 for d in degrees) and None in degrees, degrees)

    def test_remainders_are_canonical(self):
        axioms, n = php(3, 2)
        c = pc.Closure(axioms, n, 2)
        self.assertTrue(c.proper)
        f = {0b11, 0b100, 0}
        for row in c.rows.values():
            self.assertEqual(c.remainder(f ^ c.poly(row)), c.remainder(f))

    def test_a_cancelling_top_term_member_is_multiplied(self):
        # x0 x1 and x0 x1 + x2 are degree-2 members whose sum x2 has degree 1 < D = 2, so x2 x3 must enter.
        c = pc.Closure([{0b11}, {0b11, 0b100}], 4, 2)
        self.assertTrue(c.contains({0b1100}))

    def test_a_monomial_above_the_degree_is_refused(self):
        c = pc.Closure([], 3, 1)
        with self.assertRaises(ValueError):
            c.contains({0b11})
        with self.assertRaises(ValueError):
            c.contains({0b1000})


if __name__ == '__main__':
    unittest.main()
