"""The F_2 closure-degree kernel against forced values and the truncated Buchberger reference."""
import json
import pathlib
import random
import shutil
import subprocess
import sys
import tempfile
import unittest

TOOLS = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import truncated_buchberger as tb

SOURCE = TOOLS / 'f2_closure_degree.cpp'


def terms(n, mask, const):
    """The monomials, as bit masks, of the affine form with linear part `mask` and constant `const`."""
    return [1 << i for i in range(n) if mask >> i & 1] + ([0] if const else [])


class KernelTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = tempfile.mkdtemp()
        cls.binary = str(pathlib.Path(cls.dir) / 'fcd')
        subprocess.run(['g++', '-O1', '-o', cls.binary, str(SOURCE)], check=True)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.dir)

    def degree(self, n, polys, dmax):
        path = pathlib.Path(self.dir) / 'instance.txt'
        path.write_text(f'{n} {len(polys)}\n' + ''.join(
            f'{len(p)} ' + ' '.join(map(str, p)) + '\n' for p in polys))
        out = subprocess.run([self.binary, str(path), str(dmax)], check=True, capture_output=True, text=True).stdout
        return json.loads(out)

    def test_forced_values(self):
        self.assertEqual(self.degree(1, [[1], [0, 1]], 3)['degree'], 1)          # y and 1 + y
        self.assertEqual(self.degree(2, [[0]], 3)['degree'], 0)                  # the constant itself
        self.assertIsNone(self.degree(2, [[1], [2]], 2)['degree'])               # satisfiable: y1 = y2 = 0
        self.assertEqual(self.degree(2, [[1], [2]], 2)['dimensions']['2'], 3)    # all monomials but the constant
        # pairwise products, y1 + y2 + y3 and (1 + y1)(1 + y2): refuted at degree two, not one
        rows = [[3], [5], [6], [1, 2, 4], [0, 1, 2, 3]]
        self.assertEqual(self.degree(3, rows, 3)['degree'], 2)
        # four variables, each an axiom, with the product of the (1 + y_i): refuted exactly when that axiom
        # of degree four may be used
        rows = [[1], [2], [4], [8], list(range(16))]
        self.assertEqual(self.degree(4, rows, 5)['degree'], 4)
        self.assertIsNone(self.degree(4, rows, 3)['degree'])

    def test_more_variables_than_a_table_of_the_cube_allows(self):
        top = 1 << 39
        self.assertEqual(self.degree(40, [[top], [0, top]], 2)['degree'], 1)     # y40 and 1 + y40
        singles = [[1 << i] for i in range(40)]
        self.assertEqual(self.degree(40, singles, 1)['dimensions']['1'], 40)     # satisfiable; all linear monomials
        # the forty y_i with (1 + y1)(1 + y40): refuted exactly when the quadratic axiom may be used
        rows = singles + [[0, 1, top, 1 | top]]
        self.assertIsNone(self.degree(40, rows, 1)['degree'])
        self.assertEqual(self.degree(40, rows, 2)['degree'], 2)

    def test_agrees_with_the_reference_on_products_of_two_forms(self):
        rng = random.Random(5)
        for trial in range(4):
            n, polys = 6, []
            for _ in range(18):
                first, second = (terms(n, rng.randrange(1, 1 << n), rng.randrange(2)) for _ in range(2))
                product = set()
                for a in first:
                    for b in second:
                        product ^= {a | b}                # multilinear: y^2 = y
                polys.append(sorted(product))
            reference = [{tuple(1 if m >> i & 1 else 0 for i in range(n)) for m in p} for p in polys]
            with self.subTest(trial=trial):
                self.assertEqual(self.degree(n, polys, 4)['degree'], tb.pc_degree(reference, n, 4))

    def test_closure_dimensions_agree_with_the_membership_module(self):
        # tools/pc_closure.py shares this kernel's elimination design, so agreement checks both
        # implementations, not the closure convention (that rests on truncated_buchberger).
        import pc_closure as pc
        rng = random.Random(11)
        for trial in range(4):
            n = 5
            polys = [sorted({rng.randrange(1 << n) for _ in range(rng.randint(1, 3))})
                     for _ in range(rng.randint(2, 5))]
            out = self.degree(n, polys, 3)
            for D, dim in out['dimensions'].items():
                with self.subTest(trial=trial, D=D):
                    closure = pc.Closure([set(p) for p in polys], n, int(D))
                    self.assertTrue(closure.proper)
                    self.assertEqual(closure.dim, dim)


if __name__ == '__main__':
    unittest.main()
