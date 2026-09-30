#!/usr/bin/env python3
"""Check the antidiagonal description of neck corner Newton polygons against saved runs (cycle bmd-20261001-j).

Conjecture tested (conj:cube-neck-corner-antidiagonal-polygon): for the neck (m,n) let N_s be the number of
cells (k,l) of [0,m) x [0,n) with k + l < s, and c_1 < ... < c_M, M = (m-1)(n-1), the integers of
[1, mn-1] other than N_1, ..., N_{m+n-2}.  The lower boundary of the Newton polygon of the corner Pluecker
vector has the vertices v_r = (c_1 + ... + c_r, (mn - c_{r+1}) + ... + (mn - c_M)), r = 0..M, so its support
function is h(w) = min_r w . v_r; along a weight in the open normal cone of v_r the flat limit is the
complete linear system L((m-1+r)[0] + (mn-m-r)[1]); at a weight normal to the edge [v_r, v_{r+1}] the limit
has pole orders (m+r, mn-m-r).

Inputs: the saved outputs of research/tools/bmd_cube_neck_corner_polygon.gp (first run: formatted h lines;
fan run: raw h list) and bmd_cube_neck_corner_limits.gp (raw [h, alpha, beta] lists).  Reports every
mismatch and the number of compared values.
"""
import argparse
import ast
import re


def edge_params(m, n):
    starts = set()
    for s in range(1, m + n - 1):
        starts.add(sum(1 for k in range(m) for l in range(n) if k + l < s))
    return [c for c in range(1, m * n) if c not in starts]


def vertices(m, n):
    c = edge_params(m, n)
    assert len(c) == (m - 1) * (n - 1)
    mn = m * n
    return [(sum(c[:r]), sum(mn - x for x in c[r:])) for r in range(len(c) + 1)]


def predict(m, n, w):
    vs = vertices(m, n)
    vals = [w[0] * a + w[1] * b for a, b in vs]
    h = min(vals)
    arg = [r for r, v in enumerate(vals) if v == h]
    mn = m * n
    if len(arg) == 1:
        r = arg[0]
        return h, (m - 1 + r, mn - m - r)
    assert len(arg) == 2 and arg[1] == arg[0] + 1, (m, n, w, arg)
    r = arg[0]
    return h, (m + r, mn - m - r)


def raw_list(text, prefix):
    for line in text.splitlines():
        if line.startswith(prefix):
            tasks, _, res = line[len(prefix):].partition(": ")
            return ast.literal_eval(tasks), ast.literal_eval(res)
    raise SystemExit(f"no raw line {prefix!r}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--first", required=True)
    ap.add_argument("--fan", required=True)
    ap.add_argument("--limits", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    lines, bad, nh, nl = [], [], 0, 0
    for line in open(a.first).read().splitlines():
        mm = re.match(r"\(m,n\)=\((\d+),(\d+)\)", line)
        m, n = int(mm.group(1)), int(mm.group(2))
        for w1, w2, h in re.findall(r"\((\d+),(\d+)\):(\d+)\[", line):
            w, h = (int(w1), int(w2)), int(h)
            nh += 1
            if predict(m, n, w)[0] != h:
                bad.append(f"first run {(m, n)} w={w}: h={h}, predicted {predict(m, n, w)[0]}")
    tasks, res = raw_list(open(a.fan).read(), "raw h for tasks ")
    for (m, n, w1, w2), h in zip(tasks, res):
        nh += 1
        if predict(m, n, (w1, w2))[0] != h:
            bad.append(f"fan run {(m, n)} w={(w1, w2)}: h={h}, predicted {predict(m, n, (w1, w2))[0]}")
    for path in a.limits:
        tasks, res = raw_list(open(path).read(), "raw [h, alpha, beta] x two coefficient pairs for tasks ")
        for (m, n, w1, w2), rr in zip(tasks, res):
            ph, pp = predict(m, n, (w1, w2))
            for h, al, be in rr:
                nh += 1
                nl += 1
                if h != ph or (al, be) != pp:
                    bad.append(f"limits {path}: {(m, n)} w={(w1, w2)}: h={h} poles {(al, be)}, predicted {ph} {pp}")
    for m, n in [(2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (3, 3), (3, 4), (4, 4)]:
        vs = vertices(m, n)
        axis = m * n * (m - 1) * (n - 1) // 2
        assert vs[-1] == (axis, 0) and vs[0] == (0, axis)
        lines.append(f"({m},{n}): edge parameters {edge_params(m, n)}; vertices {vs}")
    lines.append(f"compared {nh} support-function values and {nl} limit pole pairs; mismatches: {len(bad)}")
    lines += bad
    open(a.out, "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
