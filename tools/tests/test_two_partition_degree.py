"""The two-partition degree kernel against forced values and an independent closure in the x variables."""
import json
import pathlib
import shutil
import subprocess
import tempfile
import unittest
from itertools import combinations

SOURCE = pathlib.Path(__file__).resolve().parents[1] / 'two_partition_degree.cpp'


def reference_has_one(m, w, bblock, d):
    """Degree-d PC closure over F_2 in the x variables, all Boolean monomials: is 1 in it?"""
    monos = sorted((frozenset(c) for k in range(d + 1) for c in combinations(range(m), k)),
                   key=lambda t: (-len(t), sorted(t)))
    index = {t: i for i, t in enumerate(monos)}

    def vec(terms):
        v = 0
        for t in terms:
            v ^= 1 << index[t]
        return v

    gens = []
    for a in range(m // w):
        for c in combinations(range(a * w, (a + 1) * w), w // 2 + 1):
            if len(c) <= d:
                gens.append(vec([frozenset(c)]))
    for b in range(m // w):
        block = [i for i in range(m) if bblock[i] == b]
        for c in combinations(block, w // 2 if w // 2 <= d else w + 1):
            gens.append(vec([frozenset(u) for k in range(len(c) + 1) for u in combinations(c, k)]))
    basis, queue = {}, []

    def insert(v):
        while v:
            p = (v & -v).bit_length() - 1
            if p not in basis:
                basis[p] = v
                if len(monos[p]) < d:
                    queue.append(p)
                return
            v ^= basis[p]

    for g in gens:
        insert(g)
    one = index[frozenset()]
    done = 0
    while done < len(queue) and one not in basis:
        v = basis[queue[done]]
        done += 1
        terms = [monos[i] for i in range(len(monos)) if v >> i & 1]
        for x in range(m):
            out = {}
            for t in terms:
                u = t | {x}
                out[u] = out.get(u, 0) ^ 1
            insert(vec([u for u, c in out.items() if c]))
    return one in basis


class KernelTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = tempfile.mkdtemp()
        cls.binary = str(pathlib.Path(cls.dir) / 'tpd')
        subprocess.run(['g++', '-O1', '-fopenmp', '-o', cls.binary, str(SOURCE)], check=True)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.dir)

    def run_kernel(self, *args):
        out = subprocess.run([self.binary, *map(str, args)], check=True, capture_output=True, text=True).stdout
        return [json.loads(line) for line in out.splitlines()]

    def test_forced_values(self):
        # w = 4: the ceiling m/2 - m/w + 1 = 3 equals the axioms' degree, so the degree is 3
        for row in self.run_kernel(8, 4, 'same', 'spread', 'random:1'):
            self.assertEqual((row['ceiling'], row['degree']), (3, 3))
        # B = A at w = 6: each block alone is the threshold system on six variables, degree 4
        self.assertEqual(self.run_kernel(12, 6, 'same')[0]['degree'], 4)

    def test_against_reference_closure(self):
        # w = 4, m = 8 in the x variables at degree 2, below the axioms' degree 3: no refutation either way;
        # and at degree 3, where both must find 1
        row = self.run_kernel(8, 4, 'spread')[0]
        self.assertEqual(row['b_block'], [i % 2 for i in range(8)])
        self.assertTrue(reference_has_one(8, 4, row['b_block'], 3))
        self.assertFalse(reference_has_one(8, 4, row['b_block'], 2))
        self.assertEqual(row['closures'][0], {'d': 3, 'monomials': 25, 'dim': row['closures'][0]['dim'], 'one': True})

    def test_degree_cap_reports_null(self):
        row = self.run_kernel(18, 6, 'dmax=4', 'spread')[0]
        self.assertIsNone(row['degree'])
        self.assertFalse(row['closures'][0]['one'])
        # the independent closure in the x variables agrees on this negative case and on a positive one
        self.assertFalse(reference_has_one(18, 6, row['b_block'], 4))
        positive = self.run_kernel(12, 6, 'dmax=4', 'spread')[0]
        self.assertTrue(positive['closures'][0]['one'])
        self.assertTrue(reference_has_one(12, 6, positive['b_block'], 4))


if __name__ == '__main__':
    unittest.main()
