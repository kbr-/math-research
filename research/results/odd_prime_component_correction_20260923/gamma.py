"""Graded dimensions of the weak unary PHP top algebra A over F_3 at n (argument, default 6) through degree 6 (sizing count for the board
version of the low-density test), from a4lib's component-wise quotients."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_degree_four_20260923'))
import a4lib as L
n = int(sys.argv[1]) if len(sys.argv) > 1 else 6; L.setup(n)
for k in range(1, 7):
    Q, g = L.quotient(k, 4); print(k, g, flush=True)
