"""Independent check of the base-block certificates written by bmd_four_base_block.py.

For each m <= 7 it rebuilds the condition rows from their definition (bmd_four_base_block.rows) and
checks over F_2[y1, y2, B], by expanding polynomials in Python:
  * at h = ceil(m/2): the EXIST vector w satisfies every condition, sum_u w_u X_{row,u} = 0, and
    its last component is 1 (so savings ceil(m/2) are attained for every B, and every l after
    multiplying by y1^l);
  * at h = ceil(m/2)+1: the NONEX polynomial f is nonzero, free of B, and equals
    sum_r LAMBDA_r row_r in the last coordinate while the other coordinates cancel, i.e.
    sum_r LAMBDA_r row_r = f e_m (so w^(m) = 0 for every solution and every B).
Usage: bmd_four_base_verify.py CERTDIR
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


def main():
    cert = Path(sys.argv[1])
    ok = True
    for m in range(1, 8):
        h0 = (m + 1) // 2
        lines = (cert / f'm{m}-h{h0}.out').read_text().split('\n')
        w = {int(l.split()[1]): parse(l.split(maxsplit=2)[2]) for l in lines if l.startswith('EXIST')}
        good = len(w) == m + 1 and w[m] == {(0, 0, 0): 1}
        for _, row in rows(m, h0):
            acc = {}
            for u in range(m + 1):
                acc = add(acc, poly_mul(w[u], row[u]))
            good = good and not acc
        lines = (cert / f'm{m}-h{h0 + 1}.out').read_text().split('\n')
        f = parse(next(l for l in lines if l.startswith('NONEX')).split(maxsplit=1)[1])
        lam = {int(l.split()[1]): parse(l.split(maxsplit=2)[2]) for l in lines if l.startswith('LAMBDA')}
        R = rows(m, h0 + 1)
        bad = len(lam) != len(R) or not f or any(k[2] for k in f)
        for u in range(m + 1):
            acc = {}
            for r, (_, row) in enumerate(R):
                acc = add(acc, poly_mul(lam[r], row[u]))
            target = f if u == m else {}
            bad = bad or acc != target
        print(f'm={m}: savings {h0} attained: {good}; savings {h0 + 1} excluded: {not bad}', flush=True)
        ok = ok and good and not bad
    print('ALL CERTIFICATES VALID' if ok else 'SOME CERTIFICATE FAILED')


if __name__ == '__main__':
    main()
