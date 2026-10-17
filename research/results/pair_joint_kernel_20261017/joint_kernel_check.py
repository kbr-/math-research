#!/usr/bin/env python3
"""Pair products' joint kernel in sector 0: affine indicator killers against the exact joint kernel.

Model.  The sector of the charged quotient spanned by the pair characters is F[W], W = F_3^s, which over
F containing F_4 is the algebra of F-valued functions on the dual group, chi in {0,1,2}^s, with m_(psi_i) the
function chi -> omega^(chi_i).  A pair product P = prod_j (1 + q_j), q_j = sum_(i in S_j) m_(psi_i), acts by
pointwise multiplication; its kernel on a space of functions is the part supported on the zero set Z(P), and
the joint kernel of P_1..P_M is the part supported on the intersection of the Z(P_a), i.e. vanishing on
U = union of the nonzero sets NZ(P_a).  The degree filtration of sector 0 is the junta degree in the one-hot
bits x_i = [chi_i = 1], y_i = [chi_i = 2] (a character of W of support k pairs has edge degree 2k): V_k is
spanned by the cylinder indicators [chi_I = pi], pi in {1,2}^I, |I| <= k.  These are 0/1 functions, and U is
defined over F_2, so the joint kernel's dimension over F equals that of the F_2 evaluation matrix.

Statements tested.
(1) Parity description, all-parameter claim of the entry: 1 + q_S vanishes at chi exactly when
    sum_(i in S) x_i = sum_(i in S) y_i = 1 + |S| (mod 2).  Checked against the direct F_4 evaluation of
    q_S(chi) = sum omega^(chi_i), with F_4 written in the basis (1, omega), omega^2 = 1 + omega.
(2) Affine indicator kernel: for one row S_a chosen per product, the set A of chi satisfying every chosen
    row's two parities lies in every Z(P_a), so 1_A is in the joint kernel, and its junta degree is at most
    min(2 r, |union of S_a|), r the F_2-rank of the chosen rows.
(3) Hypothesis H (an expectation, not a statement of the entry): on every instance where no row choice gives
    a nonempty A whose indicator has junta degree <= k, the joint kernel of V_k is zero.
Expected before the run: (1) and (2) hold on every instance; H holds on every instance that the bare count
does not already decide.
Refuted by: (1) a point where the parity rule and the direct F_4 value of 1 + q_S disagree; (2) a choice with
    1_A nonzero on some NZ(P_a), or of junta degree above min(2r, |union|); (3) an instance with no affine
    killer of degree <= k whose joint kernel dimension is positive.
Possible because: the derivation of (1) uses n_0 + n_1 + n_2 = |S| and omega^2 = 1 + omega, either of which
    a slip can break; for (3) a function supported on a union of factor zero sets of every product need not
    contain one affine set inside each product's zero set, so killers that are not affine indicators may exist.
Control: the parity rule with the wrong constant |S| in place of 1 + |S|; it must disagree with the direct
    value at some point of every instance, and its sets A' must fail to lie in Z(P_a) on some instance.
Refuted by: the wrong rule agreeing with the direct values everywhere.
Possible because: a constant shift of both parities moves the set, which the check would miss only if the
    direct evaluation were itself computed from the rule under test.
Positive control: coordinate products (unit rows), M of them all reading coordinate 0, whose transversal {0}
    gives the killer [chi_0 = 0] of degree 1 (lem:cylinder-killer-degree (b)); the joint kernel must be
    nonzero there and the affine search must find a killer.
Baseline: the bare count, joint kernel dimension >= dim V_k - |U|, decides an instance only when |U| < dim V_k;
    the product of denominators (prop:multiplier-transfer-limits) gives the single-factor indicators' product,
    junta degree <= 2M, which is the affine search restricted to rank M; the script prints which instances
    the count decides, and H is judged only on the others.
Record checked: lem:cylinder-killer-degree (coordinate products: killer degree = transversal number),
    prop:multiplier-transfer-limits (product of denominators, additive cost), lem:pair-product-rank-floor
    (a single product's rank floor); together they decide the coordinate case and not the dense one.
"""
import argparse
import itertools
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'tools'))
import f2_span  # noqa: E402  (tested canonical elimination, for the cross-check of the packed rank)

# F_4 in the basis (1, omega): code (a, b) for a + b omega; omega^0 = 1, omega^1 = omega, omega^2 = 1 + omega.
POWER = np.array([[1, 0], [0, 1], [1, 1]], dtype=np.uint8)


def grid(s):
    return np.array(list(itertools.product(range(3), repeat=s)), dtype=np.uint8)


def one_plus_q_zero_direct(points, row):
    """[1 + q_S(chi) = 0] from the F_4 sum of omega^(chi_i) over S: 1 + q = 0 iff q = 1 = code (1, 0)."""
    q = np.zeros((len(points), 2), dtype=np.uint8)
    for i in np.flatnonzero(row):
        q ^= POWER[points[:, i]]
    return (q[:, 0] == 1) & (q[:, 1] == 0)


def parity_zero(points, row, shift=1):
    """The parity rule: sum_S x = sum_S y = shift + |S| (mod 2); shift=1 is the claimed rule, 0 the control."""
    idx = np.flatnonzero(row)
    x = (points[:, idx] == 1).sum(1) % 2
    y = (points[:, idx] == 2).sum(1) % 2
    c = (shift + len(idx)) % 2
    return (x == c) & (y == c)


def junta_degree(values, s):
    """Junta degree of a 0/1 function on {0,1,2}^s in the one-hot basis {1, x_i, y_i}: interpolate over F_2 axis
    by axis (c_1 = f(0), c_x = f(1) + f(0), c_y = f(2) + f(0)) and return the largest number of non-constant
    factors among nonzero coefficients; -1 for the zero function."""
    f = values.reshape((3,) * s).astype(np.uint8)
    for axis in range(s):
        f = np.moveaxis(f, axis, 0)
        f = np.stack([f[0], f[1] ^ f[0], f[2] ^ f[0]])
        f = np.moveaxis(f, 0, axis)
    nz = np.argwhere(f)
    return int((nz != 0).sum(1).max()) if len(nz) else -1


def monomials(points, s, k):
    """Columns: cylinder indicators [chi_I = pi], pi in {1,2}^I, |I| <= k, which span V_k."""
    cols = []
    for size in range(k + 1):
        for I in itertools.combinations(range(s), size):
            for pi in itertools.product((1, 2), repeat=size):
                cols.append(np.all(points[:, list(I)] == np.array(pi, dtype=np.uint8), axis=1)
                            if size else np.ones(len(points), dtype=bool))
    return np.array(cols, dtype=bool).T          # points x monomials


def rank_f2(matrix):
    """Rank over F_2 of a 0/1 matrix by elimination on packed rows (numpy XOR of whole rows per pivot)."""
    a = np.packbits(matrix.astype(np.uint8), axis=1)
    rows, ncols = matrix.shape[0], matrix.shape[1]
    rank = 0
    for c in range(ncols):
        byte, bit = divmod(c, 8)
        col = (a[rank:, byte] >> (7 - bit)) & 1
        hit = np.flatnonzero(col)
        if not len(hit):
            continue
        p = rank + hit[0]
        if p != rank:
            a[[rank, p]] = a[[p, rank]]
        below = rank + 1 + np.flatnonzero((a[rank + 1:, byte] >> (7 - bit)) & 1)
        a[below] ^= a[rank]
        rank += 1
        if rank == rows:
            break
    return rank


def rank_f2_reference(matrix):
    """The same rank by tools/f2_span.py, columns as integers (slow; used on a sample as a cross-check)."""
    images = [int(''.join('1' if v else '0' for v in matrix[:, j]) or '0', 2) for j in range(matrix.shape[1])]
    return matrix.shape[1] - f2_span.kernel_dim(images)


def instance(rng, s, t, M, kind):
    if kind == 'dense':
        mats = []
        for _ in range(M):
            while True:
                C = rng.integers(0, 2, size=(t, s), dtype=np.uint8)
                if C.any(1).all() and np.linalg.matrix_rank(C.astype(float)) == t:   # nonzero rows; a real rank
                    break
            mats.append(C)
        return mats
    # coordinate products, every one reading coordinate 0 and t-1 other coordinates
    mats = []
    for _ in range(M):
        others = rng.choice(np.arange(1, s), size=t - 1, replace=False)
        C = np.zeros((t, s), dtype=np.uint8)
        C[0, 0] = 1
        for j, i in enumerate(others, 1):
            C[j, i] = 1
        mats.append(C)
    return mats


def run_instance(points, s, k, mats, mono, check_reference):
    out = {'M': len(mats), 't': int(mats[0].shape[0])}
    # (1) parity description, and the control with the wrong constant
    agree = control_differs = True
    zero = []
    for C in mats:
        zs = []
        for row in C:
            direct = one_plus_q_zero_direct(points, row)
            agree &= bool(np.array_equal(direct, parity_zero(points, row)))
            control_differs &= not np.array_equal(direct, parity_zero(points, row, shift=0))
            zs.append(direct)
        zero.append(zs)
    out['parity_rule_agrees'] = agree
    out['control_rule_differs'] = control_differs
    nz = np.zeros(len(points), dtype=bool)
    for zs in zero:
        nz |= ~np.any(zs, axis=0)
    out['U'] = int(nz.sum())
    # exact joint kernel of V_k
    sub = mono[nz]
    r = rank_f2(sub) if len(sub) else 0
    if check_reference:
        assert r == rank_f2_reference(sub), 'packed rank disagrees with tools/f2_span.py'
        out['rank_cross_checked'] = True
    out['dim_Vk'] = int(mono.shape[1])
    out['kernel_dim'] = int(mono.shape[1] - r)
    out['count_decides'] = out['U'] < out['dim_Vk']
    # (2) affine indicator killers over all row choices
    best = None
    killers = 0
    control_fail = False
    for choice in itertools.product(*[range(C.shape[0]) for C in mats]):
        rows = np.array([C[j] for C, j in zip(mats, choice)])
        A = np.ones(len(points), dtype=bool)
        for row in rows:
            A &= parity_zero(points, row)
        if not A.any():
            continue
        Ac = np.ones(len(points), dtype=bool)
        for row in rows:
            Ac &= parity_zero(points, row, shift=0)
        if Ac.any() and (Ac & nz).any():
            control_fail = True        # the wrong rule's set meets some NZ(P_a): seen
        assert not (A & nz).any(), 'an affine indicator meets a nonzero set'
        rank2 = len(f2_span.Span(int(''.join(map(str, row)), 2) for row in rows).piv)
        # a nonempty A needs every dependency among the chosen rows to have even length: (S_a, 1) has rank r
        assert len(f2_span.Span(int(''.join(map(str, row)) + '1', 2) for row in rows).piv) == rank2
        union = int(rows.any(0).sum())
        deg = junta_degree(A, s)
        assert deg <= min(2 * rank2, union), (deg, rank2, union)
        best = deg if best is None else min(best, deg)
        killers += deg <= k
    out['affine_killer_min_degree'] = best
    out['affine_killers_of_degree_le_k'] = killers
    out['control_sets_meet_U'] = control_fail
    out['H_tested'] = not out['count_decides'] and killers == 0
    out['H_refuted'] = out['H_tested'] and out['kernel_dim'] > 0
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--smallest', action='store_true', help='the plumbing run: s = 4, k = 2, M <= 2')
    args = ap.parse_args()
    t0 = time.time()
    rng = np.random.default_rng(20261017)
    results = []
    lines = []
    sizes = ((4, 2),) if args.smallest else ((6, 2), (7, 2), (7, 3), (8, 3))
    for s, k in sizes:
        points = grid(s)
        mono = monomials(points, s, k)
        for t in (2, 3):
            for M in range(1, 3 if args.smallest else (8 if s < 8 else 6)):
                for seed in range(3):
                    for kind in (('dense', 'coordinate') if seed == 0 else ('dense',)):
                        mats = instance(rng, s, t, M, kind)
                        out = run_instance(points, s, k, mats, mono, check_reference=(s <= 6 and seed == 0))
                        out.update(s=s, k=k, kind=kind, seed=seed)
                        results.append(out)
                        lines.append(f"s={s} k={k} t={t} M={M} {kind:10s} seed={seed}: |U|={out['U']:5d} dimVk="
                                     f"{out['dim_Vk']:4d} kernel={out['kernel_dim']:4d} affine min deg="
                                     f"{out['affine_killer_min_degree']} killers<=k={out['affine_killers_of_degree_le_k']}"
                                     f" count_decides={out['count_decides']} H_refuted={out['H_refuted']}")
                        print(lines[-1], flush=True)
    summary = {
        'instances': len(results),
        'parity_rule_agrees_everywhere': all(r['parity_rule_agrees'] for r in results),
        'control_rule_differs_everywhere': all(r['control_rule_differs'] for r in results),
        'control_sets_meet_U_somewhere': any(r['control_sets_meet_U'] for r in results),
        'positive_control_kernels_nonzero': all(r['kernel_dim'] > 0 and r['affine_killers_of_degree_le_k'] > 0
                                                for r in results if r['kind'] == 'coordinate'),
        'rank_cross_checks': sum(1 for r in results if r.get('rank_cross_checked')),
        'count_decides': sum(r['count_decides'] for r in results),
        'H_tested': sum(r['H_tested'] for r in results),
        'H_refuted': sum(r['H_refuted'] for r in results),
        'dense_with_kernel_but_no_affine_killer': [
            {k: r[k] for k in ('s', 'k', 't', 'M', 'seed', 'U', 'kernel_dim', 'affine_killer_min_degree')}
            for r in results if r['kind'] == 'dense' and r['kernel_dim'] > 0 and r['affine_killers_of_degree_le_k'] == 0],
        'seconds': round(time.time() - t0, 1),
    }
    Path(args.out).write_text(json.dumps({'summary': summary, 'instances': results}, indent=1) + '\n')
    print(json.dumps(summary, indent=1))


if __name__ == '__main__':
    main()
