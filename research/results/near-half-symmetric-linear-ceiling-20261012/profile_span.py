"""The least height at which two flats leave no symmetric static barrier, by the span of their profiles over F_2.

Setting (lem:symmetric-profile-criterion, lem:flat-profile-parity).  A flat V = {l_1 = c_1, ..., l_w = c_w} in
F_2^n is given by the sizes alpha[mu] of its atoms, mu in 1..2^w - 1 the membership vector of a variable in the
forms, alpha[0] the variables in no form, and c.  Its profile with T, pi_{V,T}(z) = sum of z^|x| over x in V with
x_T = 1, divided by (1+z)^n and written in u = z/(1+z), is
    u^|T| * P(O', c'),   P(O, c) = sum over S inside O with XOR(S) = c of u^|S| (1+u)^(|O|-|S|),
O' the labels of the atoms whose size less the variables of T in them is odd, c' = c + XOR of the labels of the
variables of T.  A symmetric barrier at D against a family exists iff 1 is NOT in the F_2-span of these polynomials
over its rows and all |T| <= D - w.  The script computes, for a row V_0 through the origin and a row V_1 through
the all-ones point, the least D* at which 1 is in the span: no symmetric barrier at any D >= D*.

Statement tested (the entry's proposition): if V_0 and V_1 have codimension w and each at least 5w variables in
no form, then D* <= 5w - 2.
Refuted by: an instance with 5w free variables in each row and D* above 5w - 2, or none through the cap.
Possible because: the elimination uses only the profiles and knows nothing of the divisor argument of the proof.

Control one, the formula against the definition: at n <= 12 the profile computed by enumeration of the flat.
Refuted by: any of the sampled (V, T) where the two polynomials differ.
Possible because: the formula's bookkeeping of parities and of c' is separate from the enumeration of points.

Control two, a recorded value (prop:all-odd-dense-row-ceiling): a single linear row with all atoms odd and one
free variable, w >= 2, has D* = w + 1.
Refuted by: another value of D* for such a row at w = 2, 3 or 4.
Possible because: the recorded proof and this elimination share only the profile formula.

The dense case, rows with no variable outside their forms: no expectation is written.  D* linear in w there too
would close symmetric witnesses for such pairs of rows; a D* of the order of 2^w, or none through the cap, would
be a pair of dense rows with a symmetric barrier far above the width, the outcome the review of 12 October named
as the one that would matter.

Usage: profile_span.py OUT.json SEED WIDEST   (widths 1 to WIDEST; at width four fewer samples)
"""
import itertools
import json
import random
import sys


def profile_table(w, odd, c):
    """P(O, c') for every c', O the labels in `odd`: a list of polynomials in u, bit i the coefficient of u^i."""
    dp = [0] * (1 << w)
    dp[0] = 1
    for mu in odd:
        dp = [(dp[x] ^ (dp[x] << 1)) ^ (dp[x ^ mu] << 1) for x in range(1 << w)]
    return dp[c]


def generators(w, alpha, c, limit):
    """{shift: set of polynomials}: u^shift * P for every way of fixing at most `limit` variables to one,
    shift = |T|: one variable in each atom of tau, then free variables one at a time and pairs inside an atom."""
    labels = range(1, 1 << w)
    odd = {mu for mu in labels if alpha[mu] % 2}
    nonempty = [mu for mu in labels if alpha[mu]]
    found = {}
    for size in range(len(nonempty) + 1):
        for tau in itertools.combinations(nonempty, size):
            shifted_c = c
            for mu in tau:
                shifted_c ^= mu
            poly = profile_table(w, sorted(odd ^ set(tau)), shifted_c)
            pairs = sum((alpha[mu] - (mu in tau)) // 2 for mu in labels)
            top = min(limit, size + alpha[0] + 2 * pairs)
            for shift in range(size, top + 1, 1 if alpha[0] else 2):
                found.setdefault(shift, set()).add(poly)
    return found


def least_height(w, rows, cap):
    """The least D <= cap with 1 in the span of u^|T| P over the rows and |T| <= D - w; None if there is none."""
    tables = [generators(w, alpha, c, cap - w) for alpha, c in rows]
    basis = {}

    def reduce(value):
        while value:
            low = value & -value
            if low not in basis:
                return value
            value ^= basis[low]
        return 0

    for budget in range(cap - w + 1):
        for table in tables:
            for poly in table.get(budget, ()):
                value = reduce(poly << budget)
                if value:
                    basis[value & -value] = value
        if reduce(1) == 0:
            return w + budget
    return None


def through_ones(w, alpha):
    c = 0
    for mu in range(1, 1 << w):
        if alpha[mu] % 2:
            c ^= mu
    return c


def enumerated_profile(w, alpha, c, t):
    """The profile of the flat by enumeration, normalised: sum over points of u^|x| (1+u)^(n-|x|)."""
    owner = [mu for mu in range(1 << w) for _ in range(alpha[mu])]
    n, fixed = len(owner), []
    for mu in range(1 << w):
        first = owner.index(mu) if alpha[mu] else 0
        fixed += list(range(first, first + t[mu]))
    total = 0
    for x in range(1 << n):
        if any(not x >> i & 1 for i in fixed):
            continue
        value = 0
        for i in range(n):
            if x >> i & 1:
                value ^= owner[i]
        if value != c:
            continue
        weight = bin(x).count('1')
        term = 1 << weight
        for _ in range(n - weight):
            term ^= term << 1
        total ^= term
    return total


def formula_profile(w, alpha, c, t):
    odd = sorted(mu for mu in range(1, 1 << w) if (alpha[mu] - t[mu]) % 2)
    shifted = c
    for mu in range(1, 1 << w):
        if t[mu] % 2:
            shifted ^= mu
    return profile_table(w, odd, shifted) << sum(t)


def spanning(w, alpha):
    span = {0}
    for mu in range(1, 1 << w):
        if alpha[mu]:
            span |= {x ^ mu for x in span}
    return len(span) == 1 << w


def random_alpha(w, rng, free, low, high):
    while True:
        alpha = [free] + [rng.randint(low, high) for _ in range((1 << w) - 1)]
        if spanning(w, alpha):
            return alpha


def main(out, seed, widest):
    rng = random.Random(seed)
    widths = range(1, widest + 1)
    report = {'formula': [], 'recorded': [], 'free': [], 'dense': []}
    for _ in range(40):                                              # control one
        w = rng.choice((1, 2, 3))
        while True:
            alpha = [rng.randint(0, 2)] + [rng.randint(0, 3) for _ in range((1 << w) - 1)]
            if sum(alpha) <= 12 and spanning(w, alpha):
                break
        c = rng.randrange(1 << w)
        t = [rng.randint(0, a) for a in alpha]
        same = enumerated_profile(w, alpha, c, t) == formula_profile(w, alpha, c, t)
        report['formula'].append({'w': w, 'alpha': alpha, 'c': c, 't': t, 'agree': same})
    for w in widths[1:]:                                             # control two
        for _ in range(3 if w < 4 else 1):
            alpha = [1] + [rng.choice((1, 3, 5)) for _ in range((1 << w) - 1)]
            got = least_height(w, [(alpha, 0)], 6 * w + 8)
            report['recorded'].append({'w': w, 'alpha': alpha, 'height': got, 'expected': w + 1})
    for w in widths:                                                 # the statement
        for _ in range(12 if w < 4 else 2):
            first = random_alpha(w, rng, 5 * w, 0, 4)
            second = random_alpha(w, rng, 5 * w, 0, 4)
            got = least_height(w, [(first, 0), (second, through_ones(w, second))], 6 * w + 8)
            report['free'].append({'w': w, 'rows': [first, second], 'height': got, 'bound': 5 * w - 2,
                                   'within': got is not None and got <= 5 * w - 2})
    for w in widths:                                                 # the dense case
        for _ in range(40 if w < 4 else 3):
            first = random_alpha(w, rng, 0, 1 if w > 1 else 2, 5)
            second = random_alpha(w, rng, 0, 1 if w > 1 else 2, 5)
            cap = 2 ** (w + 1) + 2 * w + 6
            got = least_height(w, [(first, 0), (second, through_ones(w, second))], cap)
            report['dense'].append({'w': w, 'rows': [first, second], 'height': got, 'cap': cap})
    with open(out, 'w') as handle:
        json.dump(report, handle)
    summary = {
        'formula agrees': [sum(r['agree'] for r in report['formula']), len(report['formula'])],
        'recorded value met': [sum(r['height'] == r['expected'] for r in report['recorded']), len(report['recorded'])],
        'free rows within 5w - 2': [sum(r['within'] for r in report['free']), len(report['free'])],
        'free rows, largest height by w': {w: max((r['height'] or 10 ** 6) for r in report['free'] if r['w'] == w)
                                           for w in widths},
        'dense rows, heights by w': {w: sorted({(r['height'] if r['height'] is not None else 'none through cap')
                                                for r in report['dense'] if r['w'] == w}, key=str)
                                     for w in widths},
        'dense rows, caps by w': {w: 2 ** (w + 1) + 2 * w + 6 for w in widths},
    }
    print(json.dumps(summary))


if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
