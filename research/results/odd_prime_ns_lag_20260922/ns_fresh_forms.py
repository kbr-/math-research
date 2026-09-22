"""Record the fresh blocks used by the NS tests (odd-prime thread, 22 Sept 2026).
ns_lag.py draws each fresh block with conservativity.make(tag, v, D, 3, h, seed, 'random', 2) and skips
the pair when that draw changes the base.  This script repeats the deterministic draws and records,
for each (base, h): whether the base is unchanged, the fresh forms, which forms are degenerate
(a form never vanishing on {0,1}^v makes its input 1 - L^2 identically zero; the recorded ones have
the shape a*x_k + a), and the number of monomials of the full space.
Usage: ns_fresh_forms.py   (writes ns_fresh_forms.json)"""
import itertools, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'odd_prime_c3_conservativity_20260922'))
from conservativity import make, monomials, CONFIGS

def degenerate(form, v):
    coeffs, c0 = form
    return all((sum(c * x[k] for k, c in coeffs.items()) + c0) % 3 for x in itertools.product(range(2), repeat=v))

out = []
for cfg, hs in (('r3d6', (2, 3, 4, 5)), ('r3d8', (2, 3, 4))):
    for job in CONFIGS[cfg]:
        inst0 = make(*job); v, D = inst0['v'], inst0['D']; tA = sum(len(b) for b in inst0['base'])
        for h in hs:
            inst = make(job[0], v, D, job[3], h, job[5], 'random', job[7])
            same = inst['base'] == inst0['base']
            out.append(dict(config=cfg, name=inst0['name'], D=D, h=h, base_unchanged=same,
                            fresh=[[{str(k): c for k, c in f[0].items()}, f[1]] for f in inst['fresh']],
                            degenerate_fresh=[degenerate(f, v) for f in inst['fresh']] if same else None,
                            degenerate_base=[[degenerate(f, v) for f in b] for b in inst0['base']],
                            cols=len(monomials(v, tA + h, D)) if same else None))
json.dump(out, open(os.path.join(HERE, 'ns_fresh_forms.json'), 'w'), indent=1)
used = [r for r in out if r['base_unchanged']]
print(len(out), 'pairs;', len(used), 'used;', sum(any(r['degenerate_fresh']) for r in used), 'with a degenerate fresh input;',
      'bases with a degenerate input:', sorted({r['name'] for r in out if any(any(b) for b in r['degenerate_base'])}),
      'max cols D=6:', max(r['cols'] for r in used if r['D'] == 6), 'cols D=8:', sorted({(r['h'], r['cols']) for r in used if r['D'] == 8}))
