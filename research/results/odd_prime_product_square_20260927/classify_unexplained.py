"""Classify the product-square kernel's unexplained members of R (27 September 2026).

Tested statement (shifted vanishing): an unexplained pair l1, l2 (l1^2 l2^2 in R_4, no factor single-column modulo
the row sums, product nonzero as drawn) has row-sum shifts rho_1, rho_2 with (l1-rho_1)^2 (l2-rho_2)^2 = 0 in the
collision algebra. Shifts are tried exhaustively (3^m each). Input: the kernel's output; tiny polynomials only.
Usage: classify_unexplained.py OUTPUT
"""
import itertools, re, sys


def square(cols):
    """cols: list of column vectors; returns l^2 as {frozenset of (column,row): coeff mod 3}."""
    cells = [(c, i, a) for c, u in enumerate(cols) for i, a in enumerate(u) if a]
    out = {}
    for (c, i, a), (d, j, b) in itertools.permutations(cells, 2):
        if c != d:
            k = frozenset([(c, i), (d, j)])
            out[k] = (out.get(k, 0) + a * b) % 3
    return {k: v for k, v in out.items() if v}


def product(p, q):
    out = {}
    for k1, a in p.items():
        cols1 = {c for c, _ in k1}
        for k2, b in q.items():
            if cols1 & {c for c, _ in k2}:
                continue
            k = k1 | k2
            out[k] = (out.get(k, 0) + a * b) % 3
    return {k: v for k, v in out.items() if v}


def parse(text):
    return [[int(ch) for ch in col] for col in text.split()]


def vanishes_after_shift(a, b, m):
    shifts = list(itertools.product(range(3), repeat=m))
    sq_b = {s: square([[(x - y) % 3 for x, y in zip(u, s)] for u in b]) for s in shifts}
    for s in shifts:
        sa = square([[(x - y) % 3 for x, y in zip(u, s)] for u in a])
        for t in shifts:
            if not product(sa, sq_b[t]):
                return s, t
    return None


def main():
    board = None
    for line in open(sys.argv[1]):
        if line.startswith('m='):
            board = line.split(' seed')[0]
        mt = re.match(r'\s+unexplained: l1 columns (.*) \| l2 columns (.*)', line)
        if mt:
            a, b = parse(mt.group(1)), parse(mt.group(2))
            found = vanishes_after_shift(a, b, len(a[0]))
            print(board, '|', mt.group(1), '|', mt.group(2), '|',
                  f'vanishes after shifts {found}' if found else 'no shift makes the product vanish', flush=True)


if __name__ == '__main__':
    main()
