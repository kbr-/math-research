"""An independent recomputation of top_search.json, without tools/pc_closure.py.

System: functional pigeonhole over F_2, n+1 pigeons, n holes, multilinear, at (n, D, K) = (3, 2, 1), (4, 2, 1),
(5, 3, 2). H is spanned by the non-matching monomials, so reduction modulo H deletes them. By
lem:closure-degree-locality, C_D cap V_{D-1} = C_{D-1}, so C_D is spanned modulo H by the products m Q_i with
m a monomial of degree <= D-1 (multilinear, non-matching terms deleted), and C cap V_K by those with deg m <= K-1
together with H; elimination here is a pivot table on bit vectors over the matching monomials, written here.
For E_A = sum_{j<a} x1j + sum_{j>=a} x2j it computes the C-side dim{u in V_K : uE in C} and the best domain side
max over representatives E' of dim({u : uE' in H} + C cap V_K), V_K being all multilinear monomials of degree <= K.
Statement tested: the excesses of top_search.json (0,1,1,0; 0,0,1,0,0; 0,0,12,12,0,0) by a second route.
Expected: the same C-sides, domain sides and excesses as top_search.json.
Refuted by: any C-side or domain side differing from top_search.json for some |A| and size.
Possible because: either route could hold a bug, or the closure description used here could miss members.
Control: the independent route must give the recorded x00 C-side at 4x3 (9, witness.json); asserted.
Refuted by: a C-side for x00 other than 9 at 4x3.
Possible because: an indexing or reduction error in the bit-vector elimination.
Positive control: the 4x3 witness u = 1 + x12 + x22 must kill E = x10 + x21 + x22 here; asserted.
Refuted by: the witness product not reducing to zero modulo the span.
Possible because: the span could lack the pigeon-axiom products the witness identity uses.
Baseline: the bare count bounds each excess by dim V_K minus the domain part; it decides nothing.
Record checked: the claims read were lem:closure-degree-locality (the closure description),
check:dense-linear-kernels and conj:linear-kernel-transfer; none decides these numbers.
"""
import argparse
import itertools
import json
import pathlib


class Board:
    def __init__(self, n):
        self.n, self.m = n, n + 1
        self.cells = self.m * n

    def var(self, i, j):
        return 1 << (i * self.n + j)

    def matching(self, mono):
        cs = [k for k in range(self.cells) if mono >> k & 1]
        return len({k // self.n for k in cs}) == len(cs) == len({k % self.n for k in cs})

    def monomials(self, d):
        out = []
        for k in range(d + 1):
            for cs in itertools.combinations(range(self.cells), k):
                out.append(sum(1 << c for c in cs))
        return out

    def Q(self, i):
        return {0} | {self.var(i, j) for j in range(self.n)}


def mul(a, b):
    out = set()
    for s in a:
        for t in b:
            out ^= {s | t}
    return out


class Elim:
    """Bit-vector span over an index of matching monomials; non-matching monomials are deleted (they lie in H)."""

    def __init__(self, board, index):
        self.b, self.index, self.piv = board, index, {}

    def vec(self, poly):
        x = 0
        for t in poly:
            if self.b.matching(t):
                x ^= 1 << self.index[t]
        return x

    def reduce(self, x):
        """The canonical remainder: every pivot bit cleared. (The first run returned at the first non-pivot top
        bit, a non-canonical remainder, and gave negative excesses; independent_top_run1.json.)"""
        r = 0
        while x:
            h = x.bit_length() - 1
            if h in self.piv:
                x ^= self.piv[h]
            else:
                r |= 1 << h
                x ^= 1 << h
        return r

    def add(self, x):
        x = self.reduce(x)
        if x:
            self.piv[x.bit_length() - 1] = x
            return True
        return False


def closure(board, D, deg_m):
    """Modulo H: the span of m Q_i over monomials m of degree <= deg_m."""
    index = {t: k for k, t in enumerate(t for t in board.monomials(D) if board.matching(t))}
    span = Elim(board, index)
    for t in board.monomials(deg_m):
        if board.matching(t):
            for i in range(board.m):
                span.add(span.vec(mul({t}, board.Q(i))))
    return span


def kernel_dim(span, E, VK, extra=None):
    """dim{u in span(VK) : uE in span}, plus, when extra (a list of polynomials in V_K) is given, the dimension
    of that kernel added to span(extra) inside V_K."""
    img, rank = Elim(span.b, span.index), 0
    tags = {}
    kernel = []
    for k, t in enumerate(VK):
        x = span.reduce(span.vec(mul({t}, E)))
        tag = 1 << k
        while x:
            h = x.bit_length() - 1
            if h not in img.piv:
                break
            x ^= img.piv[h]
            tag ^= tags[h]
        if x:
            img.piv[x.bit_length() - 1] = x
            tags[x.bit_length() - 1] = tag
        else:
            kernel.append(tag)
    if extra is None:
        return len(kernel)
    vk = {t: k for k, t in enumerate(VK)}
    space = {}

    def add(x):
        while x:
            h = x.bit_length() - 1
            if h not in space:
                space[h] = x
                return
            x ^= space[h]

    for x in kernel:
        add(x)
    for p in extra:
        x = 0
        for t in p:
            x ^= 1 << vk[t]
        add(x)
    return len(space)


def case(n, D, K, out):
    b = Board(n)
    span = closure(b, D, D - 1)
    VK = b.monomials(K)
    zero = Elim(b, span.index)                         # modulo H only
    CK = [mul({t}, b.Q(i)) for t in b.monomials(K - 1) for i in range(b.m)]
    CK += [{t} for t in VK if not b.matching(t)]
    reps = []
    for c in itertools.product((0, 1), repeat=b.m):
        s = set()
        for i in [i for i, ci in enumerate(c) if ci]:
            s ^= b.Q(i)
        reps.append(s)
    rows = []
    for a in range(n + 1):
        E = {b.var(1, j) for j in range(a)} | {b.var(2, j) for j in range(a, n)}
        cside = kernel_dim(span, E, VK)
        best = max(kernel_dim(zero, E ^ s, VK, CK) for s in reps)
        rows.append({'|A|': a, 'C_side': cside, 'best_H_side': best, 'excess': cside - best})
    out[f'{n + 1}x{n} D={D} K={K}'] = rows
    print(f'{n + 1}x{n} D={D} K={K}', [(r['|A|'], r['C_side'], r['best_H_side'], r['excess']) for r in rows],
          flush=True)
    return b, span


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    out = {}
    b, span = case(3, 2, 1, out)
    assert kernel_dim(span, {b.var(0, 0)}, b.monomials(1)) == 9, 'control x00'
    u = {0, b.var(1, 2), b.var(2, 2)}
    assert span.reduce(span.vec(mul(u, {b.var(1, 0), b.var(2, 1), b.var(2, 2)}))) == 0, 'positive control'
    case(4, 2, 1, out)
    case(5, 3, 2, out)
    recorded = json.loads(pathlib.Path(__file__).with_name('top_search.json').read_text())
    out['agrees_with_top_search'] = all(out[k] == recorded[k] for k in recorded)
    print('agrees with top_search.json:', out['agrees_with_top_search'], flush=True)
    pathlib.Path(args.out).write_text(json.dumps(out, indent=1) + '\n')


if __name__ == '__main__':
    main()
