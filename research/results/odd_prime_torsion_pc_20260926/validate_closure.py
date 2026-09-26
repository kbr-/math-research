"""Validate torsion_pc.closure against the recorded conservativity.closure on small weak-PHP cases."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from torsion_pc import closure, generator_matrix, to_exp, Space
import conservativity
out = []
for n, d in [(3, 2), (4, 2), (2, 3), (3, 3)]:   # recorded Space enumerates the whole cube, so nv <= 12
    nv = (n + 1) * n
    rows, cols, G = generator_matrix(n, d)
    space = Space(nv, 0, d); old = conservativity.Space(nv, 0, d)
    assert set(old.mons) == set(space.mons)   # same monomials; order within a degree may differ
    gens = [g for g in ({to_exp(m, nv): c % 3 for m, c in r.items() if c % 3} for r in rows) if g]
    a = closure(space, gens)[0].shape[0]; b = conservativity.closure(old, gens)[0].shape[0]
    out.append(dict(n=n, d=d, new=a, recorded=b)); print(out[-1], flush=True)
json.dump(out, open(os.path.join(HERE, 'validate_closure.json'), 'w'), indent=1)
