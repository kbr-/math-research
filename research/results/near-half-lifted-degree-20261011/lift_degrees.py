#!/usr/bin/env python3
"""Plain and frame degrees of systems lifted by products of pairs, exact, over F_2.

Statement tested.  For an unsatisfiable system H of polynomials of degree at most w_H in y_1..y_m (Boolean
axioms built in), let G = H(x_1 x_2, x_3 x_4, ...) on 2m variables, and let P be G written with a new variable
z_i for each pair, with the axioms z_i + x_{2i-1} x_{2i}, z_i x_{2i-1} + z_i, z_i x_{2i} + z_i and H(z): the
part of the product-tree frame at height one.  Proved on record: d(H) <= d(G) <= 2 d(H) and
d(P) <= max{d(H), 2 w_H}.  The question: is d(G) larger than d(P), that is, do the product variables lower the
degree, and is d(G) = 2 d(H)?

The degrees are computed by tools/f2_closure_degree.cpp (exact degree-D closures).  Instances: the pigeonhole
principle with 3 pigeons and 2 holes in clause polynomials (6 variables), and random systems of quadratic
polynomials on 8 variables (seeded), kept when unsatisfiable (checked on all 256 points) and when d(H) > 2,
so that the axioms' own degree does not decide the answer.

Expected before the run.
- Controls: every instance has d(H) <= d(G) <= 2 d(H) and d(P) <= max{d(H), 4}; a violation means the
  generator or the tool is wrong.  d(P) >= d(H) as well (set every second variable of a pair to one).
- Hypothesis (doubling): d(G) = 2 d(H) on every instance with d(H) >= 3.  Alternative: d(G) < 2 d(H) on some
  instance.  For d(H) = 3 the possible values of d(G) are 4, 5, 6 (the lifted axioms have degree 4), so the
  run separates "6" from "4 or 5"; and d(P) <= 4 < 6 would show the product variables lowering the degree
  by two at this size.  I expect doubling but have no proof; the count of instances with d(H) >= 3 is printed
  and the run decides nothing if it is zero.
"""
import argparse
import itertools
import json
import os
import random
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "..", "..", "..", "tools", "f2_closure_degree.cpp")


def degree(binary, nvars, polys, dmax, workdir, name):
    path = os.path.join(workdir, name)
    with open(path, "w") as fh:
        fh.write(f"{nvars} {len(polys)}\n")
        for p in polys:
            fh.write(f"{len(p)} " + " ".join(str(t) for t in sorted(p)) + "\n")
    out = subprocess.run([binary, path, str(dmax)], check=True, capture_output=True, text=True).stdout
    return json.loads(out)["degree"]


def mul(p, q):
    r = set()
    for a, b in itertools.product(p, q):
        r ^= {a | b}
    return frozenset(r)


def php(pigeons, holes):
    var = lambda i, j: 1 << (i * holes + j)
    polys = []
    for i in range(pigeons):
        p = frozenset({0})
        for j in range(holes):
            p = mul(p, frozenset({0, var(i, j)}))
        polys.append(p)
    for j in range(holes):
        for i, k in itertools.combinations(range(pigeons), 2):
            polys.append(frozenset({var(i, j) | var(k, j)}))
    return pigeons * holes, polys


def random_quadratic(m, rows, seed):
    rng = random.Random(seed)
    monos = [0] + [1 << i for i in range(m)] + [(1 << i) | (1 << j) for i, j in itertools.combinations(range(m), 2)]
    return m, [frozenset(t for t in monos if rng.random() < 0.3) or frozenset({0}) for _ in range(rows)]


def satisfiable(m, polys):
    for x in range(1 << m):
        if all(sum(1 for t in p if t & x == t) % 2 == 0 for p in polys):
            return True
    return False


def lift_mask(t, m, shift=0):
    return sum(3 << (2 * i + shift) for i in range(m) if t >> i & 1)


def lifted(m, polys):
    return 2 * m, [frozenset(lift_mask(t, m) for t in p) for p in polys]


def pair_frame(m, polys):
    """Variables x_0..x_{2m-1}, then z_0..z_{m-1}."""
    z = lambda i: 1 << (2 * m + i)
    out = [frozenset(sum(z(i) for i in range(m) if t >> i & 1) for t in p) for p in polys]
    for i in range(m):
        a, b = 1 << (2 * i), 1 << (2 * i + 1)
        out += [frozenset({z(i), a | b}), frozenset({z(i) | a, z(i)}), frozenset({z(i) | b, z(i)})]
    return 3 * m, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seeds", type=int, default=40)
    args = ap.parse_args()
    with tempfile.TemporaryDirectory() as work, open(args.out, "w") as fh:
        binary = os.path.join(work, "closure")
        subprocess.run(["g++", "-O2", "-o", binary, SOURCE], check=True)
        instances = [("php 3 pigeons 2 holes",) + php(3, 2)]
        instances += [(f"random quadratic m=8 rows=9 seed={s}",) + random_quadratic(8, 9, s) for s in range(args.seeds)]
        informative = 0
        for name, m, polys in instances:
            if satisfiable(m, polys):
                continue
            dh = degree(binary, m, polys, m, work, "h.txt")
            if dh is None or dh < 3:
                fh.write(f"{name}: d(H)={dh}, skipped (axioms' degree decides)\n")
                continue
            dg = degree(binary, *lifted(m, polys), 2 * dh, work, "g.txt")
            dp = degree(binary, *pair_frame(m, polys), max(dh, 4), work, "p.txt")
            assert dg is not None and dh <= dg <= 2 * dh, (name, dh, dg)
            assert dp is not None and dh <= dp <= max(dh, 4), (name, dh, dp)
            informative += 1
            fh.write(f"{name}: d(H)={dh} d(G)={dg} d(P)={dp} doubling={dg == 2 * dh}\n")
            fh.flush()
        fh.write(f"instances with d(H) >= 3: {informative}\n")
    print("done")


if __name__ == "__main__":
    main()
