"""Independent check of the base-block certificates written by bmd_four_base_block.py.

For each m in [MMIN, MMAX] (H(m) = 2 floor(m/8) + ceil((m mod 8)/2)) it reuses the builder's row construction (bmd_four_base_block.rows) and
checks over F_2[y1, y2, B], by expanding polynomials in Python:
  * at h = H(m): the EXIST vector w satisfies every condition, sum_u w_u X_{row,u} = 0, and
    its last component is 1 (so savings H(m) are attained for every B, and every l after
    multiplying by y1^l);
  * at h = H(m)+1: some NONEX polynomial f has y-coefficients whose gcd over F_2[B] is a power of
    1+B (so f is a nonzero polynomial in y for every B != 1), and f e_m equals
    sum_r LAMBDA_r row_r in the last coordinate while the other coordinates cancel, i.e.
    sum_r LAMBDA_r row_r = f e_m (so w^(m) = 0 for every solution and every B).
Usage: bmd_four_base_verify.py CERTDIR MMIN MMAX
"""
import re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from bmd_four_base_block import rows, poly_mul


def parse(text):
    """Singular polynomial in y1, y2, B over F_2 -> {(i, j, e): 1}."""
    text = text.strip()
    p = {}
    if text == '0':
        return p
    for term in text.split('+'):
        key = [0, 0, 0]
        for f in term.split('*'):
            mt = re.fullmatch(r'(y1|y2|B)(?:\^(\d+))?', f)
            if f == '1':
                continue
            assert mt, f'unparsed factor {f!r}'
            key[{'y1': 0, 'y2': 1, 'B': 2}[mt.group(1)]] += int(mt.group(2) or 1)
        key = tuple(key)
        p[key] = (p.get(key, 0) + 1) % 2
    return {k: v for k, v in p.items() if v}


def add(p, q):
    r = dict(p)
    for k, v in q.items():
        r[k] = (r.get(k, 0) + v) % 2
    return {k: v for k, v in r.items() if v}


def bpoly(f, mono):
    """The coefficient of the y-monomial mono in f, as a polynomial in B over F_2 (bitmask)."""
    return sum(1 << k[2] for k in f if (k[0], k[1]) == mono)


def gf2_mod(a, b):
    while a and a.bit_length() >= b.bit_length():
        a ^= b << (a.bit_length() - b.bit_length())
    return a


def gf2_gcd(a, b):
    while b:
        a, b = b, gf2_mod(a, b)
    return a


def content_is_power_of_1_plus_B(f):
    g = 0
    for mono in {(k[0], k[1]) for k in f}:
        g = gf2_gcd(g, bpoly(f, mono))
    while g > 1 and gf2_mod(g, 0b11) == 0:  # divide by 1 + B
        q, r = 0, g
        while r.bit_length() >= 2:
            sh = r.bit_length() - 2
            q ^= 1 << sh
            r ^= 0b11 << sh
        g = q
    return g == 1


def main():
    cert = Path(sys.argv[1])
    mmin, mmax = int(sys.argv[2]), int(sys.argv[3])
    ok = True
    for m in range(mmin, mmax + 1):
        h0 = 2 * (m // 8) + (m % 8 + 1) // 2
        lines = (cert / f'm{m}-h{h0}.out').read_text().split('\n')
        w = {int(l.split()[1]): parse(l.split(maxsplit=2)[2]) for l in lines if l.startswith('EXIST')}
        good = len(w) == m + 1 and w[m] == {(0, 0, 0): 1}
        for _, row in rows(m, h0):
            acc = {}
            for u in range(m + 1):
                acc = add(acc, poly_mul(w[u], row[u]))
            good = good and not acc
        lines = (cert / f'm{m}-h{h0 + 1}.out').read_text().split('\n')
        R = rows(m, h0 + 1)
        excluded = False
        for l in lines:
            if not l.startswith('NONEX'):
                continue
            i, ftext = l.split(maxsplit=2)[1:]
            f = parse(ftext)
            lam = {int(x.split()[2]): parse(x.split(maxsplit=3)[3] if len(x.split()) > 3 else '0')
                   for x in lines if x.startswith(f'LAMBDA {i} ')}
            valid = len(lam) == len(R) and bool(f) and content_is_power_of_1_plus_B(f)
            for u in range(m + 1):
                acc = {}
                for r, (_, row) in enumerate(R):
                    acc = add(acc, poly_mul(lam[r], row[u])) if r in lam else acc
                valid = valid and acc == (f if u == m else {})
            excluded = excluded or valid
        print(f'm={m}: savings {h0} attained: {good}; savings {h0 + 1} excluded for every B != 1: {excluded}',
              flush=True)
        ok = ok and good and excluded
    print('ALL CERTIFICATES VALID' if ok else 'SOME CERTIFICATE FAILED')


if __name__ == '__main__':
    main()
