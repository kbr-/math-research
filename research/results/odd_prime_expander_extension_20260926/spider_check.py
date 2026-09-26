#!/usr/bin/env python3
"""Spider row sets: a centre row r whose d holes h_1..h_d are each shared with one leg row n_i, every leg having
private holes. The leaf decomposition predicts a wedge summand S^{d-1} of M(G[S]) (s = d+1 rows), hence
H~_{s-2} != 0, refuting conj:expander-matching-filling at d = 5 (s = 6, degree 5, |N(U)| >= 3|U|).
Exact F_3 check for d = 2, 3, 4 with legs of degree d (FLINT ranks via matching_complex.py); d = 5 is covered by
the proof. Also checks the expansion condition of each spider."""
import itertools, json, sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import matching_complex as mc

def spider(d):
    centre = frozenset(range(d))                       # holes 0..d-1 shared with the legs
    legs, nxt = [], d
    for i in range(d):
        legs.append(frozenset([i] + list(range(nxt, nxt + d - 1)))); nxt += d - 1
    return [centre] + legs

def main():
    out = []
    for d in (2, 3, 4):
        nb = spider(d); s = len(nb)
        exp = min(len(set().union(*[nb[i] for i in U])) / len(U) for u in range(1, s + 1) for U in itertools.combinations(range(s), u))
        h = mc.reduced_homology(nb, s - 2)
        out.append({'d': d, 's': s, 'min_expansion_ratio': exp, 'H_s-2': h}); print(out[-1], flush=True)
    if '--out' in sys.argv:
        json.dump(out, open(sys.argv[sys.argv.index('--out') + 1], 'w'), indent=1)


if __name__ == '__main__':
    main()
