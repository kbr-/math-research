import itertools
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import f2_span


def brute_span(vecs):
    out = set()
    for cs in itertools.product((0, 1), repeat=len(vecs)):
        x = 0
        for c, v in zip(cs, vecs):
            if c:
                x ^= v
        out.add(x)
    return out


class F2SpanTest(unittest.TestCase):
    def test_remainders_are_canonical(self):
        # The defect of 17 October 2026: an early-returning reduce left lower pivot bits set, so two vectors in
        # one class could reduce to different ints. Here x and x + (a span member) must reduce alike.
        rng = random.Random(1)
        for _ in range(200):
            vecs = [rng.getrandbits(8) for _ in range(rng.randint(1, 5))]
            s = f2_span.Span(vecs)
            members = brute_span(vecs)
            x = rng.getrandbits(8)
            for y in members:
                self.assertEqual(s.reduce(x), s.reduce(x ^ y))
            self.assertEqual(x in s, x in members)

    def test_the_early_exit_case(self):
        # pivots 0b110 (bit 2) and 0b001 (bit 0); x = 0b011 has a non-pivot top bit 1 and pivot bit 0 below it
        s = f2_span.Span([0b110, 0b001])
        self.assertEqual(s.reduce(0b011), 0b010)
        self.assertEqual(s.reduce(0b010), 0b010)

    def test_rank_and_kernel(self):
        s = f2_span.Span([0b11, 0b01, 0b10])
        self.assertEqual(len(s), 2)
        self.assertEqual(f2_span.kernel_dim([0b11, 0b01, 0b10, 0]), 2)


if __name__ == '__main__':
    unittest.main()
