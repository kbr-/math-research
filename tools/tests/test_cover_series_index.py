"""The product-series indices agree with hand counts and with a direct series product."""
import importlib.util
import pathlib
import unittest
from math import comb

SPEC = importlib.util.spec_from_file_location(
    'cover_series_index', pathlib.Path(__file__).resolve().parents[1] / 'cover_series_index.py')
CSI = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CSI)


class IndexTest(unittest.TestCase):
    def test_hand_counts(self):
        # n = 18, w = 4, 342 rows: c_6 = C(18,6) - 342 C(14,2) < 0 and the partial sum turns there too
        self.assertEqual(CSI.coefficients(18, 4, 342)[:7],
                         [1, 18, 153, 816, 3060 - 342, 8568 - 342 * 14, 18564 - 342 * 91])
        self.assertEqual(CSI.indices(18, 4, 342), (6, 6))
        self.assertEqual(CSI.indices(10, 3, 110), (4, 4))

    def test_agrees_with_the_polynomial_product(self):
        # for wM <= n the series is the polynomial (1+z)^(n-wM) ((1+z)^w - z^w)^M
        n, w, rows = 9, 2, 3
        poly = [comb(n - w * rows, i) for i in range(n - w * rows + 1)]
        factor = [comb(w, i) for i in range(w)]
        for _ in range(rows):
            poly = [sum(poly[i] * factor[d - i] for i in range(len(poly)) if 0 <= d - i < len(factor))
                    for d in range(len(poly) + len(factor) - 1)]
        self.assertEqual(CSI.coefficients(n, w, rows)[:len(poly)], poly)
        self.assertEqual(CSI.indices(n, w, rows), (7, None))

    def test_level_profile(self):
        # binomial coefficients of the cube on 20 variables: the dimension at level 5 is 20, twice 2j
        profile = CSI.level_profile([comb(20, d) for d in range(21)], 6)
        self.assertEqual((profile['last_level'], profile['kk_dimension'], profile['ratio_to_2j']), (5, 20.0, 2.0))
        self.assertTrue(profile['increasing_at_end'])
        # n = 18, w = 4, 342 rows: last positive level 5 with c_5 = 3780, between binom(15,5) = 3003 and
        # binom(16,5) = 4368
        profile = CSI.level_profile(CSI.coefficients(18, 4, 342), 6)
        self.assertTrue(15 < profile['kk_dimension'] < 16)

    def test_mixed_codimensions(self):
        # one kind of row agrees with the closed form, also when wM exceeds n; two kinds split a product
        for n, w, rows in ((9, 2, 3), (10, 3, 110), (12, 2, 9)):
            self.assertEqual(CSI.mixed_coefficients(n, [(w, rows)]), CSI.coefficients(n, w, rows))
        self.assertEqual(CSI.mixed_coefficients(10, [(3, 4), (3, 6)]), CSI.coefficients(10, 3, 10))
        # n = 4, rows of codimension 1 and 2: (1+z)(1)(1+2z) = 1 + 3z + 2z^2
        self.assertEqual(CSI.mixed_coefficients(4, [(1, 1), (2, 1)]), [1, 3, 2, 0, 0])
        self.assertEqual(CSI.indices(4, None, None, [(1, 1), (2, 1)]), (3, None))


if __name__ == '__main__':
    unittest.main()
