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


if __name__ == '__main__':
    unittest.main()
