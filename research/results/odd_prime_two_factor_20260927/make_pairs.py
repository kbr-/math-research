"""Pairs for the collinear-pencil test (27 September 2026), with the triangle-pair prediction.

For each pencil (l1, l2) on m = 3 rows and N columns it writes a line "N|label|l1|l2" and prints whether the
triangle-pair lemma already excludes membership in R_4: some disjoint column triples X, Y with
F_{X,Y} = D_X(1)(x)D_Y(2) + D_X(2)(x)D_Y(1) + D_X(12)(x)D_Y(12) != 0 in Lambda^2 V (x) Lambda^2 V, where
D_X(l, l') = (alpha(x)beta' + alpha'(x)beta)/2 on the triple's column vectors (alpha = u1 - u3, beta = u2 - u3)
and a(x)b is represented by the cross product. Rank-one pencils (collinear on every triple) have F = 0 everywhere.
Usage: make_pairs.py OUT
"""
import itertools, random, sys

P = 3


def cross(a, b):
    return ((a[1]*b[2]-a[2]*b[1]) % P, (a[2]*b[0]-a[0]*b[2]) % P, (a[0]*b[1]-a[1]*b[0]) % P)


def D(cols, X, other=None):
    u = [cols[c] for c in X]
    al, be = [(u[0][i]-u[2][i]) % P for i in range(3)], [(u[1][i]-u[2][i]) % P for i in range(3)]
    if other is None:
        return cross(al, be)
    v = [other[c] for c in X]
    al2, be2 = [(v[0][i]-v[2][i]) % P for i in range(3)], [(v[1][i]-v[2][i]) % P for i in range(3)]
    s = [(x+y) % P for x, y in zip(cross(al, be2), cross(al2, be))]
    return tuple((2*x) % P for x in s)          # 1/2 = 2 mod 3


def detected(l1, l2):
    N = len(l1)
    for X in itertools.combinations(range(N), 3):
        rest = [c for c in range(N) if c not in X]
        a1, a2, a12 = D(l1, X), D(l2, X), D(l1, X, l2)
        for Y in itertools.combinations(rest, 3):
            b1, b2, b12 = D(l1, Y), D(l2, Y), D(l1, Y, l2)
            for i in range(3):
                for j in range(3):
                    if (a1[i]*b2[j] + a2[i]*b1[j] + a12[i]*b12[j]) % P:
                        return True
    return False


def rank_one(lam, q):
    return [tuple((l*x) % P for x in q) for l in lam]


def fmt(cols):
    return ' '.join(''.join(str(x) for x in c) for c in cols)


def main():
    rnd = random.Random(20260927)
    lines = []
    for N in (8, 10):
        pm = [2 if c < 4 else 1 for c in range(N)]
        lam = [rnd.randrange(3) for _ in range(N)]
        mu = [rnd.randrange(3) for _ in range(N)]
        lam2 = [rnd.choice((1, 2)) for _ in range(N)]
        pencils = {
            'common-profile-sign': (rank_one(pm, (1, 0, 0)), rank_one(pm, (0, 1, 0))),
            'common-profile-dense-rows': (rank_one(lam, (1, 2, 1)), rank_one(lam, (0, 1, 2))),
            'common-profile-affine': (rank_one(lam, (1, 1, 0)), rank_one([(2*x+1) % 3 for x in lam], (0, 1, 1))),
            'common-row-general': (rank_one(lam, (1, 1, 2)), rank_one(mu, (1, 1, 2))),
            'common-row-sign': (rank_one(pm, (1, 0, 2)), rank_one(lam2, (1, 0, 2))),
            'control-rank-one-independent': (rank_one(lam, (1, 0, 0)), rank_one(mu, (0, 1, 0))),
            'control-opposite-overlap': ([(1, 0, 0), (2, 0, 0)] + [(0, 0, 0)]*(N-2),
                                         [(0, 0, 0), (0, 1, 0), (0, 2, 0)] + [(0, 0, 0)]*(N-3)),
            'control-dense': ([tuple(rnd.randrange(3) for _ in range(3)) for _ in range(N)],
                              [tuple(rnd.randrange(3) for _ in range(3)) for _ in range(N)]),
        }
        for label, (a, b) in pencils.items():
            lines.append(f'{N}|{label}|{fmt(a)}|{fmt(b)}')
            print(f'N={N} {label}: triangle-pair lemma excludes R: {detected(a, b)}', flush=True)
    open(sys.argv[1], 'w').write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()
