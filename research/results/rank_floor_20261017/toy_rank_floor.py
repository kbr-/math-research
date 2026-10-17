"""Tests the leading-term step of the dense product rank floor in the cut-free model, where the quotient is the
whole group algebra F_2[F_3^E] and every class is a single character, so goodness holds trivially.

Statement tested (the lemma's triangularity step, without the cut space): for s disjoint edge pairs with
psi_i = e_{a_i} + e_{b_i}, a binary t-by-s matrix C, q_j = sum_i C_ji m_{psi_i} and P = prod_j (1 + q_j), let
the frame of a character alpha of support at most K be its unpaired part, its touched pairs R' whose value is
not psi_i, and those values, and S_alpha the pairs where alpha equals psi_i.  If C restricted to the columns
outside R' has rank t, with pivot set T_0(R') the lexicographically first t columns there of nonzero
determinant, and S_alpha avoids T_0, then lambda(alpha) = alpha + psi_{T_0} is the largest character of
P m_alpha in the order (support, frame, lex with T_0 first), lambda is injective, and the matrix of the rows
P m_alpha on the columns lambda(A) is triangular with unit diagonal; so rank(P on V_K) >= |A|.

Expected before the run: on every instance the triangularity and injectivity checks pass, the computed rank is
at least |A|, and the top-degree part of P equals sum_T det(C_T) m_{psi_T}.
Refuted by: a row whose largest character in that order is not lambda(alpha), or a computed rank below |A|.
Possible because: the order compares lex only inside a frame, and a term of P m_alpha could fall in another frame
or above lambda(alpha) if the proof's support count were wrong.
Positive control: the same checks with T_0 replaced by a column set of zero determinant must report a failing
diagonal on every instance where such a set exists; that the check sees a zero diagonal is what it shows.
Baseline: lem:sparse-weight-survival's bound h(K)/s_P, s_P the number of characters of P, printed beside the rank.
Record checked: cor:pair-sector-bounds (its (ii) bound c >= number of sectors met) and lem:sparse-weight-survival,
read in this turn; neither gives the rank of P inside a sector, so neither decides these instances.
"""
import itertools
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
from f2_span import Span   # noqa: E402  (tested canonical elimination)


def det2(rows):
    """Determinant over F_2 of a square 0/1 matrix given as a list of int bitmasks."""
    rows, n = list(rows), len(rows)
    for col in range(n):
        piv = next((r for r in range(col, n) if rows[r] >> col & 1), None)
        if piv is None:
            return 0
        rows[col], rows[piv] = rows[piv], rows[col]
        for r in range(n):
            if r != col and rows[r] >> col & 1:
                rows[r] ^= rows[col]
    return 1


def run(m, s, t, K, C, zero_pivot=False):
    pairs = [(2 * i, 2 * i + 1) for i in range(s)]
    unpaired = list(range(2 * s, m))
    psi = [tuple(1 if e in p else 0 for e in range(m)) for p in pairs]
    add = lambda a, b: tuple((x + y) % 3 for x, y in zip(a, b))
    zero = (0,) * m
    # P as a set of characters with coefficient 1 over F_2 (binary coefficients, exact products)
    P = {zero}
    for j in range(t):
        factor = {zero} | {psi[i] for i in range(s) if C[j][i]}
        new = {}
        for a in P:
            for b in factor:
                c = add(a, b)
                new[c] = new.get(c, 0) ^ 1
        P = {c for c, v in new.items() if v}
    supp = lambda a: sum(1 for x in a if x)
    top = {c for c in P if supp(c) == 2 * t}
    expect_top = set()
    for T in itertools.combinations(range(s), t):
        if det2([sum(C[j][i] << k for k, i in enumerate(T)) for j in range(t)]):
            v = zero
            for i in T:
                v = add(v, psi[i])
            expect_top.add(v)
    assert top == expect_top, 'top part of P differs from sum_T det(C_T) m_psi_T'

    def frame(a):
        R, S = [], []
        for i, (x, y) in enumerate(pairs):
            v = (a[x], a[y])
            if v == (0, 0):
                continue
            (S if v == (1, 1) else R).append(i)
        return tuple(a[e] for e in unpaired), tuple((i, a[pairs[i][0]], a[pairs[i][1]]) for i in R), R, S

    def pivots(R):
        cols = [i for i in range(s) if i not in R]
        for T in itertools.combinations(cols, t):
            d = det2([sum(C[j][i] << k for k, i in enumerate(T)) for j in range(t)])
            if d != zero_pivot:          # zero_pivot: the positive control takes a zero-determinant set
                return T
        return None

    ball = [a for a in itertools.product(range(3), repeat=m) if supp(a) <= K]
    A, lam = [], {}
    for a in ball:
        fu, fr, R, S = frame(a)
        T0 = pivots(R)
        if T0 is None or set(S) & set(T0):
            continue
        l = a
        for i in T0:
            l = add(l, psi[i])
        A.append(a)
        lam[a] = (l, T0)

    def key(c, T0):
        fu, fr, R, S = frame(c)
        order = list(T0) + [i for i in range(s) if i not in T0]
        return (supp(c), fu, fr, tuple(1 if i in S else 0 for i in order))

    # every term of P m_alpha sits at or below lambda(alpha) in alpha's own key order, and lambda is injective
    images = [lam[a][0] for a in A]
    assert len(set(images)) == len(images), 'lambda is not injective'
    failures = 0
    for a in A:
        l, T0 = lam[a]
        terms = {add(a, w) for w in P}
        top_terms = [c for c in terms if supp(c) == supp(l)]
        best = max(top_terms, key=lambda c: key(c, T0))
        failures += best != l or l not in terms
    # triangular with unit diagonal on the columns lambda(A): rows sorted by key of their lambda
    column = {l: k for k, l in enumerate(images)}
    span = Span()
    for a in A:
        row = 0
        for w in P:
            c = add(a, w)
            if c in column:
                row ^= 1 << column[c]
        span.add(row)
    index = {c: k for k, c in enumerate(itertools.product(range(3), repeat=m))}
    full = Span()
    for a in ball:
        row = 0
        for w in P:
            row ^= 1 << index[add(a, w)]
        full.add(row)
    return dict(ball=len(ball), A=len(A), rank_on_lambda=len(span), rank=len(full), chars=len(P),
                leading_failures=failures)


if __name__ == '__main__':
    rng = random.Random(20261017)
    cases = []
    for m, s, t, K in [(6, 3, 2, 2), (7, 3, 2, 3), (8, 4, 2, 3), (8, 4, 3, 2), (9, 4, 3, 3)]:
        for trial in range(3):
            while True:
                C = [[rng.randrange(2) for _ in range(s)] for _ in range(t)]

                if any(det2([sum(C[j][i] << k for k, i in enumerate(T)) for j in range(t)])
                       for T in itertools.combinations(range(s), t)):
                    break
            r = run(m, s, t, K, C)
            ok = r['leading_failures'] == 0 and r['rank_on_lambda'] == r['A'] and r['rank'] >= r['A']
            print(f'm={m} s={s} t={t} K={K} C={C}: ball {r["ball"]}, |A| {r["A"]}, rank on lambda(A) '
                  f'{r["rank_on_lambda"]}, rank {r["rank"]}, baseline ball/chars {r["ball"] / r["chars"]:.1f}, '
                  f'leading failures {r["leading_failures"]}: {"PASS" if ok else "FAIL"}')
            cases.append(ok)
            c = run(m, s, t, K, C, zero_pivot=True)
            print(f'  control with zero-determinant pivots: |A| {c["A"]}, rank on lambda(A) {c["rank_on_lambda"]}, '
                  f'leading failures {c["leading_failures"]}: '
                  f'{"SEEN" if c["A"] == 0 or c["leading_failures"] > 0 or c["rank_on_lambda"] < c["A"] else "MISSED"}')
    print(f'{sum(cases)} of {len(cases)} instances pass')
