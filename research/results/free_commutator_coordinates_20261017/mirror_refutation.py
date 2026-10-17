"""Validate a second refutation of the or_cut inputs x or y, not x, not y, and print each line's
translation value at the Boolean point x false, y true, for the hand computation of its citation counts.

No statement tested: this checks that the mirror refutation (eliminating y before x) is a valid
refutation of the recorded checker's calculus with no unused node and distinct cedents, and prints the
line values that the citation counts w_k(a) of lem:boolean-image-values read; the counts themselves are
computed by hand in the entry from the printed values and the compiler's weakening and cut identities.
"""
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'binary_used_tag_image_20261012' / 'check_graph.py'
spec = importlib.util.spec_from_file_location('check_graph', SOURCE)
cg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cg)


def mirror():
    f = cg.Formulas()
    x, y = f.put("var", ("x",)), f.put("var", ("y",))
    nx, ny = f.neg(x), f.neg(y)
    c, empty = f.put("or", (x, y)), f.put("or")
    p = cg.Proof(f, (c, nx, ny))
    a = p.add("input", right=(c,), arg=c)
    b = p.add("input", right=(nx,), arg=nx)
    z = p.add("input", right=(ny,), arg=ny)
    ax = p.weak(p.add("axiom", (x,), (x,), arg=x), y)
    ay = p.weak(p.add("axiom", (y,), (y,), arg=y), x)
    ef = p.weak(p.weak(p.add("false", (empty,)), x), y)
    oy = p.add("or_left", (f.put("or", (y,)),), (x, y), (ay, ef), (y,))
    oc = p.add("or_left", (c,), (x, y), (ax, oy), (x, y))
    nc = p.add("neg", right=(f.neg(c), x, y), premises=(oc,), arg=c)
    ac = p.weak(p.weak(a, x), y)
    xy = p.add("cut", right=(x, y), premises=(ac, nc), arg=c)
    bz = p.weak(z, x)                                             # -> not y, x
    xx = p.add("cut", right=(x,), premises=(xy, bz), arg=y)       # -> x
    p.add("cut", premises=(xx, b), arg=x)                         # ->
    p.validate()
    return p, f, x, y


def value(poly, point):
    """A polynomial of the checker (a frozenset of monomials, each a tuple of variable formula ids) at a point."""
    total = 0
    for mono in poly:
        term = 1
        for v in mono:
            term *= point[v]
        total ^= term
    return total


if __name__ == '__main__':
    p, f, x, y = mirror()
    # monomials hold the variables' formula ids; the checker's variable polynomial is 1+x, its falsity: x=0 is x false
    point = {x: 0, y: 1}
    print(f'valid mirror refutation: {len(p.nodes)} nodes, {p.symbols()} symbols, depth {p.depth()}')
    for i, n in enumerate(p.nodes):
        print(i, n['rule'], 'premises', tuple(n['premises']),
              'translation value at x false, y true:', value(p.line_poly(i), point))
