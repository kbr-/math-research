"""Tests for tools/truncated_buchberger.py on tiny systems with known answers."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import truncated_buchberger as tb  # noqa: E402


def var(n, i):
    return tuple(1 if j == i else 0 for j in range(n))


ONE2 = (0, 0)


class TruncatedBuchbergerTest(unittest.TestCase):
    def test_contradictory_literals_refuted_in_degree_one(self):
        x = var(1, 0)
        self.assertEqual(tb.pc_degree([{x}, {x, (0,)}], 1, 3), 1)

    def test_satisfiable_system_has_no_refutation(self):
        x, y = var(2, 0), var(2, 1)
        # x + y + 1 = 0 has Boolean solutions.
        self.assertIsNone(tb.pc_degree([{x, y, ONE2}], 2, 4))

    def test_product_of_forms_needs_degree_two(self):
        x, y = var(2, 0), var(2, 1)
        xy = (1, 1)
        # xy = 0, x = 1, y = 1: the axiom xy has degree two, so nothing below two refutes.
        self.assertEqual(tb.pc_degree([{xy}, {x, ONE2}, {y, ONE2}], 2, 3), 2)

    def test_completion_satisfies_pair_condition(self):
        n = 3
        x, y, z = (var(n, i) for i in range(n))
        one = (0, 0, 0)
        axioms = [{(1, 1, 0), z}, {(0, 1, 1), x, one}]
        leads, const = tb.complete(tb.boolean_axioms(n) + axioms, 3)
        self.assertFalse(const)
        self.assertEqual(tb.check_pairs(list(leads.values()), 3), [])

    def test_check_pairs_reports_unresolved_pair(self):
        n = 2
        x, y = var(n, 0), var(n, 1)
        # S(xy + 1, x^2 + x) = xy + x reduces to x + 1, which no leading monomial divides.
        bad = tb.check_pairs([{(1, 1), ONE2}, {(2, 0), x}, {(0, 2), y}], 3)
        self.assertEqual([r for _, r in bad][0], frozenset({x, ONE2}))
        # xy + y with the Boolean axioms is resolved: it is y(x + 1), satisfiable.
        self.assertEqual(tb.check_pairs([{(1, 1), y}, {(2, 0), x}, {(0, 2), y}], 3), [])

    def test_affine_product_matches_hand_expansion(self):
        # (x0 + x1)(x1 + 1) = x0 x1 + x0 + x1^2 + x1
        poly = tb.affine_product(2, [(0b11, 0), (0b10, 1)])
        self.assertEqual(poly, {(1, 1), (1, 0), (0, 2), (0, 1)})

    def test_check_pairs_sees_equal_leading_monomials(self):
        x = var(1, 0)
        bad = tb.check_pairs([{x, (0,)}, {x}], 1)
        self.assertEqual([r for _, r in bad], [frozenset({(0,)})])

    def test_constant_axiom_has_degree_zero(self):
        self.assertEqual(tb.pc_degree([{(0,)}], 1, 2), 0)

    def test_agrees_with_brute_force_closure(self):
        # Reference: the degree-D closure by linear algebra on all monomials of degree <= D.
        import itertools
        import random
        n = 3
        monos = [m for m in itertools.product(range(4), repeat=n) if sum(m) <= 3]

        def closure_has_one(axioms, D):
            order = sorted((m for m in monos if sum(m) <= D), key=tb.key)
            idx = {m: i for i, m in enumerate(order)}
            basis = {}  # highest bit -> vector; a vector with highest bit h has degree deg(order[h])

            def insert(poly):
                v = 0
                for m in poly:
                    v ^= 1 << idx[m]
                while v:
                    h = v.bit_length() - 1
                    if h not in basis:
                        basis[h] = v
                        return True
                    v ^= basis[h]
                return False

            for a in tb.boolean_axioms(n) + axioms:
                if max(sum(m) for m in a) <= D:
                    insert(a)
            changed = True
            while changed:
                changed = False
                # the vectors with leading degree <= D-1 span the elements of degree <= D-1
                for h, v in list(basis.items()):
                    if sum(order[h]) <= D - 1:
                        poly = {order[i] for i in range(v.bit_length()) if v >> i & 1}
                        for i in range(n):
                            if insert(tb.mul(poly, var(n, i))):
                                changed = True
            return 0 in basis and basis[0] == 1

        rng = random.Random(7)
        seen = set()
        cube = [m for m in itertools.product(range(2), repeat=n)]
        for _ in range(40):
            axioms = [set(rng.sample(cube, rng.randint(1, 5))) for _ in range(rng.randint(1, 4))]
            for D in range(1, 4):
                _, const = tb.complete(tb.boolean_axioms(n) + [set(a) for a in axioms], D)
                self.assertEqual(const, closure_has_one(axioms, D), (axioms, D))
                seen.add((D, const))
        # both outcomes occur at the top cutoff, so the comparison is not vacuous
        self.assertTrue({(3, True), (3, False)} <= seen, seen)


if __name__ == "__main__":
    unittest.main()
